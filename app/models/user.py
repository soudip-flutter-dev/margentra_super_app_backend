"""User, Vehicle, PaymentMethod, and AppSettings ORM models."""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(sa.String(15), unique=True, nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(sa.String(255), unique=True, nullable=True, index=True)
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(sa.String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    # Civil / driving score
    civil_score: Mapped[float] = mapped_column(sa.Float, default=100.0, nullable=False)
    driving_streak_days: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)

    # Relationships
    vehicles: Mapped[list["Vehicle"]] = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")
    payment_methods: Mapped[list["PaymentMethod"]] = relationship("PaymentMethod", back_populates="owner", cascade="all, delete-orphan")
    settings: Mapped[Optional["AppSettings"]] = relationship("AppSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wallet_balance: Mapped[Optional["WalletBalance"]] = relationship("WalletBalance", back_populates="user", uselist=False, cascade="all, delete-orphan")
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    challans: Mapped[list["Challan"]] = relationship("Challan", back_populates="user", cascade="all, delete-orphan")
    legal_events: Mapped[list["LegalEvent"]] = relationship("LegalEvent", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    sos_contacts: Mapped[list["EmergencyContact"]] = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} phone={self.phone}>"


class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_number: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    make: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    model: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    year: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    fuel_type: Mapped[str] = mapped_column(sa.String(50), nullable=False, default="petrol")
    insurance_expiry: Mapped[Optional[sa.Date]] = mapped_column(sa.Date, nullable=True)
    puc_expiry: Mapped[Optional[sa.Date]] = mapped_column(sa.Date, nullable=True)
    is_primary: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="vehicles")


class PaymentMethod(Base, TimestampMixin):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(sa.String(50), nullable=False)  # "fastag" | "upi" | "card"
    identifier: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    is_default: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="payment_methods")


class AppSettings(Base, TimestampMixin):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    notifications_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    location_sharing: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    dark_mode: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    language: Mapped[str] = mapped_column(sa.String(10), default="en")
    hud_overlay: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="settings")
