"""Inception API Client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import socket
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar
from urllib.parse import urlencode

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
    _review_events_update_time: ClassVar[int] = 0
    _review_events_reference_id: ClassVar[str | None] = None

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
        self.review_event_cbs: list = []
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

    async def monitor_review_events(self) -> None:
        """Monitor review events from the API."""
        _LOGGER.debug("Starting review events monitor")

        try:
            # Build query parameters for the review endpoint
            params = {
                "dir": "desc",
                "limit": 50,
            }

            # If we have a reference time and ID, use them to get newer events
            if self._review_events_update_time > 0 and self._review_events_reference_id:
                params.update(
                    {
                        "referenceId": self._review_events_reference_id,
                        "referenceTime": self._review_events_update_time,
                        "dir": "asc",
                    }
                )

            query_params = urlencode(params)
            response = await self._review_events_request(query_params)

            if not response:
                # No response from the API, try again later
                _LOGGER.debug("no response")
                return

            # The response is now a direct array of review events
            if isinstance(response, list):
                events_data = response
            else:
                # Handle case where response might be wrapped
                events_data = response.get("Data", response)

            # Process the review events
            if events_data:
                # Check if we have a list of events or need to extract them
                events = events_data if isinstance(events_data, list) else [events_data]

                # Find the latest event time to use as reference for next request
                latest_time = 0
                for event_data in events:
                    # Handle both dict and string responses
                    if not isinstance(event_data, dict):
                        _LOGGER.warning("Unexpected review Event: %s", event_data)
                        continue

                    _LOGGER.debug("Review Event: %s", event_data)

                    # Trigger review event callbacks
                    for cb in self.review_event_cbs:
                        self._schedule_review_event_callback(cb, event_data)

                    # Update reference time and ID
                    event_ref_time = event_data.get("WhenTicks", 0)
                    event_id = event_data.get("ID")

                    if not event_id:
                        continue

                    if event_ref_time > latest_time:
                        latest_time = event_ref_time
                        # Store the reference ID for the latest event
                        InceptionApiClient._review_events_reference_id = event_id

                # Update the reference time for next request
                if latest_time > self._review_events_update_time:
                    InceptionApiClient._review_events_update_time = latest_time

        except Exception:
            _LOGGER.exception("Error monitoring review events")

    def _schedule_data_callback(self, cb: Callable) -> None:
        """Schedule a data callback."""
        self.loop.call_soon_threadsafe(cb, self.data)

    def _schedule_review_event_callback(self, cb: Callable, event: dict) -> None:
        """Schedule a review event callback."""
        self.loop.call_soon_threadsafe(cb, event)

    def _schedule_data_callbacks(self) -> None:
        """Schedule a data callbacks."""
        for cb in self.data_update_cbs:
            self._schedule_data_callback(cb)

    def register_data_callback(self, callback: Callable) -> None:
        """Register a data update callback."""
        if callback not in self.data_update_cbs:
            self.data_update_cbs.append(callback)

    def register_review_event_callback(self, callback: Callable) -> None:
        """Register a review event callback."""
        if callback not in self.review_event_cbs:
            self.review_event_cbs.append(callback)

    async def _rest_task(self) -> None:
        """Poll data periodically via Rest."""
        while True:
            try:
                # Run entity state monitoring and review events
                await asyncio.gather(
                    self.monitor_entity_states(),
                    self._review_events_task(),
                    return_exceptions=True,
                )
            except Exception:
                _LOGGER.exception("_rest_task: Error in monitoring tasks")
            self._schedule_data_callbacks()

    async def _review_events_task(self) -> None:
        """Periodically poll review events."""
        while True:
            try:
                await self.monitor_review_events()
            except InceptionApiClientAuthenticationError:
                _LOGGER.exception(
                    "Authentication error in review events - stopping retries"
                )
                return
            except InceptionApiClientCommunicationError as e:
                # Check if it's a 4xx client error (irrecoverable)
                if (
                    "404" in str(e)
                    or "400" in str(e)
                    or "403" in str(e)
                    or "401" in str(e)
                ):
                    _LOGGER.exception(
                        "Client error in review events - stopping retries"
                    )
                    return
                # For other communication errors, wait and retry
                _LOGGER.warning(
                    "Communication error in review events - retrying: %s", e
                )
                await asyncio.sleep(60)
            except Exception:
                _LOGGER.exception("Unexpected error in review events task")
                await asyncio.sleep(60)

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

    async def _review_events_request(self, query_params: str) -> Any | None:
        """Get review events from the API."""
        try:
            response = await self.request(
                method="get",
                path=f"/review?{query_params}",
                api_timeout=aiohttp.ClientTimeout(
                    total=10
                ),  # Standard timeout for GET request
            )
        except TimeoutError:
            # No response from the API, try again later
            return None

        if not response:
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
