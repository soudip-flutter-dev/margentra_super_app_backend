"""Notification endpoints: list and mark as read."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep, DBDep, PaginationDep
from app.schemas.common import PaginatedResponse
from app.schemas.notification import MarkReadResponse, NotificationOut
from app.services import notification_service
from app.utils.pagination import paginate

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=PaginatedResponse[NotificationOut])
async def list_notifications(current_user: CurrentUserDep, db: DBDep, pagination: PaginationDep):
    notifs, total = await notification_service.list_notifications(
        db, current_user, offset=pagination.offset, limit=pagination.limit
    )
    return paginate(
        items=[NotificationOut.model_validate(n) for n in notifs],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.put("/{notification_id}/read", response_model=MarkReadResponse)
async def mark_read(notification_id: int, current_user: CurrentUserDep, db: DBDep):
    notif = await notification_service.mark_notification_read(db, current_user, notification_id)
    return MarkReadResponse(
        notification_id=notif.id,
        is_read=notif.is_read,
        message="Notification marked as read",
    )
