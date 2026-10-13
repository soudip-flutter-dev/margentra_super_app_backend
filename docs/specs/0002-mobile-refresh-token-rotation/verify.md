# Verify: mobile refresh token rotation and session security : spec 0002 : updated 2026-10-12
_Steps derived from spec 0002 acceptance criteria. `/check verify` runs these; `/test` locks the durable ones._

## Manual and API
- [x] Send POST request to `/api/v1/auth/refresh` with valid refresh token → expect status 200 with both access_token and refresh_token in response → AC-1, AC-2
- [x] Send POST request to `/api/v1/auth/refresh` for inactive user account → expect status 401 Unauthorized → AC-3
- [x] Send duplicate POST request with recently rotated token within thirty seconds → expect status 200 without user session revocation → AC-4
- [x] Send POST request with rotated token after thirty seconds → expect status 401 and all active sessions for that user revoked → AC-5
- [x] Send eleven rapid refresh requests from single IP within one minute → expect status 429 Too Many Requests → AC-6

## Commands
- [x] `pytest tests/test_refresh_rotation.py -v` → all refresh rotation tests pass cleanly → AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- [x] `pytest tests/ -v` → entire backend test suite passes cleanly with no regressions → AC-8
- [x] Check database schema on startup or migration → expect `revoked_at` and `replaced_by_id` columns present on `refresh_tokens` → AC-7

## Acceptance criteria coverage
- AC-1 (Rotation on refresh): covered by `test_refresh_token_rotation` in `tests/test_refresh_rotation.py`
- AC-2 (TokenResponse schema): covered by `test_refresh_token_rotation` response validation
- AC-3 (Active user validation): covered by `test_refresh_token_inactive_user`
- AC-4 (Grace window retry): covered by `test_refresh_token_grace_window`
- AC-5 (Breach cascade revocation): covered by `test_refresh_token_breach_detection`
- AC-6 (Rate limiting): covered by `test_refresh_token_rate_limit`
- AC-7 (Database schema migration): covered by `app/models/auth.py` and Alembic migration
- AC-8 (Test suite verification): covered by full pytest run
