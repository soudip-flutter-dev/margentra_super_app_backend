"""Tests for wallet endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_balance(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/wallet/balance", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "mgc_balance" in data
    assert float(data["mgc_balance"]) >= 0


@pytest.mark.asyncio
async def test_list_transactions_empty(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/wallet/transactions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_redeem_fastag_insufficient_balance(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/wallet/redeem/fastag",
        json={"amount_mgc": "99999", "fastag_id": "FAST123"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_buy_streak_protection_insufficient_balance(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/wallet/buy/streak-protection",
        headers=auth_headers,
    )
    assert resp.status_code == 400
