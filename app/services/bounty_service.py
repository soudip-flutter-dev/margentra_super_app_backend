"""Bounty service — list events and submit bounty reports."""

from __future__ import annotations


from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bounty import BountyEvent, BountySubmission
from app.models.user import User
from app.schemas.bounty import SubmitBountyRequest
from app.services.storage_service import upload_file


async def list_bounty_events(
    db: AsyncSession, offset: int = 0, limit: int = 20
) -> tuple[list[BountyEvent], int]:
    count_res = await db.execute(
        select(func.count(BountyEvent.id))
        .select_from(BountyEvent)
        .where(BountyEvent.is_active.is_(True))
    )
    total = count_res.scalar_one()
    result = await db.execute(
        select(BountyEvent)
        .where(BountyEvent.is_active.is_(True))
        .order_by(desc(BountyEvent.created_at))
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all()), total


async def submit_bounty(
    db: AsyncSession,
    user: User,
    data: SubmitBountyRequest,
    media_file: UploadFile | None = None,
) -> BountySubmission:
    event_res = await db.execute(
        select(BountyEvent).where(BountyEvent.id == data.event_id, BountyEvent.is_active.is_(True))
    )
    event = event_res.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bounty event not found or inactive")

    media_url = None
    if media_file:
        media_bytes = await media_file.read()
        ext = media_file.filename.rsplit(".", 1)[-1] if media_file.filename and "." in media_file.filename else "jpg"
        media_url = await upload_file(
            data=media_bytes,
            filename=f"bounty/{user.id}/{data.event_id}_{media_file.filename}",
            content_type=media_file.content_type or "image/jpeg",
        )

    submission = BountySubmission(
        event_id=data.event_id,
        user_id=user.id,
        latitude=data.latitude,
        longitude=data.longitude,
        media_url=media_url,
        notes=data.notes,
        status="pending",
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission
