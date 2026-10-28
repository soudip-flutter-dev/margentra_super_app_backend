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
| 3 | User profile, vehicle garage, and settings integration | Slice 3 | in-progress |
| 4 | Trip speedometer HUD and live telemetry streaming integration | Slice 4 | planned |
| 5 | MGC rewards wallet and FASTag redemption integration | Slice 5 | planned |
| 6 | Electronic challan management and RTO sync integration | Slice 6 | planned |
| 7 | Legal vault dashcam evidence and affidavit export integration | Slice 7 | planned |
| 8 | DigiLocker document storage and expiry alerts integration | Slice 8 | planned |
| 9 | Family circle and real time location sharing integration | Slice 9 | planned |
| 10 | Emergency SOS and roadside assistance integration | Slice 10 | planned |
| 11 | Bounty hazard capture and media submission integration | Slice 11 | planned |
| 12 | Hardware BLE OBD device pairing integration | Slice 12 | planned |
| 13 | Notification center and system alerts integration | Slice 13 | planned |

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

## Slice 3: User profile, vehicle garage, and settings integration

### 3. User profile, vehicle garage, and settings integration · in-progress
Connect user profile details, avatar uploads, civil score history, vehicle garage, and user preferences between Flutter and backend user endpoints.
**Done when:** user profile displays live civil score and streak, user can update profile details, upload avatar, register vehicles, and toggle preferences with state persisted.
- [x] Design it (spec): `/architect user profile vehicle garage and settings integration`
- [x] Build it: `/develop user profile vehicle garage and settings integration`
   - [x] Route registry, Dart data models, and UserRepository calling DataProvider (AC-1, AC-4, AC-6, AC-7)
   - [x] Local storage caching in SharedPrefService for offline profile and settings boot (AC-1, AC-7)
   - [x] ProfileBloc, VehicleBloc, and SettingsBloc with background sync and error mapping (AC-1, AC-2, AC-3, AC-4, AC-5, AC-7)
   - [x] Profile and vehicle garage UI with avatar picker and Add Vehicle duplicate plate validation (AC-1, AC-2, AC-3, AC-4, AC-5, AC-6)
   - [x] Settings UI with dark mode theme switching and notification toggles (AC-7)
- [x] Verify it: `/check verify user profile vehicle garage and settings integration`
- [ ] Test it: `/test user profile vehicle garage and settings integration`
Spec [0003](../specs/0003-user-profile-vehicles-settings/index.md) · code in `margnetra_super_app/lib/pages/profile_page/`, `margnetra_super_app/lib/pages/settings_page/`, `margnetra_super_app/lib/core/app_services/`

## Slice 4: Trip speedometer HUD and live telemetry streaming integration

### 4. Trip speedometer HUD and live telemetry streaming integration · needs a decision
Stream real time driving telemetry over WebSocket and synchronize trip start, telemetry batches, earnings, and completion with rewards calculation.
**Done when:** speedometer connects to live trip WebSocket, pushes telemetry batches to backend, starts and finishes trips, and displays trip completion rewards.
- [ ] Design it (spec): `/architect trip speedometer HUD and live telemetry streaming integration`

## Slice 5: MGC rewards wallet and FASTag redemption integration

### 5. MGC rewards wallet and FASTag redemption integration · needs a decision
Display live MGC coin balance, paginated reward transaction history, and enable redeeming tokens to FASTag accounts or purchasing streak protection.
**Done when:** wallet screen displays live balance and transaction feed, and user can submit FASTag redemption or activate streak protection with balance deduction.
- [ ] Design it (spec): `/architect MGC rewards wallet and FASTag redemption integration`

## Slice 6: Electronic challan management and RTO sync integration

### 6. Electronic challan management and RTO sync integration · needs a decision
Display issued traffic challans across registered vehicles, trigger live RTO sync, process fine payments, and submit dispute claims with evidence.
**Done when:** challan page lists pending and paid challans, sync button refreshes records from RTO, payment updates challan status, and disputes submit successfully.
- [ ] Design it (spec): `/architect electronic challan management and RTO sync integration`

## Slice 7: Legal vault dashcam evidence and affidavit export integration

### 7. Legal vault dashcam evidence and affidavit export integration · needs a decision
Upload dashcam video clips with server side SHA 256 hash generation for Section 65B legal admissibility and export court certified affidavit PDFs.
**Done when:** legal vault page lists incident events, video uploads generate SHA 256 certificates, and user can download generated affidavit PDFs.
- [ ] Design it (spec): `/architect legal vault dashcam evidence and affidavit export integration`

## Slice 8: DigiLocker document storage and expiry alerts integration

### 8. DigiLocker document storage and expiry alerts integration · needs a decision
Fetch and store vehicle documents such as RC, driving license, insurance, and PUC, and display proactive expiry countdown alerts.
**Done when:** DigiLocker page displays stored documents, allows uploading new files with metadata, and highlights documents expiring within thirty days.
- [ ] Design it (spec): `/architect DigiLocker document storage and expiry alerts integration`

## Slice 9: Family circle and real time location sharing integration

### 9. Family circle and real time location sharing integration · needs a decision
Invite and manage trusted family members, view last known locations on map, and stream bidirectional real time GPS updates over WebSocket.
**Done when:** family circle page displays member list, user can send phone invites, view member locations, and stream live coordinate updates via WebSocket.
- [ ] Design it (spec): `/architect family circle and real time location sharing integration`

## Slice 10: Emergency SOS and roadside assistance integration

### 10. Emergency SOS and roadside assistance integration · needs a decision
Trigger one tap emergency alerts dispatching coordinates to saved contacts and submit roadside assistance requests for flat tyres, battery, or towing.
**Done when:** SOS button triggers backend dispatch, emergency contacts can be managed and saved, and roadside assistance requests return live status and provider ETA.
- [ ] Design it (spec): `/architect emergency SOS and roadside assistance integration`

## Slice 11: Bounty hazard capture and media submission integration

### 11. Bounty hazard capture and media submission integration · needs a decision
Browse active road hazard reporting campaigns and submit photo or video evidence with GPS coordinates for MGC reward review.
**Done when:** bounty page lists active community campaigns and user can capture and upload hazard media with location to receive submission tracking.
- [ ] Design it (spec): `/architect bounty hazard capture and media submission integration`

## Slice 12: Hardware BLE OBD device pairing integration

### 12. Hardware BLE OBD device pairing integration · needs a decision
Scan, pair, and register onboard diagnostic and bluetooth hardware dongles to collect vehicle diagnostics and driving telemetry.
**Done when:** device page scans and lists paired BLE OBD hardware, registers device MAC address with backend, and displays active connection status.
- [ ] Design it (spec): `/architect hardware BLE OBD device pairing integration`

## Slice 13: Notification center and system alerts integration

### 13. Notification center and system alerts integration · needs a decision
Present in app notification center for trip reward alerts, challan notices, and document reminders, with read state synchronization.
**Done when:** notification drawer lists paginated user alerts and tapping an alert marks it read on backend and updates unread badge counter.
- [ ] Design it (spec): `/architect notification center and system alerts integration`

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
