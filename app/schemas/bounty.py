"""Pydantic schemas for Bounty Capture endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class BountyEventOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    event_type: str
    reward_mgc: Decimal
    is_active: bool
    deadline: Optional[datetime]
    max_submissions: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmitBountyRequest(BaseModel):
    event_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None
    # media uploaded separately via form-data


class SubmitBountyResponse(BaseModel):
    submission_id: int
    event_id: int
    status: str
    media_url: Optional[str]
    message: str
