"""Wallet service — balance queries and MGC redemption operations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.models.wallet import WalletBalance, WalletTransaction


async def _get_or_create_wallet(db: AsyncSession, user: User) -> WalletBalance:
    result = await db.execute(select(WalletBalance).where(WalletBalance.user_id == user.id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = WalletBalance(user_id=user.id)
        db.add(wallet)
        await db.flush()
    return wallet


async def get_balance(db: AsyncSession, user: User) -> WalletBalance:
    return await _get_or_create_wallet(db, user)


async def list_transactions(
    db: AsyncSession, user: User, offset: int = 0, limit: int = 20
) -> tuple[list[WalletTransaction], int]:
    wallet = await _get_or_create_wallet(db, user)
    from sqlalchemy import func, desc  # noqa: PLC0415

    count_result = await db.execute(
        select(func.count(WalletTransaction.id))
        .select_from(WalletTransaction)
        .where(WalletTransaction.wallet_id == wallet.id)
    )
    total = count_result.scalar_one()

    result = await db.execute(
        select(WalletTransaction)
        .where(WalletTransaction.wallet_id == wallet.id)
        .order_by(desc(WalletTransaction.created_at))
        .offset(offset)
        .limit(limit)
    )
    txs = list(result.scalars().all())
    return txs, total


async def redeem_fastag(
    db: AsyncSession, user: User, amount_mgc: Decimal, fastag_id: str
) -> dict:
    wallet = await _get_or_create_wallet(db, user)
    if wallet.mgc_balance < amount_mgc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient MGC balance. Current: {wallet.mgc_balance}",
        )
    wallet.mgc_balance -= amount_mgc
    wallet.lifetime_redeemed += amount_mgc
    tx = WalletTransaction(
        wallet_id=wallet.id,
        type="redeem_fastag",
        amount=-amount_mgc,
        description=f"FASTag recharge for {fastag_id}",
        reference_id=f"fastag:{fastag_id}",
        balance_after=wallet.mgc_balance,
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return {"transaction_id": tx.id, "mgc_spent": amount_mgc, "new_balance": wallet.mgc_balance, "fastag_id": fastag_id, "message": "FASTag recharged successfully"}


async def buy_streak_protection(db: AsyncSession, user: User) -> dict:
    wallet = await _get_or_create_wallet(db, user)
    cost = Decimal(str(settings.MGC_STREAK_PROTECTION_COST))
    if wallet.mgc_balance < cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient MGC balance. Need {cost}, have {wallet.mgc_balance}",
        )
    wallet.mgc_balance -= cost
    wallet.lifetime_redeemed += cost
    protected_until = datetime.now(timezone.utc) + timedelta(days=1)
    tx = WalletTransaction(
        wallet_id=wallet.id,
        type="buy_streak_protection",
        amount=-cost,
        description="Streak protection purchased",
        balance_after=wallet.mgc_balance,
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)
    return {
        "transaction_id": tx.id,
        "mgc_spent": cost,
        "new_balance": wallet.mgc_balance,
        "protected_until": protected_until,
        "message": "Streak protection activated for 24 hours",
    }
