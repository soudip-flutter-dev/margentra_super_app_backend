"""Family Circle endpoints: list members, invite, get member location."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep, DBDep
from app.schemas.family import (
    FamilyMemberOut,
    InviteMemberRequest,
    InviteMemberResponse,
    MemberLocationOut,
)
from app.services import family_service

router = APIRouter(prefix="/family", tags=["Family"])


@router.get("/members", response_model=list[FamilyMemberOut])
async def list_members(current_user: CurrentUserDep, db: DBDep):
    return await family_service.list_members(db, current_user)


@router.post("/invite", response_model=InviteMemberResponse, status_code=201)
async def invite_member(data: InviteMemberRequest, current_user: CurrentUserDep, db: DBDep):
    return await family_service.invite_member(db, current_user, data)


@router.get("/members/{member_id}/location", response_model=MemberLocationOut)
async def get_member_location(member_id: int, current_user: CurrentUserDep, db: DBDep):
    return await family_service.get_member_location(db, current_user, member_id)
