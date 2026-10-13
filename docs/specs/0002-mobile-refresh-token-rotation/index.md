# 0002. Mobile refresh token rotation and session security

**Date**: 2026-10-12
**Status**: Implemented

## Summary

This specification upgrades mobile session security by rotating the refresh token on every exchange. When a mobile client sends a valid refresh token, the server revokes that token, issues a fresh access token and refresh token pair, and returns both to the client. A short thirty second grace window protects mobile users from intermittent network dropouts, while any token reuse detected outside the grace window immediately revokes all active sessions for that account to stop credential theft.

## Requirements

**User stories**:
- As a mobile driver or vehicle owner, I want my app session refreshed seamlessly and securely so that my account stays logged in without exposing long lived static credentials to theft.
- As a system administrator, I want stolen or intercepted refresh tokens detected immediately so that suspicious token reuse terminates all attacker sessions without delay.

**Acceptance criteria**:
- **AC-1**: Every successful call to `POST /api/v1/auth/refresh` rotates the refresh token, revoking the presented token with a recorded revocation timestamp and issuing a brand new access token and refresh token pair.
- **AC-2**: The refresh endpoint response conforms to `TokenResponse`, returning `access_token`, `refresh_token`, `token_type: "bearer"`, and `expires_in`.
- **AC-3**: The refresh endpoint validates user status in the database, rejecting inactive, suspended, or deleted user accounts with HTTP 401 Unauthorized (`"User account inactive or deleted"`).
- **AC-4**: A thirty second rotation grace window permits concurrent or retried requests presenting the recently rotated token to succeed. Because raw refresh tokens are hashed and not stored in plaintext, a valid request arriving within thirty seconds of rotation issues a fresh valid access token and refresh token pair without triggering session revocation, preventing false lockouts from mobile network drops.
- **AC-5**: If a revoked refresh token is presented outside the thirty second grace window, the server detects token theft, immediately revokes all active refresh tokens belonging to that user, and rejects the request with HTTP 401 Unauthorized (`"Compromised session: all sessions revoked"`).
- **AC-6**: The `POST /api/v1/auth/refresh` endpoint is rate limited using SlowAPI to a maximum of 10 requests per minute per IP address.
- **AC-7**: Database schema additions to the `refresh_tokens` table provide `revoked_at` (nullable datetime with timezone) and `replaced_by_id` (nullable integer foreign key referencing `refresh_tokens.id`), compatible with SQLite batch migrations and PostgreSQL.
- **AC-8**: Comprehensive automated test coverage verifies single use rotation, active user checks, grace window reuse, breach detection cascade revocation, and rate limiting.

## Decision

**Chosen option**: Option 1: In place token rotation with thirty second grace window and breach cascade revocation

The system rotates the refresh token on every refresh call, stores revocation time and successor linkage on the token record, absorbs mobile network retries within a thirty second window, and revokes all active user tokens when detecting reuse outside that window.

**Implementation skills**: none

## Rationale

