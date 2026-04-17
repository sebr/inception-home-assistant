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
from .schemas.review_events import LiveReviewEventsRequest
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
        self.auth_error_cbs: list = []
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.rest_task: asyncio.Task | None = None
        self._last_update: int | None = None
        self._review_events_enabled: bool = False
        self._review_events_categories: list[str] = []
        self._rest_task_retry_count: int = 0
        self._rest_task_max_retry_delay: int = 300  # 5 minutes max
        self.protocol_version: int | None = None

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

    async def get_protocol_version(self) -> int | None:
        """
        Fetch the Inception API protocol version.

        Returns the `ProtocolVersion` integer reported by the controller, or
        `None` if the endpoint returns 404 (firmware too old to expose it).
        Authentication is not required by the API for this endpoint, but the
        auth header is sent anyway for simplicity — the server ignores it.
        """
        try:
            response = await self.request(
                method="get",
                path="/protocol-version",
                api_prefix="api",
            )
        except InceptionApiClientCommunicationError as err:
            if "404" in str(err):
                _LOGGER.warning(
                    "Inception firmware does not expose /api/protocol-version; "
                    "the firmware is likely older than v4.0"
                )
                self.protocol_version = None
                return None
            raise

        if not isinstance(response, dict):
            return None

        version = response.get("ProtocolVersion")
        if isinstance(version, int):
            self.protocol_version = version
            _LOGGER.info("Inception API protocol version: %d", version)
            return version
        return None

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

    REVIEW_EVENTS_REQUEST_ID: ClassVar[str] = "LiveReviewEventsRequest"

    async def monitor_entity_states(self) -> None:
        """
        Run a single long-poll iteration against `/monitor-updates`.

        The payload bundles state-change sub-requests for all four entity
        types (Input, Door, Output, Area), plus the LiveReviewEvents
        sub-request when review events are enabled. The server returns a
        response for exactly one sub-request per call (matched by `ID`),
        so the dispatch here simply routes on the response `ID`.
        """
        _LOGGER.debug("Starting long-poll monitor")
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
            for request_type in request_types.values()
        ]

        review_request = await self._build_review_events_subrequest()
        if review_request is not None:
            payload.append(review_request.get_request_payload())

        response = await self._monitor_events_request(payload)

        if not response:
            # No response from the API, try again later
            return

        response_id = response["ID"]

        if response_id == self.REVIEW_EVENTS_REQUEST_ID and self._review_events_enabled:
            self._handle_review_events_response(response)
            return

        update_request = request_types.get(response_id)
        if update_request is None:
            _LOGGER.error("Unknown response ID: %s", response_id)
            return

        self._handle_entity_state_response(response, update_request)

    def _handle_entity_state_response(
        self,
        response: dict[str, Any],
        update_request: MonitorEntityStatesRequest,
    ) -> None:
        """Apply a MonitorEntityStates sub-request response to cached data."""
        result_response = UpdateMonitorResponse[update_request.public_state_type](
            **response["Result"]
        )

        self._monitor_update_times[update_request.request_id] = (
            result_response.update_time
        )

        if self.data is None:
            return
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

    def _handle_review_events_response(self, response: dict[str, Any]) -> None:
        """Route a LiveReviewEvents sub-request response to the processor."""
        result = response.get("Result", [])
        if isinstance(result, list) and result:
            self._process_review_events_data(result)

    async def _build_review_events_subrequest(
        self,
    ) -> LiveReviewEventsRequest | None:
        """
        Construct the LiveReviewEvents sub-request payload if enabled.

        On first use it establishes the reference point via
        `_get_latest_review_event`; if that fails we skip adding the
        sub-request this iteration rather than crashing the whole bundle.
        """
        if not self._review_events_enabled:
            return None

        if not self._review_events_reference_id:
            latest = await self._get_latest_review_event()
            if latest is None:
                _LOGGER.warning(
                    "Failed to establish review events reference point; "
                    "skipping review events this iteration"
                )
                return None
            InceptionApiClient._review_events_update_time = latest.get("WhenTicks", 0)
            InceptionApiClient._review_events_reference_id = latest.get("ID")
            _LOGGER.info(
                "Established review events reference point: ID=%s, Time=%d",
                self._review_events_reference_id,
                self._review_events_update_time,
            )

        return LiveReviewEventsRequest(
            request_id=self.REVIEW_EVENTS_REQUEST_ID,
            reference_id=self._review_events_reference_id,
            reference_time=self._review_events_update_time,
            category_filter=self._review_events_categories or None,
        )

    async def _get_latest_review_event(self) -> dict[str, Any] | None:
        """Get the latest review event to establish reference point."""
        try:
            params = {"dir": "desc", "limit": 1}
            query_params = urlencode(params)
            response = await self._review_events_request(query_params)

            if not response:
                return None

            # The response should be a list of events
            if isinstance(response, list) and response:
                return response[0]

            if isinstance(response, dict) and "Data" in response:
                data = response["Data"]
                if isinstance(data, list) and data:
                    return data[0]

            return None  # noqa: TRY300
        except Exception:
            _LOGGER.exception("Error getting latest review event")
            return None

    def _process_review_events_data(self, events_data: Any) -> None:
        """Process review events data and trigger callbacks."""
        # Check if we have a list of events or need to extract them
        events = events_data if isinstance(events_data, list) else [events_data]

        # Find the latest event time to use as reference for next request
        latest_time = 0
        is_initial_load = self._review_events_update_time == 0

        for event_data in events:
            # Handle both dict and string responses
            if not isinstance(event_data, dict):
                _LOGGER.warning("Unexpected review Event: %s", event_data)
                continue

            _LOGGER.debug("Review Event: %s", event_data)

            # Update reference time and ID
            event_ref_time = event_data.get("WhenTicks", 0)
            event_id = event_data.get("ID")

            if not event_id:
                continue

            if event_ref_time > latest_time:
                latest_time = event_ref_time
                # Store the reference ID for the latest event
                InceptionApiClient._review_events_reference_id = event_id

            # Only trigger callbacks for new events (not during initial load)
            if not is_initial_load:
                # Trigger review event callbacks for new events only
                for cb in self.review_event_cbs:
                    self._schedule_review_event_callback(cb, event_data)

        # Update the reference time for next request
        if latest_time > self._review_events_update_time:
            InceptionApiClient._review_events_update_time = latest_time

        # Log the initial load behavior
        if is_initial_load:
            _LOGGER.info(
                "Initial review events load completed. Found %d historical event(s), "
                "reference time set to %d. Future events will be emitted to HA.",
                len(events),
                latest_time,
            )

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

    def register_auth_error_callback(self, callback: Callable) -> None:
        """Register a callback invoked when the controller rejects auth."""
        if callback not in self.auth_error_cbs:
            self.auth_error_cbs.append(callback)

    def _schedule_auth_error_callbacks(self) -> None:
        """Fan out auth-error notifications on the main loop."""
        for cb in self.auth_error_cbs:
            self.loop.call_soon_threadsafe(cb)

    async def _rest_task(self) -> None:
        """Poll data periodically via Rest."""
        while True:
            try:
                await self.monitor_entity_states()
                self._reset_retry_count("rest_task")
            except InceptionApiClientAuthenticationError:
                _LOGGER.exception(
                    "rest_task: Authentication error, stopping monitoring"
                )
                self._schedule_auth_error_callbacks()
                break
            except (
                InceptionApiClientCommunicationError,
                InceptionApiClientError,
                TimeoutError,
            ) as err:
                _LOGGER.warning("rest_task: Connection error: %s", err)
                delay = self._increment_retry_count("rest_task")
                await asyncio.sleep(delay)
            except Exception:
                _LOGGER.exception("rest_task: Unexpected error in monitoring")
                delay = self._increment_retry_count("rest_task")
                await asyncio.sleep(delay)
            self._schedule_data_callbacks()

    @staticmethod
    def _get_retry_delay(retry_count: int, max_delay: int = 300) -> int:
        """Calculate exponential backoff delay for retries."""
        if retry_count == 0:
            return 5  # First retry after 5 seconds

        # Exponential backoff: 5, 10, 20, 40, 80, 160, 300 (capped)
        return min(
            5 * (2 ** (retry_count - 1)),
            max_delay,
        )

    def _reset_retry_count(self, task_name: str) -> None:
        """Reset retry count after successful operation."""
        count_attr = f"_{task_name}_retry_count"
        if getattr(self, count_attr) > 0:
            _LOGGER.debug("%s: Connection recovered, resetting retry count", task_name)
            setattr(self, count_attr, 0)

    def _increment_retry_count(self, task_name: str) -> int:
        """Increment retry count, log the backoff strategy, and return the delay."""
        count_attr = f"_{task_name}_retry_count"
        max_attr = f"_{task_name}_max_retry_delay"
        count = getattr(self, count_attr) + 1
        setattr(self, count_attr, count)
        delay = self._get_retry_delay(count, getattr(self, max_attr))
        _LOGGER.warning(
            "%s: error #%d, retrying in %d seconds",
            task_name,
            count,
            delay,
        )
        return delay

    async def close(self) -> None:
        """Close the session."""
        _LOGGER.debug("Closing session")

        # Disable review-event bundling so a partial restart doesn't inherit it.
        self._review_events_enabled = False
        self._review_events_categories = []

        # Stop main rest task (which owns the single long-poll connection).
        if self.rest_task:
            if not self.rest_task.cancelled():
                self.rest_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await asyncio.gather(self.rest_task)

        # Clear callback lists to prevent memory leaks
        self.data_update_cbs.clear()
        self.review_event_cbs.clear()
        self.auth_error_cbs.clear()

        # Reset task references
        self.rest_task = None

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
            _LOGGER.debug("Request: %s", f"/review?{query_params}")
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
        api_prefix: str = "api/v1",
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
            prefix = api_prefix.strip("/")

            response = await self._session.request(
                method=method,
                url=f"{self._host}/{prefix}/{path}",
                headers=headers,
                json=data,
                timeout=api_timeout,
            )
            if response.status in (401, 403):
                # Surface 401/403 as a specific auth error so the coordinator
                # can route it into Home Assistant's re-auth flow rather than
                # treating it as a transient connection failure.
                msg = "Invalid credentials"
                raise InceptionApiClientAuthenticationError(msg)  # noqa: TRY301
            response.raise_for_status()
            return await response.json(content_type=None)
        except InceptionApiClientError:
            # Our own exception hierarchy must propagate unchanged — the
            # broad `except Exception` below would otherwise rewrap the
            # auth error as a generic client error.
            raise
        except TimeoutError as exception:
            _LOGGER.debug("Timeout fetching %s", path)
            raise TimeoutError from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            _LOGGER.debug(msg)
            raise InceptionApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            _LOGGER.debug(msg)
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

    async def start_review_listener(self, categories: list[str]) -> None:
        """
        Enable bundled review-event polling on the next long-poll iteration.

        No separate task is spawned: the main `_rest_task` long-poll picks
        up the flag on its next iteration and adds a LiveReviewEvents
        sub-request to the same HTTP request.
        """
        _LOGGER.debug(
            "Enabling review events listener for categories: %s (was enabled: %s)",
            categories,
            self._review_events_enabled,
        )
        self._review_events_enabled = True
        self._review_events_categories = categories[:]
        _LOGGER.info("Review events listener enabled for categories: %s", categories)

    async def stop_review_listener(self) -> None:
        """Disable bundled review-event polling from the next iteration."""
        _LOGGER.debug(
            "Disabling review events listener (was enabled: %s)",
            self._review_events_enabled,
        )
        self._review_events_enabled = False
        self._review_events_categories = []
        _LOGGER.info("Review events listener disabled")
