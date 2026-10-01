"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.utils.exceptions import register_exception_handlers

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("margnetra")


# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])


# ── App lifespan ──────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 MargNetra backend starting up...")
    await init_db()
    yield
    logger.info("🛑 MargNetra backend shutting down...")


# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="MargNetra Super App API",
    description=(
        "Production-grade FastAPI backend for MargNetra — driving behaviour rewards, "
        "e-Challan management, Legal Vault, DigiLocker, Family Circle, Emergency SOS, "
        "Bounty Capture, BLE/OBD devices, and MGC Wallet."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)

# ── Serve local uploads in dev ────────────────────────────────────────────────
if settings.USE_LOCAL_STORAGE:
    import os  # noqa: PLC0415
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.LOCAL_STORAGE_PATH), name="uploads")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}
