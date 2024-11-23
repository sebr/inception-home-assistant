"""Inception API Client."""

from __future__ import annotations

import asyncio
import contextlib
import socket
from typing import Any

import aiohttp
import async_timeout

from .data import InceptionData
from .schema import Area, Door, Input


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
        token: str,
        host: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Inception API Client."""
        self._token = token
        self._host = host.rstrip("/")
        self._session = session
        self.data: dict[str, InceptionData] = {}
        self.data_update_cbs: list = []
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.rest_task: asyncio.Task | None = None

    async def get_doors(self) -> list[Door]:
        """Get doors from the API."""
        return await self._api_wrapper(
            method="get",
            path="/control/door",
        )

    async def get_inputs(self) -> list[Input]:
        """Get doors from the API."""
        return await self._api_wrapper(
            method="get",
            path="/control/input",
        )

    async def get_areas(self) -> list[Area]:
        """Get doors from the API."""
        return await self._api_wrapper(
            method="get",
            path="/control/areas",
        )

    async def authenticate(self) -> bool:
        """Authenticate with the API."""
        await self._api_wrapper(
            method="get",
            path="/control/input",
        )
        return True

    async def monitor_updates(
        self,
    ) -> None:
        """Monitor updates from the API."""
        update_monitor = [
            {
                "ID": "LiveReviewEvents",
                "RequestType": "LiveReviewEvents",
                "InputData": {"referenceId": "null", "referenceTime": "null"},
            }
        ]

        await self._api_wrapper(
            method="post",
            data=update_monitor,
            path="/control/monitor-updates",
        )

    def _schedule_data_callback(self, cb) -> None:
        """Schedule a data callback."""
        self.loop.call_soon_threadsafe(cb, self.data)

    def _schedule_data_callbacks(self) -> None:
        """Schedule a data callbacks."""
        for cb in self.data_update_cbs:
            self._schedule_data_callback(cb)

    def register_monitor_callback(self, callback) -> None:
        """Register a data update callback."""
        if callback not in self.data_update_cbs:
            self.data_update_cbs.append(callback)

    async def _rest_task(self) -> None:
        """Poll data periodically via Rest."""
        while True:
            await self.monitor_updates()
            self._schedule_data_callbacks()
            await asyncio.sleep(30)

    async def close(self) -> None:
        """Close the session."""
        if self.rest_task:
            if not self.rest_task.cancelled():
                self.rest_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(self.rest_task)

    async def _api_wrapper(
        self, method: str, path: str, data: Any | None = None
    ) -> Any:
        """Get information from the API."""
        try:
            headers = {"Authorization": f"APIToken {self._token}"}

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
