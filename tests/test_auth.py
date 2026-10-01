"""Tests for auth endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Alice",
            "phone": "+911234567890",
            "email": "alice@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["phone"] == "+911234567890"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_phone(client: AsyncClient):
    payload = {
        "full_name": "Bob",
        "phone": "+910000000001",
        "password": "SecurePass1",
        "confirm_password": "SecurePass1",
    }
    await client.post("/api/v1/auth/register", json=payload)
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_password_mismatch(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Charlie",
            "phone": "+910000000002",
            "password": "pass1",
            "confirm_password": "pass2",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Dave",
            "phone": "+910000000003",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "+910000000003", "password": "SecurePass1"},
    )
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Eve",
            "phone": "+910000000004",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "+910000000004", "password": "WrongPass"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Frank",
            "phone": "+910000000005",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "+910000000005", "password": "SecurePass1"},
    )
    refresh_token = login_resp.json()["refresh_token"]
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Grace",
            "phone": "+910000000006",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "+910000000006", "password": "SecurePass1"},
    )
    refresh_token = login_resp.json()["refresh_token"]
    resp = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    # Refreshing after logout should fail
    resp2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp2.status_code == 401
