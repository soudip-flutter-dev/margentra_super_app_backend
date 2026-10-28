# 0003. User profile, vehicle garage, and settings integration

**Date**: 2026-10-27
**Status**: In Progress

## Summary

This specification defines the mobile integration connecting the Flutter profile, garage, and settings screens to the existing FastAPI user endpoints. It establishes Dart data models, repository methods, and dedicated BLoC state managers for driver profile details, avatar uploads, civil score history, vehicle registration, and user preferences. Building this slice enables users to manage their identity and vehicles, which provides the essential foundation needed by subsequent driving trip and electronic challan slices.

## Requirements

**User stories**:
- As a driver, I want to view my profile details, civil score, driving streak, and coin balance so that I know my current standing and rewards.
- As a driver, I want to edit my name, email, and avatar picture so that my profile reflects my current identity.
- As a vehicle owner, I want to register and view my vehicles so that my driving trips and electronic challans link to the right car or motorcycle.
- As a driver, I want to view and add saved payment methods so that I can easily pay challans and manage tolls.
- As an app user, I want to customize dark mode, push notifications, and language so that the application adapts to my preferences.

**Acceptance criteria**:
- **AC-1**: Profile screen renders live user details, civil driving score, driving streak day count, and MGC balance from `GET /api/v1/user/profile`, falling back to local cached storage on cold launch.
- **AC-2**: User can edit their full name and email via `PUT /api/v1/user/profile`, updating both remote backend state and local cached state.
- **AC-3**: User can select an avatar image from camera or gallery, compress it on device, and upload via multipart form data to `POST /api/v1/user/avatar`, displaying the updated avatar image immediately upon success.
- **AC-4**: Vehicle garage lists all user registered vehicles from `GET /api/v1/user/vehicles` and renders make, model, registration plate, and fuel type.
- **AC-5**: User can register a new vehicle through an add vehicle bottom sheet modal via `POST /api/v1/user/vehicles`, showing inline validation warnings for duplicate registration numbers without dismissing input.
- **AC-6**: User can view saved payment methods and register a new UPI ID or card via `POST /api/v1/user/payment-methods`.
- **AC-7**: Settings screen displays toggles for push notifications, dark mode theme, and language selection, syncing changes in the background via `PUT /api/v1/user/settings` and applying theme and locale changes immediately to the Flutter client.

## Decision

**Chosen option**: Option 1: Modular BLoCs with dedicated repository and local shared preferences caching

We integrate the user profile, vehicle garage, and settings modules into Flutter using the existing BLoC, repository, and `DataProvider` architectural pattern. `UserRepository` handles all HTTP communication and token injection. `SharedPrefService` caches user profile and preference state so screens render instantly without blank loading states on app cold start.

## Feature design

**Data model sketch**:

```
UserProfileModel (matches UserProfileOut):
- id: int (required)
- full_name: String (required)
- phone: String (required)
- email: String? (nullable)
- avatar_url: String? (nullable)
- civil_score: double (required, default 750.0)
- driving_streak_days: int (required, default 0)
- mgc_balance: double (required, default 0.0)

VehicleModel (matches VehicleOut):
- id: int (required)
- registration_number: String (required, unique)
- make: String (required)
- model: String (required)
- year: int (required)
- fuel_type: String (required: petrol, diesel, ev, cng)
- is_primary: bool (default false)
- insurance_expiry: DateTime? (nullable)
- puc_expiry: DateTime? (nullable)

PaymentMethodModel (matches PaymentMethodOut):
- id: int (required)
- type: String (required: upi, card, fastag)
- identifier: String (required, e.g. user@okhdfcbank)
- is_default: bool (default false)

AppSettingsModel (matches AppSettingsOut):
- notifications_enabled: bool (default true)
- location_sharing: bool (default true)
- dark_mode: bool (default true)
- language: String (default en)
- hud_overlay: bool (default true)

CivilScoreOut:
- current_score: double
- streak_days: int
- history: List<CivilScoreHistoryItem> (date: DateTime, score: double, delta: double, reason: String)
```

**State transitions**:

