"""Pydantic schemas for User, Vehicle, PaymentMethod, AppSettings."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, field_validator


# ── Vehicle ───────────────────────────────────────────────────────────────────
class VehicleCreate(BaseModel):
    registration_number: str
    make: str
    model: str
    year: int
    fuel_type: str = "petrol"
    insurance_expiry: Optional[date] = None
    puc_expiry: Optional[date] = None
    is_primary: bool = False


class VehicleOut(VehicleCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── PaymentMethod ─────────────────────────────────────────────────────────────
class PaymentMethodCreate(BaseModel):
    type: str  # "fastag" | "upi" | "card"
    identifier: str
    is_default: bool = False


class PaymentMethodOut(PaymentMethodCreate):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── AppSettings ────────────────────────────────────────────────────────────────
class AppSettingsUpdate(BaseModel):
    notifications_enabled: Optional[bool] = None
    location_sharing: Optional[bool] = None
    dark_mode: Optional[bool] = None
    language: Optional[str] = None
    hud_overlay: Optional[bool] = None


class AppSettingsOut(BaseModel):
    notifications_enabled: bool
    location_sharing: bool
    dark_mode: bool
    language: str
    hud_overlay: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── User Profile ───────────────────────────────────────────────────────────────
class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserProfileOut(BaseModel):
    id: int
    full_name: str
    phone: str
    email: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    civil_score: float
    driving_streak_days: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Civil Score ────────────────────────────────────────────────────────────────
class CivilScoreHistoryEntry(BaseModel):
    date: datetime
    score: float
    delta: float
    reason: str


class CivilScoreOut(BaseModel):
    current_score: float
    streak_days: int
    history: list[CivilScoreHistoryEntry]
