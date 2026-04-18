"""Test the pyinception API client."""

from __future__ import annotations

import asyncio
import contextlib
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

if TYPE_CHECKING:
    from collections.abc import Callable

import aiohttp
import pytest

from custom_components.inception.pyinception.api import (
    InceptionApiClient,
    InceptionApiClientAuthenticationError,
    InceptionApiClientCommunicationError,
    InceptionApiClientError,
)


class TestInceptionApiClient:
    """Test InceptionApiClient class basic functionality."""

    def test_constants_defined(self) -> None:
        """Test that API client constants are properly defined."""
        # Test that the class exists and has expected attributes
        assert hasattr(InceptionApiClient, "__init__")
        assert hasattr(InceptionApiClient, "get_data")
        assert hasattr(InceptionApiClient, "authenticate")
        assert hasattr(InceptionApiClient, "connect")

    def test_review_events_methods_exist(self) -> None:
        """Test that review events methods exist on API client."""
        # Review events are now bundled into the main /monitor-updates
        # long-poll. The helpers that remain are:
        assert hasattr(InceptionApiClient, "start_review_listener")
        assert hasattr(InceptionApiClient, "stop_review_listener")
        assert hasattr(InceptionApiClient, "_build_review_events_subrequest")
        assert hasattr(InceptionApiClient, "_process_review_events_data")
        assert hasattr(InceptionApiClient, "_review_events_request")

    def test_review_events_class_variable_exists(self) -> None:
        """Test that review events class variable exists."""
        # Test that the class variable exists
        assert hasattr(InceptionApiClient, "_review_events_update_time")
        assert InceptionApiClient._review_events_update_time == 0

    def test_exception_hierarchy(self) -> None:
        """Test exception class hierarchy."""
        # Test exception inheritance
        assert issubclass(
            InceptionApiClientAuthenticationError, InceptionApiClientError
        )
        assert issubclass(InceptionApiClientCommunicationError, InceptionApiClientError)

        # Test exception creation
        auth_error = InceptionApiClientAuthenticationError("test")
        comm_error = InceptionApiClientCommunicationError("test")

        assert str(auth_error) == "test"
        assert str(comm_error) == "test"


class TestRetryBackoffDelay:
    """Static retry-delay helper used by _rest_task's backoff."""

    @pytest.mark.asyncio
    async def test_exponential_backoff(self) -> None:
        """The exponential backoff ladder is capped at 5 minutes."""
        assert InceptionApiClient._get_retry_delay(0) == 5  # First retry
        assert InceptionApiClient._get_retry_delay(1) == 5  # 5 * 2^0 = 5
        assert InceptionApiClient._get_retry_delay(2) == 10  # 5 * 2^1 = 10
        assert InceptionApiClient._get_retry_delay(3) == 20  # 5 * 2^2 = 20
        assert InceptionApiClient._get_retry_delay(4) == 40  # 5 * 2^3 = 40
        assert InceptionApiClient._get_retry_delay(5) == 80  # 5 * 2^4 = 80
        assert InceptionApiClient._get_retry_delay(6) == 160  # 5 * 2^5 = 160
        assert (
            InceptionApiClient._get_retry_delay(7) == 300
        )  # Capped at max (5 minutes)
        assert InceptionApiClient._get_retry_delay(10) == 300  # Still capped at max