Profile flow:
- `ProfileInitial` -> `ProfileLoading` (reads local cache first if present) -> `ProfileLoaded` (renders profile, civil score, vehicles, and payment methods) -> `ProfileUpdating` (while saving name or uploading avatar) -> `ProfileLoaded` (with fresh data) or `ProfileError` (with retry action)

Vehicle flow:
- `VehicleModalInitial` -> `VehicleSubmitting` -> `VehicleSubmitSuccess` (closes modal and appends to garage list) or `VehicleSubmitError` (keeps modal open with inline error message)

Settings flow:
- `SettingsLoaded` -> user toggles setting -> `SettingsOptimisticUpdate` (applies theme or toggle instantly) -> background sync via `PUT /api/v1/user/settings` -> `SettingsSynced`

**API surface**:

| Endpoint | Method | Key inputs | Key outputs | Auth | Key errors |
|---|---|---|---|---|---|
| `/api/v1/user/profile` | `GET` | none | `UserProfileOut` | Bearer Token | `401 Unauthorized` |
| `/api/v1/user/profile` | `PUT` | `full_name: string?`, `email: string?` | `UserProfileOut` | Bearer Token | `401 Unauthorized`, `422 Invalid` |
| `/api/v1/user/avatar` | `POST` | `file: UploadFile` (multipart form data) | `UserProfileOut` (updated `avatar_url`) | Bearer Token | `400 Bad Request`, `401 Unauthorized` |
| `/api/v1/user/civil-score` | `GET` | none | `CivilScoreOut` | Bearer Token | `401 Unauthorized` |
| `/api/v1/user/vehicles` | `GET` | none | `list[VehicleOut]` | Bearer Token | `401 Unauthorized` |
| `/api/v1/user/vehicles` | `POST` | `registration_number: string`, `make: string`, `model: string`, `year: int`, `fuel_type: string` | `VehicleOut` | Bearer Token | `400 Duplicate Plate`, `422 Invalid` |
| `/api/v1/user/payment-methods` | `GET` | none | `list[PaymentMethodOut]` | Bearer Token | `401 Unauthorized` |
| `/api/v1/user/payment-methods` | `POST` | `type: string`, `identifier: string` | `PaymentMethodOut` | Bearer Token | `400 Invalid Identifier`, `422 Invalid` |
| `/api/v1/user/settings` | `GET` | none | `AppSettingsOut` | Bearer Token | `401 Unauthorized` |
| `/api/v1/user/settings` | `PUT` | `notifications_enabled: bool?`, `dark_mode: bool?`, `language: string?` | `AppSettingsOut` | Bearer Token | `401 Unauthorized`, `422 Invalid` |

**Value sourcing**:

| Action | Value produced / displayed | Source |
|---|---|---|
| Load profile screen | Driver name, phone, civil score, streak days, MGC balance | Backend `GET /api/v1/user/profile` response, cached in `SharedPrefService` |
| Update profile name or email | Updated profile details | User input in profile edit text fields sent to `PUT /api/v1/user/profile` |
| Upload profile picture | Fresh `avatar_url` | Image file picked from camera or gallery sent to `POST /api/v1/user/avatar` |
| List vehicles in garage | Vehicle list (make, model, plate, fuel type) | Backend `GET /api/v1/user/vehicles` response |
| Register new vehicle | New vehicle card in garage | Form fields in Add Vehicle bottom sheet sent to `POST /api/v1/user/vehicles` |
| Duplicate vehicle validation | Inline field error message | Backend `HTTP 400` detail message (`Vehicle with this registration number already registered`) |
| Toggle app settings | Theme mode, notification state, language | Switch toggles in `SettingsPage` synced to `PUT /api/v1/user/settings` |

**Key invariants**:
- Profile state must render immediately from local storage cache while the network request executes in the background.
- Adding a vehicle requires all mandatory fields: registration number plate, make, model, year, and fuel type.
- Vehicle registration number input must be capitalized and stripped of whitespace before submission.
- Duplicate vehicle registration plate errors must not wipe the form fields, allowing the user to correct the plate number.
- Avatar image files must be compressed to under two megabytes before upload to minimize mobile data usage.

