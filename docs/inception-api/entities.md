# Entities

[← Back to index](README.md)

Retrieving entity information and controlling Inception's primary entity types
— Areas, Doors, Inputs, Outputs, Lift Floors, Storage Units, and (read-only)
Users — via activity requests.

## Contents

- [Endpoint conventions](#endpoint-conventions)
- [Areas](#areas)
  - [Example: Getting Area Information](#example-getting-area-information)
  - [Example: Arming an Area (Standard Mode)](#example-arming-an-area-standard-mode)
  - [Other Area activities](#other-area-activities)
- [Doors](#doors)
  - [Example: Listing Doors and their attached readers](#example-listing-doors-and-their-attached-readers)
  - [Example: Unlocking a Door (timed)](#example-unlocking-a-door-timed)
  - [Other Door activities](#other-door-activities)
- [Inputs](#inputs)
  - [Example: Isolating and De-Isolating an Input](#example-isolating-and-de-isolating-an-input)
  - [Custom Inputs](#custom-inputs)
- [Outputs](#outputs)
  - [Example: Controlling an Output (turn on)](#example-controlling-an-output-turn-on)
  - [Other Output activities](#other-output-activities)
- [Lift Floors](#lift-floors)
- [Storage Units](#storage-units)
- [Users (read-only control endpoints)](#users-read-only-control-endpoints)

## Endpoint conventions

Every entity type exposes the same four shapes of endpoint under
`api/v1/control/[type]`:

| Purpose                    | Method | Path                                |
| -------------------------- | ------ | ----------------------------------- |
| List visible items         | `GET`  | `/control/[type]`                   |
| Bundled list + live state  | `GET`  | `/control/[type]/summary`           |
| Get single item            | `GET`  | `/control/[type]/[id]`              |
| Get single item's state    | `GET`  | `/control/[type]/[id]/state`        |
| Submit a control request   | `POST` | `/control/[type]/[id]/activity`     |
| Submit a system-wide request | `POST` | `/activity`                       |

The value of `[type]` is one of: `area`, `door`, `input`, `output`,
`lift-floor`, `storage-unit`, or `user` (read-only control semantics).
For entity-type-specific extras (e.g. an Area's associated inputs and
arm-info, or a Door's attached readers), see the per-section examples
below.

Control activity responses all follow the same envelope:

```json
{
  "Response": { "Result": "Success", "Message": "OK" },
  "ActivityID": "d9b90072-745b-49eb-be01-10ae9a8c1792"
}
```

The returned `ActivityID` can be fed into the
[`activity` endpoints](activities.md) or the
[Activity Progress long-poll](long-polling.md#example-monitoring-the-progress-of-an-area-arm-activity)
to track execution.

## Areas

### Example: Getting Area Information

1. Authenticate as an API User (see
   [Authentication](getting-started.md#authentication--logging-in)), and save
   the session ID from the `Cookie` header and use it for the following
   requests.
2. Send a `GET` request to `api/v1/control/area` (with the authorised session
   ID in the `Cookie` header).
3. The server will respond with a JSON object array containing entries for
   each Area in the Inception system that the API User has permission to
   interact with. The entities' `ID` field value can be used in API requests
   to query for more information or to control the Area whose ID it is.

   ```json
   [
     {
       "ReportingID": 1,
       "ID": "09492660-72ed-4807-bc59-c1fef83981a5",
       "Name": "Default Area"
     },
     {
       "ReportingID": 2,
       "ID": "26556643-819b-4c41-8e6f-e804114c986b",
       "Name": "Area B"
     }
   ]
   ```

4. Alternatively, you can also send a `GET` request to
   `api/v1/control/area/summary` if you want a combined response containing
   supplementary information relating to Areas in the system, including the
   Area's associated inputs, its entry/exit delay times, and its current
   state.

   ```json
   {
     "Areas": {
       "481d30ac-9108-45e9-b8df-80fe98a2e349": {
         "EntityInfo": {
           "ReportingID": 1,
           "ID": "481d30ac-9108-45e9-b8df-80fe98a2e349",
           "Name": "Default Area"
         },
         "AssociatedInputs": [
           {
             "Input": "07590f0f-e958-4c25-917f-62cf5e46214c",
             "InputName": "CustomInput 1",
             "ProcessGroup": "71696099-c2fb-4522-b033-9213c5a8858e"
           }
         ],
         "ArmInfo": {
           "EntryDelaySecs": 45,
           "ExitDelaySecs": 60,
           "DeferArmDelaySecs": 3600,
           "AreaWarnTimeSecs": 60,
           "MultiModeArmEnabled": false
         },
         "CurrentState": 2048
       }
     }
   }
   ```

5. Two narrower read-only endpoints are also exposed if you only need a
   subset of the summary data:

   - `GET /control/area/[areaID]/inputs` → just the `AssociatedInputs`
     array.
   - `GET /control/area/[areaID]/arm-info` → just the `ArmInfo` object
     (entry / exit / warn delays and multi-mode flag).

### Example: Arming an Area (Standard Mode)

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Find the ID of the Area that you want to arm (see the previous [Getting
   Area Information](#example-getting-area-information) example); the
   placeholder `[areaID]` will represent this area's ID in the following
   steps.
3. Send a `POST` request to `api/v1/control/area/[areaID]/activity` with a
   JSON request body of:

   ```json
   {
     "Type": "ControlArea",
     "AreaControlType": "Arm"
   }
   ```

4. If the Arm activity was successfully created, the server will return a
   `"Success"` JSON response with the new Activity's ID present in the body.
   The returned `ActivityID` can be used to monitor the progress of the
   activity (see [Monitoring the progress of an Area Arm
   activity](long-polling.md#example-monitoring-the-progress-of-an-area-arm-activity)).
   If the request failed due to insufficient permission or another reason,
   the response result will be `"Failure"` and no `ActivityID` will be
   returned.

   ```json
   {
     "Response": {
       "Result": "Success",
       "Message": "OK"
     },
     "ActivityID": "b1ba25f2-118a-4170-b4d0-57432b6196fc"
   }
   ```

### Other Area activities

Each variant uses the same URL (`POST /control/area/[areaID]/activity`) and
differs only in the body:

| Action                          | Body                                                                                                         |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Disarm                          | `{ "Type": "ControlArea", "AreaControlType": "Disarm" }`                                                     |
| Arm (Perimeter / Stay)          | `{ "Type": "ControlArea", "AreaControlType": "ArmStay" }`                                                    |
| Arm (Night / Sleep)             | `{ "Type": "ControlArea", "AreaControlType": "ArmSleep" }`                                                   |
| Arm with seal check             | `{ "Type": "ControlArea", "AreaControlType": "Arm", "SealCheck": true }`                                     |
| Arm with exit delay             | `{ "Type": "ControlArea", "AreaControlType": "Arm", "ExitDelay": true }`                                     |
| Arm with seal check + exit delay | `{ "Type": "ControlArea", "AreaControlType": "Arm", "SealCheck": true, "ExitDelay": true }`                 |
| Arm **all** areas               | `POST /activity` with `{ "Type": "ControlArea", "AreaControlType": "Arm", "ControlAll": true }`              |

## Doors

### Example: Listing Doors and their attached readers

1. `GET /control/door` returns the list of visible Doors (same shape as
   [Areas](#example-getting-area-information)). `/summary` bundles live
   state in the same way.
2. For each door, `GET /control/door/[doorID]/attached-readers` returns the
   card/PIN readers associated with that door — useful when you plan to
   virtually badge or send a PIN (see [Activities](activities.md)).

### Example: Unlocking a Door (timed)

Send a `POST` to `api/v1/control/door/[doorID]/activity` with:

```json
{
  "Type": "ControlDoor",
  "DoorControlType": "TimedUnlock",
  "TimeSecs": 5
}
```

### Other Door activities

All use `POST /control/door/[doorID]/activity` with `"Type": "ControlDoor"`:

| Action              | `DoorControlType` | Extra fields             |
| ------------------- | ----------------- | ------------------------ |
| Momentary open      | `Open`            | —                        |
| Lock                | `Lock`            | —                        |
| Unlock (permanent)  | `Unlock`          | —                        |
| Timed unlock        | `TimedUnlock`     | `TimeSecs: <int>`        |
| Lockout             | `Lockout`         | —                        |
| Clear override      | `Reinstate`       | —                        |
| Unlock **all** doors | `Unlock`          | `ControlAll: true` (POST to `/activity`) |

## Inputs

### Example: Isolating and De-Isolating an Input

1. `GET /control/input` / `GET /control/input/summary` list visible Inputs
   and their live state.
2. To isolate (bypass) an input — e.g. temporarily suppress a noisy sensor
   while the alarm is armed — `POST /control/input/[inputID]/activity`:

   ```json
   {
     "Type": "ControlInput",
     "InputControlType": "Isolate"
   }
   ```

3. To remove the isolation, submit the same request with
   `"InputControlType": "DeIsolate"`.

### Custom Inputs

Custom Inputs (virtual inputs authored in the Inception config) accept a
different `Type`: `ControlCustomInput`. Use the same
`POST /control/input/[customInputID]/activity` endpoint, with one of three
control verbs:

| Action      | Body                                                                            |
| ----------- | ------------------------------------------------------------------------------- |
| Activate    | `{ "Type": "ControlCustomInput", "CustomInputControlType": "Activate" }`        |
| Deactivate  | `{ "Type": "ControlCustomInput", "CustomInputControlType": "Deactivate" }`      |
| Pulse       | `{ "Type": "ControlCustomInput", "CustomInputControlType": "Pulse" }`           |

`Pulse` activates the input for its configured pulse duration and then
automatically deactivates it.

## Outputs

### Example: Controlling an Output (turn on)

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Find the ID of the Output that you want to turn on (this can be found by
   using the `GET api/v1/control/output` endpoint); the placeholder
   `[outputID]` will represent this output's ID in the following steps.
3. Send a `POST` request to `api/v1/control/output/[outputID]/activity` with
   a JSON request body of:

   ```json
   {
     "Type": "ControlOutput",
     "OutputControlType": "On"
   }
   ```

4. If the activity was successfully submitted, a `"Success"` JSON response
   will be returned by the server, and the `ActivityID` can be used to monitor
   the activity's progress. If the request failed, the response result will
   be `"Failure"` and no `ActivityID` will be returned.

   ```json
   {
     "Response": {
       "Result": "Success",
       "Message": "OK"
     },
     "ActivityID": "d9b90072-745b-49eb-be01-10ae9a8c1792"
   }
   ```

### Other Output activities

| Action                       | Body                                                                                  |
| ---------------------------- | ------------------------------------------------------------------------------------- |
| Turn on (permanent)          | `{ "Type": "ControlOutput", "OutputControlType": "On" }`                              |
| Turn on for **N** seconds    | `{ "Type": "ControlOutput", "OutputControlType": "On", "TimeSecs": 5 }`               |
| Turn off                     | `{ "Type": "ControlOutput", "OutputControlType": "Off" }`                             |
| Toggle                       | `{ "Type": "ControlOutput", "OutputControlType": "Toggle" }`                          |

## Lift Floors

Lift Floors are controlled with `"Type": "ControlFloor"`. List them with
`GET /control/lift-floor` (or `/summary`).

| Action                              | URL                                            | Body                                                                     |
| ----------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------ |
| Timed free access (N seconds)       | `POST /control/lift-floor/[floorID]/activity`  | `{ "Type": "ControlFloor", "FloorControlType": "TimedFreeAccess", "TimeSecs": 5 }` |
| Secure **all** lift floors          | `POST /activity`                               | `{ "Type": "ControlFloor", "FloorControlType": "Secure", "ControlAll": true }`     |

## Storage Units

Storage Units represent lockers / cabinets that can be unlocked, secured, or
marked vacant. Note the listing endpoint has a trailing slash
(`/control/storage-unit/`) — the controller is tolerant of both with and
without.

| Action              | Body                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------- |
| Unlock              | `{ "Type": "ControlStorageUnit", "StorageUnitControlType": "Unlock" }`                |
| Secure              | `{ "Type": "ControlStorageUnit", "StorageUnitControlType": "Secure" }`                |
| Mark vacant         | `{ "Type": "ControlStorageUnit", "StorageUnitControlType": "Vacant" }`                |
| Clear vacancy       | `{ "Type": "ControlStorageUnit", "StorageUnitControlType": "ClearVacancy" }`          |

All four use `POST /control/storage-unit/[storageUnitID]/activity`.

## Users (read-only control endpoints)

Users do not support `POST .../activity` control verbs on `/control/user`;
instead the control endpoints just expose read-only views intended for
live-state monitoring:

- `GET /control/user` — list visible Users.
- `GET /control/user/summary` — list bundled with live state (current
  location, public-state flags).
- `GET /control/user/[userID]` — single user's control view.
- `GET /control/user/[userID]/state` — single user's live state only.

Full CRUD + photo management lives under `/config/user/...`; see
[User Management](user-management.md).

---

**Next:** [Activities →](activities.md)
