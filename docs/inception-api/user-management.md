# User Management

[← Back to index](README.md)

CRUD operations on the User entity, plus user photos, PIN generation, PIN
lookup, and SkyCommand mobile-app linking.

## Contents

- [Example: Querying for Users](#example-querying-for-users)
  - [Query parameters cheat sheet](#query-parameters-cheat-sheet)
- [Example: Getting a single User's Data](#example-getting-a-single-users-data)
- [Example: Creating a New User](#example-creating-a-new-user)
- [Example: Deleting a User](#example-deleting-a-user)
- [Example: Updating User Data (full overwrite)](#example-updating-user-data-full-overwrite)
- [Example: Patching User Data (partial update)](#example-patching-user-data-partial-update)
- [Example: Adding or Updating a User Photo (new in protocol version 8)](#example-adding-or-updating-a-user-photo-new-in-protocol-version-8)
- [Example: Getting a User's Photo](#example-getting-a-users-photo)
- [Example: Deleting a User Photo (new in protocol version 8)](#example-deleting-a-user-photo-new-in-protocol-version-8)
- [Example: Generating an unused PIN for a user (new in protocol version 11)](#example-generating-an-unused-pin-for-a-user-new-in-protocol-version-11)
- [Example: Looking up a User by PIN](#example-looking-up-a-user-by-pin)
- [Example: Linking a User to SkyCommand](#example-linking-a-user-to-skycommand)

## Example: Querying for Users

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `GET` request to `api/v1/config/user`. The server will respond with
   a list of all the Users in the system.

   ```json
   [
     {
       "ID": "69f57d11-d153-411e-b963-498d99352df7",
       "Name": "NewTest User",
       "DateTimeUpdated": "2019-05-29T15:05:10.4210209+10:00"
     },
     {
       "ID": "211c9106-3f92-439e-9f6e-32e597456b7b",
       "Name": "John Smith",
       "DateTimeUpdated": "2019-05-29T16:19:42.0570493+10:00"
     }
   ]
   ```

3. **Optional**: By default, only `User ID`, `Name` and `Last Modified Time`
   properties are returned in the query. Additional properties can be
   selectively included by setting the `includedProperties` query parameter
   to the desired properties, e.g.
   `api/v1/config/user?includedProperties=Permissions,PhysicalCredentials`
   will include the `Permissions` and `PhysicalCredentials` arrays in the
   JSON response. A list of all available property names can be found in the
   live API docs.

### Query parameters cheat sheet

| Param                | Example                                  | Purpose                                                                                       |
| -------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------- |
| `modifiedSince`      | `modifiedSince=2019-05-29T15:00:00`      | Only return users whose data has changed since the given ISO-8601 timestamp. Great for incremental sync. |
| `includedProperties` | `includedProperties=EmailAddress,Permissions` | Opt-in to additional fields. Works on both list and single-user GETs.                       |
| `count`              | `count=10`                               | Cap the number of results. Results are sorted by last-updated time, so `count=10` on the list endpoint returns the 10 most recently changed users. |

All three params can be combined.

## Example: Getting a single User's Data

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `GET` request to `api/v1/config/user/[userID]`, where `userID` is
   the ID of the User whose configuration data you want to retrieve.
3. The server will respond with a JSON object containing the User's data
   (example partially shortened).

   ```json
   {
     "DateTimeCreated": "2019-05-20T13:26:46.7984609+10:00",
     "DateTimeUpdated": "2019-05-28T14:30:28.260618+10:00",
     "ID": "448f141c-8658-4eaf-906d-22a644cc8ba2",
     "Name": "API User",
     "Notes": "",
     "EmailAddress": "",
     "SecurityPin": "",
     "Permissions": [
       {
         "Item": "09492660-72ed-4807-bc59-c1fef83981a5",
         "Allow": true
       }
     ],
     "UserCancelled": false
   }
   ```

4. As with the list endpoint, `includedProperties` narrows the response to
   specific fields, e.g.
   `api/v1/config/user/[userID]?includedProperties=EmailAddress,Permissions`
   returns only those two fields alongside the required `ID` / `Name`.

## Example: Creating a New User

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `POST` request to `api/v1/config/user` with a JSON request body
   similar to the following example, for a User named `"John Smith"` who has
   a PIN of `1234` and will expire on 28 May 2019 5:00PM server time (any
   properties not supplied in the JSON object will be filled in with default
   values).

   ```json
   {
     "Name": "John Smith",
     "Notes": "Sample user",
     "SecurityPin": "1234",
     "EnableExpiry": true,
     "ExpireAfter": "2019-05-28T17:00:00"
   }
   ```

3. You should receive a response from the server containing the entire new
   JSON User object if the User was successfully created. If there was an
   error creating the User, due to duplicate Security PIN, invalid data, etc.,
   the server will respond with an error and a text description of the
   problem.

   ```json
   {
     "DateTimeCreated": "2019-05-29T15:41:58.2848989+10:00",
     "DateTimeUpdated": "2019-05-29T15:41:58.2848989+10:00",
     "ID": "f8eecdc9-5088-42cc-b63d-230eb091c847",
     "Name": "John Smith",
     "Notes": "Sample user",
     "EmailAddress": null,
     "SecurityPin": "********",
     "Permissions": [],
     "UseExtendedUnlockTimes": false,
     "Credentials": [],
     "RemoteFobs": [],
     "TerminalProfile": "fe4e00f4-24b2-4dda-9355-761d37448650",
     "WebLoginEnabled": false,
     "WebLoginUsername": null,
     "WebLoginPassword": null,
     "WebPagePermissions": "0e44dc2c-b0d2-4fa2-80af-f5d076f090e9",
     "PermanentCache": false,
     "EnableExpiry": true,
     "ValidFrom": "0001-01-01T00:00:00",
     "ExpireAfter": "2019-05-28T17:00:00",
     "WhenToCancel": 0,
     "UserCancelled": false
   }
   ```

## Example: Deleting a User

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `DELETE` request to `api/v1/config/user/[userID]` where `[userID]`
   is the ID of the User you want to delete.
3. The server will respond with an empty `200 OK` response if the deletion
   was successful, or a `404 Not Found` if the user did not exist.

## Example: Updating User Data (full overwrite)

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `PUT` request to `api/v1/config/user/[userID]` where `[userID]` is
   the ID of the User whose data you want to replace, with a JSON request
   body containing the replacement User data.

   > **NOTE**: All User fields that are omitted from the JSON request body
   > will be reset to default values when overwriting. If you want to retain
   > existing field values while updating only specific data fields, see the
   > [Patching User Data](#example-patching-user-data-partial-update) example.

3. The server will respond with an empty `200 OK` response if the update was
   successful, or a description of the error if the update failed.

## Example: Patching User Data (partial update)

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `PATCH` request to `api/v1/config/user/[userID]` where `[userID]`
   is the ID of the User you want to patch, with a JSON request body
   containing the patch data. The example below updates `Notes`, enables
   extended unlock times, assigns a new web-permission profile, grants the
   user three control abilities on an area, and adds a physical credential
   — while leaving every other field unchanged:

   ```json
   {
     "Notes": "The quick brown fox jumps over the lazy dog",
     "UseExtendedUnlockTimes": true,
     "WebPagePermissions": "428B2B7B-E7A2-4DE1-8AD4-36C136647917",
     "Permissions": [
       {
         "Item": "[areaID]",
         "ControlAbilities": [1, 2, 8]
       }
     ],
     "PhysicalCredentials": [
       {
         "CardTemplate": "5ef5bc02-a512-447d-a0c4-65657b8dc5cd",
         "CardNumber": "123456"
       }
     ]
   }
   ```

3. The server will respond with an empty `200 OK` response if the patch
   request was successful, or a description of the error if the request
   failed.

## Example: Adding or Updating a User Photo (new in protocol version 8)

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `POST` request to `api/v1/config/user/[userID]/photo` where
   `[userID]` is the ID of the User you want to upload the photo for. The
   `POST` request should contain a `multipart/form-data` type body which
   contains the image file contents. The method to add a `multipart/form-data`
   body may differ depending on the HTTP client you are using, but the raw
   HTTP body should look similar to the following example if you are
   uploading a PNG file:

   ```http
   POST /api/v1/config/user/{id}/photo HTTP/1.1
   Accept: application/json
   Cookie: LoginSessId=(removed)
   User-Agent: (removed)
   Host: (removed)
   Accept-Encoding: gzip, deflate, br
   Connection: keep-alive
   Content-Type: multipart/form-data; boundary=--------------------------459156084925464413565125
   Content-Length: 1340824

   ----------------------------459156084925464413565125
   Content-Disposition: form-data; name="image"; filename="UserPhoto.png"
   Content-Type: image/png

   PNG
   (raw image bytes here)
   ```

3. The server will respond with an empty `200 OK` response if the photo
   upload was successful, or a description of the error if the request
   failed.

## Example: Getting a User's Photo

Send a `GET` request to `api/v1/config/user/[userID]/photo`. The response is
the raw image bytes, with an appropriate `Content-Type` header (e.g.
`image/png`). The server returns `404 Not Found` if the user has no photo.

## Example: Deleting a User Photo (new in protocol version 8)

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `DELETE` request to `api/v1/config/user/[userID]/photo` where
   `[userID]` is the ID of the User whose photo you want to delete.
3. The server will respond with an empty `200 OK` response if the request was
   successful, or a description of the error if the request failed.

## Example: Generating an unused PIN for a user (new in protocol version 11)

1. Authenticate as API User, save session ID from cookie and use it for future
   requests.
2. Send a `GET` request to `api/v1/config/user/generate-unused-pin`, with
   optional values for the `minLength`/`maxLength` query parameters if
   desired. If a custom min/max PIN length is specified, it must be within
   the system's configured PIN length range ("Access Configuration" section
   of the **Configuration > General > System** page in the web interface), or
   the request will be rejected as invalid.
3. The server will respond with a `200 OK` response similar to the following
   if a PIN was successfully generated, or a `500` error if there was a
   problem generating the PIN:

   ```json
   {
     "Success": true,
     "Pin": "71400526",
     "Error": ""
   }
   ```

4. The generated PIN can now be used for user creation or editing (see the
   [Creating a New User](#example-creating-a-new-user) example for more
   information).

## Example: Looking up a User by PIN

Useful if you already have the PIN in hand (e.g. captured at a terminal) and
want to resolve the matching user.

1. Send a `GET` request to `api/v1/config/user/by-pin/[pin]`, where `[pin]`
   is the numeric Security PIN value.
2. The server responds with the matching user's JSON object (same shape as
   `GET /config/user/[userID]`) if a match is found, or a `404 Not Found` if
   no user has that PIN. PINs remain write-only in every other response —
   this endpoint is the one exception.

## Example: Linking a User to SkyCommand

Associates an Inception user with a SkyCommand (Inner Range's mobile app)
account so push-to-arm / push-to-unlock features can be used.

1. Send a `POST` request to `api/v1/config/user/[userID]/skycommand` with:

   ```json
   {
     "Email": "[skycommand-registered-email]"
   }
   ```

2. A successful response is an empty `200 OK`; a `Failure` envelope is
   returned if the email does not match a SkyCommand account or if the link
   already exists.

---

**Next:** [Configuration →](configuration.md)
