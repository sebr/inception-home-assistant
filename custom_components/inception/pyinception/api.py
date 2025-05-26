"""Inception API Client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import socket
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

import aiohttp

from .data import InceptionApiData
from .schemas.area import AreaPublicState, AreaSummary
from .schemas.door import DoorPublicState, DoorSummary
from .schemas.input import InputPublicState, InputSummary
from .schemas.output import OutputPublicState, OutputSummary
from .schemas.update_monitor import (
    MonitorEntityStatesRequest,
    UpdateMonitorResponse,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from .schemas.entities import (
        InceptionSummary,
    )

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
        self.data: InceptionApiData | None = None
        self.data_update_cbs: list = []
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.rest_task: asyncio.Task | None = None
        self._last_update: int | None = None

    T = TypeVar("T", DoorSummary, InputSummary, OutputSummary, AreaSummary)

    async def get_controls(self, Type: type[T]) -> T:  # noqa: N803
        """Get control item summaries."""
        path_map = {
            DoorSummary: "door",
            InputSummary: "input",
            OutputSummary: "output",
            AreaSummary: "area",
        }
        if Type not in path_map:
            msg = f"Unsupported entity type: {Type}"
            raise ValueError(msg)

        data = await self.request(
            method="get",
            path=f"/control/{path_map[Type]}/summary",
        )
        return Type(**data)

    async def authenticate(self) -> bool:
        """Authenticate with the API."""
        await self.request(
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
            doors, outputs, inputs, areas = await asyncio.gather(
                self.get_controls(DoorSummary),
                self.get_controls(OutputSummary),
                self.get_controls(InputSummary),
                self.get_controls(AreaSummary),
            )

            self.data = InceptionApiData(
                inputs=inputs,
                doors=doors,
                areas=areas,
                outputs=outputs,
            )

        return self.data

    async def monitor_entity_states(self) -> None:
        """Monitor updates from the API."""
        _LOGGER.info("Starting long-poll monitor")
        if self.data is None:
            _LOGGER.warning("state monitor: no data to update")
            return

        request_types = {
            request_id: MonitorEntityStatesRequest(
                request_id=request_id,
                state_type=state_type,
                public_state_type=public_state_type,
                time_since_last_update=self._monitor_update_times.get(request_id, 0),
                api_data=api_data,
            )
            for request_id, state_type, public_state_type, api_data in [
                ("InputStateRequest", "InputState", InputPublicState, "inputs"),
                ("DoorStateRequest", "DoorState", DoorPublicState, "doors"),
                ("OutputStateRequest", "OutputState", OutputPublicState, "outputs"),
                ("AreaStateRequest", "AreaState", AreaPublicState, "areas"),
            ]
        }

        payload = [
            request_type.get_request_payload()
            for request_id, request_type in request_types.items()
        ]

        response = await self._monitor_events_request(payload)

        if not response:
            # No response from the API, try again later
            return

        response_id = response["ID"]

        update_request = request_types.get(response_id)
        if update_request is None:
            _LOGGER.error("Unknown response ID: %s", response_id)
            return

        result_response = UpdateMonitorResponse[update_request.public_state_type](
            **response["Result"]
        )

        self._monitor_update_times[response_id] = result_response.update_time

        entity_data: InceptionSummary = getattr(self.data, update_request.api_data)
        if entity_data is None:
            _LOGGER.error("No entity data for %s", update_request.api_data)
            return

        for event in result_response.state_data:
            try:
                if event.id not in entity_data.items:
                    _LOGGER.warning(
                        "Item %s not found in entity data, perhaps it was added recently? Please reload the integration.",  # noqa: E501
                        event.id,
                    )
                    continue

                _LOGGER.debug(
                    "Event: %s, %s, %s",
                    entity_data.items[event.id].entity_info.name,
                    event.public_state,
                    event.extra_fields,
                )

                entity_data.items[event.id].public_state = event.public_state
                entity_data.items[event.id].extra_fields.update(event.extra_fields)
            except Exception:
                _LOGGER.exception("Error processing event")

        self._schedule_data_callbacks()

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
            try:
                await self.monitor_entity_states()
            except Exception:
                _LOGGER.exception("_rest_task: Error monitoring entity states")
            self._schedule_data_callbacks()

    async def close(self) -> None:
        """Close the session."""
        _LOGGER.debug("Closing session")
        if self.rest_task:
            if not self.rest_task.cancelled():
                self.rest_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(self.rest_task)

    async def _monitor_events_request(self, payload: Any) -> Any | None:
        """Monitor updates from the API."""
        try:
            response = await self.request(
                method="post",
                data=payload,
                path="/monitor-updates",
                api_timeout=aiohttp.ClientTimeout(
                    total=70
                ),  # Inception long-poll timeout is 60 seconds, this should be enough
            )
        except TimeoutError:
            # No response from the API, try again later
            return None

        if not response or "Result" not in response or "ID" not in response:
            # No response from the API, try again later
            return None

        return response

    async def request(
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
            path = path.removeprefix("/")

            response = await self._session.request(
                method=method,
                url=f"{self._host}/api/v1/{path}",
                headers=headers,
                json=data,
                timeout=api_timeout,
            )
            _verify_response_or_raise(response)
            return await response.json(content_type=None)
        except TimeoutError as exception:
            _LOGGER.exception("TimeoutError")
            raise TimeoutError from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            _LOGGER.exception(msg)
            raise InceptionApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            _LOGGER.exception(msg)
            raise InceptionApiClientError(
                msg,
            ) from exception

    async def _control_item(self, item: str, data: Any | None = None) -> None:
        """Control the switch."""
        return await self.request(
            method="post", path=f"/control/{item}/activity", data=data
        )

    async def control_output(self, output_id: str, data: Any | None = None) -> None:
        """Send a control payload to an output."""
        return await self._control_item(item=f"output/{output_id}", data=data)

    async def control_input(self, input_id: str, data: Any | None = None) -> None:
        """Send a control payload to an input."""
        return await self._control_item(item=f"input/{input_id}", data=data)
