"""RefreshToken and PasswordResetOTP ORM models."""

from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(sa.String(512), nullable=False, unique=True)
    expires_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[sa.DateTime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    replaced_by_id: Mapped[Optional[int]] = mapped_column(
        sa.Integer,
        sa.ForeignKey("refresh_tokens.id", ondelete="SET NULL"),
        nullable=True,
    )


class PasswordResetOTP(Base, TimestampMixin):
    __tablename__ = "password_reset_otps"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    otp_hash: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    expires_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