Reasoning and options: see [rationale.md](file:///d:/office_dev/margentra_super_app_backend_python/docs/specs/0002-mobile-refresh-token-rotation/rationale.md).

## Feature design

**Data model sketch**:

Table: `refresh_tokens`
- `id`: integer primary key, indexed
- `user_id`: integer foreign key referencing `users.id` with cascade deletion, indexed
- `token_hash`: string(512), unique, indexed (SHA256 digest of raw refresh token)
- `expires_at`: datetime with timezone, non nullable
- `is_revoked`: boolean, default `False`, set to `True` on logout, rotation, or breach
- `revoked_at`: datetime with timezone, nullable (recorded when revoked or rotated)
- `replaced_by_id`: integer, nullable foreign key referencing `refresh_tokens.id` with set null on deletion
- `created_at`: datetime with timezone (from TimestampMixin)
- `updated_at`: datetime with timezone (from TimestampMixin)

**State transitions**:
- `Active`: `is_revoked = False`, current time < `expires_at`.
- `Rotated`: `is_revoked = True`, `revoked_at` recorded, `replaced_by_id` set to new token primary key.
- `Grace window`: token is `Rotated`, but current time <= `revoked_at + 30 seconds`. Request returns valid active successor pair.
- `Breach detected`: token is `Rotated`, but current time > `revoked_at + 30 seconds`. All active tokens for user set to `is_revoked = True`.
- `Expired`: current time >= `expires_at`. Request rejected with HTTP 401.

**API surface**:

| Endpoint | Method | Key inputs | Key outputs | Auth | Key errors |
|---|---|---|---|---|---|
| `/api/v1/auth/refresh` | POST | `refresh_token: str` | `access_token: str`, `refresh_token: str`, `token_type: str`, `expires_in: int` | Public / Refresh token | 401 (invalid, expired, inactive user, or breach detected), 429 (rate limited) |

**Value sourcing**:

| Action | Value produced / displayed | Source |
|---|---|---|
| Rotate token | `access_token` | Generated JWT access token containing subject `str(user.id)` and role claims |
| Rotate token | `refresh_token` | Generated cryptographic random token string, hashed for storage in `refresh_tokens.token_hash` |
| Token lookup | `token_hash` | SHA256 digest computed from raw `refresh_token` request input |
| Successor link | `replaced_by_id` | Primary key id of newly created `RefreshToken` row |
| Expiration | `expires_in` | Computed from `settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60` |
| Grace check | Grace duration | `settings.REFRESH_TOKEN_ROTATION_GRACE_SECONDS` (default 30 seconds) |

**Key invariants**:
- A raw refresh token is never stored in plaintext in the database; only its SHA256 hash is persisted.
- A refresh token can only rotate if its owner user account has `is_active = True`.
- Presenting a rotated token after the grace window triggers immediate revocation of every active token for that user.
- The `replaced_by_id` foreign key always references a successor token row belonging to the exact same `user_id`.

**Security model**:
- No bearer access token is required to invoke `/api/v1/auth/refresh`; authorization is established by cryptographic validity of the submitted refresh token.
- Refresh tokens are hashed using SHA256 before database lookup, mitigating exposure from database read leaks.
- Compromise detection enforces automatic invalidation across all devices if a token is reused by an attacker.

**Configuration required**:
- `REFRESH_TOKEN_ROTATION_GRACE_SECONDS`: integer, default `30` (number of seconds a rotated token remains accepted for idempotent retries).

**Critical test scenarios**:
- Happy path rotation: submit valid refresh token, verify previous token is marked revoked with timestamp and replaced id, and verify new access token and refresh token work, verifies **AC-1**, **AC-2**.
- Inactive user rejection: set `user.is_active = False` on user record and attempt refresh, verify HTTP 401 response, verifies **AC-3**.
- Mobile grace period retry: send duplicate refresh request with recently rotated token within thirty seconds, verify successful return of active token pair without session revocation, verifies **AC-4**.
- Breach detection cascade revocation: send refresh request with an already rotated token sixty seconds later, verify HTTP 401 response and verify all active refresh tokens for that user are revoked, verifies **AC-5**.
- Rate limiting: submit more than ten refresh requests in a single minute from the same IP address, verify HTTP 429 Too Many Requests response, verifies **AC-6**.

## Migration plan

**Strategy**: Single migration with batch mode support.
**Phases**:
1. Add columns `revoked_at` (nullable datetime with timezone) and `replaced_by_id` (nullable integer foreign key) to `refresh_tokens`.
2. Existing active tokens remain valid with `revoked_at = NULL` and `replaced_by_id = NULL`.
**Rollback**: Drop added columns `revoked_at` and `replaced_by_id`.
**Risks**: None; added columns are fully nullable and preserve existing rows.

## Build plan

1. Add `REFRESH_TOKEN_ROTATION_GRACE_SECONDS` setting in [app/core/config.py](file:///d:/office_dev/margentra_super_app_backend_python/app/core/config.py), satisfies **AC-4**.
2. Add `revoked_at` and `replaced_by_id` columns to `RefreshToken` model in [app/models/auth.py](file:///d:/office_dev/margentra_super_app_backend_python/app/models/auth.py), satisfies **AC-7**.
3. Create Alembic migration script for `refresh_tokens` table changes, satisfies **AC-7**.
4. Update `refresh_access_token` in [app/services/auth_service.py](file:///d:/office_dev/margentra_super_app_backend_python/app/services/auth_service.py) with rotation, active user validation, grace period handling, and breach detection cascade revocation, satisfies **AC-1**, **AC-3**, **AC-4**, **AC-5**.
5. Update `POST /auth/refresh` endpoint in [app/api/v1/endpoints/auth.py](file:///d:/office_dev/margentra_super_app_backend_python/app/api/v1/endpoints/auth.py) to return `TokenResponse` and apply SlowAPI rate limiting, satisfies **AC-2**, **AC-6**.
6. Write test suite in `tests/test_refresh_rotation.py` verifying rotation, grace window, breach detection, and rate limiting, satisfies **AC-8**.

## Consequences

**Positive**:
- Eliminates perpetual refresh token vulnerability where an intercepted token could be used indefinitely.
- Mobile clients receive fresh refresh tokens on every app wake or token refresh cycle.
- Grace window eliminates sudden mobile logouts caused by intermittent mobile connection drops.
- Account deactivations take effect immediately on token refresh rather than waiting for multi day refresh expiration.

**Negative / tradeoffs**:
- Slightly higher database write volume on token refresh (updating old token row and inserting new token row).
- Mobile client must update its persisted secure storage with the new refresh token on every refresh call.

**Neutral**:
- The `/auth/refresh` response schema now provides `TokenResponse` with both tokens, matching the `/auth/login` payload format.

## Follow-up

- [ ] Inform mobile team that `/api/v1/auth/refresh` now returns both `access_token` and `refresh_token`, requiring local secure storage update after each refresh call.
