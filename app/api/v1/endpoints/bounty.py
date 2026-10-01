"""Bounty Capture endpoints: list events, submit."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.core.dependencies import CurrentUserDep, DBDep, PaginationDep
from app.schemas.bounty import BountyEventOut, SubmitBountyRequest, SubmitBountyResponse
from app.schemas.common import PaginatedResponse
from app.services import bounty_service
from app.utils.pagination import paginate

router = APIRouter(prefix="/bounty", tags=["Bounty"])


@router.get("/events", response_model=PaginatedResponse[BountyEventOut])
async def list_bounty_events(db: DBDep, current_user: CurrentUserDep, pagination: PaginationDep):
    events, total = await bounty_service.list_bounty_events(
        db, offset=pagination.offset, limit=pagination.limit
    )
    return paginate(
        items=[BountyEventOut.model_validate(e) for e in events],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.post("/submit", response_model=SubmitBountyResponse, status_code=201)
async def submit_bounty(
    current_user: CurrentUserDep,
    db: DBDep,
    event_id: int = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    media: Optional[UploadFile] = File(None),
):
    data = SubmitBountyRequest(event_id=event_id, latitude=latitude, longitude=longitude, notes=notes)
    submission = await bounty_service.submit_bounty(db, current_user, data, media)
    return SubmitBountyResponse(
        submission_id=submission.id,
        event_id=submission.event_id,
        status=submission.status,
        media_url=submission.media_url,
        message="Bounty submission received, pending review",
    )
