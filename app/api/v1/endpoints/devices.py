"""Device (BLE/OBD) endpoints: register and list."""

from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import CurrentUserDep, DBDep
from app.models.device import Device
from app.schemas.device import DeviceOut, RegisterDeviceRequest, RegisterDeviceResponse

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/register", response_model=RegisterDeviceResponse, status_code=201)
async def register_device(data: RegisterDeviceRequest, current_user: CurrentUserDep, db: DBDep):
    device = Device(**data.model_dump(), user_id=current_user.id)
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return RegisterDeviceResponse(
        device_id=device.id,
        device_name=device.device_name,
        message="Device registered successfully",
    )


@router.get("/list", response_model=list[DeviceOut])
async def list_devices(current_user: CurrentUserDep, db: DBDep):
    result = await db.execute(select(Device).where(Device.user_id == current_user.id))
    return result.scalars().all()
