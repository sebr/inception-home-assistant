"""Test the Inception integration setup and unload."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import Platform

from custom_components.inception import (
    PLATFORMS,
    async_reload_entry,
    async_remove_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.inception.const import DOMAIN
from custom_components.inception.pyinception.api import InceptionApiClient


class TestInceptionIntegration:
    """Test Inception integration setup and teardown."""

    def test_platforms_list(self) -> None:
        """Test that all required platforms are included."""
        expected_platforms = [
            Platform.ALARM_CONTROL_PANEL,
            Platform.BINARY_SENSOR,
            Platform.LOCK,
            Platform.NUMBER,
            Platform.SELECT,
            Platform.SENSOR,
            Platform.SWITCH,
        ]

        assert set(PLATFORMS) == set(expected_platforms)

    def test_domain_constant(self) -> None:
        """Test domain constant is correct."""
        assert DOMAIN == "inception"

    def test_integration_functions_exist(self) -> None:
        """Test that integration functions exist."""
        # Test that functions exist and are callable
        assert callable(async_setup_entry)
        assert callable(async_unload_entry)
        assert callable(async_reload_entry)
        assert callable(async_remove_entry)


@pytest.mark.asyncio
async def test_async_unload_entry_cleans_up_coordinator() -> None:
    """Test that async_unload_entry properly cleans up the coordinator."""
    # Create mock objects
    mock_hass = Mock()
    mock_entry = Mock()
    mock_entry.entry_id = "test_entry_id"

    # Create a mock coordinator
    mock_coordinator = Mock()
    mock_coordinator.async_unload = AsyncMock()

    # Set up hass.data with the coordinator
    mock_hass.data = {DOMAIN: {mock_entry.entry_id: mock_coordinator}}

    # Mock async_unload_platforms to return True
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    # Call async_unload_entry
    result = await async_unload_entry(mock_hass, mock_entry)

    # Verify platforms were unloaded
    mock_hass.config_entries.async_unload_platforms.assert_called_once_with(
        mock_entry, PLATFORMS
    )

    # Verify coordinator was cleaned up
    mock_coordinator.async_unload.assert_called_once()

    # Verify coordinator was removed from hass.data
    assert mock_entry.entry_id not in mock_hass.data[DOMAIN]

    # Verify function returned True
    assert result is True


@pytest.mark.asyncio
async def test_async_unload_entry_fails_if_platforms_fail() -> None:
    """Test that async_unload_entry returns False if platform unload fails."""
    # Create mock objects
    mock_hass = Mock()
    mock_entry = Mock()
    mock_entry.entry_id = "test_entry_id"

    # Create a mock coordinator
    mock_coordinator = Mock()
    mock_coordinator.async_unload = AsyncMock()

    # Set up hass.data with the coordinator
    mock_hass.data = {DOMAIN: {mock_entry.entry_id: mock_coordinator}}

    # Mock async_unload_platforms to return False (failure)
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

    # Call async_unload_entry
    result = await async_unload_entry(mock_hass, mock_entry)

    # Verify platforms were attempted to unload
    mock_hass.config_entries.async_unload_platforms.assert_called_once_with(
        mock_entry, PLATFORMS
    )

    # Verify coordinator was NOT cleaned up (since platforms failed)
    mock_coordinator.async_unload.assert_not_called()

    # Verify coordinator was NOT removed from hass.data
    assert mock_entry.entry_id in mock_hass.data[DOMAIN]

    # Verify function returned False
    assert result is False


@pytest.mark.asyncio
async def test_async_remove_entry_cleans_up_storage() -> None:
    """Test that async_remove_entry removes stored settings."""
    # Create mock objects
    mock_hass = Mock()
    mock_entry = Mock()
    mock_entry.entry_id = "test_entry_id"

    # Mock the Store class
    mock_store = Mock()
    mock_store.async_remove = AsyncMock()

    # Patch Store in the __init__ module where it's imported
    with patch("custom_components.inception.Store", return_value=mock_store):
        # Call async_remove_entry
        await async_remove_entry(mock_hass, mock_entry)

        # Verify store was removed
        mock_store.async_remove.assert_called_once()


@pytest.mark.asyncio
async def test_api_client_close_clears_callbacks() -> None:
    """Test that API client close method clears callback lists."""
    # Create a mock session
    mock_session = Mock()

    # Create API client
    api_client = InceptionApiClient(
        token="test_token",
        host="http://test.com",
        session=mock_session,
    )

    # Add some mock callbacks
    mock_callback1 = Mock()
    mock_callback2 = Mock()
    api_client.register_data_callback(mock_callback1)
    api_client.register_review_event_callback(mock_callback2)

    # Verify callbacks were added
    assert len(api_client.data_update_cbs) == 1
    assert len(api_client.review_event_cbs) == 1

    # Close the API client
    await api_client.close()

    # Verify callbacks were cleared
    assert len(api_client.data_update_cbs) == 0
    assert len(api_client.review_event_cbs) == 0

    # Verify task references were reset
    assert api_client.rest_task is None
    assert api_client._review_events_task is None
