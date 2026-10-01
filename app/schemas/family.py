"""Pydantic schemas for Family Circle endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FamilyMemberOut(BaseModel):
    id: int
    user_id: int
    full_name: str
    phone: str
    relation: Optional[str]
    invite_status: str
    last_lat: Optional[float]
    last_lng: Optional[float]
    last_seen_at: Optional[datetime]

    model_config = {"from_attributes": True}


class InviteMemberRequest(BaseModel):
    phone: str
    relation: Optional[str] = None


class InviteMemberResponse(BaseModel):
    member_id: int
    phone: str
    invite_status: str
    message: str


class MemberLocationOut(BaseModel):
    member_id: int
    user_id: int
    full_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    last_seen_at: Optional[datetime]
