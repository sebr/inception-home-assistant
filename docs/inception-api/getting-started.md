# Getting Started

[← Back to index](README.md)

## Contents

- [Introduction](#introduction)
- [Retrieving the API Protocol version](#retrieving-the-api-protocol-version)
- [Authentication / Logging In](#authentication--logging-in)
- [Using the REST API over SkyTunnel](#using-the-rest-api-over-skytunnel)

## Introduction

This document aims to demonstrate some of the various ways the Inception REST
API can be used to retrieve data and control entities in the system, with
specific examples of common use cases, including the extensive real-time update
capabilities available through long polling HTTP requests.

It is recommended that the reader already has some general level of experience
with sending HTTP requests, interaction with REST APIs, and JSON serialized
data.

The information in this document is relevant to the Inception REST API
protocol v8 released in Inception firmware version 4.0; previous firmware
versions may not support certain API features used in examples.

The complete documentation for the Inception REST API can be found on-board on
any Inception device at the URL `http://[inception-address]/ApiDoc`, where
`[inception-address]` is your Inception's hostname or IP address. If you don't
have access to an Inception controller, the documentation is also publicly
accessible via SkyTunnel at
`https://skytunnel.com.au/Inception/API_SAMPLE/ApiDoc`. The REST API
documentation also contains a downloadable Postman collection of example API
requests, which shows some practical samples of HTTP requests that can be sent
to the Inception API.

## Retrieving the API Protocol version

Before using the Inception REST API to interact with an Inception device, it
is recommended to first query for the device's API protocol version, to ensure
that the API methods you are planning to use are supported by the currently
loaded firmware version. This is done by sending a `GET` request to the
`api/protocol-version` URL on the targeted Inception, and reading the protocol
version number in the response. **Checking the API protocol version does not
require an authenticated session ID** in the HTTP request.

Certain API methods are marked in the API documentation with a minimum
supported API protocol version. Make sure that the Inception device's protocol
version is equal to or higher than the minimum protocol versions for the
methods you are planning on using, or you won't be able to use those API
methods without first upgrading the Inception device's firmware.

Follow these steps to retrieve the current API protocol version of the device:

1. Send a `GET` request to `api/protocol-version`.
2. Depending on how old the Inception firmware is, you may receive a valid
   JSON response, or a `404 Not Found` response if the firmware is too old.
   1. If the response contains a valid JSON response, the `ProtocolVersion`
      property will contain the API protocol version number. Compare this with
      the required protocol version of the API methods you are planning to use
      to see which methods are supported, and which ones are too new (i.e.
      required version > current protocol version). If certain API methods you
      wish to use are not supported, you can choose not to use those methods
      or to upgrade the Inception firmware to a newer version which supports
      those methods.

      ```json
      {
        "ProtocolVersion": 2
      }
      ```

   2. The request may return a `404 Not Found` response if the firmware is
      running an early version of the REST API. This may indicate that the
      firmware is running an early version of the REST API (before the
      protocol version endpoint was added), or that the firmware does not
      include the REST API at all. In either case, it is recommended that the
      device's firmware be upgraded before attempting to use REST API features
      to ensure maximum compatibility.

## Authentication / Logging In

Most of the Inception API methods require an authenticated session ID in the
request's `Cookie` header before the server will respond with the requested
data. It is necessary to authenticate with valid credentials before the rest
of the API can be used. See the API Overview documentation page for more
general information on setting up API User credentials to enable authenticated
requests to be made.

1. Send a `POST` request to `api/v1/authentication/login` on the targeted
   Inception's hostname/IP address with a JSON request body like the following
   (where `[username]` and `[password]` are the web credentials of an API User
   that exists on the targeted Inception):

   ```json
   {
     "Username": "[username]",
     "Password": "[password]"
   }
   ```

2. If the authentication was successful, the server will respond with a JSON
   object containing a new session ID (the `UserID` field), similar to the
   following. If not, the `Result` value will be `"Failure"`, with a reason
   given (incorrect credentials, system locked out), and no `UserID`.

   ```json
   {
     "Response": {
       "Result": "Success",
       "Message": "OK",
       "FailureReason": 0
     },
     "UserID": "ab6d680e-e481-4dca-a151-11dbc4c1e2ac"
   }
   ```

3. You can now send authorised REST API requests by putting the response's
   `UserID` string into the `Cookie` header of subsequent requests (i.e. set
   the `Cookie` HTTP header value to `LoginSessId=[sessionID]`). **This
   session ID will be valid for the next 10 minutes, and will be refreshed for
   another 10 minutes every time you make a request to the server.** If the
   session expires, you will have to repeat the process to authenticate again
   and receive a new session ID.
   1. Alternatively, if you are in an environment where you cannot edit HTTP
      request headers or cookies, the session ID can also be appended to the
      URL as a query string parameter with every API request you send (e.g.
      `GET api/v1/control/area?session-id=[id]`).

## Using the REST API over SkyTunnel

The Inception REST API can be accessed over Inner Range's free SkyTunnel
service from anywhere in the world if the controller is configured to allow
web access over SkyTunnel (enabled by default).

To enable API usage over SkyTunnel, log into the Inception web interface and
go to the **Configuration > General > Network** page and make sure the
**"Enable Web Access over SkyTunnel"** checkbox in the "SkyTunnel" section is
ticked.

API requests can be made through SkyTunnel simply by changing the root of the
URL to `https://www.skytunnel.com.au/inception/[serial]`. For example, if your
controller's serial number is `IN001234`, you can retrieve the API protocol
version of the controller's firmware over SkyTunnel by sending a `GET` request
to `https://www.skytunnel.com.au/inception/IN001234/api/protocol-version`.

> **NOTE**: Due to popularity, Inner Range's free SkyTunnel service has been
> upgraded to include multiple servers to support increased scale and
> geolocation optimization. This change affects integrations that communicate
> with the API over SkyTunnel. Requests sent to a SkyTunnel URL (for example:
> `https://www.skytunnel.com.au/inception/IN001234`) may respond with a
> **`307 Redirect`** status code containing the instance-specific URL in the
> `Location` header. There is no guarantee that an Inception controller will
> always remain connected to the same SkyTunnel instance, so integrations must
> make sure that redirect responses are followed correctly.

---

**Next:** [Entities →](entities.md)
