"""Inception API Client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import socket
from typing import TYPE_CHECKING, Any, ClassVar

import aiohttp

from custom_components.inception.pyinception.states_schema import InputPublicStates

from .data import InceptionApiData
from .schema import Area, Door, Input, InputStateResponse, LiveReviewEventsResult

if TYPE_CHECKING:
    from collections.abc import Callable

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

    _monitor_update_times: ClassVar[dict[str, int]] = {}

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
        self._last_update: str | int = "null"

    async def get_controls(self, control_type: str) -> list[Any]:
        """Get entities from the API."""
        path_map = {
            "door": Door,
            "input": Input,
            "area": Area,
        }
        if control_type not in path_map:
            msg = f"Unsupported entity type: {control_type}"
            raise ValueError(msg)

        data = await self._api_wrapper(
            method="get",
            path=f"/control/{control_type}",
        )
        return [path_map[control_type](**item) for item in data]

    async def authenticate(self) -> bool:
        """Authenticate with the API."""
        await self._api_wrapper(
            method="get",
            path="/control/input",
        )
        return True

    async def connect(self) -> None:
        """Connect to the API."""
        self._schedule_data_callbacks()
        self.rest_task = asyncio.create_task(self._rest_task())

    async def get_data(self) -> InceptionApiData:
        """Get the status of the API."""
        if self.data is None:
            i_data = InceptionApiData()
            inputs, doors, areas = await asyncio.gather(
                self.get_controls("inputs"),
                self.get_controls("doors"),
                self.get_controls("areas"),
            )
            i_data.inputs = {i.ID: i for i in inputs}
            i_data.doors = {i.ID: i for i in doors}
            i_data.areas = {i.ID: i for i in areas}

            self.data = i_data

        return self.data

    async def monitor_entity_states(self) -> None:
        """Monitor updates from the API."""
        payload = [
            {
                "ID": entity_request_type,
                "RequestType": "MonitorEntityStates",
                "InputData": {
                    "stateType": state_type,
                    "timeSinceUpdate": self._monitor_update_times.get(
                        entity_request_type, "0"
                    ),
                },
            }
            for (entity_request_type, state_type) in [
                ("InputStateRequest", "InputState"),
                ("DoorStateRequest", "DoorState"),
            ]
        ]
        response = await self._api_wrapper(
            method="post",
            data=payload,
            path="/monitor-updates",
            api_timeout=aiohttp.ClientTimeout(total=60),
        )
        response_id = response["ID"]
        update_time = response["Result"]["updateTime"]
        state_data = response["Result"]["stateData"]

        self._monitor_update_times[response_id] = update_time

        events = [InputStateResponse(**item) for item in state_data]
        if self.data is not None:
            for event in events:
                state_description = InputPublicStates.get_state_description(
                    event.PublicState
                )
                _LOGGER.debug(
                    "Event: %s, %s, %s",
                    self.data.inputs[event.ID].Name,
                    event.PublicState,
                    state_description,
                )
                self.data.inputs[event.ID].extra_fields["state_description"] = (
                    state_description
                )
                self.data.inputs[event.ID].PublicState = event.PublicState
        else:
            _LOGGER.debug("state monitor: no data to update")

        self._schedule_data_callbacks()

    async def _monitor_live_review_events(
        self,
    ) -> None:
        """Monitor updates from the API."""
        payload = [
            {
                "ID": "LiveReviewEvents",
                "RequestType": "LiveReviewEvents",
                "InputData": {
                    "referenceId": "null",
                    "referenceTime": self._last_update,
                },
            }
        ]

        response = await self._api_wrapper(
            method="post",
            data=payload,
            path="/monitor-updates",
            api_timeout=aiohttp.ClientTimeout(total=60),
        )

        events = [LiveReviewEventsResult(**item) for item in response["Result"]]

        if events:
            for event in events:
                _LOGGER.debug(
                    "Event: %s, %s, %s", event.ID, event.What, event.Description
                )
            self._last_update = events[-1].WhenTicks
        else:
            _LOGGER.debug("No events from state monitor")

    def _schedule_data_callback(self, cb: Callable) -> None:
        """Schedule a data callback."""
        self.loop.call_soon_threadsafe(cb, self.data)

    def _schedule_data_callbacks(self) -> None:
        """Schedule a data callbacks."""
        for cb in self.data_update_cbs:
            self._schedule_data_callback(cb)

    def register_data_callback(self, callback: Callable) -> None:
        """Register a data update callback."""
        if callback not in self.data_update_cbs:
            self.data_update_cbs.append(callback)

    async def _rest_task(self) -> None:
        """Poll data periodically via Rest."""
        while True:
            await self.monitor_entity_states()
            self._schedule_data_callbacks()

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
        api_timeout: aiohttp.ClientTimeout | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            if api_timeout is None:
                api_timeout = aiohttp.ClientTimeout(total=10)
            headers = {
                "Authorization": f"APIToken {self._token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            # If path begins with a slash, remove it
            if path.startswith("/"):
                path = path[1:]

            response = await self._session.request(
                method=method,
                url=f"{self._host}/api/v1/{path}",
                headers=headers,
                json=data,
                timeout=api_timeout,
            )
            _verify_response_or_raise(response)
            return await response.json(content_type=None)

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
