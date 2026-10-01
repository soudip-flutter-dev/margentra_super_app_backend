"""Family circle service — member management and live location."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family import FamilyCircle, FamilyMember
from app.models.user import User
from app.schemas.family import InviteMemberRequest


async def _get_or_create_circle(db: AsyncSession, user: User) -> FamilyCircle:
    result = await db.execute(
        select(FamilyCircle).where(FamilyCircle.owner_id == user.id)
    )
    circle = result.scalar_one_or_none()
    if not circle:
        circle = FamilyCircle(name=f"{user.full_name}'s Family", owner_id=user.id)
        db.add(circle)
        await db.flush()
    return circle


async def list_members(db: AsyncSession, user: User) -> list[dict]:
    circle = await _get_or_create_circle(db, user)
    result = await db.execute(
        select(FamilyMember, User)
        .join(User, FamilyMember.user_id == User.id)
        .where(FamilyMember.circle_id == circle.id)
    )
    rows = result.all()
    out = []
    for member, member_user in rows:
        out.append(
            {
                "id": member.id,
                "user_id": member.user_id,
                "full_name": member_user.full_name,
                "phone": member_user.phone,
                "relation": member.relation,
                "invite_status": member.invite_status,
                "last_lat": member.last_lat,
                "last_lng": member.last_lng,
                "last_seen_at": member.last_seen_at,
            }
        )
    return out


async def invite_member(
    db: AsyncSession, user: User, data: InviteMemberRequest
) -> dict:
    # Find user by phone
    result = await db.execute(select(User).where(User.phone == data.phone))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with that phone not found")
    if target_user.id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot invite yourself")

    circle = await _get_or_create_circle(db, user)

    existing = await db.execute(
        select(FamilyMember).where(
            FamilyMember.circle_id == circle.id, FamilyMember.user_id == target_user.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already in circle")

    member = FamilyMember(
        circle_id=circle.id,
        user_id=target_user.id,
        relation=data.relation,
        invite_status="pending",
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return {
        "member_id": member.id,
        "phone": data.phone,
        "invite_status": member.invite_status,
        "message": "Invite sent successfully",
    }


async def get_member_location(
    db: AsyncSession, user: User, member_id: int
) -> dict:
    circle = await _get_or_create_circle(db, user)
    result = await db.execute(
        select(FamilyMember, User)
        .join(User, FamilyMember.user_id == User.id)
        .where(FamilyMember.id == member_id, FamilyMember.circle_id == circle.id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in your family circle")
    member, member_user = row
    return {
        "member_id": member.id,
        "user_id": member.user_id,
        "full_name": member_user.full_name,
        "latitude": member.last_lat,
        "longitude": member.last_lng,
        "last_seen_at": member.last_seen_at,
    }
