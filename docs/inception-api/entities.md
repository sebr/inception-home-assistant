# Entities

[← Back to index](README.md)

Retrieving entity information (Areas, Outputs) and controlling them via
activity requests.

## Contents

- [Requesting Entity Information](#requesting-entity-information)
  - [Example: Getting Area Information](#example-getting-area-information)
- [Controlling Entities](#controlling-entities)
  - [Example: Arming an Area (Standard Mode)](#example-arming-an-area-standard-mode)
  - [Example: Controlling an Output (turn on)](#example-controlling-an-output-turn-on)

## Requesting Entity Information

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

## Controlling Entities

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

---

**Next:** [Activities →](activities.md)
