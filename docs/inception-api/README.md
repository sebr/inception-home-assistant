# Inception REST API — Sample Usage

> Source: **Inner Range "Inception REST API Sample Usage"** (April 2021).
> Converted to Markdown from the official Inner Range PDF for developer reference
> in this repository. This is an external third-party document; Inner Range
> retains all rights to the original content.
>
> The information in this document is relevant to the Inception REST API
> **protocol v8** (released in Inception firmware 4.0). Features flagged *"new
> in protocol version N"* require the corresponding firmware.
>
> **Canonical live docs**: `http://[inception-address]/ApiDoc` on any Inception
> device, or publicly via SkyTunnel at
> `https://skytunnel.com.au/Inception/API_SAMPLE/ApiDoc`. The live docs also
> include a downloadable Postman collection of example requests.
>
> Editorial notes: page numbering and the repeated footer from the PDF have
> been removed. A few JSON examples in the source PDF are missing commas or
> closing braces (clearly typesetting errors); those have been corrected so the
> snippets parse as valid JSON.

## Sections

Read in order for a complete tour, or jump to what you need:

1. **[Getting Started](getting-started.md)** — Introduction, protocol version
   check, authentication, and SkyTunnel access.
2. **[Entities](entities.md)** — Requesting entity info (Areas) and controlling
   entities (arming Areas, toggling Outputs).
3. **[Activities](activities.md)** — Virtually badging a credential or
   presenting a PIN at a door reader.
4. **[User Management](user-management.md)** — Query, get, create, delete,
   update, patch Users; manage user photos; generate unused PINs.
5. **[Review Events](review-events.md)** — Query historical review events with
   category, date-range, message-type, and involved-entity filters.
6. **[Long Polling & Monitoring](long-polling.md)** — Real-time updates for
   entity states, activity progress, and review events via
   `api/v1/monitor-updates`.

## Conventions used throughout

- `[placeholder]` in request paths and bodies indicates a value you must
  substitute (e.g. `[areaID]`, `[userID]`).
- All authenticated requests must include the session ID in the `Cookie`
  header as `LoginSessId=[sessionID]`; sessions expire after 10 minutes of
  inactivity. See [Authentication](getting-started.md#authentication--logging-in).
- Unless otherwise noted, request/response bodies are JSON with
  `Content-Type: application/json`.
