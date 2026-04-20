# Inception REST API — Sample Usage

> Source: **Inner Range "Inception REST API Sample Usage"** (April 2021),
> extended against the official **Postman sample collection** shipped with the
> controller (`Inception REST API Samples`, **API Version 16**). Converted to
> Markdown from the original sources for developer reference in this
> repository. This is an external third-party document; Inner Range retains
> all rights to the original content.
>
> The prose examples were originally written for **protocol v8** (Inception
> firmware 4.0); the Postman collection targets **protocol v16**. Endpoints
> marked *"new in protocol version N"* require the corresponding firmware —
> always check the live controller's protocol version before relying on a
> newer-only endpoint (see
> [Getting Started → Retrieving the API Protocol version](getting-started.md#retrieving-the-api-protocol-version)).
>
> **Canonical live docs**: `http://[inception-address]/ApiDoc` on any Inception
> device, or publicly via SkyTunnel at
> `https://skytunnel.com.au/Inception/API_SAMPLE/ApiDoc`. The live docs also
> include the source Postman collection (`Inception_RestApi.postman_collection.json`
> in this directory is a local copy).
>
> Editorial notes: page numbering and the repeated footer from the PDF have
> been removed. A few JSON examples in the source PDF are missing commas or
> closing braces (clearly typesetting errors); those have been corrected so the
> snippets parse as valid JSON.

## Sections

Read in order for a complete tour, or jump to what you need:

1. **[Getting Started](getting-started.md)** — Introduction, protocol version
   check, authentication (password, hashed, 2FA, API token), logout, and
   SkyTunnel access.
2. **[Entities](entities.md)** — Controlling Areas, Doors, Inputs, Outputs,
   Lift Floors, Storage Units, and querying per-entity configuration /
   state.
3. **[Activities](activities.md)** — Virtually badging credentials or PINs at
   a reader, sending user-duress alerts, and tracking in-flight activities
   (state, updates, cancel).
4. **[User Management](user-management.md)** — Query, get, create, delete,
   update, patch Users; manage user photos; generate unused PINs; look up
   users by PIN; link SkyCommand.
5. **[Configuration](configuration.md)** — Listing permission groups,
   credential templates, terminal profiles, and other configuration
   catalogues.
6. **[Review Events](review-events.md)** — Query historical review events
   with category, date-range, message-type, involved-entity, and
   reference-event filters.
7. **[Long Polling & Monitoring](long-polling.md)** — Real-time updates for
   entity states, activity progress, recent user info, live review events,
   and data changes via `api/v1/monitor-updates`.
8. **[System](system.md)** — Unauthenticated protocol-version probe and the
   authenticated system-info (system name, serial number) endpoint.

## Conventions used throughout

- `[placeholder]` in request paths and bodies indicates a value you must
  substitute (e.g. `[areaID]`, `[userID]`).
- All authenticated requests must include the session ID in the `Cookie`
  header as `LoginSessId=[sessionID]`; sessions expire after 10 minutes of
  inactivity. See [Authentication](getting-started.md#authentication--logging-in).
  API tokens are an alternative to session cookies — see
  [API Token authentication](getting-started.md#api-token-authentication).
- Unless otherwise noted, request/response bodies are JSON with
  `Content-Type: application/json`.
- Entity-control endpoints follow a consistent shape:
  `GET /control/[type]` lists visible items, `GET /control/[type]/summary`
  returns items bundled with state, `GET /control/[type]/[id]/state` returns
  a single item's live state, and `POST /control/[type]/[id]/activity`
  submits a control request.
