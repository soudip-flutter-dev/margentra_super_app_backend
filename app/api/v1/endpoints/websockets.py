"""WebSocket endpoints: /ws/trip/live and /ws/family/live."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import verify_access_token
from app.ws.connection_manager import family_manager, trip_manager

router = APIRouter(tags=["WebSockets"])
logger = logging.getLogger(__name__)


async def _authenticate_ws(websocket: WebSocket, token: str | None) -> str | None:
    """
    Authenticate a WebSocket connection. Token can be passed as:
    - Query param: ?token=<jwt>
    - First message: {"token": "<jwt>"}
    Returns user_id string on success, None on failure.
    """
    if token:
        payload = verify_access_token(token)
        if payload:
            return payload.get("sub")

    # Try first-message auth
    try:
        raw = await websocket.receive_text()
        data = json.loads(raw)
        token = data.get("token")
        if token:
            payload = verify_access_token(token)
            if payload:
                return payload.get("sub")
    except Exception:
        pass
    return None


@router.websocket("/ws/trip/live")
async def trip_live_socket(
    websocket: WebSocket,
    token: str | None = Query(default=None, description="JWT access token"),
    trip_id: int = Query(..., description="Active trip ID to subscribe to"),
):
    """
    Stream live trip telemetry.

    Connect with `?token=<jwt>&trip_id=<id>`.
    The server pushes JSON frames:
    ```json
    {"event": "telemetry", "data": {"speed": 60, "rpm": 2000, ...}}
    ```
    Telemetry is pushed here whenever POST /trip/telemetry is called.
    """
    await websocket.accept()
    user_id = await _authenticate_ws(websocket, token)
    if not user_id:
        await websocket.send_text(json.dumps({"error": "Unauthorized"}))
        await websocket.close(code=4001)
        return

    room_id = f"trip:{trip_id}"
    await trip_manager.connect(websocket, room_id)
    logger.info("User %s connected to trip WS room %s", user_id, room_id)

    try:
        # Keep alive — echo any pings back
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        trip_manager.disconnect(websocket, room_id)
        logger.info("User %s disconnected from trip WS room %s", user_id, room_id)


@router.websocket("/ws/family/live")
async def family_live_socket(
    websocket: WebSocket,
    token: str | None = Query(default=None, description="JWT access token"),
    family_circle_id: int = Query(..., description="Family circle ID to subscribe to"),
):
    """
    Stream live family member locations.

    Connect with `?token=<jwt>&family_circle_id=<id>`.
    The server pushes JSON frames:
    ```json
    {"event": "location_update", "data": {"member_id": 1, "lat": 12.9, "lng": 77.6, ...}}
    ```
    """
    await websocket.accept()
    user_id = await _authenticate_ws(websocket, token)
    if not user_id:
        await websocket.send_text(json.dumps({"error": "Unauthorized"}))
        await websocket.close(code=4001)
        return

    room_id = f"family:{family_circle_id}"
    await family_manager.connect(websocket, room_id)
    logger.info("User %s connected to family WS room %s", user_id, room_id)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            # Members can push their own location update
            if msg.get("type") == "location_update":
                payload = msg.get("data", {})
                payload["user_id"] = user_id
                await family_manager.broadcast(
                    room_id,
                    {"event": "location_update", "data": payload},
                )
            elif msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        family_manager.disconnect(websocket, room_id)
        logger.info("User %s disconnected from family WS room %s", user_id, room_id)
