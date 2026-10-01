"""Legal Vault endpoints: list, upload (with SHA-256), export affidavit."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.core.dependencies import CurrentUserDep, DBDep, PaginationDep
from app.schemas.common import PaginatedResponse
from app.schemas.legal import (
    ExportAffidavitResponse,
    LegalEventOut,
    UploadLegalEventResponse,
)
from app.services import legal_service
from app.utils.pagination import paginate

router = APIRouter(prefix="/legal", tags=["Legal"])


@router.get("/events", response_model=PaginatedResponse[LegalEventOut])
async def list_legal_events(current_user: CurrentUserDep, db: DBDep, pagination: PaginationDep):
    events, total = await legal_service.list_legal_events(
        db, current_user, offset=pagination.offset, limit=pagination.limit
    )
    return paginate(
        items=[LegalEventOut.model_validate(e) for e in events],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.post("/events/upload", response_model=UploadLegalEventResponse, status_code=201)
async def upload_legal_event(
    current_user: CurrentUserDep,
    db: DBDep,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    incident_date: Optional[date] = Form(None),
    location: Optional[str] = Form(None),
    video: UploadFile = File(..., description="Dashcam video file"),
):
    """Upload a dashcam clip; SHA-256 is computed server-side for Sec 65B."""
    event = await legal_service.upload_legal_event(
        db, current_user, title, description, incident_date, location, video
    )
    return UploadLegalEventResponse(
        event_id=event.id,
        video_url=event.video_url,
        video_sha256=event.video_sha256,
        message="Legal event uploaded and certified",
    )


@router.get("/events/{event_id}/export", response_model=ExportAffidavitResponse)
async def export_affidavit(event_id: int, current_user: CurrentUserDep, db: DBDep):
    """Generate and return a Sec 65B affidavit PDF for the legal event."""
    event = await legal_service.export_affidavit(db, current_user, event_id)
    return ExportAffidavitResponse(
        event_id=event.id,
        affidavit_pdf_url=event.affidavit_pdf_url,
        video_sha256=event.video_sha256,
        message="Affidavit generated",
    )
