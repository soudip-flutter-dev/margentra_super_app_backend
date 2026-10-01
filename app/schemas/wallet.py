"""Pydantic schemas for Wallet and Transactions."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class WalletBalanceOut(BaseModel):
    mgc_balance: Decimal
    lifetime_earned: Decimal
    lifetime_redeemed: Decimal
    updated_at: datetime

    model_config = {"from_attributes": True}


class WalletTransactionOut(BaseModel):
    id: int
    type: str
    amount: Decimal
    description: Optional[str]
    reference_id: Optional[str]
    balance_after: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class RedeemFastagRequest(BaseModel):
    amount_mgc: Decimal
    fastag_id: str


class RedeemFastagResponse(BaseModel):
    transaction_id: int
    mgc_spent: Decimal
    new_balance: Decimal
    fastag_id: str
    message: str


class BuyStreakProtectionRequest(BaseModel):
    pass  # cost is fixed; no payload needed


class BuyStreakProtectionResponse(BaseModel):
    transaction_id: int
    mgc_spent: Decimal
    new_balance: Decimal
    protected_until: Optional[datetime]
    message: str
