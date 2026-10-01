"""Trip and TripTelemetry ORM models."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Trip(Base, TimestampMixin):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        sa.Integer, sa.ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[str] = mapped_column(sa.String(20), nullable=False, default="active")
    # "active" | "completed" | "cancelled"

    start_lat: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    start_lng: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    end_lat: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    end_lng: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)

    distance_km: Mapped[Decimal] = mapped_column(sa.Numeric(10, 3), default=Decimal("0"), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)

    avg_speed_kmh: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    max_speed_kmh: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    harsh_braking_count: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)
    harsh_acceleration_count: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)
    over_speed_count: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)

    mgc_earned: Mapped[Decimal] = mapped_column(sa.Numeric(14, 4), default=Decimal("0"), nullable=False)
    civil_score_delta: Mapped[float] = mapped_column(sa.Float, default=0.0, nullable=False)

    started_at: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[sa.DateTime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="trips")
    telemetry: Mapped[list["TripTelemetry"]] = relationship(
        "TripTelemetry", back_populates="trip", cascade="all, delete-orphan"
    )


class TripTelemetry(Base):
    __tablename__ = "trip_telemetry"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    trip_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    speed_kmh: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    rpm: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    g_force: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    engine_temp_c: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    fuel_level: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="telemetry")
