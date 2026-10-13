# MargNetra Super App Backend

## Stack

- **Language / Runtime**: Python 3.11+
- **Framework**: FastAPI with Uvicorn
- **Key dependencies**: SQLAlchemy 2.0 (async), Pydantic v2, Alembic, asyncpg, Redis, SlowAPI
- **Package manager**: pip

## Build approach

Tracer Bullet (vertical slices built end to end through every layer)

## Commands

```bash
# Install
pip install -r requirements.txt

# Dev server
uvicorn app.main:app --reload

# Database migrations
alembic upgrade head

# Test
pytest
```

## Specs

Stored in `docs/specs/`. Format: `docs/specs/NNNN-title.md`.

## Rules

- Keep routers thin and put core business logic in `app/services`
- Use async SQLAlchemy 2.0 patterns with `AsyncSession` and `select()`
- Declare request and response schemas with Pydantic v2
- Inject database and auth dependencies via `DBDep` and `CurrentUserDep`
- Protect state changing endpoints with SlowAPI rate limiters
- Write tests using async pytest fixtures and SQLite

## Agent skills

Declined: FastAPI, SQLAlchemy, Alembic, Redis, Pytest

## Context files

- [app/services/AGENTS.md](app/services/AGENTS.md): Business logic, calculations, legal affidavits, and integrations

_Drafted by /audit from the repo, worth a quick human pass. Edit freely: once a line stops matching this draft, later runs treat it as curated and will flag rather than overwrite it._
