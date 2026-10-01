"""Pydantic schemas for Challan endpoints."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ChallanOut(BaseModel):
    id: int
    challan_number: str
    violation_type: str
    violation_date: Optional[date]
    issued_by: Optional[str]
    fine_amount: Decimal
    status: str
    paid_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncChallanResponse(BaseModel):
    synced: int
    new_challans: int
    message: str


class PayChallanRequest(BaseModel):
    challan_id: int
    payment_method_id: int


class PayChallanResponse(BaseModel):
    challan_id: int
    amount_paid: Decimal
    status: str
    message: str


class DisputeChallanRequest(BaseModel):
    challan_id: int
    reason: str
    evidence_url: Optional[str] = None


class DisputeOut(BaseModel):
    id: int
    challan_id: int
    reason: str
    evidence_url: Optional[str]
    status: str
    resolution_note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
