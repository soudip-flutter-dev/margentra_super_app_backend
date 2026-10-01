"""Trip service — start/end trip, telemetry ingestion, MGC + civil score."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.trip import Trip, TripTelemetry
from app.models.user import User
from app.models.wallet import WalletBalance, WalletTransaction
from app.schemas.trip import (
    EndTripRequest,
    PostTelemetryRequest,
    StartTripRequest,
)


# ── Civil score calculation ────────────────────────────────────────────────────
def _compute_civil_score_delta(trip: Trip) -> float:
    """Simple heuristic; replace with ML model in production."""
    delta = 0.0
    if trip.distance_km and trip.distance_km > 0:
        delta += float(trip.distance_km) * 0.05
    delta -= trip.harsh_braking_count * 2.0
    delta -= trip.harsh_acceleration_count * 1.5
    delta -= trip.over_speed_count * 3.0
    return round(max(-20.0, min(10.0, delta)), 2)


# ── MGC earning calculation ────────────────────────────────────────────────────
def _compute_mgc_earned(trip: Trip, user: User) -> Decimal:
    base = Decimal(str(trip.distance_km)) * Decimal(str(settings.MGC_PER_KM_RATE))
    streak_bonus = Decimal("0")
    if user.driving_streak_days >= settings.MGC_BONUS_STREAK_DAYS:
        streak_bonus = base * Decimal("0.1")  # +10% for streak
    return (base + streak_bonus).quantize(Decimal("0.0001"))


async def start_trip(db: AsyncSession, user: User, data: StartTripRequest) -> Trip:
    # Check for already-active trip
    result = await db.execute(
        select(Trip).where(Trip.user_id == user.id, Trip.status == "active")
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A trip is already active. End the current trip first.",
        )
    trip = Trip(
        user_id=user.id,
        vehicle_id=data.vehicle_id,
        status="active",
        start_lat=data.start_lat,
        start_lng=data.start_lng,
        started_at=datetime.now(timezone.utc),
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip


async def end_trip(db: AsyncSession, user: User, data: EndTripRequest) -> dict:
    result = await db.execute(
        select(Trip).where(Trip.id == data.trip_id, Trip.user_id == user.id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trip is not active")

    trip.status = "completed"
    trip.ended_at = datetime.now(timezone.utc)
    trip.end_lat = data.end_lat
    trip.end_lng = data.end_lng
    if data.distance_km is not None:
        trip.distance_km = data.distance_km

    if trip.started_at:
        started = trip.started_at.replace(tzinfo=timezone.utc) if trip.started_at.tzinfo is None else trip.started_at
        ended = trip.ended_at.replace(tzinfo=timezone.utc) if trip.ended_at.tzinfo is None else trip.ended_at
        trip.duration_seconds = max(0, int((ended - started).total_seconds()))

    # Compute scores & earnings
    score_delta = _compute_civil_score_delta(trip)
    mgc_earned = _compute_mgc_earned(trip, user)

    trip.civil_score_delta = score_delta
    trip.mgc_earned = mgc_earned

    # Update user civil score
    user.civil_score = max(0.0, min(1000.0, user.civil_score + score_delta))
    user.driving_streak_days += 1

    # Update wallet
    wallet_result = await db.execute(
        select(WalletBalance).where(WalletBalance.user_id == user.id)
    )
    wallet = wallet_result.scalar_one_or_none()
    if wallet:
        wallet.mgc_balance += mgc_earned
        wallet.lifetime_earned += mgc_earned
        tx = WalletTransaction(
            wallet_id=wallet.id,
            type="earn",
            amount=mgc_earned,
            description=f"Trip #{trip.id} earnings",
            reference_id=f"trip:{trip.id}",
            balance_after=wallet.mgc_balance,
        )
        db.add(tx)

    await db.commit()
    await db.refresh(trip)

    return {
        "trip": trip,
        "mgc_earned": mgc_earned,
        "civil_score_delta": score_delta,
        "new_civil_score": user.civil_score,
        "new_mgc_balance": wallet.mgc_balance if wallet else Decimal("0"),
    }


async def post_telemetry(
    db: AsyncSession, user: User, data: PostTelemetryRequest
) -> int:
    result = await db.execute(
        select(Trip).where(Trip.id == data.trip_id, Trip.user_id == user.id)
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if trip.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trip is not active")

    records = []
    for pt in data.points:
        records.append(
            TripTelemetry(
                trip_id=trip.id,
                timestamp=pt.timestamp,
                speed_kmh=pt.speed_kmh,
                rpm=pt.rpm,
                g_force=pt.g_force,
                engine_temp_c=pt.engine_temp_c,
                latitude=pt.latitude,
                longitude=pt.longitude,
                fuel_level=pt.fuel_level,
            )
        )
        # Detect harsh events
        if pt.g_force and pt.g_force > 0.5:
            trip.harsh_braking_count += 1
        if pt.speed_kmh and pt.speed_kmh > 120:
            trip.over_speed_count += 1

    db.add_all(records)
    await db.commit()
    return len(records)


async def get_current_earnings(db: AsyncSession, user: User) -> dict:
    result = await db.execute(
        select(Trip).where(Trip.user_id == user.id, Trip.status == "active")
    )
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active trip")

    mgc_so_far = _compute_mgc_earned(trip, user)

    # Get latest telemetry for current speed
    from sqlalchemy import desc  # noqa: PLC0415
    tel_result = await db.execute(
        select(TripTelemetry)
        .where(TripTelemetry.trip_id == trip.id)
        .order_by(desc(TripTelemetry.timestamp))
        .limit(1)
    )
    latest = tel_result.scalar_one_or_none()

    return {
        "trip_id": trip.id,
        "mgc_earned_so_far": mgc_so_far,
        "distance_km": trip.distance_km,
        "duration_seconds": trip.duration_seconds,
        "current_speed_kmh": latest.speed_kmh if latest else None,
    }
