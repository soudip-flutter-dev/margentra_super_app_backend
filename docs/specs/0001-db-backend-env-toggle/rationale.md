# 0001. Database Backend Environment Toggle: Rationale

## Context

The backend currently points to a remote Neon PostgreSQL database located in an AWS Singapore region. While Neon provides managed PostgreSQL with connection pooling, developing and testing mobile Flutter applications against a remote database introduces significant latency for every network request. Testing also stalls whenever internet connectivity is weak or absent.

The repository already includes support for SQLite in its test suite and has a local database file in the project root. However, switching between local SQLite and remote Neon currently requires manual edits to connection strings in the environment file. If an engineer forgets to revert their edits, local changes can accidentally touch shared cloud databases.

We need a clean, explicit configuration toggle that allows switching backends effortlessly while keeping credentials for all targets safely in the environment configuration.

## Options considered

### Option 1: Dedicated URL settings per backend with a DB_BACKEND selector

Define separate variables for `SQLITE_DATABASE_URL`, `NEON_DATABASE_URL`, and `POSTGRES_DATABASE_URL`, with `DB_BACKEND` selecting which one becomes active.

**Pros**:
- Keeps credentials for all environments stored safely without commenting lines in and out.
- Switching environments requires changing only one variable.
- Eliminates configuration syntax errors when switching targets.

**Cons**:
- Slightly more environment variables in the environment file.

### Option 2: Single DATABASE_URL with manual edits

Keep a single `DATABASE_URL` variable and instruct developers to comment or uncomment lines in `.env`.

**Pros**:
- Fewer environment variables.

**Cons**:
- Error prone and tedious when switching back and forth during mobile testing.
- High risk of accidentally connecting to the wrong database.

### Option 3: Automatic fallback from Neon to SQLite on connection timeout

Attempt to connect to Neon first, and silently fall back to local SQLite if the connection fails or times out.

**Pros**:
- Works even if the developer forgets to change their environment file while offline.

**Cons**:
- Masks connection problems in staging or production.
- Causes silent data divergence between local SQLite and remote Neon.

## Rationale

Option 1 provides the safest and most convenient developer experience. Mobile developers can toggle `DB_BACKEND=sqlite` for instant local responses, or set `DB_BACKEND=neon` to verify cloud staging, without altering any connection strings or passwords. Option 3 was rejected because automatic fallbacks risk masking critical connection failures in production. Option 2 was rejected because manual text swapping is prone to human error.
