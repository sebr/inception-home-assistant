# System

[← Back to index](README.md)

Non-entity endpoints that describe the controller itself — its API protocol
version and its system metadata.

## Contents

- [Protocol version](#protocol-version)
- [System info](#system-info)

## Protocol version

The unauthenticated `api/protocol-version` endpoint reports the REST API
version implemented by the firmware currently loaded on the controller. See
[Getting Started →
Retrieving the API Protocol version](getting-started.md#retrieving-the-api-protocol-version)
for the full walk-through; the short form is:

```
GET /api/protocol-version   →   { "ProtocolVersion": 16 }
```

A `404` indicates firmware too old to advertise a protocol version (before
the endpoint was introduced); treat it as "upgrade needed" and fall back to
the minimum-feature set.

> **NOTE**: This endpoint lives under `api/` — **not** `api/v1/` — because
> it is intended to be callable before you know which API version the
> controller supports.

## System info

`GET /api/v1/system-info` returns metadata that identifies **this specific
controller**. Authentication is required. The payload is a small `SystemInfo`
object; only the two fields below are documented in the Postman sample:

| Property       | Type   | Description                              |
| -------------- | ------ | ---------------------------------------- |
| `SerialNumber` | String | The Inception device's serial number.    |
| `SystemName`   | String | The configured name of this system.      |

Example:

```http
GET /api/v1/system-info HTTP/1.1
Cookie: LoginSessId=[sessionID]
```

```json
{
  "SerialNumber": "IN001234",
  "SystemName": "Acme HQ"
}
```

### Why this matters

- **Device identity**: use `SerialNumber` as a stable device identifier.
  Integrations that manage multiple controllers can key on it rather than
  on user-editable strings.
- **UI labelling**: `SystemName` mirrors the name configured in
  **Configuration → General → System** in the web UI; show it in clients so
  the user sees a consistent label for the same controller across tools.
- **SkyTunnel routing**: the `SerialNumber` is the same value that appears
  in the SkyTunnel URL path
  (`https://www.skytunnel.com.au/inception/[serial]/...` — see
  [SkyTunnel](getting-started.md#using-the-rest-api-over-skytunnel)).
