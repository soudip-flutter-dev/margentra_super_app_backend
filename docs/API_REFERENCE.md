# MargNetra Super App — API Reference

> **Base URL:** `http://<host>/api/v1`  
> **Auth:** Bearer JWT in `Authorization: Bearer <access_token>` header (unless noted as public).  
> **Rate limit on `/auth/refresh`:** 10 requests / minute per IP.

---

## Table of Contents

1. [Health](#health)
2. [Auth](#auth)
3. [User](#user)
4. [Wallet](#wallet)
5. [Trip](#trip)
6. [Challan (e-Challan)](#challan-e-challan)
7. [Legal Vault](#legal-vault)
8. [DigiLocker](#digilocker)
9. [Family Circle](#family-circle)
10. [SOS (Emergency)](#sos-emergency)
11. [Bounty Capture](#bounty-capture)
12. [Devices (BLE / OBD)](#devices-ble--obd)
13. [Notifications](#notifications)
14. [WebSockets](#websockets)

---

## Health

### `GET /health`

> 🔓 Public — no authentication required.

Returns application health status.

**Response `200`**

```json
{
  "status": "ok",
  "app": "MargNetra",
  "version": "1.0.0",
  "db_backend": "postgresql"
}
```

---

## Auth

> **Prefix:** `/api/v1/auth` · **Tag:** `Auth` · 🔓 All endpoints are **public** (no token required).

### `POST /auth/register`

Register a new MargNetra user.

**Request body**

```json
{
  "full_name": "string",
  "phone": "string",
  "email": "string",
  "password": "string"
}
```

**Response `201` — `UserProfileOut`**

```json
{
  "id": 1,
  "full_name": "Rahul Sharma",
  "phone": "+919876543210",
  "email": "rahul@example.com",
  "avatar_url": null,
  "civil_score": 750.0,
  "driving_streak_days": 0,
  "mgc_balance": 0.0
}
```

---

### `POST /auth/login`

Authenticate and receive JWT access + refresh tokens.

**Request body**

```json
{
  "phone": "string",
  "password": "string"
}
```

**Response `200` — `TokenResponse`**

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<uuid>",
  "token_type": "bearer"
}
```

---

### `POST /auth/forgot-password`

Send OTP to registered phone for password reset.

**Request body**

```json
{
  "phone": "string"
}
```

**Response `200` — `MessageResponse`**

```json
{
  "message": "OTP sent to +919876543210"
}
```

---

### `POST /auth/reset-password`

Reset password using OTP received on phone.

**Request body**

```json
{
  "phone": "string",
  "otp": "string",
  "new_password": "string"
}
```

**Response `200` — `MessageResponse`**

```json
{
  "message": "Password reset successfully"
}
```

---

### `POST /auth/logout`

Revoke refresh token (client should also discard access token locally).

**Request body**

```json
{
  "refresh_token": "string"
}
```

**Response `200` — `MessageResponse`**

```json
{
  "message": "Logged out successfully"
}
```

---

### `POST /auth/refresh`

> ⏱ Rate limited: **10 requests / minute**.

Exchange a valid refresh token for a new access token and a rotated refresh token.

**Request body**

```json
{
  "refresh_token": "string"
}
```

**Response `200` — `TokenResponse`**

```json
{
  "access_token": "<new_jwt>",
  "refresh_token": "<new_uuid>",
  "token_type": "bearer"
}
```

---

## User

> **Prefix:** `/api/v1/user` · **Tag:** `User` · 🔒 All endpoints require Bearer token.

### `GET /user/profile`

Get the authenticated user's profile.

**Response `200` — `UserProfileOut`**

```json
{
  "id": 1,
  "full_name": "Rahul Sharma",
  "phone": "+919876543210",
  "email": "rahul@example.com",
  "avatar_url": "https://cdn.example.com/avatars/1/avatar.jpg",
  "civil_score": 820.5,
  "driving_streak_days": 14,
  "mgc_balance": 340.0
}
```

---

### `PUT /user/profile`

Update the authenticated user's profile (name and/or email).

**Request body**

```json
{
  "full_name": "string | null",
  "email": "string | null"
}
```

**Response `200` — `UserProfileOut`** *(same as GET profile)*

---

### `GET /user/civil-score`

Get current civil score plus last 30 completed trips history.

**Response `200` — `CivilScoreOut`**

```json
{
  "current_score": 820.5,
  "streak_days": 14,
  "history": [
    {
      "date": "2026-10-26T15:00:00",
      "score": 817.5,
      "delta": 3.0,
      "reason": "Trip #42 completed (12.5 km)"
    }
  ]
}
```

---

### `GET /user/vehicles`

List all registered vehicles for the current user.

**Response `200` — `list[VehicleOut]`**

```json
[
  {
    "id": 1,
    "registration_number": "KA01AB1234",
    "make": "Maruti",
    "model": "Swift",
    "year": 2022,
    "fuel_type": "petrol"
  }
]
```

---

### `POST /user/vehicles`

Register a new vehicle.

**Request body**

```json
{
  "registration_number": "string",
  "make": "string",
  "model": "string",
  "year": 2022,
  "fuel_type": "string"
}
```

**Response `201` — `VehicleOut`**

---

### `GET /user/payment-methods`

List saved payment methods.

**Response `200` — `list[PaymentMethodOut]`**

```json
[
  {
    "id": 1,
    "type": "upi",
    "identifier": "rahul@okaxis"
  }
]
```

---

### `POST /user/payment-methods`

Add a new payment method.

**Request body**

```json
{
  "type": "string",
  "identifier": "string"
}
```

**Response `201` — `PaymentMethodOut`**

---

### `GET /user/settings`

Get (or auto-create) app settings for the current user.

**Response `200` — `AppSettingsOut`**

```json
{
  "notifications_enabled": true,
  "dark_mode": false,
  "language": "en"
}
```

---

### `PUT /user/settings`

Update app settings (partial update supported).

**Request body**

```json
{
  "notifications_enabled": true,
  "dark_mode": true,
  "language": "hi"
}
```

**Response `200` — `AppSettingsOut`**

---

### `POST /user/avatar`

Upload a profile avatar image (`multipart/form-data`).

| Field | Type | Description |
|-------|------|-------------|
| `file` | `UploadFile` | Image file (JPEG recommended) |

**Response `200` — `UserProfileOut`** *(includes updated `avatar_url`)*

---

## Wallet

> **Prefix:** `/api/v1/wallet` · **Tag:** `Wallet` · 🔒 All endpoints require Bearer token.

### `GET /wallet/balance`

Get current MGC wallet balance.

**Response `200` — `WalletBalanceOut`**

```json
{
  "mgc_balance": 340.0,
  "currency": "MGC"
}
```

---

### `GET /wallet/transactions`

Paginated wallet transaction history.

**Query params**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | `int` | `1` | Page number |
| `limit` | `int` | `20` | Items per page |

**Response `200` — `PaginatedResponse[WalletTransactionOut]`**

```json
{
  "items": [
    {
      "id": 1,
      "type": "credit",
      "amount": 50.0,
      "description": "Trip reward",
      "created_at": "2026-10-26T10:00:00"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20
}
```

---

### `POST /wallet/redeem/fastag`

Redeem MGC tokens to a FASTag account.

**Request body**

```json
{
  "amount_mgc": 100.0,
  "fastag_id": "string"
}
```

**Response `200` — `RedeemFastagResponse`**

```json
{
  "success": true,
  "mgc_deducted": 100.0,
  "fastag_credited": 100.0,
  "new_balance": 240.0
}
```

---

### `POST /wallet/buy/streak-protection`

Purchase a streak protection shield (deducts MGC).

**Response `200` — `BuyStreakProtectionResponse`**

```json
{
  "success": true,
  "mgc_deducted": 50.0,
  "new_balance": 190.0,
  "message": "Streak protection activated"
}
```

---

## Trip

> **Prefix:** `/api/v1/trip` · **Tag:** `Trip` · 🔒 All endpoints require Bearer token.

### `POST /trip/start`

Start a new driving trip.

**Request body**

```json
{
  "vehicle_id": 1,
  "start_lat": 12.9716,
  "start_lng": 77.5946
}
```

**Response `201` — `StartTripResponse`**

```json
{
  "trip_id": 10,
  "started_at": "2026-10-27T08:00:00",
  "message": "Trip started"
}
```

---

### `POST /trip/end`

End an active trip.

**Request body**

```json
{
  "trip_id": 10,
  "end_lat": 12.9352,
  "end_lng": 77.6245,
  "distance_km": 8.3
}
```

**Response `200` — `EndTripResponse`**

```json
{
  "trip": { "...TripSummaryOut..." },
  "mgc_earned": 24.9,
  "civil_score_delta": 3.5,
  "new_civil_score": 824.0,
  "new_mgc_balance": 364.9,
  "message": "Trip ended successfully"
}
```

---

### `POST /trip/telemetry`

Post OBD/sensor telemetry data for an active trip. Also broadcasts to WebSocket subscribers.

**Request body**

```json
{
  "trip_id": 10,
  "points": [
    {
      "timestamp": "2026-10-27T08:05:00",
      "speed_kmh": 55.0,
      "rpm": 2200,
      "g_force": 0.1,
      "engine_temp_c": 88.0
    }
  ]
}
```

**Response `200` — `PostTelemetryResponse`**

```json
{
  "accepted": 1,
  "message": "1 telemetry points stored"
}
```

---

### `GET /trip/earnings/current`

Get current/today's trip earnings summary.

**Response `200` — `CurrentEarningsResponse`**

```json
{
  "today_mgc": 74.5,
  "today_trips": 3,
  "current_trip_id": 10
}
```

---

### `GET /trip/history`

Paginated list of completed trips.

**Query params**

| Param | Type | Default |
|-------|------|---------|
| `page` | `int` | `1` |
| `limit` | `int` | `20` |

**Response `200` — `PaginatedResponse[TripSummaryOut]`**

```json
{
  "items": [
    {
      "id": 9,
      "started_at": "2026-10-26T07:30:00",
      "ended_at": "2026-10-26T08:00:00",
      "distance_km": 12.5,
      "civil_score_delta": 3.0,
      "mgc_earned": 37.5,
      "status": "completed"
    }
  ],
  "total": 41,
  "page": 1,
  "limit": 20
}
```

---

## Challan (e-Challan)

> **Prefix:** `/api/v1/challan` · **Tag:** `Challan` · 🔒 All endpoints require Bearer token.

### `GET /challan/list`

Paginated list of e-Challans for the current user's vehicles.

**Query params:** `page`, `limit`

**Response `200` — `PaginatedResponse[ChallanOut]`**

```json
{
  "items": [
    {
      "id": 5,
      "challan_number": "KA-2026-001234",
      "vehicle_registration": "KA01AB1234",
      "offence": "Speeding",
      "fine_amount": 500.0,
      "status": "pending",
      "issued_at": "2026-10-20T10:00:00"
    }
  ],
  "total": 3,
  "page": 1,
  "limit": 20
}
```

---

### `POST /challan/sync`

Fetch latest challans from RTO/Vahan for all registered vehicles.

**Response `200` — `SyncChallanResponse`**

```json
{
  "synced": 2,
  "new_challans": 1,
  "message": "Sync completed"
}
```

---

### `POST /challan/pay`

Pay a pending challan using a saved payment method.

**Request body**

```json
{
  "challan_id": 5,
  "payment_method_id": 1
}
```

**Response `200` — `PayChallanResponse`**

```json
{
  "challan_id": 5,
  "amount_paid": 500.0,
  "status": "paid",
  "transaction_ref": "TXN20261027XXXX"
}
```

---

### `POST /challan/dispute`

Raise a dispute for a challan.

**Request body**

```json
{
  "challan_id": 5,
  "reason": "string",
  "evidence_url": "string | null"
}
```

**Response `201` — `DisputeOut`**

```json
{
  "id": 1,
  "challan_id": 5,
  "reason": "Vehicle was not at the location",
  "status": "submitted",
  "created_at": "2026-10-27T09:00:00"
}
```

---

## Legal Vault

> **Prefix:** `/api/v1/legal` · **Tag:** `Legal` · 🔒 All endpoints require Bearer token.

### `GET /legal/events`

Paginated list of stored legal/dashcam events.

**Query params:** `page`, `limit`

**Response `200` — `PaginatedResponse[LegalEventOut]`**

```json
{
  "items": [
    {
      "id": 2,
      "title": "Accident near MG Road",
      "description": "Vehicle hit from behind",
      "incident_date": "2026-10-15",
      "location": "MG Road, Bengaluru",
      "video_url": "https://cdn.example.com/legal/2/clip.mp4",
      "video_sha256": "a3f5...",
      "affidavit_pdf_url": null,
      "created_at": "2026-10-15T18:00:00"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 20
}
```

---

### `POST /legal/events/upload`

Upload a dashcam clip; SHA-256 is computed server-side for Sec 65B admissibility.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | `string` | Yes | Event title |
| `description` | `string` | No | Optional description |
| `incident_date` | `date` | No | `YYYY-MM-DD` |
| `location` | `string` | No | Location string |
| `video` | `file` | Yes | Dashcam video file |

**Response `201` — `UploadLegalEventResponse`**

```json
{
  "event_id": 3,
  "video_url": "https://cdn.example.com/legal/3/clip.mp4",
  "video_sha256": "e7a2...",
  "message": "Legal event uploaded and certified"
}
```

---

### `GET /legal/events/{event_id}/export`

Generate and return a Sec 65B affidavit PDF for the legal event.

**Path params:** `event_id` (int)

**Response `200` — `ExportAffidavitResponse`**

```json
{
  "event_id": 3,
  "affidavit_pdf_url": "https://cdn.example.com/legal/3/affidavit.pdf",
  "video_sha256": "e7a2...",
  "message": "Affidavit generated"
}
```

---

## DigiLocker

> **Prefix:** `/api/v1/digilocker` · **Tag:** `DigiLocker` · 🔒 All endpoints require Bearer token.

### `GET /digilocker/documents`

Paginated list of stored documents.

**Query params:** `page`, `limit`

**Response `200` — `PaginatedResponse[DocumentOut]`**

```json
{
  "items": [
    {
      "id": 1,
      "doc_type": "RC",
      "doc_number": "KA01AB1234",
      "expiry_date": "2032-06-30",
      "issued_by": "RTO Bengaluru",
      "issuing_state": "Karnataka",
      "doc_url": "https://cdn.example.com/docs/1/rc.pdf"
    }
  ],
  "total": 4,
  "page": 1,
  "limit": 20
}
```

---

### `POST /digilocker/documents/upload`

Upload a document to the DigiLocker vault.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `doc_type` | `string` | Yes | e.g. `RC`, `DL`, `Insurance`, `PUC` |
| `doc_number` | `string` | No | Document number |
| `expiry_date` | `date` | No | `YYYY-MM-DD` |
| `issued_by` | `string` | No | Issuing authority |
| `issuing_state` | `string` | No | State code |
| `file` | `file` | Yes | Document file (PDF/image) |

**Response `201` — `UploadDocumentResponse`**

```json
{
  "document_id": 5,
  "doc_url": "https://cdn.example.com/docs/5/dl.pdf",
  "message": "Document uploaded"
}
```

---

### `GET /digilocker/alerts`

Get list of documents expiring soon.

**Response `200` — `list[ExpiryAlertOut]`**

```json
[
  {
    "document_id": 2,
    "doc_type": "Insurance",
    "expiry_date": "2026-11-15",
    "days_remaining": 19
  }
]
```

---

## Family Circle

> **Prefix:** `/api/v1/family` · **Tag:** `Family` · 🔒 All endpoints require Bearer token.

### `GET /family/members`

List all family circle members.

**Response `200` — `list[FamilyMemberOut]`**

```json
[
  {
    "id": 2,
    "name": "Priya Sharma",
    "phone": "+919876540000",
    "relation": "spouse",
    "status": "active"
  }
]
```

---

### `POST /family/invite`

Invite a new member to the family circle.

**Request body**

```json
{
  "phone": "string",
  "relation": "string"
}
```

**Response `201` — `InviteMemberResponse`**

```json
{
  "member_id": 3,
  "phone": "+919000000001",
  "status": "invited",
  "message": "Invitation sent"
}
```

---

### `GET /family/members/{member_id}/location`

Get the last known location of a family circle member.

**Path params:** `member_id` (int)

**Response `200` — `MemberLocationOut`**

```json
{
  "member_id": 2,
  "name": "Priya Sharma",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "updated_at": "2026-10-27T09:45:00"
}
```

---

## SOS (Emergency)

> **Prefix:** `/api/v1/sos` · **Tag:** `SOS` · 🔒 All endpoints require Bearer token.

### `POST /sos/trigger`

Trigger an emergency SOS alert to all registered emergency contacts.

**Request body**

```json
{
  "latitude": 12.9716,
  "longitude": 77.5946,
  "message": "string | null"
}
```

**Response `201` — `TriggerSOSResponse`**

```json
{
  "alert_id": 7,
  "status": "sent",
  "contacted_numbers": ["+919876540000", "+919876540001"],
  "message": "SOS alert triggered"
}
```

---

### `GET /sos/contacts`

List all emergency contacts.

**Response `200` — `list[EmergencyContactOut]`**

```json
[
  {
    "id": 1,
    "name": "Priya Sharma",
    "phone": "+919876540000",
    "relation": "spouse"
  }
]
```

---

### `POST /sos/contacts`

Add or update an emergency contact (keyed on phone number).

**Request body**

```json
{
  "name": "string",
  "phone": "string",
  "relation": "string"
}
```

**Response `200` — `EmergencyContactOut`**

---

### `POST /sos/road-assistance`

Request roadside assistance.

**Request body**

```json
{
  "latitude": 12.9716,
  "longitude": 77.5946,
  "issue_type": "flat_tyre | battery | towing | fuel",
  "notes": "string | null"
}
```

**Response `201` — `RoadAssistanceResponse`**

```json
{
  "request_id": 4,
  "status": "dispatched",
  "provider_name": "MargNetra Assist",
  "eta_minutes": 25,
  "message": "Road assistance request submitted"
}
```

---

## Bounty Capture

> **Prefix:** `/api/v1/bounty` · **Tag:** `Bounty` · 🔒 All endpoints require Bearer token.

### `GET /bounty/events`

Paginated list of active bounty capture events.

**Query params:** `page`, `limit`

**Response `200` — `PaginatedResponse[BountyEventOut]`**

```json
{
  "items": [
    {
      "id": 1,
      "title": "Pothole Reporting Drive",
      "description": "Capture potholes on NH-48",
      "reward_mgc": 20.0,
      "deadline": "2026-11-01",
      "status": "active"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

---

### `POST /bounty/submit`

Submit a bounty capture with optional media evidence.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `int` | Yes | Bounty event ID |
| `latitude` | `float` | No | GPS latitude |
| `longitude` | `float` | No | GPS longitude |
| `notes` | `string` | No | Additional notes |
| `media` | `file` | No | Photo/video evidence |

**Response `201` — `SubmitBountyResponse`**

```json
{
  "submission_id": 12,
  "event_id": 1,
  "status": "pending_review",
  "media_url": "https://cdn.example.com/bounty/12/photo.jpg",
  "message": "Bounty submission received, pending review"
}
```

---

## Devices (BLE / OBD)

> **Prefix:** `/api/v1/devices` · **Tag:** `Devices` · 🔒 All endpoints require Bearer token.

### `POST /devices/register`

Register a BLE or OBD device.

**Request body**

```json
{
  "device_name": "string",
  "device_type": "BLE | OBD",
  "mac_address": "string"
}
```

**Response `201` — `RegisterDeviceResponse`**

```json
{
  "device_id": 3,
  "device_name": "OBD Pro 2",
  "message": "Device registered successfully"
}
```

---

### `GET /devices/list`

List all registered devices for the current user.

**Response `200` — `list[DeviceOut]`**

```json
[
  {
    "id": 3,
    "device_name": "OBD Pro 2",
    "device_type": "OBD",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "registered_at": "2026-10-01T10:00:00"
  }
]
```

---

## Notifications

> **Prefix:** `/api/v1/notifications` · **Tag:** `Notifications` · 🔒 All endpoints require Bearer token.

### `GET /notifications`

Paginated list of notifications for the current user.

**Query params:** `page`, `limit`

**Response `200` — `PaginatedResponse[NotificationOut]`**

```json
{
  "items": [
    {
      "id": 20,
      "title": "Trip Reward",
      "body": "You earned 24.9 MGC for your last trip!",
      "is_read": false,
      "created_at": "2026-10-27T08:30:00"
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 20
}
```

---

### `PUT /notifications/{notification_id}/read`

Mark a notification as read.

**Path params:** `notification_id` (int)

**Response `200` — `MarkReadResponse`**

```json
{
  "notification_id": 20,
  "is_read": true,
  "message": "Notification marked as read"
}
```

---

## WebSockets

> Auth via `?token=<jwt>` query param **or** first message `{"token": "<jwt>"}`.  
> Close code `4001` = Unauthorized.

### `WS /ws/trip/live`

Stream live trip telemetry for an active trip.

**Query params**

| Param | Required | Description |
|-------|----------|-------------|
| `token` | No | JWT access token (alternative: first message auth) |
| `trip_id` | Yes | Active trip ID to subscribe to |

**Server to Client push frame**

```json
{
  "event": "telemetry",
  "data": {
    "speed": 60,
    "rpm": 2000,
    "g_force": 0.1,
    "engine_temp": 88.0,
    "timestamp": "2026-10-27T08:10:00"
  }
}
```

**Client to Server keep-alive / pong**

```json
{ "type": "ping" }
```

---

### `WS /ws/family/live`

Stream live family member location updates.

**Query params**

| Param | Required | Description |
|-------|----------|-------------|
| `token` | No | JWT access token |
| `family_circle_id` | Yes | Family circle ID to subscribe to |

**Server to Client push frame**

```json
{
  "event": "location_update",
  "data": {
    "member_id": 2,
    "lat": 12.97,
    "lng": 77.59,
    "user_id": "42"
  }
}
```

**Client to Server location push**

```json
{
  "type": "location_update",
  "data": { "lat": 12.97, "lng": 77.59 }
}
```

---

## Common Schemas

### `PaginatedResponse`

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "limit": 20
}
```

### `MessageResponse`

```json
{ "message": "string" }
```

### Error responses

| Status | Meaning |
|--------|---------|
| `400` | Bad request / validation error |
| `401` | Missing or invalid token |
| `403` | Forbidden (resource belongs to another user) |
| `404` | Resource not found |
| `422` | Unprocessable entity (Pydantic validation) |
| `429` | Rate limit exceeded |
| `500` | Internal server error |

---

*Generated from `app/api/v1/endpoints/` — 2026-10-27*
