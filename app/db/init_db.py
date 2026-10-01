"""DB startup initialisation — run migrations and optionally seed data."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.session import engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Run at application startup. Tables are managed by Alembic in production."""
    # In development we can create all tables directly for convenience.
    # In production, rely on `alembic upgrade head` in the Docker entrypoint.
    from app.db.base import Base  # noqa: PLC0415
    import app.models  # noqa: F401, PLC0415

    async with engine.begin() as conn:
        # Only create tables that don't exist yet (idempotent).
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialised.")
