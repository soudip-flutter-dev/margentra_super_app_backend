"""Pydantic schemas for Notification endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    category: str
    is_read: bool
    reference_id: Optional[str]
    action_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MarkReadResponse(BaseModel):
    notification_id: int
    is_read: bool
    message: str
