"""Tests for surfacing Inception auth failures via HA Repairs."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock, patch

import aiohttp
import pytest

from custom_components.inception.const import DOMAIN
from custom_components.inception.coordinator import (
    AUTH_ISSUE_ID_PREFIX,
    InceptionUpdateCoordinator,
)
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


class TestCoordinatorRepairsIntegration:
    """The coordinator should create/clear HA Repairs issues on auth events."""

    def _build_coordinator(self) -> InceptionUpdateCoordinator:
        """Build a minimal coordinator instance without going through __init__."""
        coordinator = InceptionUpdateCoordinator.__new__(InceptionUpdateCoordinator)
        coordinator.hass = SimpleNamespace()
        coordinator.config_entry = SimpleNamespace(
            entry_id="entry-xyz",
            title="Home Inception",
        )
        return coordinator

    def test_auth_issue_id_is_stable_per_entry(self) -> None:
        """The issue id should be deterministic and include the entry id."""
        coordinator = self._build_coordinator()

        assert coordinator._auth_issue_id == f"{AUTH_ISSUE_ID_PREFIX}_entry-xyz"

    def test_report_auth_failure_creates_issue(self) -> None:
        """Reporting an auth failure delegates to issue_registry.async_create_issue."""
        coordinator = self._build_coordinator()

        with patch(
            "custom_components.inception.coordinator.ir.async_create_issue"
        ) as mock_create:
            coordinator._report_auth_failure()

        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        assert args[0] is coordinator.hass
        assert args[1] == DOMAIN
        assert args[2] == coordinator._auth_issue_id
        assert kwargs["translation_key"] == "auth_failure"
        assert kwargs["translation_placeholders"] == {"entry_title": "Home Inception"}
        assert kwargs["is_fixable"] is False

    def test_clear_auth_failure_deletes_issue(self) -> None:
        """Clearing delegates to issue_registry.async_delete_issue."""
        coordinator = self._build_coordinator()

        with patch(
            "custom_components.inception.coordinator.ir.async_delete_issue"
        ) as mock_delete:
            coordinator._clear_auth_failure()

        mock_delete.assert_called_once_with(
            coordinator.hass,
            DOMAIN,
            coordinator._auth_issue_id,
        )
