# Long Polling & Monitoring

[← Back to index](README.md)

Real-time updates for entity states, activity progress, and review events
via the `api/v1/monitor-updates` endpoint.

## Contents

- [Introduction to Long Polling](#introduction-to-long-polling)
- [Monitoring for Long Poll Updates](#monitoring-for-long-poll-updates)
  - [Example: Monitoring Area States](#example-monitoring-area-states)
  - [Example: Monitoring User States & Locations](#example-monitoring-user-states--locations)
  - [Example: Monitoring both Area states and Output states](#example-monitoring-both-area-states-and-output-states)
  - [Example: Monitoring the progress of an Area Arm activity](#example-monitoring-the-progress-of-an-area-arm-activity)
  - [Example: Monitoring real-time Review Events](#example-monitoring-real-time-review-events)
  - [Example: Monitoring real-time Review Events (only Security and Access events)](#example-monitoring-real-time-review-events-only-security-and-access-events)
  - [Example: Monitoring real-time Review Events for a specific Item](#example-monitoring-real-time-review-events-for-a-specific-item)
  - [Example: Monitoring specific Review Event types](#example-monitoring-specific-review-event-types)

## Introduction to Long Polling

Inception's REST API uses **HTTP long polling** to deliver real-time updates
for entity states, review events, activity progress, etc. without the need to
manually poll for updates. HTTP long polling involves opening a HTTP request
connection to a certain endpoint on the server as normal, but with the
expectation that the server will not necessarily respond immediately; rather,
it will hold the request open until the relevant response data becomes
available (e.g. new state changes or new events). In Inception's case,
**requests are held open for up to a minute**, at which point the server will
reply with an empty response if no new information became available in that
minute. From there, the client can re-send the request with the same JSON body
contents to continue waiting for updates. Using this technique removes the
need to potentially make a multitude of expensive manual polling requests for
state information from the server.

Inception's long poll requests are **repeatable** so that information is not
lost in between requests, for example: a request for all area state updates
since a given timestamp will always return with every area whose state has
changed since that timestamp.

Typical usage of the API will usually involve having at least 1 HTTP long
poll request open waiting for updates (entity states, review events), while
other synchronous requests (e.g. retrieving Area/User information, sending
control commands) are sent and processed on a different thread while the long
poll request is waiting to return.

**Multiple sub-requests can be bundled** into a single HTTP request body to
save having to leave multiple requests hanging open. For example, you could
have 3 separate sub-requests to monitor Area, Door, and Output states and
combine them into the body of a single HTTP long polling request to the
`api/v1/monitor-updates` endpoint on an Inception device, and the request
will return with updates as soon as they become available for any of the 3
sub-requests. For an example of this usage, see [Monitoring both Area states
and Output states](#example-monitoring-both-area-states-and-output-states)
below.

For details on the JSON data types used in Inception's Update Monitor / long
polling requests, see the Update Monitor page of the API documentation.

## Monitoring for Long Poll Updates

### Example: Monitoring Area States

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Send a `POST` request to `api/v1/monitor-updates` with a JSON request body
   of:

   ```json
   [
     {
       "ID": "Monitor_AreaStates",
       "RequestType": "MonitorEntityStates",
       "InputData": {
         "stateType": "AreaState",
         "timeSinceUpdate": "0"
       }
     }
   ]
   ```

3. Hold the request open for up to 60 seconds until a response is received
   from the server.
   1. If the response body is empty (no new updates to report), you can
      re-send the request unmodified to wait for new events (i.e. go back to
      step 2).
   2. If the response body contains data, continue to step 4.
4. Read the array of state updates in the response (in the
   `Result.stateData` field) and process the data as needed. The sample
   response will look similar to the JSON snippet below. The `PublicState`
   field contains the set of bit flags that represent the Area's current
   state, the `Info1` field contains information about the Area's next
   scheduled arm time (if applicable), and the `Info2` field contains the
   number of Users that are currently in the Area. See the API Docs for
   information on how to interpret the Area's state flags.

   ```json
   {
     "ID": "Monitor_AreaStates",
     "Result": {
       "updateTime": "16158053",
       "stateData": [
         {
           "ID": "09492660-72ed-4807-bc59-c1fef83981a5",
           "stateValue": 8,
           "PublicState": 2048,
           "Info1": null,
           "Info2": "0"
         }
       ]
     }
   }
   ```

5. To continue monitoring for newer area state updates, take the value from
   the `updateTime` field of the response (`"16158053"` in this example) and
   use it to replace the value of the `timeSinceUpdate` field of your
   previous request's JSON body, and send the new request. The request will
   be handled in the same way as the previous one, except it will only
   monitor for updates that are newer than this timestamp. Sending new long
   poll requests in this way will ensure that new updates are delivered
   contiguously in chronological order.

### Example: Monitoring User States & Locations

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Send a `POST` request to `api/v1/monitor-updates` with a JSON request body
   of:

   ```json
   [
     {
       "ID": "Monitor_UserStates",
       "RequestType": "MonitorEntityStates",
       "InputData": {
         "stateType": "UserState",
         "timeSinceUpdate": "0"
       }
     }
   ]
   ```

3. Hold the request open for up to 60 seconds until a response is received
   from the server.
   1. If the response body is empty (no new updates to report), you can
      re-send the request unmodified to wait for new events (i.e. go back to
      step 2).
   2. If the response body contains data, continue to step 4.
4. Read the array of state updates in the response (in the
   `Result.stateData` field) and process the data as needed. The sample
   response will look similar to the JSON snippet below. The `Info1` field
   contains the name of the User's current location if applicable. The User's
   `PublicState` flags can be interpreted with the API documentation page for
   `UserPublicStates`.

   ```json
   {
     "ID": "Monitor_UserStates",
     "Result": {
       "updateTime": "21884069",
       "stateData": [
         {
           "ID": "b4d4a1e5-a848-4535-86b9-687be491614a",
           "stateValue": -1,
           "PublicState": 0,
           "Info1": "Lobby",
           "Info2": ""
         },
         {
           "ID": "8410f634-07e7-4116-8ed1-ca73ea7c78f3",
           "stateValue": -1,
           "PublicState": 0,
           "Info1": "",
           "Info2": ""
         }
       ]
     }
   }
   ```

5. Take the timestamp value from the response's `updateTime` field and put
   it in the original request's `timeSinceUpdate` field, and repeat from
   step 2 to wait for new updates for as many times as desired.

### Example: Monitoring both Area states and Output states

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Send a `POST` request to `api/v1/monitor-updates` with a JSON request body
   containing 2 sub-requests like the following.

   > **NOTE**: The `ID` field of each JSON sub-request object must be unique
   > when monitoring multiple types of updates from a single HTTP request, in
   > order to determine which server responses correspond to which
   > sub-request.

   ```json
   [
     {
       "ID": "Monitor_AreaStates",
       "RequestType": "MonitorEntityStates",
       "InputData": {
         "stateType": "AreaState",
         "timeSinceUpdate": "0"
       }
     },
     {
       "ID": "Monitor_OutputStates",
       "RequestType": "MonitorEntityStates",
       "InputData": {
         "stateType": "OutputState",
         "timeSinceUpdate": "0"
       }
     }
   ]
   ```

3. Hold the request open for up to 60 seconds until a response is received
   from the server.
   1. If the response body is empty (no new updates to report), you can
      re-send the request unmodified to wait for new events (i.e. go back to
      step 2).
   2. If the response body contains data, continue to step 4.
4. Read the `ID` field of the response to determine which sub-request this
   update is relevant to (in this example, the response was for the
   `Monitor_AreaStates` request). **The response body will only ever contain
   a response to a single sub-request.** Read the array of state updates in
   the response (in the `Result.stateData` field) and process the data as
   needed.

   ```json
   {
     "ID": "Monitor_AreaStates",
     "Result": {
       "updateTime": "8128806",
       "stateData": [
         {
           "ID": "26556643-819b-4c41-8e6f-e804114c986b",
           "stateValue": 8,
           "PublicState": 2048,
           "Info1": null,
           "Info2": "0"
         },
         {
           "ID": "09492660-72ed-4807-bc59-c1fef83981a5",
           "stateValue": 4,
           "PublicState": 2064,
           "Info1": "Area will automatically Arm at …",
           "Info2": "0"
         }
       ]
     }
   }
   ```

5. After processing the response data, take the `updateTime` field value
   from the response and replace the `timeSinceUpdate` field value in the
   relevant sub-request (`Monitor_AreaStates` in this example), before
   resending the whole request again in a new HTTP long poll request.
   Updating the specific sub-request parameter fields in this way after each
   response allows each one to be processed independently, but combined in a
   single HTTP request to avoid the overhead of waiting simultaneously on
   multiple requests to return.

### Example: Monitoring the progress of an Area Arm activity

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Start an Area Arm activity (see [Arming an
   Area](entities.md#example-arming-an-area-standard-mode)) and retrieve the
   activity ID (will be referred to as `[activityID]`).
3. Send a `POST` request to `api/v1/monitor-updates` with a JSON request body
   of:

   ```json
   [
     {
       "ID": "Monitor_ArmActivity",
       "RequestType": "ActivityProgress",
       "InputData": {
         "activityId": "[activityID]",
         "receivedMsgs": ""
       }
     }
   ]
   ```

4. Hold the request open for up to 60 seconds until a response is received
   from the server.
   1. If the response body is empty (no new updates to report), you can
      re-send the request unmodified to wait for new events (i.e. go back to
      step 3).
   2. If the response body contains data, continue to step 5.
5. Process the activity update messages (in the `Result.Messages` field).
   The `Type` sub-field in each Message object is an `ActivityProgressState`
   enum, where a value of **2 or 3** (`Success` or `Failure` respectively)
   indicates that the activity has run to completion and will not need to be
   monitored for any future messages.

   ```json
   {
     "ID": "Monitor_ArmActivity",
     "Result": {
       "ActivityId": "[activityID]",
       "AllSentMsgIds": "311d7547-1571-464e-91a2-34489a7b71a9",
       "Messages": [
         {
           "Type": 1,
           "Message": "Area arming process started",
           "Current": 1,
           "Total": 5,
           "Data": null
         },
         {
           "Type": 1,
           "Message": "Arming Area(s)",
           "Current": 4,
           "Total": 5,
           "Data": null
         },
         {
           "Type": 2,
           "Message": "Areas armed",
           "Current": 1,
           "Total": 1,
           "Data": null
         }
       ]
     }
   }
   ```

6. If there are more messages to come for this activity (i.e. a "Finished"
   message has not been received), take the value of the `AllSentMsgIds`
   field in the response and place it in the `receivedMsgs` field of your
   original request. Repeat from step 3 again with the updated request body,
   until the activity is completed and has no more progress messages to send.

### Example: Monitoring real-time Review Events

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Before sending the long poll request, get the most recent review event ID
   to use as a reference point to only receive newer events, by sending a
   `GET` request to `api/v1/review?dir=desc&limit=1`. Record the event's `ID`
   and `WhenTicks` fields.

   ```json
   {
     "Offset": 0,
     "Count": 1,
     "Data": [
       {
         "ID": "604fc423-891c-4d66-abaa-9576ca58b3b8",
         "Description": "Alarm Event Failed…",
         "MessageCategory": 5801,
         "When": "2019-07-10T10:07:04.2642453+10:00",
         "WhenTicks": 636983140242642453,
         "Who": "",
         "WhoID": "00000000-0000-0000-0000-000000000000",
         "What": "Area Open/Close",
         "WhatID": "00000000-0000-0000-0000-000000000000",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       }
     ]
   }
   ```

3. Send a `POST` request to `api/v1/monitor-updates` with a JSON request body
   similar to the following, where `[eventId]` and `[eventTime]` represent
   the previously retrieved event's `ID` and `WhenTicks` values respectively:

   ```json
   [
     {
       "ID": "Monitor_ReviewEvents",
       "RequestType": "LiveReviewEvents",
       "InputData": {
         "referenceId": "[eventId]",
         "referenceTime": "[eventTime]"
       }
     }
   ]
   ```

4. Hold the request open for up to 60 seconds until a response is received
   from the server.
   1. If the response body is empty (no new updates to report), you can
      re-send the request unmodified to wait for new events.
   2. If the response body contains data, continue to step 5.
5. Process the array of review messages (in the `Result` field).

   ```json
   {
     "ID": "Monitor_ReviewEvents",
     "Result": [
       {
         "ID": "a3c50fcf-5797-4964-8b19-cb46e7a57a71",
         "Description": "Area Disarmed by User",
         "MessageCategory": 5201,
         "When": "2019-07-10T10:34:29.9797368+10:00",
         "WhenTicks": 636983156699797368,
         "Who": "Installer",
         "WhoID": "fbec7c22-500d-4f3b-b94e-4c19ff501f9f",
         "What": "Area 3",
         "WhatID": "7419bc70-8a7d-4f4b-8d18-fd1c7f734202",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       }
     ]
   }
   ```

6. If you want to poll for more review events, send the `POST` request again
   like in step 3, but update the `[eventId]` and `[eventTime]` parameters
   to match the `ID` and `WhenTicks` value of the most recently received
   event. Repeat this process for as long as you want to monitor for new
   events.

### Example: Monitoring real-time Review Events (only Security and Access events)

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Before sending the long poll request, get the most recent review event ID
   to use as a reference point to only receive newer events (see step 2 of
   [Monitoring real-time Review
   Events](#example-monitoring-real-time-review-events)).
3. Send a `POST` request to `api/v1/monitor-updates` with a JSON request body
   similar to the following, where `[eventId]` and `[eventTime]` represent
   the previously retrieved event's `ID` and `WhenTicks` values respectively.
   The allowed category types for the `categoryFilter` field can be found on
   the Update Monitor API docs page.

   ```json
   [
     {
       "ID": "Monitor_ReviewEvents",
       "RequestType": "LiveReviewEvents",
       "InputData": {
         "referenceId": "[eventId]",
         "referenceTime": "[eventTime]",
         "categoryFilter": "Security,Access"
       }
     }
   ]
   ```

4. Hold the request open for up to 60 seconds until a response is received
   from the server.
   1. If the response body is empty (no new updates to report), you can
      re-send the request unmodified to wait for new events.
   2. If the response body contains data, continue to step 5.
5. Process the array of review messages (in the `Result` field).

   ```json
   {
     "ID": "Monitor_ReviewEvents",
     "Result": [
     ]
   }
   ```

6. Re-send the `POST` request with the newest event `ID` and `WhenTicks`
   value in the `referenceId` and `referenceTime` fields if you want to
   retrieve later events.

### Example: Monitoring real-time Review Events for a specific Item

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Before sending the long poll request, get the most recent review event ID
   to use as a reference point to only receive newer events (see step 2 of
   [Monitoring real-time Review
   Events](#example-monitoring-real-time-review-events)).
3. Send a `POST` request to `api/v1/monitor-updates` with a JSON request body
   similar to the following, where `[eventId]` and `[eventTime]` represent
   the previously retrieved event's `ID` and `WhenTicks`, and `[itemId]`
   represents the ID of the Area/Door/User/etc. you wish to filter the events
   for. You can also specify multiple item IDs by passing them in the form
   of a comma-separated string.

   ```json
   [
     {
       "ID": "Monitor_ReviewEvents",
       "RequestType": "LiveReviewEvents",
       "InputData": {
         "referenceId": "[eventId]",
         "referenceTime": "[eventTime]",
         "involvedEntityIdFilter": "[itemId]"
       }
     }
   ]
   ```

4. Hold the request open for up to 60 seconds until a response is received
   from the server.
   1. If the response body is empty (no new updates to report), you can
      re-send the request unmodified to wait for new events.
   2. If the response body contains data, continue to step 5.
5. Process the array of review messages (in the `Result` field).

   ```json
   {
     "ID": "Monitor_ReviewEvents",
     "Result": [
     ]
   }
   ```

6. Re-send the `POST` request with the newest event `ID` and `WhenTicks`
   value in the `referenceId` and `referenceTime` fields if you want to
   retrieve more events.

### Example: Monitoring specific Review Event types

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Before sending the long poll request, get the most recent review event ID
   to use as a reference point to only receive newer events (see step 2 of
   [Monitoring real-time Review
   Events](#example-monitoring-real-time-review-events)).
3. Send a `POST` request to `api/v1/monitor-updates` with a JSON request body
   similar to the following, where `[eventId]` and `[eventTime]` represent
   the previously retrieved event's `ID` and `WhenTicks`, and the
   `messageTypeIdFilter` field contains a comma-separated list of event type
   IDs that you want to filter events for. This example is using **2006**
   (`Door Access Granted for User`) and **2007** (`Door User Access Denied –
   No Permission`); the full list of event type IDs can be found in the API
   Docs. Optionally, the `involvedEntityIdFilter` parameter can also be
   included to further filter the events to ones involving specific Items.

   ```json
   [
     {
       "ID": "Monitor_ReviewEvents",
       "RequestType": "LiveReviewEvents",
       "InputData": {
         "referenceId": "[eventId]",
         "referenceTime": "[eventTime]",
         "messageTypeIdFilter": "2006,2007"
       }
     }
   ]
   ```

4. Hold the request open for up to 60 seconds until a response is received
   from the server.
   1. If the response body is empty (no new updates to report), you can
      re-send the request unmodified to wait for new events.
   2. If the response body contains data, continue to step 5.
5. Process the array of review messages (in the `Result` field).

   ```json
   {
     "ID": "Monitor_ReviewEvents",
     "Result": [
     ]
   }
   ```

6. Re-send the `POST` request with the newest event `ID` and `WhenTicks`
   value in the `referenceId` and `referenceTime` fields if you want to
   retrieve more events.
