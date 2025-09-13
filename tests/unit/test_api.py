"""Test the pyinception API client."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from custom_components.inception.pyinception.api import (
    InceptionApiClientAuthenticationError,
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
