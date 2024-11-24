"""Inception API Client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import socket
from typing import Any

import aiohttp

from .data import InceptionApiData, InceptionEntryData
from .schema import Area, Door, Input

_LOGGER = logging.getLogger(__name__)


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
        self._is_connected = False
        self.data: InceptionApiData | None = None
        self.data_update_cbs: list = []
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.rest_task: asyncio.Task | None = None
        self._last_update = None

    async def get_doors(self) -> list[Door]:
        """Get doors from the API."""
        data = await self._api_wrapper(
            method="get",
            path="/control/door",
        )
        return [Door(**item) for item in data]

    async def get_inputs(self) -> list[Input]:
        """Get doors from the API."""
        data = await self._api_wrapper(
            method="get",
            path="/control/input",
        )
        return [Input(**item) for item in data]

    async def get_areas(self) -> list[Area]:
        """Get doors from the API."""
        data = await self._api_wrapper(
            method="get",
            path="/control/area",
        )
        return [Area(**item) for item in data]

    async def authenticate(self) -> bool:
        """Authenticate with the API."""
        await self._api_wrapper(
            method="get",
            path="/control/input",
        )
        return True

    async def connect(self) -> None:
        self._schedule_data_callbacks()
        self.rest_task = asyncio.create_task(self._rest_task())

    async def get_status(self) -> InceptionApiData:
        """Get the status of the API."""
        _LOGGER.debug(
            "get_status: %s / %s",
            self._is_connected,
            self.data,
        )
        if not self._is_connected or self.data is None:
            i_data = InceptionApiData()
            inputs, doors, areas = await asyncio.gather(
                self.get_inputs(), self.get_doors(), self.get_areas()
            )
            i_data.inputs = {i.ID: i for i in inputs}
            i_data.doors = {i.ID: i for i in doors}
            i_data.areas = {i.ID: i for i in areas}

            self.data = i_data
            self._is_connected = True

        await self._monitor_updates()

        return self.data

    async def _monitor_updates(
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

        response = await self._api_wrapper(
            method="post",
            data=update_monitor,
            path="/monitor-updates",
            timeout=aiohttp.ClientTimeout(total=60),
        )
        _LOGGER.debug(
            "Monitor update response: %s",
            response,
        )

    def _schedule_data_callback(self, cb) -> None:
        """Schedule a data callback."""
        self.loop.call_soon_threadsafe(cb, self.data)

    def _schedule_data_callbacks(self) -> None:
        """Schedule a data callbacks."""
        for cb in self.data_update_cbs:
            self._schedule_data_callback(cb)

    def register_data_callback(self, callback) -> None:
        """Register a data update callback."""
        if callback not in self.data_update_cbs:
            self.data_update_cbs.append(callback)

    async def _rest_task(self) -> None:
        """Poll data periodically via Rest."""
        while True:
            # await self.connect()
            self._schedule_data_callbacks()
            await asyncio.sleep(60)

    async def close(self) -> None:
        """Close the session."""
        if self.rest_task:
            if not self.rest_task.cancelled():
                self.rest_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(self.rest_task)

    async def _api_wrapper(
        self,
        method: str,
        path: str,
        data: Any | None = None,
        timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=10),
    ) -> Any:
        """Get information from the API."""
        try:
            headers = {"Authorization": f"APIToken {self._token}"}

            # If path begins with a slash, remove it
            if path.startswith("/"):
                path = path[1:]

            response = await self._session.request(
                method=method,
                url=f"{self._host}/api/v1/{path}",
                headers=headers,
                json=data,
                timeout=timeout,
            )
            _verify_response_or_raise(response)
            return await response.json()

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
