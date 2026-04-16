# Review Event Queries

[← Back to index](README.md)

Query historical review events via `api/v1/review` with category, date range,
message type, and involved entity filters. For real-time event monitoring see
[Long Polling & Monitoring](long-polling.md).

## Contents

- [Example: Retrieve the oldest 50 Review Events](#example-retrieve-the-oldest-50-review-events)
- [Example: Retrieve Access and Security-related Events created between two Dates](#example-retrieve-access-and-security-related-events-created-between-two-dates)
- [Example: Retrieve User Area Arm/Disarm Events created between two Dates](#example-retrieve-user-area-armdisarm-events-created-between-two-dates)
- [Example: Retrieve all Events involving a certain User](#example-retrieve-all-events-involving-a-certain-user)
- [Example: Retrieve First 50 Events older than a Reference Event](#example-retrieve-first-50-events-older-than-a-reference-event)

## Example: Retrieve the oldest 50 Review Events

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `GET` request to `api/v1/review?limit=50`. The `limit` query
   parameter sets the maximum number of events the server will return, and
   the `offset` parameter can be used to skip a number of events, e.g. for
   paginated results. If no value is given for the `limit` parameter, the
   default limit is set to `100`. The `dir` parameter can also be used to
   choose where to start (`dir=asc` for ascending/oldest events first,
   `dir=desc` for descending/newest events first); results are returned in
   ascending order by default.
3. The server will respond with the oldest 50 Review Events (example results
   shortened):

   ```json
   {
     "Offset": 0,
     "Count": 50,
     "Data": [
       {
         "ID": "bd678364-8221-4410-bf61-fec872c90499",
         "Description": "System Started",
         "MessageCategory": 1,
         "When": "2019-05-30T15:08:56.7991171+10:00",
         "WhenTicks": 636947897367991171,
         "Who": "",
         "WhoID": "00000000-0000-0000-0000-000000000000",
         "What": "No Reset Reason (Windows)",
         "WhatID": "00000000-0000-0000-0000-000000000000",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       },
       {
         "ID": "ca96e12f-a20b-444b-aab9-ade452008c60",
         "Description": "System Application Version",
         "MessageCategory": 2,
         "When": "2019-05-30T15:08:56.8061178+10:00",
         "WhenTicks": 636947897368061178,
         "Who": "",
         "WhoID": "00000000-0000-0000-0000-000000000000",
         "What": "1.0.0.0",
         "WhatID": "00000000-0000-0000-0000-000000000000",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       }
     ]
   }
   ```

4. The next contiguous block of Review Events can be retrieved by making the
   same request except increasing the number of the `offset` query parameter
   by the previous amount of the `limit` parameter, e.g.
   `api/v1/review?offset=50&limit=50` to retrieve the second-oldest block of
   50 events.

## Example: Retrieve Access and Security-related Events created between two Dates

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `GET` request similar to
   `api/v1/review?categoryFilter=Access,Security&start=2019-04-21T09:00:00&end=2019-04-25T17:00:00`
   for events between 21 April 9:00AM and 25 April 5:00PM, for example.
   1. The `categoryFilter` query parameter determines which categories of
      events are returned, using a list of comma-separated category names.
      The list of possible categories can be found in the live API docs.
   2. The `start` and `end` parameters are ISO 8601 formatted date/time
      values specifying the query range. These parameters can be used when
      the search direction is descending, except the `start` must be more
      recent than the `end` as results are returned in reverse.
3. The server will respond with the first 100 (the default query limit)
   Access and Security-related events from the given time period. If there
   are more than 100 events in the period, you can send the request again,
   but with an increased `offset` parameter value to fetch the next block of
   results.

   ```json
   {
     "Offset": 0,
     "Count": 100,
     "Data": [
       {
         "ID": "4e7e499c-d41d-48e7-b0aa-7021f0e8644c",
         "Description": "Web Login was Successful by User",
         "MessageCategory": 141,
         "When": "2019-05-30T15:31:57.4650017+10:00",
         "WhenTicks": 636947911174650017,
         "Who": "Installer",
         "WhoID": "fbec7c22-500d-4f3b-b94e-4c19ff501f9f",
         "What": "",
         "WhatID": "00000000-0000-0000-0000-000000000000",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       },
       {
         "ID": "7aeed56c-bb69-4b08-9576-e300e7b127c8",
         "Description": "Item Created",
         "MessageCategory": 1500,
         "When": "2019-05-30T15:33:51.0470017+10:00",
         "WhenTicks": 636947912310470017,
         "Who": "System",
         "WhoID": "00000000-0000-0000-0000-000000000000",
         "What": "User - Beau Munoz",
         "WhatID": "00000000-0000-0000-0000-000000000000",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       }
     ]
   }
   ```

## Example: Retrieve User Area Arm/Disarm Events created between two Dates

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `GET` request similar to
   `api/v1/review?messageTypeIdFilter=5000,5201&start=2019-04-21T09:00:00&end=2019-04-25T17:00:00`
   for events between 21 April 9:00AM and 25 April 5:00PM, for example.
   1. The `messageTypeIdFilter` query parameter determines which event type
      IDs are returned in the query, specified by a comma-separated list of
      integer values. A list of all message type IDs can be found in the live
      API docs.
3. The server will respond with a block of up to 100 events that match the
   filter and the time period. If there are more than 100 events in the
   period, you can send the request again, but with an increased `offset`
   parameter value to fetch the next block of results.

   ```json
   {
     "Offset": 0,
     "Count": 100,
     "Data": [
       {
         "ID": "16c1e41e-43de-4af0-9307-152a85122e10",
         "Description": "Area Armed by User",
         "MessageCategory": 5000,
         "When": "2019-06-03T13:31:15.7335622+10:00",
         "WhenTicks": 636951294757335622,
         "Who": "Installer",
         "WhoID": "fbec7c22-500d-4f3b-b94e-4c19ff501f9f",
         "What": "Default Area",
         "WhatID": "481d30ac-9108-45e9-b8df-80fe98a2e349",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       },
       {
         "ID": "b4b122c8-aab9-4436-a5ce-f2f49c150c24",
         "Description": "Area Disarmed by User",
         "MessageCategory": 5201,
         "When": "2019-06-03T13:31:16.794059+10:00",
         "WhenTicks": 636951294767940590,
         "Who": "Installer",
         "WhoID": "fbec7c22-500d-4f3b-b94e-4c19ff501f9f",
         "What": "Default Area",
         "WhatID": "481d30ac-9108-45e9-b8df-80fe98a2e349",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       }
     ]
   }
   ```

## Example: Retrieve all Events involving a certain User

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Find the ID of the User you are interested in retrieving events for, and
   send a `GET` request similar to
   `api/v1/review?involvedEntityIdFilter=[userID]&start=2019-04-21T09:00:00&end=2019-04-25T17:00:00`
   (where `userID` is the ID of the User in question) for events between 21
   April 9:00AM and 25 April 5:00PM, for example.
   1. The `involvedEntityIdFilter` query parameter allows you to filter event
      queries to include only those which reference particular entity IDs
      (Users, Areas, Doors, etc.) in their `WhoID`, `WhatID` or `WhereID`
      fields. Multiple IDs can be included as a comma-separated list if
      needed.
3. The server will respond with a block of up to 100 events that match the
   filter and the time period. If there are more than 100 events in the
   period, you can send the request again, but with an increased `offset`
   parameter value to fetch the next block of results. (Example response with
   `[userID]` of `fbec7c22-500d-4f3b-b94e-4c19ff501f9f`.)

   ```json
   {
     "Offset": 0,
     "Count": 100,
     "Data": [
       {
         "ID": "46a9048d-1f79-4cc8-b805-e7bdd78955a5",
         "Description": "Item Changed",
         "MessageCategory": 1501,
         "When": "2019-06-03T13:30:35.7834783+10:00",
         "WhenTicks": 636951294357834783,
         "Who": "Installer",
         "WhoID": "fbec7c22-500d-4f3b-b94e-4c19ff501f9f",
         "What": "User - Installer",
         "WhatID": "00000000-0000-0000-0000-000000000000",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       },
       {
         "ID": "16c1e41e-43de-4af0-9307-152a85122e10",
         "Description": "Area Armed by User",
         "MessageCategory": 5000,
         "When": "2019-06-03T13:31:15.7335622+10:00",
         "WhenTicks": 636951294757335622,
         "Who": "Installer",
         "WhoID": "fbec7c22-500d-4f3b-b94e-4c19ff501f9f",
         "What": "Default Area",
         "WhatID": "481d30ac-9108-45e9-b8df-80fe98a2e349",
         "Where": "",
         "WhereID": "00000000-0000-0000-0000-000000000000"
       }
     ]
   }
   ```

## Example: Retrieve First 50 Events older than a Reference Event

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Retrieve a review event to use as a reference event by following one of
   the previous examples, and store the `ID` and `WhenTicks` values of the
   event.
3. Send a `GET` request to
   `api/v1/review?limit=50&dir=desc&referenceId=[msgId]&referenceTime=[msgTime]`,
   where `[msgId]` is the ID of the reference event and `[msgTime]` is the
   `WhenTicks` value of the reference event.
4. The server will respond with a block of up to 50 events that occurred
   before the reference event, ordered from newest to oldest.

   ```json
   {
     "Offset": 0,
     "Count": 50,
     "Data": [
       {
         "ID": "9d9c9bfa-c3bb-4d4e-aa7a-a9f43f5c5952",
         "Description": "Area Event Created",
         "MessageCategory": 5505,
         "When": "2019-07-10T10:07:04.2642453+10:00",
         "WhenTicks": 636983140242642453,
         "Who": "",
         "WhoID": "00000000-0000-0000-0000-000000000000",
         "What": "Armed",
         "WhatID": "00000000-0000-0000-0000-000000000000",
         "Where": "Area 3",
         "WhereID": "7419bc70-8a7d-4f4b-8d18-fd1c7f734202"
       }
     ]
   }
   ```

---

**Next:** [Long Polling & Monitoring →](long-polling.md)