class TestReviewEventCallbacks:
    """Test review event callback functionality."""

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Create a mock session."""
        return Mock(spec=aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_review_event_callback_registration(self, mock_session: Mock) -> None:
        """Test that review event callbacks can be registered."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        callback = Mock()
        api_client.register_review_event_callback(callback)

        assert callback in api_client.review_event_cbs

    @pytest.mark.asyncio
    async def test_review_event_callback_triggered(self, mock_session: Mock) -> None:
        """A bundled review-events response routes events to registered callbacks."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        # Pretend the reference point has been established; otherwise
        # _process_review_events_data treats the batch as initial load
        # and suppresses callbacks.
        InceptionApiClient._review_events_update_time = 1_000_000_000
        InceptionApiClient._review_events_reference_id = "prior-event"

        callback = Mock()
        api_client.register_review_event_callback(callback)

        bundled_response = {
            "ID": InceptionApiClient.REVIEW_EVENTS_REQUEST_ID,
            "Result": [
                {
                    "ID": "event123",
                    "MessageType": "DoorAccess",
                    "Description": "Card access granted",
                    "MessageCategory": "Access",
                    "When": "2023-12-01T10:30:00Z",
                    "Who": "John Doe",
                    "What": "Door 1",
                    "Where": "Main Entrance",
                    "WhenTicks": 2_000_000_000,
                    "MessageID": 5001,
                }
            ],
        }

        scheduled: list[tuple[Mock, dict]] = []
        api_client.loop = SimpleNamespace(
            call_soon_threadsafe=lambda cb, event: scheduled.append((cb, event))
        )

        api_client._handle_review_events_response(bundled_response)

        assert len(scheduled) == 1
        assert scheduled[0][0] is callback
        assert scheduled[0][1]["ID"] == "event123"
        # The reference-time update happens in-process (not deferred).
        assert InceptionApiClient._review_events_update_time == 2_000_000_000
        assert InceptionApiClient._review_events_reference_id == "event123"

    @pytest.mark.asyncio
    async def test_multiple_review_event_callbacks(self, mock_session: Mock) -> None:
        """Test that multiple review event callbacks can be registered."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        callback1 = Mock()
        callback2 = Mock()

        api_client.register_review_event_callback(callback1)
        api_client.register_review_event_callback(callback2)

        assert len(api_client.review_event_cbs) == 2
        assert callback1 in api_client.review_event_cbs
        assert callback2 in api_client.review_event_cbs

    @pytest.mark.asyncio
    async def test_duplicate_callback_not_added(self, mock_session: Mock) -> None:
        """Test that duplicate callbacks are not added twice."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        callback = Mock()

        api_client.register_review_event_callback(callback)
        api_client.register_review_event_callback(
            callback
        )  # Try to add same callback again

        assert len(api_client.review_event_cbs) == 1
        assert callback in api_client.review_event_cbs


class TestReviewEventsInitialLoad:
    """Test review events initial load behavior."""

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Create a mock session."""
        return Mock(spec=aiohttp.ClientSession)

    def setup_method(self) -> None:
        """Set up test method with clean state."""
        # Reset class variables for test isolation
        InceptionApiClient._review_events_update_time = 0
        InceptionApiClient._review_events_reference_id = None

    @pytest.mark.asyncio
    async def test_initial_load_doesnt_emit_historical_events(
        self, mock_session: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that historical events on initial load are not emitted."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        # Register a callback to track emissions
        callback = Mock()
        api_client.register_review_event_callback(callback)

        # Reset class variables to ensure clean state
        InceptionApiClient._review_events_update_time = 0
        InceptionApiClient._review_events_reference_id = None

        # Simulate initial state (no previous events loaded)
        assert api_client._review_events_update_time == 0

        # Mock historical event from initial load (only 1 event on initial load)
        historical_events = [
            {
                "ID": "event1",
                "Description": "Most recent historical event",
                "WhenTicks": 1701432800,
            },
        ]

        # Process the historical events
        api_client._process_review_events_data(historical_events)

        # Verify callbacks were NOT called for historical events
        callback.assert_not_called()

        # Verify reference time was updated
        assert InceptionApiClient._review_events_update_time == 1701432800
        assert InceptionApiClient._review_events_reference_id == "event1"

        # Verify appropriate log message
        log_messages = [record.message for record in caplog.records]
        assert any(
            "Initial review events load completed. Found 1 historical event(s)" in msg
            for msg in log_messages
        )

    @pytest.mark.asyncio
    async def test_subsequent_events_are_emitted(self, mock_session: Mock) -> None:
        """Test that new events after initial load are properly emitted."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        # Mock the callback scheduling to directly call the callback
        callback = Mock()
        api_client.register_review_event_callback(callback)

        def direct_callback(
            cb: Callable[[dict[str, Any]], None], event: dict[str, Any]
        ) -> None:
            """Call callback directly instead of scheduling."""
            cb(event)

        api_client._schedule_review_event_callback = direct_callback

        # Simulate that initial load has already occurred
        # (non-zero time means not initial)
        InceptionApiClient._review_events_update_time = 1701432800
        InceptionApiClient._review_events_reference_id = "event1"

        # Mock new events after initial load
        new_events = [
            {
                "ID": "event4",
                "Description": "New event",
                "WhenTicks": 1701432900,
            },
        ]

        # Verify that it's not treated as initial load
        assert api_client._review_events_update_time == 1701432800

        # Process the new events
        api_client._process_review_events_data(new_events)

        # Verify callback WAS called for new events
        assert callback.call_count == 1


class TestRestTaskBackoff:
    """Test _rest_task exponential backoff behavior."""

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Create a mock session."""
        return Mock(spec=aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_rest_task_backoff_on_communication_error(
        self, mock_session: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that _rest_task uses backoff on communication errors."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )
        api_client.data = Mock()

        call_count = 0

        async def failing_monitor() -> None:
            nonlocal call_count
            call_count += 1
            msg = "Connection refused"
            raise InceptionApiClientCommunicationError(msg)

        with patch.object(
            api_client, "monitor_entity_states", side_effect=failing_monitor
        ):
            task = asyncio.create_task(api_client._rest_task())
            # Let it attempt once and start sleeping on backoff
            await asyncio.sleep(0.2)
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        assert call_count == 1
        assert api_client._rest_task_retry_count == 1
        log_messages = [record.message for record in caplog.records]
        assert any("rest_task: Connection error:" in msg for msg in log_messages), (
            f"Expected connection error not found in: {log_messages}"
        )

    @pytest.mark.asyncio
    async def test_rest_task_auth_error_stops_loop(
        self, mock_session: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that authentication errors stop the _rest_task loop."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )
        api_client.data = Mock()

        with patch.object(api_client, "monitor_entity_states") as mock_monitor:
            mock_monitor.side_effect = InceptionApiClientAuthenticationError(
                "Invalid credentials"
            )
            # _rest_task should exit (break) on auth error
            await api_client._rest_task()

        assert mock_monitor.call_count == 1
        log_messages = [record.message for record in caplog.records]
        assert any(
            "Authentication error, stopping monitoring" in msg for msg in log_messages
        ), f"Expected auth error not found in: {log_messages}"

    @pytest.mark.asyncio
    async def test_rest_task_retry_resets_on_success(self, mock_session: Mock) -> None:
        """Test that retry count resets after successful monitoring."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )
        api_client.data = Mock()
        api_client._rest_task_retry_count = 5  # Simulate previous errors

        call_count = 0

        async def succeed_then_stop() -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return  # Success
            raise asyncio.CancelledError  # Stop the loop

        with (
            patch.object(
                api_client, "monitor_entity_states", side_effect=succeed_then_stop
            ),
            contextlib.suppress(asyncio.CancelledError),
        ):
            await api_client._rest_task()

        assert api_client._rest_task_retry_count == 0

    @pytest.mark.asyncio
    async def test_rest_task_backoff_on_timeout(self, mock_session: Mock) -> None:
        """Test that _rest_task uses backoff on timeout errors."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )
        api_client.data = Mock()

        call_count = 0

        async def timeout_monitor() -> None:
            nonlocal call_count
            call_count += 1
            raise TimeoutError

        with patch.object(
            api_client, "monitor_entity_states", side_effect=timeout_monitor
        ):
            task = asyncio.create_task(api_client._rest_task())
            await asyncio.sleep(0.2)
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

        assert call_count == 1
        assert api_client._rest_task_retry_count == 1


class _AwaitableValue:
    """Minimal awaitable wrapper so session.request can be mocked synchronously."""

    def __init__(self, value: Any) -> None:
        self._value = value

    def __await__(self) -> Any:
        async def _inner() -> Any:
            return self._value

        return _inner().__await__()


class TestProtocolVersion:
    """Tests for the protocol-version probe."""

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Return a mocked aiohttp session."""
        return Mock(spec=aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_get_protocol_version_stores_integer(
        self, mock_session: Mock
    ) -> None:
        """A 200 response with ProtocolVersion caches and returns the int."""
        api_client = InceptionApiClient(
            token="test-token",
            host="http://test.example.com",
            session=mock_session,
        )
        assert api_client.protocol_version is None

        with patch.object(
            api_client, "request", return_value={"ProtocolVersion": 11}
        ) as mock_request:
            version = await api_client.get_protocol_version()

        assert version == 11
        assert api_client.protocol_version == 11
        mock_request.assert_awaited_once_with(
            method="get",
            path="/protocol-version",
            api_prefix="api",
        )

    @pytest.mark.asyncio
    async def test_get_protocol_version_404_returns_none(
        self, mock_session: Mock
    ) -> None:
        """Old firmware returns 404; we swallow it and return None."""
        api_client = InceptionApiClient(
            token="t", host="http://test.example.com", session=mock_session
        )
        with patch.object(
            api_client,
            "request",
            side_effect=InceptionApiClientCommunicationError(
                "Error fetching information - 404, message='Not Found', url='...'"
            ),
        ):
            version = await api_client.get_protocol_version()

        assert version is None
        assert api_client.protocol_version is None

    @pytest.mark.asyncio
    async def test_get_protocol_version_non_404_communication_error_raises(
        self, mock_session: Mock
    ) -> None:
        """Connectivity failures (non-404) bubble up."""
        api_client = InceptionApiClient(
            token="t", host="http://test.example.com", session=mock_session
        )
        with (
            patch.object(
                api_client,
                "request",
                side_effect=InceptionApiClientCommunicationError(
                    "Error fetching information - Cannot connect to host"
                ),
            ),
            pytest.raises(InceptionApiClientCommunicationError),
        ):
            await api_client.get_protocol_version()

    @pytest.mark.asyncio
    async def test_get_protocol_version_malformed_response(
        self, mock_session: Mock
    ) -> None:
        """A response without ProtocolVersion yields None, doesn't crash."""
        api_client = InceptionApiClient(
            token="t", host="http://test.example.com", session=mock_session
        )
        with patch.object(api_client, "request", return_value={"unexpected": "shape"}):
            version = await api_client.get_protocol_version()

        assert version is None

    @pytest.mark.asyncio
    async def test_get_protocol_version_non_dict_response(
        self, mock_session: Mock
    ) -> None:
        """A non-dict response (e.g. list) yields None rather than raising."""
        api_client = InceptionApiClient(
            token="t", host="http://test.example.com", session=mock_session
        )
        with patch.object(api_client, "request", return_value=[1, 2, 3]):
            version = await api_client.get_protocol_version()

        assert version is None


class TestRequestApiPrefix:
    """Tests for the api_prefix argument to request()."""

    @pytest.mark.asyncio
    async def test_request_uses_custom_api_prefix(self) -> None:
        """The api_prefix argument overrides the default v1 path prefix."""
        mock_session = Mock(spec=aiohttp.ClientSession)
        mock_response = Mock()
        mock_response.status = 200
        mock_response.raise_for_status.return_value = None

        async def _json(content_type: Any = None) -> dict[str, int]:  # noqa: ARG001
            return {"ProtocolVersion": 8}

        mock_response.json = _json
        mock_session.request = Mock(return_value=_AwaitableValue(mock_response))

        client = InceptionApiClient(
            token="t",
            host="http://h.test",
            session=mock_session,
        )

        result = await client.request(
            method="get",
            path="/protocol-version",
            api_prefix="api",
        )

        assert result == {"ProtocolVersion": 8}
        called_url = mock_session.request.call_args.kwargs["url"]
        assert called_url == "http://h.test/api/protocol-version"

    @pytest.mark.asyncio
    async def test_request_default_api_prefix_is_v1(self) -> None:
        """Default prefix remains api/v1 so existing callers are unchanged."""
        mock_session = Mock(spec=aiohttp.ClientSession)
        mock_response = Mock()
        mock_response.status = 200
        mock_response.raise_for_status.return_value = None

        async def _json(content_type: Any = None) -> dict[str, str]:  # noqa: ARG001
            return {}

        mock_response.json = _json
        mock_session.request = Mock(return_value=_AwaitableValue(mock_response))

        client = InceptionApiClient(
            token="t",
            host="http://h.test",
            session=mock_session,
        )

        await client.request(method="get", path="/control/input")

        called_url = mock_session.request.call_args.kwargs["url"]
        assert called_url == "http://h.test/api/v1/control/input"


class TestBundledLongPoll:
    """The single long-poll now bundles entity-state AND review-event requests."""

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Return a mocked aiohttp session."""
        return Mock(spec=aiohttp.ClientSession)

    def setup_method(self) -> None:
        """Reset shared class state between tests."""
        InceptionApiClient._review_events_update_time = 0
        InceptionApiClient._review_events_reference_id = None
        InceptionApiClient._monitor_update_times = {}

    @pytest.mark.asyncio
    async def test_payload_excludes_review_request_when_disabled(
        self, mock_session: Mock
    ) -> None:
        """With review events disabled, only the 4 entity sub-requests are sent."""
        api_client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )
        api_client.data = Mock()
        api_client._review_events_enabled = False

        captured_payloads: list[list[dict[str, Any]]] = []

        async def fake_request(payload: list[dict[str, Any]]) -> None:
            captured_payloads.append(payload)

        with patch.object(
            api_client, "_monitor_events_request", side_effect=fake_request
        ):
            await api_client.monitor_entity_states()

        assert len(captured_payloads) == 1
        ids = [entry["ID"] for entry in captured_payloads[0]]
        assert ids == [
            "InputStateRequest",
            "DoorStateRequest",
            "OutputStateRequest",
            "AreaStateRequest",
        ]

    @pytest.mark.asyncio
    async def test_payload_includes_review_request_when_enabled(
        self, mock_session: Mock
    ) -> None:
        """With review events enabled, a 5th LiveReviewEvents sub-request is added."""
        api_client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )
        api_client.data = Mock()
        api_client._review_events_enabled = True
        api_client._review_events_categories = ["Access", "Security"]

        # Pretend reference point is already set so we don't hit the API.
        InceptionApiClient._review_events_reference_id = "prior-event"
        InceptionApiClient._review_events_update_time = 123

        captured_payloads: list[list[dict[str, Any]]] = []

        async def fake_request(payload: list[dict[str, Any]]) -> None:
            captured_payloads.append(payload)

        with patch.object(
            api_client, "_monitor_events_request", side_effect=fake_request
        ):
            await api_client.monitor_entity_states()

        assert len(captured_payloads) == 1
        ids = [entry["ID"] for entry in captured_payloads[0]]
        assert InceptionApiClient.REVIEW_EVENTS_REQUEST_ID in ids
        assert len(ids) == 5

    @pytest.mark.asyncio
    async def test_review_events_response_routed_to_processor(
        self, mock_session: Mock
    ) -> None:
        """A response tagged with the review events ID routes to events handling."""
        api_client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )
        api_client.data = Mock()
        api_client._review_events_enabled = True
        api_client._review_events_categories = ["Access"]
        InceptionApiClient._review_events_reference_id = "prior"
        InceptionApiClient._review_events_update_time = 1_000_000_000

        review_response = {
            "ID": InceptionApiClient.REVIEW_EVENTS_REQUEST_ID,
            "Result": [
                {
                    "ID": "new-event",
                    "Description": "Door access granted",
                    "WhenTicks": 2_000_000_000,
                }
            ],
        }

        with (
            patch.object(
                api_client, "_monitor_events_request", return_value=review_response
            ),
            patch.object(
                api_client, "_handle_review_events_response"
            ) as mock_review_handler,
            patch.object(
                api_client, "_handle_entity_state_response"
            ) as mock_entity_handler,
        ):
            await api_client.monitor_entity_states()

        mock_review_handler.assert_called_once_with(review_response)
        mock_entity_handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_entity_state_response_routed_to_entity_handler(
        self, mock_session: Mock
    ) -> None:
        """A response tagged with an entity ID routes to entity-state handling."""
        api_client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )
        api_client.data = Mock()
        api_client._review_events_enabled = False

        state_response = {
            "ID": "DoorStateRequest",
            "Result": {"updateTime": "1", "stateData": []},
        }

        with (
            patch.object(
                api_client, "_monitor_events_request", return_value=state_response
            ),
            patch.object(
                api_client, "_handle_entity_state_response"
            ) as mock_entity_handler,
            patch.object(
                api_client, "_handle_review_events_response"
            ) as mock_review_handler,
        ):
            await api_client.monitor_entity_states()

        mock_entity_handler.assert_called_once()
        mock_review_handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_start_review_listener_flips_flag_without_task(
        self, mock_session: Mock
    ) -> None:
        """start_review_listener just enables bundling; no task is spawned."""
        api_client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )

        await api_client.start_review_listener(["Access", "Security"])

        assert api_client._review_events_enabled is True
        assert api_client._review_events_categories == ["Access", "Security"]
        # No separate task should exist.
        assert not hasattr(api_client, "_review_events_task")

    @pytest.mark.asyncio
    async def test_stop_review_listener_clears_flag(self, mock_session: Mock) -> None:
        """stop_review_listener disables bundling and clears categories."""
        api_client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )
        api_client._review_events_enabled = True
        api_client._review_events_categories = ["Access"]

        await api_client.stop_review_listener()

        assert api_client._review_events_enabled is False
        assert api_client._review_events_categories == []
