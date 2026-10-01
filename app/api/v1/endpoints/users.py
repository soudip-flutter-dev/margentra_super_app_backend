"""User profile, vehicles, payment methods, settings, avatar endpoints."""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.core.dependencies import CurrentUserDep, DBDep
from app.models.user import AppSettings, PaymentMethod, User, Vehicle
from app.schemas.user import (
    AppSettingsOut,
    AppSettingsUpdate,
    CivilScoreOut,
    PaymentMethodCreate,
    PaymentMethodOut,
    UserProfileOut,
    UserProfileUpdate,
    VehicleCreate,
    VehicleOut,
)
from app.schemas.common import MessageResponse  # noqa: F401 kept for potential use
from app.services.storage_service import upload_file
from sqlalchemy import select

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile", response_model=UserProfileOut)
async def get_profile(current_user: CurrentUserDep):
    return current_user


@router.put("/profile", response_model=UserProfileOut)
async def update_profile(data: UserProfileUpdate, current_user: CurrentUserDep, db: DBDep):
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.email is not None:
        current_user.email = data.email
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/civil-score", response_model=CivilScoreOut)
async def get_civil_score(current_user: CurrentUserDep, db: DBDep):
    from app.models.trip import Trip  # noqa: PLC0415
    from sqlalchemy import desc  # noqa: PLC0415

    result = await db.execute(
        select(Trip)
        .where(Trip.user_id == current_user.id, Trip.status == "completed")
        .order_by(desc(Trip.ended_at))
        .limit(30)
    )
    trips = result.scalars().all()
    history = [
        {
            "date": t.ended_at,
            "score": round(current_user.civil_score - t.civil_score_delta, 2),
            "delta": t.civil_score_delta,
            "reason": f"Trip #{t.id} completed ({t.distance_km} km)",
        }
        for t in trips
    ]
    return {
        "current_score": current_user.civil_score,
        "streak_days": current_user.driving_streak_days,
        "history": history,
    }


@router.get("/vehicles", response_model=list[VehicleOut])
async def list_vehicles(current_user: CurrentUserDep, db: DBDep):
    result = await db.execute(select(Vehicle).where(Vehicle.user_id == current_user.id))
    return result.scalars().all()


@router.post("/vehicles", response_model=VehicleOut, status_code=201)
async def add_vehicle(data: VehicleCreate, current_user: CurrentUserDep, db: DBDep):
    vehicle = Vehicle(**data.model_dump(), user_id=current_user.id)
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return vehicle


@router.get("/payment-methods", response_model=list[PaymentMethodOut])
async def list_payment_methods(current_user: CurrentUserDep, db: DBDep):
    result = await db.execute(
        select(PaymentMethod).where(PaymentMethod.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/payment-methods", response_model=PaymentMethodOut, status_code=201)
async def add_payment_method(data: PaymentMethodCreate, current_user: CurrentUserDep, db: DBDep):
    pm = PaymentMethod(**data.model_dump(), user_id=current_user.id)
    db.add(pm)
    await db.commit()
    await db.refresh(pm)
    return pm


@router.get("/settings", response_model=AppSettingsOut)
async def get_settings(current_user: CurrentUserDep, db: DBDep):
    result = await db.execute(
        select(AppSettings).where(AppSettings.user_id == current_user.id)
    )
    settings_obj = result.scalar_one_or_none()
    if not settings_obj:
        settings_obj = AppSettings(user_id=current_user.id)
        db.add(settings_obj)
        await db.commit()
        await db.refresh(settings_obj)
    return settings_obj


@router.put("/settings", response_model=AppSettingsOut)
async def update_settings(data: AppSettingsUpdate, current_user: CurrentUserDep, db: DBDep):
    result = await db.execute(
        select(AppSettings).where(AppSettings.user_id == current_user.id)
    )
    settings_obj = result.scalar_one_or_none()
    if not settings_obj:
        settings_obj = AppSettings(user_id=current_user.id)
        db.add(settings_obj)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(settings_obj, field, value)
    await db.commit()
    await db.refresh(settings_obj)
    return settings_obj


@router.post("/avatar", response_model=UserProfileOut)
async def upload_avatar(
    current_user: CurrentUserDep,
    db: DBDep,
    file: UploadFile = File(...),
):
    """Upload a profile avatar image."""
    data = await file.read()
    url = await upload_file(
        data=data,
        filename=f"avatars/{current_user.id}/avatar.jpg",
        content_type=file.content_type or "image/jpeg",
    )
    current_user.avatar_url = url
    await db.commit()
    await db.refresh(current_user)
    return current_user
