"""Inception API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout


class InceptionApiClientError(Exception):
    """Exception to indicate a general API error."""


class InceptionApiClientCommunicationError(
    InceptionApiClientError,
):
    """Exception to indicate a communication error."""


class InceptionApiClientAuthenticationError(
    InceptionApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise InceptionApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class InceptionApiClient:
    """Inception API Client."""

    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Inception API Client."""
        self._username = username
        self._password = password
        self._host = host.rstrip("/")
        self._session = session
        self._sessionCookie = None

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        if self._sessionCookie is None:
            await self.authenticate()

        doors = await self._api_wrapper(
            method="get",
            path="/control/door",
        )
        for key, value in doors.items():
            print(key, ":", value)

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch", path="/control/door", data={"title": value}
        )

    async def authenticate(self) -> Any:
        """Authenticate with the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.post(
                    f"{self._host}/api/v1/authentication/login",
                    json={"Username": self._username, "Password": self._password},
                )
                _verify_response_or_raise(response)
                data = await response.json()
                self._sessionCookie = data["UserID"]
        except TimeoutError as exception:
            msg = f"Timeout error authenticating - {exception}"
            raise InceptionApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error authenticating - {exception}"
            raise InceptionApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise InceptionApiClientError(
                msg,
            ) from exception

    async def _api_wrapper(
        self, method: str, path: str, data: dict | None = None
    ) -> Any:
        """Get information from the API."""
        try:
            headers = {"Cookie": f"LoginSessId=${self._sessionCookie}"}

            # If path begins with a slash, remove it
            if path.startswith("/"):
                path = path[1:]

            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=f"{self._host}/api/v1/{path}",
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise InceptionApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise InceptionApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise InceptionApiClientError(
                msg,
            ) from exception
