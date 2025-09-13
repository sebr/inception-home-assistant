"""Test the pyinception API client."""

from __future__ import annotations

import asyncio
from unittest.mock import Mock, patch

import aiohttp
import pytest

from custom_components.inception.pyinception.api import (
    InceptionApiClient,
    InceptionApiClientAuthenticationError,
    InceptionApiClientCommunicationError,
    _verify_response_or_raise,
)


class TestVerifyResponseOrRaise:
    """Test _verify_response_or_raise function."""

    def test_verify_response_success(self) -> None:
        """Test successful response verification."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.raise_for_status.return_value = None

        # Should not raise any exception
        _verify_response_or_raise(mock_response)
        mock_response.raise_for_status.assert_called_once()

    def test_verify_response_401_raises_auth_error(self) -> None:
        """Test 401 response raises authentication error."""
        mock_response = Mock()
        mock_response.status = 401

        with pytest.raises(
            InceptionApiClientAuthenticationError, match="Invalid credentials"
        ):
            _verify_response_or_raise(mock_response)

    def test_verify_response_403_raises_auth_error(self) -> None:
        """Test 403 response raises authentication error."""
        mock_response = Mock()
        mock_response.status = 403

        with pytest.raises(
            InceptionApiClientAuthenticationError, match="Invalid credentials"
        ):
            _verify_response_or_raise(mock_response)


class TestInceptionApiClient:
    """Test InceptionApiClient class basic functionality."""

    def test_constants_defined(self) -> None:
        """Test that API client constants are properly defined."""
        from custom_components.inception.pyinception.api import InceptionApiClient

        # Test that the class exists and has expected attributes
        assert hasattr(InceptionApiClient, "__init__")
        assert hasattr(InceptionApiClient, "get_data")
        assert hasattr(InceptionApiClient, "authenticate")
        assert hasattr(InceptionApiClient, "connect")

    def test_review_events_methods_exist(self) -> None:
        """Test that review events methods exist on API client."""
        from custom_components.inception.pyinception.api import InceptionApiClient

        # Test that review events methods exist
        assert hasattr(InceptionApiClient, "monitor_review_events")
        assert hasattr(InceptionApiClient, "_review_events_request")

    def test_review_events_class_variable_exists(self) -> None:
        """Test that review events class variable exists."""
        from custom_components.inception.pyinception.api import InceptionApiClient

        # Test that the class variable exists
        assert hasattr(InceptionApiClient, "_review_events_update_time")
        assert InceptionApiClient._review_events_update_time == 0

    def test_exception_hierarchy(self) -> None:
        """Test exception class hierarchy."""
        from custom_components.inception.pyinception.api import (
            InceptionApiClientAuthenticationError,
            InceptionApiClientCommunicationError,
            InceptionApiClientError,
        )

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

        # Mock the monitor_review_events method to raise a 404 error
        with patch.object(api_client, "monitor_review_events") as mock_monitor:
            # Simulate a 404 response by raising a communication error with 404
            mock_monitor.side_effect = InceptionApiClientCommunicationError(
                "Error fetching information - 404, message='Not Found', url='http://test.com/api/v1/review'"
            )

            # Start the review events task - it should exit after the first error
            await api_client._review_events_task()

            # Verify that the error was logged and task stopped
            log_messages = [record.message for record in caplog.records]
            assert any(
                "Client error in review events - stopping retries" in msg
                for msg in log_messages
            ), f"Expected error log not found in: {log_messages}"
            assert any("404" in msg for msg in log_messages), (
                f"404 not found in logs: {log_messages}"
            )

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

        # Mock the monitor_review_events method to raise a 403 error
        with patch.object(api_client, "monitor_review_events") as mock_monitor:
            # Simulate a 403 response
            mock_monitor.side_effect = InceptionApiClientCommunicationError(
                "Error fetching information - 403, message='Forbidden', url='http://test.com/api/v1/review'"
            )

            # Start the review events task - it should exit after the first error
            await api_client._review_events_task()

            # Verify that the error was logged and task stopped
            log_messages = [record.message for record in caplog.records]
            assert any(
                "Client error in review events - stopping retries" in msg
                for msg in log_messages
            ), f"Expected error log not found in: {log_messages}"
            assert any("403" in msg for msg in log_messages), (
                f"403 not found in logs: {log_messages}"
            )

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

        # Mock the monitor_review_events method to raise an authentication error
        with patch.object(api_client, "monitor_review_events") as mock_monitor:
            mock_monitor.side_effect = InceptionApiClientAuthenticationError(
                "Invalid credentials"
            )

            # Start the review events task - it should exit after the first error
            await api_client._review_events_task()

            # Verify that the authentication error was logged
            log_messages = [record.message for record in caplog.records]
            assert any(
                "Authentication error in review events - stopping retries" in msg
                for msg in log_messages
            ), f"Expected auth error log not found in: {log_messages}"

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

        # Mock the monitor_review_events method to raise a network error (5xx)
        call_count = 0

        def side_effect():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call raises error
                raise InceptionApiClientCommunicationError(
                    "Error fetching information - 500, message='Internal Server Error'"
                )
            # Second call would succeed, but we'll cancel before then

        with patch.object(api_client, "monitor_review_events", side_effect=side_effect):
            # Start the review events task, let it run once to see retry behavior
            task = asyncio.create_task(api_client._review_events_task())

            # Let it run briefly to process the first error and start waiting
            await asyncio.sleep(0.1)
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

            # Verify that the communication error was logged as a warning (retry)
            log_messages = [record.message for record in caplog.records]
            assert any(
                "Communication error in review events - retrying" in msg
                for msg in log_messages
            ), f"Expected retry warning not found in: {log_messages}"
