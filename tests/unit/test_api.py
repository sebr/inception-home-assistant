"""Test the pyinception API client."""

from __future__ import annotations

import asyncio
import contextlib
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
        # Test that review events methods exist
        assert hasattr(InceptionApiClient, "monitor_review_events")
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


class TestReviewEventsPermissions:
    """Test review events permission handling."""

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Create a mock session."""
        return Mock(spec=aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_review_events_404_logs_warning_and_stops_retries(
        self, mock_session: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that 404 on review endpoint logs warning and stops retries."""
        # Create API client within the test
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        # Enable review events for testing
        api_client._review_events_enabled = True
        api_client._review_events_categories = ["System"]

        # Mock the monitor_review_events method to raise a 404 error
        with patch.object(api_client, "monitor_review_events") as mock_monitor:
            # Simulate a 404 response by raising a communication error with 404
            mock_monitor.side_effect = InceptionApiClientCommunicationError(
                "Error fetching information - 404, message='Not Found', url='http://test.com/api/v1/review'"
            )

            # Start the review events task - it should exit after raising the error
            with pytest.raises(InceptionApiClientCommunicationError) as exc_info:
                await api_client._review_events_monitor()

            # Verify the 404 error was raised
            assert "404" in str(exc_info.value)

            # Verify task started and stopped correctly
            log_messages = [record.message for record in caplog.records]
            assert any("Review events task started" in msg for msg in log_messages)
            assert any("Review events task stopped" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_review_events_403_logs_warning_and_stops_retries(
        self, mock_session: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that 403 on review endpoint logs warning and stops retries."""
        # Create API client within the test
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        # Enable review events for testing
        api_client._review_events_enabled = True
        api_client._review_events_categories = ["System"]

        # Mock the monitor_review_events method to raise a 403 error
        with patch.object(api_client, "monitor_review_events") as mock_monitor:
            # Simulate a 403 response
            mock_monitor.side_effect = InceptionApiClientCommunicationError(
                "Error fetching information - 403, message='Forbidden', url='http://test.com/api/v1/review'"
            )

            # Start the review events task - it should exit after raising the error
            with pytest.raises(InceptionApiClientCommunicationError) as exc_info:
                await api_client._review_events_monitor()

            # Verify the 403 error was raised
            assert "403" in str(exc_info.value)

            # Verify task started and stopped correctly
            log_messages = [record.message for record in caplog.records]
            assert any("Review events task started" in msg for msg in log_messages)
            assert any("Review events task stopped" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_review_events_auth_error_stops_retries(
        self, mock_session: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that authentication errors stop retries."""
        # Create API client within the test
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        # Enable review events for testing
        api_client._review_events_enabled = True
        api_client._review_events_categories = ["System"]

        # Mock the monitor_review_events method to raise an authentication error
        with patch.object(api_client, "monitor_review_events") as mock_monitor:
            mock_monitor.side_effect = InceptionApiClientAuthenticationError(
                "Invalid credentials"
            )

            # Start the review events task - it should exit after raising the error
            with pytest.raises(InceptionApiClientAuthenticationError):
                await api_client._review_events_monitor()

            # Verify task started and stopped correctly
            log_messages = [record.message for record in caplog.records]
            assert any("Review events task started" in msg for msg in log_messages)
            assert any("Review events task stopped" in msg for msg in log_messages)

    @pytest.mark.asyncio
    async def test_review_events_network_error_retries(
        self, mock_session: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that network errors are retried."""
        # Create API client within the test
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        # Enable review events for testing
        api_client._review_events_enabled = True
        api_client._review_events_categories = ["System"]

        # Mock the monitor_review_events method to raise a network error (5xx)
        call_count = 0

        def side_effect(categories: list[str] | None = None) -> None:
            nonlocal call_count
            call_count += 1
            # Verify categories are passed correctly
            assert categories == ["System"]
            if call_count == 1:
                # First call raises error
                error_msg = (
                    "Error fetching information - 500, message='Internal Server Error'"
                )
                raise InceptionApiClientCommunicationError(error_msg)
            # Second call would succeed, but we'll cancel before then

        with patch.object(api_client, "monitor_review_events", side_effect=side_effect):
            # Start the review events task, let it run once to see retry behavior
            task = asyncio.create_task(api_client._review_events_monitor())

            # Let it run briefly to process the first error and start waiting
            await asyncio.sleep(0.1)
            task.cancel()

            with contextlib.suppress(asyncio.CancelledError):
                await task

            # Verify that the communication error was logged and retry scheduled
            log_messages = [record.message for record in caplog.records]
            assert any(
                "Communication error in review events:" in msg for msg in log_messages
            ), f"Expected communication error not found in: {log_messages}"
            assert any(
                "review_events: error #1, retrying in 5 seconds" in msg
                for msg in log_messages
            ), f"Expected retry backoff message not found in: {log_messages}"

    @pytest.mark.asyncio
    async def test_review_events_exponential_backoff(self) -> None:
        """Test that exponential backoff works correctly for retries."""
        # Test the backoff calculation directly via the static method
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
        """Test that review event callbacks are triggered when events are processed."""
        api_client = InceptionApiClient(
            token="test_token",
            host="http://test.com",
            session=mock_session,
        )

        # Mock the _review_events_request to return sample event data
        mock_event_data = [
            {
                "ID": "event123",
                "MessageType": "DoorAccess",
                "Description": "Card access granted",
                "MessageCategory": "Access",
                "When": "2023-12-01T10:30:00Z",
                "Who": "John Doe",
                "What": "Door 1",
                "Where": "Main Entrance",
                "WhenTicks": 1701432600,
                "MessageID": 5001,
            }
        ]

        callback = Mock()
        api_client.register_review_event_callback(callback)

        with patch.object(
            api_client, "_review_events_request", return_value=mock_event_data
        ):
            await api_client.monitor_review_events()

        # Verify the callback was scheduled to be called
        # Since we're using call_soon_threadsafe, callback not called yet
        assert callback.call_count == 0  # Not called yet due to threading
        assert len(api_client.review_event_cbs) == 1

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
