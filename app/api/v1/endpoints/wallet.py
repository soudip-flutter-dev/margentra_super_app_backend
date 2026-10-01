"""Wallet endpoints: balance, transactions, FastTag redeem, streak protection."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep, DBDep, PaginationDep
from app.schemas.wallet import (
    BuyStreakProtectionRequest,
    BuyStreakProtectionResponse,
    RedeemFastagRequest,
    RedeemFastagResponse,
    WalletBalanceOut,
    WalletTransactionOut,
)
from app.schemas.common import PaginatedResponse
from app.services import wallet_service
from app.utils.pagination import paginate

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/balance", response_model=WalletBalanceOut)
async def get_balance(current_user: CurrentUserDep, db: DBDep):
    return await wallet_service.get_balance(db, current_user)


@router.get("/transactions", response_model=PaginatedResponse[WalletTransactionOut])
async def list_transactions(current_user: CurrentUserDep, db: DBDep, pagination: PaginationDep):
    txs, total = await wallet_service.list_transactions(
        db, current_user, offset=pagination.offset, limit=pagination.limit
    )
    return paginate(
        items=[WalletTransactionOut.model_validate(tx) for tx in txs],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.post("/redeem/fastag", response_model=RedeemFastagResponse)
async def redeem_fastag(data: RedeemFastagRequest, current_user: CurrentUserDep, db: DBDep):
    return await wallet_service.redeem_fastag(db, current_user, data.amount_mgc, data.fastag_id)


@router.post("/buy/streak-protection", response_model=BuyStreakProtectionResponse)
async def buy_streak_protection(current_user: CurrentUserDep, db: DBDep):
    return await wallet_service.buy_streak_protection(db, current_user)
