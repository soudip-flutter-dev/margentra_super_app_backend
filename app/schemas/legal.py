"""Pydantic schemas for Legal Vault endpoints."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class LegalEventOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    incident_date: Optional[date]
    location: Optional[str]
    video_url: Optional[str]
    video_sha256: Optional[str]
    affidavit_pdf_url: Optional[str]
    is_certified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadLegalEventResponse(BaseModel):
    event_id: int
    video_url: str
    video_sha256: str
    message: str


class ExportAffidavitResponse(BaseModel):
    event_id: int
    affidavit_pdf_url: str
    video_sha256: str
    message: str
