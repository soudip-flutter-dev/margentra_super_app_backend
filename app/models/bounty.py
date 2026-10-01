"""Bounty Capture ORM models."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class BountyEvent(Base, TimestampMixin):
    __tablename__ = "bounty_events"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    event_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    # "pothole" | "red_light_jump" | "wrong_way" | "hazard" | "other"
    reward_mgc: Mapped[Decimal] = mapped_column(sa.Numeric(10, 4), nullable=False, default=Decimal("10"))
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    deadline: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    max_submissions: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)

    submissions: Mapped[list["BountySubmission"]] = relationship(
        "BountySubmission", back_populates="event", cascade="all, delete-orphan"
    )


class BountySubmission(Base, TimestampMixin):
    __tablename__ = "bounty_submissions"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("bounty_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    latitude: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    media_url: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    status: Mapped[str] = mapped_column(sa.String(30), nullable=False, default="pending")
    # "pending" | "approved" | "rejected"
    mgc_awarded: Mapped[Decimal] = mapped_column(sa.Numeric(10, 4), default=Decimal("0"), nullable=False)
    reviewed_at: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    event: Mapped["BountyEvent"] = relationship("BountyEvent", back_populates="submissions")