**Security model**:
- All ten endpoints require Bearer JWT authentication via `Authorization: Bearer <token>`.
- Token expiry is handled automatically by the API client interceptor using refresh token rotation.
- Vehicle records and settings belong strictly to the authenticated user ID extracted from the JWT token.
- Users cannot access or modify another user's vehicles or settings.

**Configuration required**:
- None. Uses existing `baseUrl` defined in [api_urls.dart](file:///d:/office_dev/margentra_super_app_backend_python/margnetra_super_app/lib/core/app_services/api_services/api_urls.dart) and existing shared preferences storage.

**Critical test scenarios**:
- Happy path: Profile screen cold boots with cached data, fetches fresh profile and vehicle list, and renders updated balance and civil score, verifying **AC-1**, **AC-4**.
- Happy path: User opens Add Vehicle modal, enters valid details, and sees the new vehicle appear in the garage list upon submission, verifying **AC-5**.
- Happy path: User updates profile name and uploads a new avatar image, verifying **AC-2**, **AC-3**.
- Happy path: User toggles dark mode switch in settings and the client theme changes instantly while syncing to backend, verifying **AC-7**.
- Failure case: User enters an already registered vehicle plate number and sees an inline duplicate plate error without losing entered make or model, verifying **AC-5**.
- Failure case: Avatar upload fails due to network disconnection, leaving the existing avatar unchanged and offering a retry option, verifying **AC-3**.
- Auth permission: Expired access token triggers silent refresh token rotation, or redirects to login if the refresh token is revoked, verifying **AC-1**.

## Build plan

1. Register all ten user, vehicle, payment, and settings endpoint routes in [api_urls.dart](file:///d:/office_dev/margentra_super_app_backend_python/margnetra_super_app/lib/core/app_services/api_services/api_urls.dart) and create corresponding Dart data models with `fromJson` and `toJson`, satisfies **AC-1**, **AC-4**, **AC-6**, **AC-7**
2. Implement `UserRepository` and `IUserRepository` in Flutter calling `DataProvider` for profile retrieval, profile updates, multipart avatar uploads, vehicle operations, payment methods, and settings, satisfies **AC-1**, **AC-2**, **AC-3**, **AC-4**, **AC-5**, **AC-6**, **AC-7**
3. Extend `SharedPrefService` with helper methods to cache user profile data and app preferences for instant offline rendering, satisfies **AC-1**, **AC-7**
4. Build `ProfileBloc`, `VehicleBloc`, and `SettingsBloc` with events and states handling network calls, optimistic updates, and error mapping, satisfies **AC-1**, **AC-2**, **AC-3**, **AC-4**, **AC-5**, **AC-7**
5. Wire `ProfileWidget` UI with `BlocBuilder` to display live driver details, civil score badge, driving streak counter, avatar image picker, and payment methods list, satisfies **AC-1**, **AC-2**, **AC-3**, **AC-6**
6. Implement Add Vehicle bottom sheet modal with form validation, fuel type dropdown, and inline duplicate registration number warning display, satisfies **AC-4**, **AC-5**
7. Wire `SettingsPage` UI with `SettingsBloc` for dark mode theme toggling, push notifications switch, and language selector, satisfies **AC-7**

## Consequences

**Positive**:
- Replaces static placeholder data on profile and settings screens with real backend integration.
- Provides vehicle garage data required by subsequent trip tracking and electronic challan slices.
- Caching user profile in local storage eliminates empty loading screens during app launch.

**Negative / tradeoffs**:
- Requires adding `image_picker` and `image` compression packages to Flutter dependencies for avatar handling.
- Background settings sync introduces optimistic state that must gracefully rollback if network calls fail.

**Neutral**:
- Settings preferences must be loaded in `main.dart` during app bootstrap to set the initial dark or light theme before widget rendering.

## Follow-up

- [ ] Add `image_picker` package to Flutter `pubspec.yaml` for avatar photo selection.
- [ ] Connect vehicle selection in HUD speedometer slice (Slice 4) to read from this vehicle garage repository.

## Rationale

Reasoning and options: see rationale.md
