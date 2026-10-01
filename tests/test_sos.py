"""Tests for SOS endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upsert_and_list_contacts(client: AsyncClient, auth_headers: dict):
    # Add a contact
    resp = await client.post(
        "/api/v1/sos/contacts",
        json={"name": "Mom", "phone": "+919876543210", "relation": "Mother", "is_primary": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    contact = resp.json()
    assert contact["name"] == "Mom"

    # List contacts
    list_resp = await client.get("/api/v1/sos/contacts", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


@pytest.mark.asyncio
async def test_trigger_sos(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/sos/trigger",
        json={"latitude": 12.9716, "longitude": 77.5946, "message": "Help!"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "triggered"


@pytest.mark.asyncio
async def test_road_assistance(client: AsyncClient, auth_headers: dict):
    resp = await client.post(
        "/api/v1/sos/road-assistance",
        json={"latitude": 12.97, "longitude": 77.59, "issue_type": "flat_tyre"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"
