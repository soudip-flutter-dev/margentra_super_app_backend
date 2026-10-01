"""Pydantic schemas for Emergency SOS endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TriggerSOSRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    message: Optional[str] = None


class TriggerSOSResponse(BaseModel):
    alert_id: int
    status: str
    contacted_numbers: list[str]
    message: str


class EmergencyContactOut(BaseModel):
    id: int
    name: str
    phone: str
    relation: Optional[str]
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpsertContactRequest(BaseModel):
    name: str
    phone: str
    relation: Optional[str] = None
    is_primary: bool = False


class RoadAssistanceRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    issue_type: str  # "flat_tyre" | "engine_failure" | "battery_dead" | "accident" | "other"
    description: Optional[str] = None


class RoadAssistanceResponse(BaseModel):
    request_id: int
    status: str
    provider_name: Optional[str]
    eta_minutes: Optional[int]
    message: str
