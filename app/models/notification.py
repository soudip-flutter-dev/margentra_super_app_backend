"""Notification ORM model."""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    body: Mapped[str] = mapped_column(sa.Text, nullable=False)
    category: Mapped[str] = mapped_column(sa.String(50), nullable=False, default="general")
    # "challan" | "document_expiry" | "bounty" | "sos" | "wallet" | "general"
    is_read: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    reference_id: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    # e.g. "challan:42" to deep-link from notification to record
    action_url: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notifications")
