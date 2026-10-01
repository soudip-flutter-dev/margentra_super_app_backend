"""API v1 router — aggregates all endpoint sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    bounty,
    challans,
    devices,
    digilocker,
    family,
    legal,
    notifications,
    sos,
    trips,
    users,
    wallet,
    websockets,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(wallet.router)
api_router.include_router(trips.router)
api_router.include_router(challans.router)
api_router.include_router(legal.router)
api_router.include_router(digilocker.router)
api_router.include_router(family.router)
api_router.include_router(sos.router)
api_router.include_router(bounty.router)
api_router.include_router(devices.router)
api_router.include_router(notifications.router)
# WebSocket routes are included without prefix (they have full paths)
api_router.include_router(websockets.router)
