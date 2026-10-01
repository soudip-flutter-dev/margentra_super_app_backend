"""LegalEvent ORM model — dashcam clip with Sec 65B SHA-256 certification."""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class LegalEvent(Base, TimestampMixin):
    __tablename__ = "legal_events"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    incident_date: Mapped[Optional[sa.Date]] = mapped_column(sa.Date, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)

    video_url: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)
    video_sha256: Mapped[Optional[str]] = mapped_column(sa.String(64), nullable=True)
    # SHA-256 hex digest for Sec 65B chain-of-custody

    affidavit_pdf_url: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)
    is_certified: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="legal_events")
