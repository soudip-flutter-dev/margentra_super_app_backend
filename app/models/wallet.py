"""WalletBalance and WalletTransaction ORM models."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class WalletBalance(Base, TimestampMixin):
    __tablename__ = "wallet_balances"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    mgc_balance: Mapped[Decimal] = mapped_column(sa.Numeric(14, 4), default=Decimal("0"), nullable=False)
    lifetime_earned: Mapped[Decimal] = mapped_column(sa.Numeric(14, 4), default=Decimal("0"), nullable=False)
    lifetime_redeemed: Mapped[Decimal] = mapped_column(sa.Numeric(14, 4), default=Decimal("0"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="wallet_balance")
    transactions: Mapped[list["WalletTransaction"]] = relationship(
        "WalletTransaction", back_populates="wallet", cascade="all, delete-orphan"
    )


class WalletTransaction(Base, TimestampMixin):
    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    wallet_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("wallet_balances.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    # "earn" | "redeem_fastag" | "buy_streak_protection" | "bounty_reward" | "challan_penalty"
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(14, 4), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    balance_after: Mapped[Decimal] = mapped_column(sa.Numeric(14, 4), nullable=False)

    wallet: Mapped["WalletBalance"] = relationship("WalletBalance", back_populates="transactions")
