"""Tests for e-Challan endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_challans_empty(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/challan/list", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_sync_challans(client: AsyncClient, auth_headers: dict):
    # Add a vehicle first so sync has something to query
    await client.post(
        "/api/v1/user/vehicles",
        json={
            "registration_number": "KA01AB1234",
            "make": "Maruti",
            "model": "Swift",
            "year": 2022,
            "fuel_type": "petrol",
        },
        headers=auth_headers,
    )
    resp = await client.post("/api/v1/challan/sync", headers=auth_headers)
    assert resp.status_code == 200
    assert "synced" in resp.json()


@pytest.mark.asyncio
async def test_pay_challan_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/challan/pay",
        json={"challan_id": 99999, "payment_method_id": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 404
