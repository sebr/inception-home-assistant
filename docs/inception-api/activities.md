# Activities

[← Back to index](README.md)

Virtually perform access actions at a door reader — badging a credential or
presenting a PIN — as though the event happened physically at the reader, or
raise a system-wide user duress alert, and track the lifecycle of any
activity (state, progress messages, cancellation).

## Contents

- [Example: Virtually Badging a Card/Credential at a Door Reader](#example-virtually-badging-a-cardcredential-at-a-door-reader)
- [Example: Virtually Presenting a User PIN at a Door Reader](#example-virtually-presenting-a-user-pin-at-a-door-reader)
- [Example: Sending a User Duress alert](#example-sending-a-user-duress-alert)
- [Tracking an Activity](#tracking-an-activity)
  - [Example: Getting the current state of an Activity](#example-getting-the-current-state-of-an-activity)
  - [Example: Fetching queued progress messages for an Activity](#example-fetching-queued-progress-messages-for-an-activity)
  - [Example: Cancelling an Activity](#example-cancelling-an-activity)

## Example: Virtually Badging a Card/Credential at a Door Reader

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Find the ID of the Reader that you want to virtually badge the credential
   at (this can be found by using the `GET
   api/v1/control/door/[id]/attached-readers` endpoint on the Door that the
   Reader is attached to); the placeholder `[readerID]` will represent this
   reader's ID in the following steps.
3. Find the Credential Template and Credential Number of the User credential
   that you want to virtually badge at the reader. Credential data can be
   retrieved from the User's `Credentials` property (`GET
   api/v1/config/user/[id]`). The placeholders `[templateID]` and
   `[cardNumber]` will represent the Credential Template ID and the Card
   Number respectively in the following steps.
4. Send a `POST` request to `api/v1/activity` with a JSON request body of:

   ```json
   {
     "Type": "BadgeCredentialAtReader",
     "CredentialData": {
       "CredentialTemplate": "[templateID]",
       "Data": "[cardNumber]"
     },
     "Entity": "[readerID]"
   }
   ```

5. The access attempt will be carried out by the Inception system as though
   the credential was physically badged at the reader. If the activity was
   successfully submitted, a `"Success"` JSON response will be returned by
   the server, and the `ActivityID` can be used to monitor the activity's
   progress. If the request failed, the response result will be `"Failure"`
   and no `ActivityID` will be returned.

   ```json
   {
     "Response": {
       "Result": "Success",
       "Message": "OK"
     },
     "ActivityID": "d9b90072-745b-49eb-be01-10ae9a8c1792"
   }
   ```

## Example: Virtually Presenting a User PIN at a Door Reader

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Find the ID of the Reader that you want to virtually badge the credential
   at (this can be found by using the `GET
   api/v1/control/door/[id]/attached-readers` endpoint on the Door that the
   Reader is attached to); the placeholder `[readerID]` will represent this
   reader's ID in the following steps.
3. Find the User PIN that you want to virtually present at the door reader.
   **User PINs cannot be retrieved from User data in the REST API as they are
   write-only for security purposes**; you will need to know what the User PIN
   was set to beforehand. The placeholder `[userPin]` will represent the
   user's PIN in the following steps.
4. Send a `POST` request to `api/v1/activity` with a JSON request body of:

   ```json
   {
     "Type": "SendPINDataToReader",
     "Entity": "[readerID]",
     "PINData": "[userPin]"
   }
   ```

5. The access attempt will be carried out by the Inception system as though
   the PIN was physically entered at the reader. If the activity was
   successfully submitted, a `"Success"` JSON response will be returned by
   the server, and the `ActivityID` can be used to monitor the activity's
   progress. If the request failed, the response result will be `"Failure"`
   and no `ActivityID` will be returned.

   ```json
   {
     "Response": {
       "Result": "Success",
       "Message": "OK"
     },
     "ActivityID": "6a6fa14e-1f99-4483-be32-687c99057f66"
   }
   ```

## Example: Sending a User Duress alert

Raises a duress alert on the Inception system as though the logged-in
user had entered their configured duress PIN at a terminal. The activity is
attributed to the currently authenticated API User.

1. Authenticate API User, save session ID from cookie and use it for future
   requests.
2. Send a `POST` request to `api/v1/activity` with the following body. There
   is no `Entity` field — duress is a system-level alert rather than a
   per-reader action:

   ```json
   {
     "Type": "SendUserDuress"
   }
   ```

3. On success the response contains the usual `ActivityID` which can be
   tracked with the endpoints in the next section.

## Tracking an Activity

Every successful control / activity request returns an `ActivityID`. You can
inspect an in-flight (or already completed) activity synchronously with the
endpoints below — or subscribe to its progress asynchronously via
[Activity Progress long polling](long-polling.md#example-monitoring-the-progress-of-an-area-arm-activity).

### Example: Getting the current state of an Activity

`GET /activity/[activityID]` returns a JSON snapshot of the activity's
current state (message log, completion status, etc.).

### Example: Fetching queued progress messages for an Activity

`GET /activity/[activityID]/updates` returns the progress messages that have
been generated since the previous call. This is the synchronous equivalent
of the [Activity Progress](long-polling.md#example-monitoring-the-progress-of-an-area-arm-activity)
long-poll and is useful when your client cannot keep a long-lived request
open.

### Example: Cancelling an Activity

`DELETE /activity/[activityID]` asks the controller to abort the activity.
Not every activity type can be cancelled partway through — unsupported
cancellations will return a `Failure` envelope.

---

**Next:** [User Management →](user-management.md)
