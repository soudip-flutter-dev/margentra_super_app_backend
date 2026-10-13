# 0001. Database Backend Environment Toggle

**Date**: 2026-10-12
**Status**: In Progress

## Summary

This decision adds an environment setting named DB_BACKEND to switch between local SQLite, remote Neon PostgreSQL, and local Docker PostgreSQL. It enables mobile app developers to run the backend locally with zero cloud latency and no internet dependence. The application boots with SQLite by default, automatically creates local tables on startup, and exposes the active database engine on the health check endpoint.

## Requirements

**User stories**:
- As a mobile app engineer, I want to run the FastAPI backend locally against SQLite so that I can build and test mobile screens quickly without network latency.
- As a backend engineer, I want to select the database backend with an environment variable so that the same codebase runs in local mobile development, Docker, and cloud staging.

**Acceptance criteria**:
- **AC-1**: The settings schema includes a `DB_BACKEND` configuration accepting `sqlite`, `neon`, or `postgres`, defaulting to `sqlite`.
- **AC-2**: When `DB_BACKEND` is `sqlite`, the application connects to `./margnetra.db` using `sqlite+aiosqlite` for async queries and `sqlite` for synchronous operations.
- **AC-3**: When `DB_BACKEND` is `neon` or `postgres`, the application connects to the selected connection string with connection pooling enabled (including pool pre ping, pool size 10, and max overflow 20).
- **AC-4**: In `sqlite` mode, connection pooling limits are bypassed and `check_same_thread: False` is applied to allow concurrent access without pool timeouts.
- **AC-5**: In `sqlite` mode, application startup runs `Base.metadata.create_all` idempotently through `init_db()`, creating all missing tables automatically.
- **AC-6**: When `DB_BACKEND` is set to `neon` or `postgres` and the database cannot be reached on startup, the application fails fast with a clear diagnostic error suggesting `DB_BACKEND=sqlite` as a local option.
- **AC-7**: The `/health` endpoint response includes a `db_backend` field reporting the active engine, and startup logs state the selected backend.
- **AC-8**: Alembic migrations in `alembic/env.py` dynamically resolve `settings.SYNC_DATABASE_URL` from the active backend setting, and apply `render_as_batch=True` when running under SQLite mode.

## Decision

**Chosen option**: Option 1: Dedicated URL settings per backend with a DB_BACKEND selector.

The application configuration defines explicit settings for each supported target and uses `DB_BACKEND` to resolve the active async and sync database URLs dynamically.

## Rationale

Reasoning and options: see [rationale.md](./rationale.md).

## Feature design

**API surface**:
| Endpoint | Method | Key inputs | Key outputs | Auth | Key errors |
|---|---|---|---|---|---|
| /health | GET | none | status, app, version, db_backend | none | none |

**Value sourcing**:
| Action | Value produced / displayed | Source |
|---|---|---|
| GET /health | db_backend | settings.DB_BACKEND |
| Startup log | active database target | settings.DB_BACKEND and sanitized connection url |

**Key invariants**:
- `DB_BACKEND` must strictly validate against `sqlite`, `neon`, or `postgres`.
- SQLite mode must never configure connection pool queues or overflow limits.
- Remote database connection failures must never silently fall back to local storage.

**Security model**:
- The SQLite file `./margnetra.db` remains on local disk and is excluded from git.
- Neon credentials remain stored in `.env` and are never exposed in `/health` or startup logs.

**Configuration required**:
- `DB_BACKEND`: `sqlite`, `neon`, or `postgres` (defaults to `sqlite`)
- `SQLITE_DATABASE_URL`: `sqlite+aiosqlite:///./margnetra.db`
- `SQLITE_SYNC_DATABASE_URL`: `sqlite:///./margnetra.db`
- `NEON_DATABASE_URL`: asyncpg connection string for Neon
- `NEON_SYNC_DATABASE_URL`: sync connection string for Neon
- `POSTGRES_DATABASE_URL`: asyncpg connection string for local Docker
- `POSTGRES_SYNC_DATABASE_URL`: sync connection string for local Docker

**Critical test scenarios**:
- SQLite happy path: boot application with `DB_BACKEND=sqlite`, query `/health`, verify `db_backend` equals `sqlite` and verify tables exist, satisfies **AC-1**, **AC-2**, **AC-4**, **AC-5**, **AC-7**
- Neon mode connection: boot application with `DB_BACKEND=neon`, verify engine options contain connection pooling settings, satisfies **AC-3**
- Unreachable database failure: simulate unreachable remote host in Neon mode, verify clean fail fast startup exception with diagnostic message, satisfies **AC-6**
- Alembic URL resolution: invoke migration environment helper, verify target URL matches active `DB_BACKEND`, satisfies **AC-8**

## Build plan

- [x] 1. Update `app/core/config.py` with `DB_BACKEND` setting and dynamic assembly of `DATABASE_URL` and `SYNC_DATABASE_URL` across SQLite, Neon, and Postgres, satisfies **AC-1**, **AC-2**, **AC-3**
- [x] 2. Update `app/db/session.py` to tailor engine options (bypass pool limits for SQLite, apply `check_same_thread: False`, maintain pooling for Postgres/Neon), satisfies **AC-4**
- [x] 3. Update `app/db/init_db.py` and `app/main.py` lifespan to verify connection, log active `db_backend`, handle fail fast diagnostics, and expose `db_backend` on `/health`, satisfies **AC-5**, **AC-6**, **AC-7**
- [x] 4. Update `alembic/env.py` to read `settings.SYNC_DATABASE_URL` dynamically for migrations, satisfies **AC-8**
- [x] 5. Update `.env` and `.env.example` templates with all backend URL options and default `DB_BACKEND=sqlite`, satisfies **AC-1**, **AC-2**

## Consequences

**Positive**:
- Mobile developers get sub millisecond local database queries without internet dependency.
- Switching between local SQLite, Docker, and Neon requires editing only one configuration key.
- Table creation happens automatically in local development without running manual migrations.

**Negative / tradeoffs**:
- SQLite does not enforce identical constraint behaviors as PostgreSQL (for example, case sensitive text matching and concurrent write locking).
- Developers must periodically run against Neon or Postgres to verify database specific behaviors before production deployments.

**Neutral**:
- The project root continues to hold `./margnetra.db`, which is already ignored by git.

## Migration plan

**Strategy**: no migration needed
**Phases**:
1. Configuration and engine updates applied in place with backward compatibility for existing `DATABASE_URL` entries.
**Rollback**: Revert configuration changes to restore single `DATABASE_URL` parsing.
**Risks**: None; existing models use standard SQLAlchemy types compatible with both engines.

## Follow-up

- [ ] Add a seed script to populate test driver accounts and vehicles in SQLite for fresh mobile test setups.
