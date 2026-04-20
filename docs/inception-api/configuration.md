# Configuration

[← Back to index](README.md)

Read-only catalogue endpoints under `api/v1/config/` that expose configured
entities and their associated templates/profiles. These complement the live
control endpoints in [Entities](entities.md) — use `/config/...` when you
need the **configured** definition of an item (e.g. its configured name,
linked templates, permissions) rather than its live state.

User CRUD lives on its own page; see
[User Management](user-management.md).

## Contents

- [Listing configured entities](#listing-configured-entities)
- [Listing templates and profiles](#listing-templates-and-profiles)
- [Using configuration data](#using-configuration-data)

## Listing configured entities

Each of the following returns a JSON array of `{ID, Name, ...}` objects for
the configured entities of that type. The results include every entity the
API user has configuration access to, regardless of whether the user has
live-control permission on them.

| Endpoint                          | Returns                                               |
| --------------------------------- | ----------------------------------------------------- |
| `GET /config/permission-group`    | Permission Groups (used as values for `Permissions[].Item` on Users). |
| `GET /config/door`                | Configured Doors.                                     |
| `GET /config/area`                | Configured Areas.                                     |
| `GET /config/output`              | Configured Outputs.                                   |
| `GET /config/lift-floor`          | Configured Lift Floors.                               |
| `GET /config/storage-unit`        | Configured Storage Units.                             |

## Listing templates and profiles

These endpoints expose the catalogues you reference from User records:

| Endpoint                              | Used for                                                           |
| ------------------------------------- | ------------------------------------------------------------------ |
| `GET /config/credential-template`    | Card / badge templates — the `CardTemplate` ID on a user's `PhysicalCredentials[]` entry. Also used for [virtual badging](activities.md#example-virtually-badging-a-cardcredential-at-a-door-reader). |
| `GET /config/fob-template`            | Remote-fob templates — the `FobTemplate` ID on a user's `RemoteFobs[]` entry. |
| `GET /config/lcdterminal-profile`    | LCD Terminal profiles — the `TerminalProfile` ID on a User record. |
| `GET /config/webpermission-profile`  | Web-permission profiles — the `WebPagePermissions` ID on a User record. |

## Using configuration data

Typical patterns:

- **Bootstrap**: on first run, pull
  `GET /config/permission-group` + `GET /config/credential-template` +
  `GET /config/lcdterminal-profile` + `GET /config/webpermission-profile`
  to populate option pickers before creating or patching users.
- **Sync**: combine with
  [`DataChange` long polling](long-polling.md#data-changes) and
  `GET /config/user?modifiedSince=[lastSyncTime]` for incremental user
  replication.
- **Validation**: look up a user's assigned template/profile IDs against
  these lists to render friendly names in a UI.

---

**Next:** [Review Events →](review-events.md)
