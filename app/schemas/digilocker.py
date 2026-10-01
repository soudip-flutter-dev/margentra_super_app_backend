"""Pydantic schemas for DigiLocker document endpoints."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    doc_type: str
    doc_number: Optional[str]
    doc_url: str
    thumbnail_url: Optional[str]
    expiry_date: Optional[date]
    is_expired: bool
    alert_days_before: int
    issued_by: Optional[str]
    issuing_state: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadDocumentResponse(BaseModel):
    document_id: int
    doc_url: str
    message: str


class ExpiryAlertOut(BaseModel):
    document_id: int
    doc_type: str
    doc_number: Optional[str]
    expiry_date: Optional[date]
    days_remaining: int
    severity: str  # "critical" | "warning" | "info"
