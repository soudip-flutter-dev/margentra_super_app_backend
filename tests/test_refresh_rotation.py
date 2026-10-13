"""Tests for mobile refresh token rotation, grace window, breach detection, and session security."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import RefreshToken
from app.models.user import User


@pytest.mark.asyncio
async def test_refresh_token_rotation_success(client: AsyncClient, db_session: AsyncSession):
    """AC-1 & AC-2: Verify refresh token rotates and returns fresh TokenResponse pair."""
    phone = "+919876500001"
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Rotation Tester",
            "phone": phone,
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": phone, "password": "Password123"},
    )
    assert login_resp.status_code == 200
    token1 = login_resp.json()["refresh_token"]
    access1 = login_resp.json()["access_token"]

    # First rotation
    refresh_resp1 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token1},
    )
    assert refresh_resp1.status_code == 200
    data1 = refresh_resp1.json()
    assert "access_token" in data1
    assert "refresh_token" in data1
    assert data1["token_type"] == "bearer"
    token2 = data1["refresh_token"]
    access2 = data1["access_token"]
    assert token2 != token1
    assert access2 != access1

    # Verify database record for token1 was marked revoked with replaced_by_id
    records = (
        await db_session.execute(
            select(RefreshToken).order_by(RefreshToken.id.asc())
        )
    ).scalars().all()
    user_records = [r for r in records if r.user_id == (await db_session.execute(select(User.id).where(User.phone == phone))).scalar_one()]
    assert len(user_records) >= 2
    old_record = user_records[-2]
    new_record = user_records[-1]
    assert old_record.is_revoked is True
    assert old_record.revoked_at is not None
    assert old_record.replaced_by_id == new_record.id
    assert new_record.is_revoked is False

    # Second rotation using token2
    refresh_resp2 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token2},
    )
    assert refresh_resp2.status_code == 200
    data2 = refresh_resp2.json()
    token3 = data2["refresh_token"]
    assert token3 != token2


@pytest.mark.asyncio
async def test_refresh_token_inactive_user_rejected(client: AsyncClient, db_session: AsyncSession):
    """AC-3: Inactive, suspended, or deleted users cannot rotate tokens."""
    phone = "+919876500002"
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Inactive User",
            "phone": phone,
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": phone, "password": "Password123"},
    )
    token = login_resp.json()["refresh_token"]

    # Deactivate the user
    await db_session.execute(
        update(User).where(User.phone == phone).values(is_active=False)
    )
    await db_session.commit()

    # Attempt refresh
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token},
    )
    assert refresh_resp.status_code == 401
    assert "inactive" in refresh_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_grace_window_retry(client: AsyncClient, db_session: AsyncSession):
    """AC-4: Retrying with a recently rotated token within thirty seconds succeeds."""
    phone = "+919876500003"
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Grace User",
            "phone": phone,
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": phone, "password": "Password123"},
    )
    token1 = login_resp.json()["refresh_token"]

    # Primary rotation
    resp1 = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token1},
    )
    assert resp1.status_code == 200

    # Immediate duplicate request with token1 (simulating network dropout retry)
    retry_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token1},
    )
    assert retry_resp.status_code == 200
    retry_data = retry_resp.json()
    assert "access_token" in retry_data
    assert "refresh_token" in retry_data


@pytest.mark.asyncio
async def test_refresh_token_breach_detection_revokes_all(
    client: AsyncClient, db_session: AsyncSession
):
    """AC-5: Token reuse outside the grace window revokes all active sessions for the user."""
    phone = "+919876500004"
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Breach User",
            "phone": phone,
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": phone, "password": "Password123"},
    )
    token1 = login_resp.json()["refresh_token"]

    # Normal rotation: token1 is now revoked
    rotate_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token1},
    )
    assert rotate_resp.status_code == 200
    token2 = rotate_resp.json()["refresh_token"]

    # Age the revocation timestamp of token1 past thirty seconds (e.g. 60 seconds ago)
    from app.services.auth_service import _hash_token
    token1_hash = _hash_token(token1)
    rec1 = (
        await db_session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token1_hash)
        )
    ).scalar_one()
    rec1.revoked_at = datetime.now(timezone.utc) - timedelta(seconds=60)
    await db_session.commit()

    # Attacker or stale client presents token1 outside grace window
    compromise_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token1},
    )
    assert compromise_resp.status_code == 401
    assert "compromised" in compromise_resp.json()["detail"].lower()

    # Verify that token2 was also revoked by the breach detection cascade
    subsequent_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token2},
    )
    assert subsequent_resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_malformed_rejected(client: AsyncClient):
    """Verify that submitting an invalid or malformed refresh token returns 401."""
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "malformed.token.string"},
    )
    assert resp.status_code == 401
    assert "invalid" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_rate_limiting(client: AsyncClient):
    """AC-6: Exceeding rate limit on /auth/refresh returns 429 Too Many Requests."""
    hit_429 = False
    for _ in range(15):
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "dummy_string"},
        )
        if resp.status_code == 429:
            hit_429 = True
            break
    assert hit_429 is True

