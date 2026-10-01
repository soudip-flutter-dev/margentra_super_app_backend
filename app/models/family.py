"""FamilyCircle and FamilyMember ORM models."""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class FamilyCircle(Base, TimestampMixin):
    __tablename__ = "family_circles"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    members: Mapped[list["FamilyMember"]] = relationship(
        "FamilyMember", back_populates="circle", cascade="all, delete-orphan"
    )


class FamilyMember(Base, TimestampMixin):
    __tablename__ = "family_members"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    circle_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("family_circles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relation: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    invite_status: Mapped[str] = mapped_column(sa.String(30), nullable=False, default="pending")
    # "pending" | "accepted" | "declined"

    last_lat: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    last_lng: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    last_seen_at: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    circle: Mapped["FamilyCircle"] = relationship("FamilyCircle", back_populates="members")
