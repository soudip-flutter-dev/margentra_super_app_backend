"""DB startup initialisation — run migrations and optionally seed data."""

from __future__ import annotations

import logging

from app.core.config import settings
from app.db.session import engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Run at application startup. Tables are managed by Alembic in production."""
    from app.db.base import Base  # noqa: PLC0415
    import app.models  # noqa: F401, PLC0415

    try:
        async with engine.begin() as conn:
            if settings.DB_BACKEND == "sqlite" or "sqlite" in settings.DATABASE_URL:
                # Only create tables that don't exist yet (idempotent).
                await conn.run_sync(Base.metadata.create_all)
                logger.info("SQLite database tables verified and initialised (backend=%s).", settings.DB_BACKEND)
            else:
                from sqlalchemy import text  # noqa: PLC0415
                await conn.execute(text("SELECT 1"))
                logger.info(
                    "Database connection established successfully (backend=%s).",
                    settings.DB_BACKEND,
                )
    except Exception as exc:
        target_display = (
            settings.DATABASE_URL.split("@")[-1]
            if "@" in settings.DATABASE_URL
            else settings.DATABASE_URL
        )
        logger.critical(
            "Database connection failed for backend '%s' at '%s': %s",
            settings.DB_BACKEND,
            target_display,
            exc,
        )
        if settings.DB_BACKEND in ("neon", "postgres"):
            logger.error(
                "Tip: To run locally with zero cloud dependencies for fast mobile development, "
                "set DB_BACKEND=sqlite in your .env file."
            )
        raise
