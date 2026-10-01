"""Pydantic schemas for Trip and Telemetry."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class StartTripRequest(BaseModel):
    vehicle_id: Optional[int] = None
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None


class StartTripResponse(BaseModel):
    trip_id: int
    started_at: datetime
    message: str


class EndTripRequest(BaseModel):
    trip_id: int
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    distance_km: Optional[Decimal] = None


class TelemetryPoint(BaseModel):
    timestamp: datetime
    speed_kmh: Optional[float] = None
    rpm: Optional[float] = None
    g_force: Optional[float] = None
    engine_temp_c: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fuel_level: Optional[float] = None


class PostTelemetryRequest(BaseModel):
    trip_id: int
    points: list[TelemetryPoint]


class PostTelemetryResponse(BaseModel):
    accepted: int
    message: str


class CurrentEarningsResponse(BaseModel):
    trip_id: int
    mgc_earned_so_far: Decimal
    distance_km: Decimal
    duration_seconds: int
    current_speed_kmh: Optional[float]


class TripSummaryOut(BaseModel):
    id: int
    status: str
    start_lat: Optional[float]
    start_lng: Optional[float]
    end_lat: Optional[float]
    end_lng: Optional[float]
    distance_km: Decimal
    duration_seconds: int
    avg_speed_kmh: Optional[float]
    max_speed_kmh: Optional[float]
    harsh_braking_count: int
    harsh_acceleration_count: int
    over_speed_count: int
    mgc_earned: Decimal
    civil_score_delta: float
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class EndTripResponse(BaseModel):
    trip: TripSummaryOut
    mgc_earned: Decimal
    civil_score_delta: float
    new_civil_score: float
    new_mgc_balance: Decimal
    message: str
