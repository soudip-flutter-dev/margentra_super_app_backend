"""Device (BLE/OBD) ORM model."""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Device(Base, TimestampMixin):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    device_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    # "ble" | "obd" | "dashcam"
    device_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    mac_address: Mapped[Optional[str]] = mapped_column(sa.String(17), nullable=True, unique=True)
    firmware_version: Mapped[Optional[str]] = mapped_column(sa.String(50), nullable=True)
    is_connected: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    last_seen_at: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="devices")
