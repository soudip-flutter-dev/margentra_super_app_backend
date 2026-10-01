"""WebSocket connection manager for trip telemetry and family live location."""

from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    In-memory connection manager. For multi-instance deployments, replace
    the broadcast logic with Redis pub/sub (see events.py for the Redis adapter).
    """

    def __init__(self) -> None:
        # room_id -> list of active WebSocket connections
        self._rooms: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, room_id: str) -> None:
        await websocket.accept()
        self._rooms[room_id].append(websocket)
        logger.info("WS connected: room=%s, total=%d", room_id, len(self._rooms[room_id]))

    def disconnect(self, websocket: WebSocket, room_id: str) -> None:
        try:
            self._rooms[room_id].remove(websocket)
        except ValueError:
            pass
        if not self._rooms[room_id]:
            del self._rooms[room_id]
        logger.info("WS disconnected: room=%s", room_id)

    async def broadcast(self, room_id: str, payload: dict[str, Any]) -> None:
        """Send JSON payload to all clients in the room."""
        message = json.dumps(payload, default=str)
        dead: list[WebSocket] = []
        for ws in list(self._rooms.get(room_id, [])):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, room_id)

    async def send_personal(self, websocket: WebSocket, payload: dict[str, Any]) -> None:
        await websocket.send_text(json.dumps(payload, default=str))

    def room_count(self, room_id: str) -> int:
        return len(self._rooms.get(room_id, []))


# Singleton instances
trip_manager = ConnectionManager()
family_manager = ConnectionManager()
