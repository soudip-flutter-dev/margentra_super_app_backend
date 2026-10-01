"""DigiLocker Document ORM model."""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    doc_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    # "dl" | "rc" | "insurance" | "puc" | "other"
    doc_number: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    doc_url: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)

    expiry_date: Mapped[Optional[sa.Date]] = mapped_column(sa.Date, nullable=True)
    is_expired: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    alert_days_before: Mapped[int] = mapped_column(sa.Integer, default=30, nullable=False)
    # Days before expiry to trigger a notification

    issued_by: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    issuing_state: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="documents")
