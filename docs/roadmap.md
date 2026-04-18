# Roadmap & Ideas

Forward-looking work items for the Inception Home Assistant integration,
organised by tier. Each item lists the files most likely affected, the
shape of the change, and any dependencies. Pick from any tier — they are
independent unless a dependency is called out.

The tiers below were drafted after a pass over the official
[Inner Range REST API docs](inception-api/README.md) (protocol v8). Where
relevant, links point at the topic file that motivates the feature.

## Status legend

- [x] merged
- [ ] open
- (idea) not started

## Tier 1 — resilience & observability (done)

Closed real gaps against the documented API surface. Kept here for
reference.

- [x] **Bundle review events into the main `/monitor-updates` long-poll**
      — #164. Single HTTP connection, single retry ladder; see
      [`long-polling.md`](inception-api/long-polling.md).
- [x] **Protocol-version probe at setup** — #162. Calls the
      unauthenticated [`/api/protocol-version`](inception-api/getting-started.md#retrieving-the-api-protocol-version)
      once during `_async_setup`; caches `protocol_version` on the
      client so future features can be version-gated.
- [x] **Auth failures → HA re-auth flow** — #163. `ConfigEntryAuthFailed`
      from `_async_update_data` + `config_entry.async_start_reauth` from
      the background long-poll, with a `reauth_confirm` step in the
      config flow.
- [x] **HA Diagnostics** — #161. Redacted coordinator dump for bug
      reports.

## Tier 2 — new user-visible features

### 2.1 Review events via the HA `event` entity platform (idea)

Today review events are fired on the bus (`inception_review_event`) and
a single "last event" sensor holds the most recent one. The HA `event`
platform is the idiomatic home for this: one `event` entity per Door
(access events) and per Area (arm/alarm events), with typed event types
driven by `MessageCategory` / `messageTypeIdFilter`.

- **Why**: typed triggers in the automation UI, persistent "last fired"
  timestamps per entity, cleaner UX than "sensor stores the last event".
- **Shape**: new `custom_components/inception/event.py`, add
  `Platform.EVENT` to the `PLATFORMS` list in `__init__.py`, fan out
  `review_event_callback` in the coordinator to the right per-entity
  entities. `pyinception/message_categories.py` already contains the
  category → name mapping.
- **Effort**: M. Contained to one new file plus coordinator wiring.
- **Follow-up**: once this lands, the "Last Review Event" sensor
  (`sensor.py`) becomes redundant and can be removed with a deprecation
  window.

### 2.2 ActivityProgress monitoring for arm / unlock (idea)

Arm and unlock commands currently `POST` an activity and return
immediately. Alarm / lock entities optimistically flip state, and a
failed arm (unsealed zone) or denied unlock surfaces nowhere.
[`long-polling.md`](inception-api/long-polling.md#example-monitoring-the-progress-of-an-area-arm-activity)
shows the `ActivityProgress` sub-request: follow an `ActivityID` through
`ActivityProgressState` values (2 = Success, 3 = Failure) and react
accordingly.

- **Why**: biggest correctness win for the existing controls. Users
  currently have no signal when their arm fails.
- **Shape**: add a third sub-request type to the bundled long-poll in
  `pyinception/api.py`. On arm/unlock service calls, register the
  returned `ActivityID`; when a `Failure` progress message arrives,
  raise a `HomeAssistantError` out of the originating service call (and
  roll back any optimistic state). On `Success`, commit the optimistic
  state.
- **Effort**: M-L. Threads through `api.py`, `alarm_control_panel.py`,
  `lock.py`.
- **Dependency**: none — `/monitor-updates` already bundles arbitrary
  sub-requests after Tier 1 #1.

### 2.3 UserState → `device_tracker` (idea)

`MonitorEntityStates` with `stateType: "UserState"` gives `Info1` =
user's current location name (e.g. "Lobby"). One `device_tracker` per
User unlocks presence automations ("when Alice arrives, disarm Area A").
While here, `AreaState.Info2` is occupancy count — expose as an
attribute on the alarm panel entity.

- **Why**: genuine presence automations from the access-control system.
- **Shape**: new `device_tracker.py`, new `User` schema under
  `pyinception/schemas/`, extend `monitor_entity_states` to bundle a
  fifth `UserState` sub-request (gated on an opt-in option because it
  exposes personnel data to HA), occupancy attribute on
  `alarm_control_panel.py`.
- **Effort**: L. Schema + platform + option flow.
- **Note**: redact user location in diagnostics (already done for
  `Info1` / `Info2` in `diagnostics.py`).

## Tier 3 — opportunistic additions

### 3.1 Virtual badge / virtual PIN services (idea)

[`activities.md`](inception-api/activities.md) — `POST /api/v1/activity`
with `BadgeCredentialAtReader` or `SendPINDataToReader` lets HA "press
the reader" on behalf of a user. Useful for "unlock door as Alice when
her phone arrives".

- **Shape**: two HA services (`inception.badge_credential`,
  `inception.send_pin`) + reader discovery via
  `GET /control/door/[id]/attached-readers`.
- **Dependency**: User schema from 2.3.

### 3.2 Historical review-event query service (idea)

[`review-events.md`](inception-api/review-events.md) — `GET /api/v1/review`
with category / date-range / entity filters. Expose as a service with
`SupportsResponse.ONLY` so scripts and blueprints can query history.

- **Effort**: S. Uses existing `aiohttp_session`.

### 3.3 `generate-unused-pin` service (idea)

Protocol v11+ only. Handy adjunct to any user-management story; gate
behind the protocol-version cache from Tier 1 #2.

## Infra

### I.1 Add `mypy` or `pyright` to CI (idea)

`.ruff.toml` runs with `select = ["ALL"]` but there's no static type
check. The codebase uses type hints throughout and Pydantic schemas —
a strict type check would catch real issues without changing product
code.

- **Files**: new `.github/workflows/typecheck.yml`, `pyproject.toml`
  (tool config).

### I.2 Pytest coverage gate (idea)

`tests/unit/` is ~3.7k lines across all platforms, but coverage isn't
measured. Add `pytest-cov` with a soft threshold so new untested code
shows up in PRs.

- **Files**: `scripts/tests`, CI workflow.

## Verification approach

For any of the above:

- Unit tests using the patterns in `tests/fixtures/responses.py` — mock
  the new endpoints and assert coordinator → entity state wiring.
- Live smoke test via `scripts/develop` against a real controller, or
  the SkyTunnel sample at
  `https://skytunnel.com.au/Inception/API_SAMPLE/ApiDoc`.
- `scripts/lint` + `scripts/tests` + hassfest/HACS CI gates already
  enforce the bar.
