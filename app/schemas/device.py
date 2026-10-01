"""Pydantic schemas for Device endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RegisterDeviceRequest(BaseModel):
    device_type: str  # "ble" | "obd" | "dashcam"
    device_name: str
    mac_address: Optional[str] = None
    firmware_version: Optional[str] = None


class DeviceOut(BaseModel):
    id: int
    device_type: str
    device_name: str
    mac_address: Optional[str]
    firmware_version: Optional[str]
    is_connected: bool
    last_seen_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterDeviceResponse(BaseModel):
    device_id: int
    device_name: str
    message: str
