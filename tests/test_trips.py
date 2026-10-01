"""Tests for trip endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_start_and_end_trip(client: AsyncClient, auth_headers: dict):
    # Start
    start_resp = await client.post(
        "/api/v1/trip/start",
        json={"start_lat": 12.9716, "start_lng": 77.5946},
        headers=auth_headers,
    )
    assert start_resp.status_code == 201
    trip_id = start_resp.json()["trip_id"]
    assert trip_id > 0

    # Post telemetry
    tel_resp = await client.post(
        "/api/v1/trip/telemetry",
        json={
            "trip_id": trip_id,
            "points": [
                {
                    "timestamp": "2026-09-25T05:00:00Z",
                    "speed_kmh": 60.0,
                    "rpm": 2500,
                    "g_force": 0.1,
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                }
            ],
        },
        headers=auth_headers,
    )
    assert tel_resp.status_code == 200
    assert tel_resp.json()["accepted"] == 1

    # End trip
    end_resp = await client.post(
        "/api/v1/trip/end",
        json={"trip_id": trip_id, "end_lat": 13.0, "end_lng": 77.6, "distance_km": "5.2"},
        headers=auth_headers,
    )
    assert end_resp.status_code == 200
    data = end_resp.json()
    assert data["trip"]["status"] == "completed"
    assert float(data["mgc_earned"]) >= 0


@pytest.mark.asyncio
async def test_cannot_start_two_trips(client: AsyncClient, auth_headers: dict):
    start_resp = await client.post("/api/v1/trip/start", json={}, headers=auth_headers)
    resp = await client.post("/api/v1/trip/start", json={}, headers=auth_headers)
    assert resp.status_code == 409
    if start_resp.status_code == 201:
        trip_id = start_resp.json()["trip_id"]
        await client.post("/api/v1/trip/end", json={"trip_id": trip_id}, headers=auth_headers)


@pytest.mark.asyncio
async def test_trip_history(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/trip/history", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_current_earnings_no_active_trip(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/trip/earnings/current", headers=auth_headers)
    assert resp.status_code == 404
