"""Trip / HUD endpoints: start, end, telemetry, earnings, history."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep, DBDep, PaginationDep
from app.schemas.trip import (
    CurrentEarningsResponse,
    EndTripRequest,
    EndTripResponse,
    PostTelemetryRequest,
    PostTelemetryResponse,
    StartTripRequest,
    StartTripResponse,
    TripSummaryOut,
)
from app.schemas.common import PaginatedResponse
from app.services import trip_service
from app.utils.pagination import paginate
from app.ws.events import push_telemetry
from sqlalchemy import func, select, desc
from app.models.trip import Trip

router = APIRouter(prefix="/trip", tags=["Trip"])


@router.post("/start", response_model=StartTripResponse, status_code=201)
async def start_trip(data: StartTripRequest, current_user: CurrentUserDep, db: DBDep):
    trip = await trip_service.start_trip(db, current_user, data)
    return StartTripResponse(trip_id=trip.id, started_at=trip.started_at, message="Trip started")


@router.post("/end", response_model=EndTripResponse)
async def end_trip(data: EndTripRequest, current_user: CurrentUserDep, db: DBDep):
    result = await trip_service.end_trip(db, current_user, data)
    return EndTripResponse(
        trip=TripSummaryOut.model_validate(result["trip"]),
        mgc_earned=result["mgc_earned"],
        civil_score_delta=result["civil_score_delta"],
        new_civil_score=result["new_civil_score"],
        new_mgc_balance=result["new_mgc_balance"],
        message="Trip ended successfully",
    )


@router.post("/telemetry", response_model=PostTelemetryResponse)
async def post_telemetry(data: PostTelemetryRequest, current_user: CurrentUserDep, db: DBDep):
    accepted = await trip_service.post_telemetry(db, current_user, data)
    # Broadcast last telemetry point to WebSocket subscribers
    if data.points:
        last = data.points[-1]
        await push_telemetry(
            data.trip_id,
            {
                "speed": last.speed_kmh,
                "rpm": last.rpm,
                "g_force": last.g_force,
                "engine_temp": last.engine_temp_c,
                "timestamp": last.timestamp.isoformat(),
            },
        )
    return PostTelemetryResponse(accepted=accepted, message=f"{accepted} telemetry points stored")


@router.get("/earnings/current", response_model=CurrentEarningsResponse)
async def get_current_earnings(current_user: CurrentUserDep, db: DBDep):
    result = await trip_service.get_current_earnings(db, current_user)
    return result


@router.get("/history", response_model=PaginatedResponse[TripSummaryOut])
async def get_trip_history(current_user: CurrentUserDep, db: DBDep, pagination: PaginationDep):
    count_res = await db.execute(
        select(func.count(Trip.id))
        .select_from(Trip)
        .where(Trip.user_id == current_user.id, Trip.status == "completed")
    )
    total = count_res.scalar_one()
    result = await db.execute(
        select(Trip)
        .where(Trip.user_id == current_user.id, Trip.status == "completed")
        .order_by(desc(Trip.ended_at))
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    trips = result.scalars().all()
    return paginate(
        items=[TripSummaryOut.model_validate(t) for t in trips],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )
