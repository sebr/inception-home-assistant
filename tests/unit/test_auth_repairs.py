"""Tests for surfacing Inception auth failures via HA re-auth flow."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed

from custom_components.inception.coordinator import InceptionUpdateCoordinator
from custom_components.inception.pyinception.api import (
    InceptionApiClient,
    InceptionApiClientAuthenticationError,
)


class TestAuthErrorCallback:
    """The api client should fan out auth-error callbacks at the right moments."""

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Return a mocked aiohttp session."""
        return Mock(spec=aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_register_auth_error_callback_deduplicates(
        self, mock_session: Mock
    ) -> None:
        """Registering the same callback twice should only store it once."""
        client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )

        cb = Mock()
        client.register_auth_error_callback(cb)
        client.register_auth_error_callback(cb)

        assert client.auth_error_cbs.count(cb) == 1

    @pytest.mark.asyncio
    async def test_rest_task_fires_auth_callback_on_auth_error(
        self, mock_session: Mock
    ) -> None:
        """When _rest_task sees a 401, registered auth callbacks should fire."""
        client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )
        scheduled: list[object] = []
        client.loop = SimpleNamespace(
            call_soon_threadsafe=lambda cb, *_: scheduled.append(cb)
        )

        cb = Mock()
        client.register_auth_error_callback(cb)

        async def raise_auth_error() -> None:
            msg = "Invalid credentials"
            raise InceptionApiClientAuthenticationError(msg)

        with patch.object(
            client, "monitor_entity_states", side_effect=raise_auth_error
        ):
            await client._rest_task()

        assert cb in scheduled

    @pytest.mark.asyncio
    async def test_review_events_fires_auth_callback_on_auth_error(
        self, mock_session: Mock
    ) -> None:
        """Auth errors bubbling out of _review_events_monitor also fire cbs."""
        client = InceptionApiClient(
            token="t", host="http://h.test", session=mock_session
        )
        scheduled: list[object] = []
        client.loop = SimpleNamespace(
            call_soon_threadsafe=lambda cb, *_: scheduled.append(cb)
        )
        client._review_events_enabled = True
        client._review_events_categories = ["System"]

        cb = Mock()
        client.register_auth_error_callback(cb)

        async def raise_auth_error(_categories: list[str] | None = None) -> None:
            msg = "Invalid credentials"
            raise InceptionApiClientAuthenticationError(msg)

        with (
            patch.object(client, "monitor_review_events", side_effect=raise_auth_error),
            pytest.raises(InceptionApiClientAuthenticationError),
        ):
            await client._review_events_monitor()

        assert cb in scheduled


class TestRequestPreservesAuthErrorType:
    """`request()` must not rewrap our auth errors as generic errors."""

    @pytest.mark.asyncio
    async def test_401_response_raises_auth_error_not_generic(self) -> None:
        """A 401 from the server reaches the caller as auth error, not generic."""
        mock_session = Mock(spec=aiohttp.ClientSession)

        class _Resp:
            status = 401

            def raise_for_status(self) -> None:
                return None

            async def json(self, content_type: object = None) -> dict[str, str]:  # noqa: ARG002
                return {}

        async def fake_request(*_args: object, **_kwargs: object) -> _Resp:
            return _Resp()

        mock_session.request = fake_request

        client = InceptionApiClient(
            token="bad", host="http://h.test", session=mock_session
        )

        # This used to raise InceptionApiClientError (generic) because the
        # broad `except Exception` clause was rewrapping our own auth
        # exception. Assert the specific type survives.
        with pytest.raises(InceptionApiClientAuthenticationError):
            await client.request(method="get", path="/control/input")

    @pytest.mark.asyncio
    async def test_403_response_raises_auth_error_not_generic(self) -> None:
        """Same guarantee for a 403 response."""
        mock_session = Mock(spec=aiohttp.ClientSession)

        class _Resp:
            status = 403

            def raise_for_status(self) -> None:
                return None

            async def json(self, content_type: object = None) -> dict[str, str]:  # noqa: ARG002
                return {}

        async def fake_request(*_args: object, **_kwargs: object) -> _Resp:
            return _Resp()

        mock_session.request = fake_request

        client = InceptionApiClient(
            token="bad", host="http://h.test", session=mock_session
        )

        with pytest.raises(InceptionApiClientAuthenticationError):
            await client.request(method="get", path="/control/input")


class TestCoordinatorReauthIntegration:
    """The coordinator should start HA's re-auth flow on auth events."""

    def _build_coordinator(self) -> InceptionUpdateCoordinator:
        """Build a minimal coordinator instance without going through __init__."""
        coordinator = InceptionUpdateCoordinator.__new__(InceptionUpdateCoordinator)
        coordinator.hass = SimpleNamespace()
        coordinator.config_entry = SimpleNamespace(
            entry_id="entry-xyz",
            title="Home Inception",
            async_start_reauth=Mock(),
        )
        coordinator.api = Mock()
        coordinator.monitor_connected = False
        coordinator._callbacks_registered = False
        return coordinator

    def test_trigger_reauth_delegates_to_config_entry(self) -> None:
        """The coordinator's auth callback should call entry.async_start_reauth."""
        coordinator = self._build_coordinator()

        coordinator._trigger_reauth()

        coordinator.config_entry.async_start_reauth.assert_called_once_with(
            coordinator.hass
        )

    @pytest.mark.asyncio
    async def test_update_data_raises_config_entry_auth_failed(self) -> None:
        """Foreground auth failures should raise ConfigEntryAuthFailed."""
        coordinator = self._build_coordinator()
        coordinator.api.get_data = AsyncMock(
            side_effect=InceptionApiClientAuthenticationError("bad token")
        )

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_update_data_registers_reauth_callback_after_success(self) -> None:
        """On successful fetch, the API client gets the reauth callback wired."""
        coordinator = self._build_coordinator()
        coordinator.api.get_data = AsyncMock(return_value=Mock())
        coordinator.api.connect = AsyncMock()
        coordinator.api.register_data_callback = Mock()
        coordinator.api.register_review_event_callback = Mock()
        coordinator.api.register_auth_error_callback = Mock()

        await coordinator._async_update_data()

        coordinator.api.register_auth_error_callback.assert_called_once_with(
            coordinator._trigger_reauth
        )
