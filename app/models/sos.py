"""Emergency SOS models: EmergencyContact, SOSAlert, RoadAssistanceRequest."""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class EmergencyContact(Base, TimestampMixin):
    __tablename__ = "emergency_contacts"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(sa.String(15), nullable=False)
    relation: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="sos_contacts")


class SOSAlert(Base, TimestampMixin):
    __tablename__ = "sos_alerts"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    latitude: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    message: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    status: Mapped[str] = mapped_column(sa.String(30), nullable=False, default="triggered")
    # "triggered" | "acknowledged" | "resolved"
    contacted_numbers: Mapped[Optional[list]] = mapped_column(sa.JSON, nullable=True)
    resolved_at: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)


class RoadAssistanceRequest(Base, TimestampMixin):
    __tablename__ = "road_assistance_requests"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    latitude: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    issue_type: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    # "flat_tyre" | "engine_failure" | "battery_dead" | "accident" | "other"
    description: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    status: Mapped[str] = mapped_column(sa.String(30), nullable=False, default="pending")
    # "pending" | "dispatched" | "completed"
    provider_name: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    eta_minutes: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
