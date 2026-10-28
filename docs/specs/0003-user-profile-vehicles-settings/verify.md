# Verify: user profile vehicle garage and settings integration : spec 0003 : updated 2026-10-27
_Steps derived from spec 0003 acceptance criteria. `/check verify` runs these; `/test` locks the durable ones._

## Mobile and API Verification
- [x] Open profile screen on mobile client, expect live driver name, phone, civil score, driving streak, and MGC balance loaded from `GET /api/v1/user/profile` → AC-1
- [x] Edit full name or email and submit, expect profile update reflected on screen and in database via `PUT /api/v1/user/profile` → AC-2
- [x] Pick an avatar image from camera or gallery and upload, expect new avatar URL saved and image rendered in avatar circle via `POST /api/v1/user/avatar` → AC-3
- [x] Inspect vehicle garage on profile, expect list of user registered vehicles matching `GET /api/v1/user/vehicles` → AC-4
- [x] Open Add Vehicle modal, submit valid registration plate, make, model, year, and fuel type, expect new vehicle card appended to list via `POST /api/v1/user/vehicles` → AC-5
- [x] Submit vehicle with an already registered number plate, expect inline validation error without wiping entered form fields → AC-5
- [x] View saved payment methods and add a new UPI ID, expect payment method saved via `POST /api/v1/user/payment-methods` → AC-6
- [x] Open settings screen, toggle dark mode, push notifications, and language, expect client theme or locale updated instantly and synced to backend via `PUT /api/v1/user/settings` → AC-7
- [x] Cold launch mobile app with network turned off, expect cached profile details and preferences rendered from local shared preferences storage → AC-1, AC-7

## Acceptance criteria coverage
- AC-1 (Profile details and civil score): covered by profile screen load and offline cache fallback
- AC-2 (Profile editing): covered by profile update form submission
- AC-3 (Avatar upload): covered by camera and gallery image picker multipart upload
- AC-4 (Vehicle listing): covered by garage vehicle list rendering
- AC-5 (Vehicle registration and duplicate validation): covered by Add Vehicle bottom sheet and error handling
- AC-6 (Payment methods): covered by payment method list and creation
- AC-7 (App settings and theme synchronization): covered by settings toggles and background sync
