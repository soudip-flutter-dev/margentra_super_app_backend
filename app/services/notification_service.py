"""Notification service — create and list in-app notifications."""

from __future__ import annotations

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User


async def create_notification(
    db: AsyncSession,
    user_id: int,
    title: str,
    body: str,
    category: str = "general",
    reference_id: str | None = None,
    action_url: str | None = None,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        title=title,
        body=body,
        category=category,
        reference_id=reference_id,
        action_url=action_url,
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)
    return notif


async def list_notifications(
    db: AsyncSession, user: User, offset: int = 0, limit: int = 20
) -> tuple[list[Notification], int]:
    count_res = await db.execute(
        select(func.count(Notification.id))
        .select_from(Notification)
        .where(Notification.user_id == user.id)
    )
    total = count_res.scalar_one()
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(desc(Notification.created_at))
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all()), total


async def mark_notification_read(
    db: AsyncSession, user: User, notification_id: int
) -> Notification:
    from fastapi import HTTPException, status  # noqa: PLC0415

    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user.id
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return notif
