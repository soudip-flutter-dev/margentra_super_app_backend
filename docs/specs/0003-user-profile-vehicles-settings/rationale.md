# Rationale: 0003. User profile, vehicle garage, and settings integration

## Context

The MargNetra mobile application has UI layouts for driver profile, vehicle garage, and application settings, but these screens currently display static mock data. The FastAPI backend already exposes complete endpoints for retrieving and updating user profiles, civil driving score history, avatar image uploads, vehicle registration, and user settings.

Without this integration, users cannot view their actual civil score, customize their profile, or register the vehicles needed by subsequent driving trip rewards and electronic challan management modules. The primary technical questions for this slice involve how state is managed across profile, vehicles, and settings, how avatar media is picked and uploaded, and how offline cold starts are handled.

## Options considered

### Option 1: Modular BLoCs with dedicated repository and local shared preferences caching (Recommended)

Keep business logic and API requests in a dedicated `UserRepository` implementing an abstract interface, accessed by focused BLoCs (`ProfileBloc`, `VehicleBloc`, `SettingsBloc`). Cache profile and settings in `SharedPrefService` so screens render immediately on cold launch without blank loading states.

**Pros**:
- Consistent with the existing authentication module architecture in the mobile app.
- Clear separation between UI presentation, business logic, and network transport.
- Instant render from local cache creates a fast and responsive user experience.
- Focused BLoCs prevent state bloat and reduce unnecessary widget rebuilds.

**Cons**:
- Requires creating separate event and state classes for each sub concern.

### Option 2: Monolithic single UserBloc managing all profile, vehicle, and settings state

Combine profile details, vehicle lists, payment methods, and settings toggles into one large BLoC and single state class.

**Pros**:
- Only one BLoC instance to register and inject at the root widget tree.

**Cons**:
- Any small setting toggle (such as switching notifications) triggers a state emit that can cause the vehicle list and profile widgets to rebuild.
- Difficult to test and maintain as more garage and profile features expand over time.

### Option 3: Direct API calls inside widget State classes without BLoC

Call `DataProvider` directly from widget `initState` methods using `setState`.

**Pros**:
- Fastest to write initially for a quick prototype.

**Cons**:
- Violates separation of concerns and breaks the pattern established in the authentication slice.
- Difficult to unit test and impossible to share vehicle or profile state across different tabs.
- Poor error handling and state recovery across app lifecycles.

## Rationale

We selected Option 1 because it directly follows the architecture established in the authentication module while keeping concerns cleanly divided. The user profile, vehicle garage, and settings screens have distinct lifecycles: profile data is loaded once and rarely modified, vehicle additions happen inside a modal dialog, and settings toggles occur frequently and require immediate visual feedback. Splitting them into focused BLoCs prevents unnecessary widget rebuilds while maintaining a single, clean `UserRepository` for all HTTP communication. Caching profile and preference data in `SharedPrefService` ensures the app feels fast and works reliably even in low connectivity situations.
