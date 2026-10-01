"""Challan and ChallanDispute ORM models."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Challan(Base, TimestampMixin):
    __tablename__ = "challans"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        sa.Integer, sa.ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )

    challan_number: Mapped[str] = mapped_column(sa.String(100), nullable=False, unique=True)
    violation_type: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    violation_date: Mapped[Optional[sa.Date]] = mapped_column(sa.Date, nullable=True)
    issued_by: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    fine_amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(30), nullable=False, default="pending")
    # "pending" | "paid" | "disputed" | "cancelled"
    paid_at: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    rto_source_data: Mapped[Optional[dict]] = mapped_column(sa.JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="challans")
    disputes: Mapped[list["ChallanDispute"]] = relationship(
        "ChallanDispute", back_populates="challan", cascade="all, delete-orphan"
    )


class ChallanDispute(Base, TimestampMixin):
    __tablename__ = "challan_disputes"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    challan_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("challans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(sa.Text, nullable=False)
    evidence_url: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)
    status: Mapped[str] = mapped_column(sa.String(30), nullable=False, default="submitted")
    # "submitted" | "under_review" | "resolved" | "rejected"
    resolution_note: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

    challan: Mapped["Challan"] = relationship("Challan", back_populates="disputes")
