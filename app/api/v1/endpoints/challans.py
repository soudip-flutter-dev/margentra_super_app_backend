"""e-Challan endpoints: list, sync, pay, dispute."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep, DBDep, PaginationDep
from app.schemas.challan import (
    ChallanOut,
    DisputeChallanRequest,
    DisputeOut,
    PayChallanRequest,
    PayChallanResponse,
    SyncChallanResponse,
)
from app.schemas.common import PaginatedResponse
from app.services import challan_service
from app.utils.pagination import paginate

router = APIRouter(prefix="/challan", tags=["Challan"])


@router.get("/list", response_model=PaginatedResponse[ChallanOut])
async def list_challans(current_user: CurrentUserDep, db: DBDep, pagination: PaginationDep):
    challans, total = await challan_service.list_challans(
        db, current_user, offset=pagination.offset, limit=pagination.limit
    )
    return paginate(
        items=[ChallanOut.model_validate(c) for c in challans],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.post("/sync", response_model=SyncChallanResponse)
async def sync_challans(current_user: CurrentUserDep, db: DBDep):
    """Fetch latest challans from RTO/Vahan for all registered vehicles."""
    return await challan_service.sync_challans(db, current_user)


@router.post("/pay", response_model=PayChallanResponse)
async def pay_challan(data: PayChallanRequest, current_user: CurrentUserDep, db: DBDep):
    return await challan_service.pay_challan(db, current_user, data.challan_id, data.payment_method_id)


@router.post("/dispute", response_model=DisputeOut, status_code=201)
async def dispute_challan(data: DisputeChallanRequest, current_user: CurrentUserDep, db: DBDep):
    dispute = await challan_service.dispute_challan(db, current_user, data)
    return dispute
