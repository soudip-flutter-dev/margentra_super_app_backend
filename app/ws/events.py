"""WebSocket event helpers — push telemetry and location events."""

from __future__ import annotations

from typing import Any

from app.ws.connection_manager import family_manager, trip_manager


async def push_telemetry(trip_id: int, data: dict[str, Any]) -> None:
    """Broadcast a telemetry frame to all subscribers of a trip."""
    await trip_manager.broadcast(f"trip:{trip_id}", {"event": "telemetry", "data": data})


async def push_family_location(family_circle_id: int, data: dict[str, Any]) -> None:
    """Broadcast updated member locations to a family room."""
    await family_manager.broadcast(f"family:{family_circle_id}", {"event": "location_update", "data": data})
