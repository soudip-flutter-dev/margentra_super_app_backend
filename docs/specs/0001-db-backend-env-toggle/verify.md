# Verify: database backend environment toggle · spec 0001 · updated 2026-10-12
_Steps derived from spec 0001 acceptance criteria. `/check verify` runs these; `/test` locks the durable ones._

## UI / manual
- [x] Send GET request to `/health` with `DB_BACKEND=sqlite` → expect status 200, `db_backend: "sqlite"` → AC-7
- [x] Inspect root directory on startup → expect `./margnetra.db` verified with application tables → AC-2, AC-5
- [x] Set `DB_BACKEND=neon` in `.env` with unreachable host → expect startup to fail fast with diagnostic log pointing to `DB_BACKEND=sqlite` → AC-6

## Commands
- [x] `pytest tests/test_db_backend.py -v` → all 4 tests pass (verifies settings resolution, /health response, backend URLs) → AC-1, AC-2, AC-3, AC-7
- [x] `pytest tests/ -v` → all 25 test suite tests pass cleanly → AC-2, AC-4, AC-5
- [x] `python -c "from app.core.config import settings; print(settings.DB_BACKEND, settings.DATABASE_URL)"` → prints `sqlite` and `sqlite+aiosqlite:///./margnetra.db` → AC-1, AC-2

## Acceptance criteria coverage
- AC-1 (DB_BACKEND configuration): covered by `test_sqlite_backend_resolution` in `tests/test_db_backend.py`
- AC-2 (SQLite database connection): covered by `pytest tests/` and `test_sqlite_backend_resolution`
- AC-3 (Neon and Postgres connection pooling): covered by `test_neon_backend_resolution` and `test_postgres_backend_resolution`
- AC-4 (Engine kwargs tuning without pool limits for SQLite): covered by `app/db/session.py` configuration and full test suite
- AC-5 (Idempotent table initialization on startup): covered by startup test and `pytest tests/`
- AC-6 (Fail fast diagnostic error on unreachable remote database): covered by error handling in `app/db/init_db.py`
- AC-7 (Health endpoint db_backend field and startup logging): covered by `test_health_check_returns_db_backend`
- AC-8 (Alembic dynamic target URL and batch mode for SQLite): covered by `alembic/env.py` configuration
