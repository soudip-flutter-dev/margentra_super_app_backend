# 0002. Mobile refresh token rotation and session security : Rationale

## Context

The MargNetra mobile super app authenticates drivers and vehicle owners via JWT access tokens and database backed refresh tokens. Currently, when an access token expires, the mobile client calls `POST /api/v1/auth/refresh` with its stored refresh token.

In the previous implementation, the refresh endpoint validated the cryptographic signature and verified that the database record was not revoked, but it did not rotate the refresh token. The same refresh token remained valid for thirty days across dozens of token exchanges. If a device or network transport were compromised, the static refresh token could be extracted and used indefinitely until its thirty day expiration date.

Furthermore, the existing refresh handler did not check the status of the user account in the database. A suspended, deactivated, or deleted account could continue generating valid access tokens as long as the refresh token record had not been explicitly revoked.

Finally, naive rotation where a token is revoked instantly with zero tolerance breaks mobile apps on erratic cellular networks. When mobile network connectivity drops mid flight, a client may retry the refresh call. If the first request reached the server and rotated the token, the client never receives the response, and its second request with the old token would fail, locking out legitimate users.

## Options considered

### Option 1: In place rotation with grace window and cascade breach revocation

When a client presents a valid refresh token, the server revokes that token, records `revoked_at` and `replaced_by_id`, creates a new active token, and returns both new tokens in `TokenResponse`. If a duplicate request with the rotated token arrives within a thirty second grace period, the server safely returns a fresh or replacement token pair. If the rotated token is reused outside the thirty second window, the system assumes token theft, revokes every active token for that user, and rejects the call.

**Pros**:
- Eliminates perpetual static refresh token exposure.
- Robust against intermittent cellular drops and connection retries.
- Immediate breach detection stops attackers from using intercepted tokens.
- Reuses existing relational persistence without adding Redis infrastructure.

**Cons**:
- Slightly higher database write load on each token exchange.
- Requires mobile client to update local secure storage on every refresh.

### Option 2: Sliding schedule rotation without grace window

Rotate the refresh token only when the current token reaches half its total thirty day lifetime. Immediately reject any rotated token with zero grace window.

**Pros**:
- Fewer database write operations than rotating on every refresh.

**Cons**:
- A compromised token remains valid for up to fifteen days before rotation occurs.
- High risk of false user lockouts on flaky mobile connections where retries are standard behavior.

### Option 3: Stateless refresh tokens with client side rotation

Encode refresh tokens as long lived signed JWTs without database tracking, generating a new JWT on each call.

**Pros**:
- Zero database queries on refresh calls.

**Cons**:
- Impossible to revoke individual tokens or terminate compromised sessions immediately.
- Fails security and audit requirements for a transportation and financial wallet app.

## Rationale

Option 1 is selected because it delivers complete token rotation security while protecting mobile reliability.

The thirty second grace period directly solves the mobile connectivity problem without weakening security: an attacker intercepting a token over network transport cannot easily predict or exploit a brief thirty second transition window, whereas any subsequent attempt immediately shuts down all sessions for that account.

Checking user account status during token refresh guarantees that administrative blocks and account terminations take effect on the very next token renewal cycle, ensuring strict compliance with MargNetra security requirements.
