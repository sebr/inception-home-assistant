# User Management

[← Back to index](README.md)

CRUD operations on the User entity, plus user photos and PIN generation.

## Contents

- [Example: Querying for Users](#example-querying-for-users)
- [Example: Getting a single User's Data](#example-getting-a-single-users-data)
- [Example: Creating a New User](#example-creating-a-new-user)
- [Example: Deleting a User](#example-deleting-a-user)
- [Example: Updating User Data (full overwrite)](#example-updating-user-data-full-overwrite)
- [Example: Patching User Data (partial update)](#example-patching-user-data-partial-update)
- [Example: Adding or Updating a User Photo (new in protocol version 8)](#example-adding-or-updating-a-user-photo-new-in-protocol-version-8)
- [Example: Deleting a User Photo (new in protocol version 8)](#example-deleting-a-user-photo-new-in-protocol-version-8)
- [Example: Generating an unused PIN for a user (new in protocol version 11)](#example-generating-an-unused-pin-for-a-user-new-in-protocol-version-11)

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
   `api/v1/config/user?includedProperties=Permissions,Credentials` will
   include the `Permissions` and `Credentials` properties in the JSON
   response. A list of all available property names can be found in the live
   API docs. Additionally, the results can be filtered to only include Users
   with new changes since a certain time, in the case where an integration
   needs to periodically sync User data from Inception but only requires the
   latest changes. This can be done with the `modifiedSince` query parameter,
   like `api/v1/config/user?modifiedSince=2019-05-29T15:00:00`.

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
   containing the patch data. The example below will assign a new `Notes`
   field value, a new Permission Group (where `[permissionGroupID]` is a
   valid Permission Group GUID) and Security PIN to the User, while leaving
   the rest of the User's data unchanged:

   ```json
   {
     "Notes": "User has been modified",
     "SecurityPin": "5678",
     "Permissions": [
       {
         "Item": "[permissionGroupID]"
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

---

**Next:** [Review Events →](review-events.md)
