"""Authentication service — register, login, token refresh, password reset."""

from __future__ import annotations

import hashlib
import random
import string
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.auth import PasswordResetOTP, RefreshToken
from app.models.user import AppSettings, User
from app.models.wallet import WalletBalance
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def _utcnow() -> datetime:
    """Return UTC-aware now; safe to compare against both aware and naive DB datetimes."""
    return datetime.now(timezone.utc)


def _is_expired(dt: datetime) -> bool:
    """Compare possibly-naive DB datetime against UTC now without raising TypeError."""
    now = _utcnow()
    if dt.tzinfo is None:
        # DB returned naive datetime — treat as UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt < now


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    # Check uniqueness
    existing = await db.execute(select(User).where(User.phone == data.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered")

    if data.email:
        existing_email = await db.execute(select(User).where(User.email == data.email))
        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        full_name=data.full_name,
        phone=data.phone,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.flush()  # get user.id

    # Create default wallet balance
    wallet = WalletBalance(user_id=user.id)
    db.add(wallet)

    # Create default app settings
    app_settings = AppSettings(user_id=user.id)
    db.add(app_settings)

    await db.commit()
    await db.refresh(user)
    return user


async def login_user(db: AsyncSession, data: LoginRequest) -> TokenResponse:
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    access_token = create_access_token(user.id)
    refresh_token_raw = create_refresh_token(user.id)

    # Store hashed refresh token
    token_record = RefreshToken(
        user_id=user.id,
        token_hash=_hash_token(refresh_token_raw),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token_record)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_raw,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def logout_user(db: AsyncSession, refresh_token_raw: str) -> None:
    token_hash = _hash_token(refresh_token_raw)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False),
        )
    )
    record = result.scalar_one_or_none()
    if record:
        record.is_revoked = True
        await db.commit()


async def refresh_access_token(db: AsyncSession, refresh_token_raw: str) -> dict:
    from app.core.security import verify_refresh_token  # noqa: PLC0415

    payload = verify_refresh_token(refresh_token_raw)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_hash = _hash_token(refresh_token_raw)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked.is_(False),
        )
    )
    record = result.scalar_one_or_none()
    if not record or _is_expired(record.expires_at):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

    user_id = payload["sub"]
    new_access = create_access_token(user_id)
    return {"access_token": new_access, "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}


async def forgot_password(db: AsyncSession, phone: str) -> str:
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        # Security: don't reveal whether phone exists
        return "OTP sent if phone is registered"

    otp = _generate_otp()
    record = PasswordResetOTP(
        user_id=user.id,
        otp_hash=_hash_token(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    db.add(record)
    await db.commit()
    # In production: send OTP via SMS gateway
    return "OTP sent if phone is registered"


async def reset_password(db: AsyncSession, data: ResetPasswordRequest) -> None:
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP or phone")

    otp_hash = _hash_token(data.otp)
    otp_result = await db.execute(
        select(PasswordResetOTP).where(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.otp_hash == otp_hash,
            PasswordResetOTP.is_used.is_(False),
        )
    )
    record = otp_result.scalar_one_or_none()
    if not record or _is_expired(record.expires_at):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    user.hashed_password = hash_password(data.new_password)
    record.is_used = True
    await db.commit()
