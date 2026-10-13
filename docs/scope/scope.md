# Scope: MargNetra Super App Backend

Production backend for MargNetra driving behavior rewards, electronic challan management, legal vault, emergency SOS, and wallet services.

**Build approach:** Tracer Bullet (vertical slices built end to end through every layer).
**Workflow:** Beta (after develop, check verify then test). The project default level of rigor. `/architect` is the recommended first stop for a feature with a real decision, but skippable when you already know the build. Any feature can carry its own tag to do more or less.

_These are recommendations to keep your build orderly, not requirements. Skip anything that does not fit: if you already know how to build a feature, use `/develop` and skip `/architect`. You decide when a feature is `done`._

## At a glance

| # | Feature | Phase | Status |
|---|---------|-------|--------|
| A | Core backend services | Existing foundation | existing |
| 1 | Database backend environment toggle | Slice 1 | in-progress |
| 2 | Mobile refresh token rotation and session security | Slice 2 | in-progress |

## Existing features

### A. Core backend services · existing
Existing backend foundation: user authentication, trip telemetry ingestion, civil score calculation, electronic challans, MGC coin wallet, legal evidence vault, family circle, and emergency SOS. code in `app/`

## Slice 1: Local and remote database switching

### 1. Database backend environment toggle · in-progress
Switch database connection between local SQLite, remote Neon PostgreSQL, and local Docker PostgreSQL via an environment setting for fast mobile development without cloud latency.
**Done when:** `DB_BACKEND` setting in `.env` selects between sqlite, neon, or postgres, and FastAPI boots and connects cleanly on both SQLite and Neon.
- [x] Design it (spec): `/architect database backend environment toggle`
- [x] Build it: `/develop database backend environment toggle`
   - [x] Configuration settings and URL resolvers in `app/core/config.py` (AC-1, AC-2, AC-3)
   - [x] Engine kwargs tuning and pool bypass in `app/db/session.py` (AC-4)
   - [x] Schema init, startup logging, fail fast check, and `/health` status (AC-5, AC-6, AC-7)
   - [x] Alembic environment dynamic target and batch migration support (AC-8)
- [x] Verify it: `/check verify database backend environment toggle`
- [ ] Test it: `/test database backend environment toggle`
Spec [0001](../specs/0001-db-backend-env-toggle/index.md) · code in `app/core/config.py`, `app/db/`, `app/main.py`, `alembic/env.py`

## Slice 2: Mobile authentication security

### 2. Mobile refresh token rotation and session security · in-progress
Secure mobile sessions by rotating refresh tokens on every refresh call, invalidating previous tokens, checking active user status, and returning a fresh token pair to the mobile client.
**Done when:** the refresh endpoint returns a fresh access and refresh token pair, revokes the submitted refresh token, and rejects deactivated accounts.
- [x] Design it (spec): `/architect mobile refresh token rotation and session security`
- [x] Build it: `/develop mobile refresh token rotation and session security`
   - [x] Configuration setting for rotation grace window in `app/core/config.py` (AC-4)
   - [x] RefreshToken model schema with `revoked_at` and `replaced_by_id` plus migration (AC-7)
   - [x] Token rotation, user status check, grace retry, and breach cascade revocation in `app/services/auth_service.py` (AC-1, AC-3, AC-4, AC-5)
   - [x] Refresh endpoint updating to `TokenResponse` with SlowAPI rate limiting in `app/api/v1/endpoints/auth.py` (AC-2, AC-6)
- [x] Verify it: `/check verify mobile refresh token rotation and session security`
- [x] Test it: `/test mobile refresh token rotation and session security`
Spec [0002](../specs/0002-mobile-refresh-token-rotation/index.md) · code in `app/core/config.py`, `app/models/auth.py`, `app/services/auth_service.py`, `app/api/v1/endpoints/auth.py`

## Deferred
- **SQLite test seed script**: populate test driver accounts and vehicles in SQLite for fresh mobile test setups · from spec 0001

## Legend

**The decision box.** Every feature carries exactly one, the sub task whose label ends with `(spec)`. Its wording varies (`Design it (spec)` normally), so skills locate it by that `(spec)` suffix, never by an exact label. Every other box is an execution box and `/architect` never ticks one.

**Feature lifecycle**: the scope updates as a feature moves; each row is what it shows and who sets it:

| State | Set by | The feature shows |
|---|---|---|
| `planned` · needs a decision | `/scope` | one box: `Design it (spec): /architect <feature>` |
| `in-progress` (designed) | `/architect` at spec capture | `Design it` ticked; spec linked; `Build it: /develop <feature>` plus milestones; the tier closing boxes |
| `in-progress` (building) | `/develop` | milestone sub boxes tick one by one; code pointer filled |
| `in-progress` (verified) | `/check verify` | `Build it` plus milestones ticked; `Verify it` ticked |
| `done` | you, when you decide it is; `/sync` reconciles | boxes you ran ticked; `/sync` captures conventions |
