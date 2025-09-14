"""Test coordinator event emission functionality."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.inception.const import EVENT_REVIEW_EVENT
from custom_components.inception.coordinator import InceptionUpdateCoordinator


@pytest.mark.asyncio
async def test_review_event_callback_emits_ha_event() -> None:
    """Test that review event callback emits Home Assistant event."""
    # Create mock objects
    mock_entry = Mock()
    mock_entry.data = {"token": "test_token", "host": "http://test.com"}

    mock_hass = Mock()
    mock_hass.bus = Mock()
    mock_hass.bus.async_fire = Mock()

    # Create coordinator
    coordinator = InceptionUpdateCoordinator(mock_hass, mock_entry)

    # Create sample event data
    event_data = {
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

    # Call the review event callback directly
    coordinator.review_event_callback(event_data)

    # Verify the Home Assistant event was fired
    expected_event_data = {
        "event_id": "event123",
        "event_type": "DoorAccess",
        "description": "Card access granted",
        "message_category": "Access",
        "when": "2023-12-01T10:30:00Z",
        "who": "John Doe",
        "what": "Door 1",
        "where": "Main Entrance",
        "when_ticks": 1701432600,
        "message_id": 5001,
    }

    mock_hass.bus.async_fire.assert_called_once_with(
        event_type=EVENT_REVIEW_EVENT,
        event_data=expected_event_data,
    )


@pytest.mark.asyncio
async def test_review_event_callback_filters_none_values() -> None:
    """Test that review event callback filters out None values."""
    # Create mock objects
    mock_entry = Mock()
    mock_entry.data = {"token": "test_token", "host": "http://test.com"}

    mock_hass = Mock()
    mock_hass.bus = Mock()
    mock_hass.bus.async_fire = Mock()

    # Create coordinator
    coordinator = InceptionUpdateCoordinator(mock_hass, mock_entry)

    # Create sample event data with some None values
    event_data = {
        "ID": "event123",
        "MessageType": "DoorAccess",
        "Description": "Card access granted",
        "MessageCategory": None,  # This should be filtered out
        "When": "2023-12-01T10:30:00Z",
        "Who": None,  # This should be filtered out
        "What": "Door 1",
        "Where": "Main Entrance",
        "WhenTicks": 1701432600,
        "MessageID": None,  # This should be filtered out
    }

    # Call the review event callback directly
    coordinator.review_event_callback(event_data)

    # Verify the Home Assistant event was fired with None values filtered out
    expected_event_data = {
        "event_id": "event123",
        "event_type": "DoorAccess",
        "description": "Card access granted",
        "when": "2023-12-01T10:30:00Z",
        "what": "Door 1",
        "where": "Main Entrance",
        "when_ticks": 1701432600,
    }

    mock_hass.bus.async_fire.assert_called_once_with(
        event_type=EVENT_REVIEW_EVENT,
        event_data=expected_event_data,
    )


@pytest.mark.asyncio
async def test_coordinator_registers_review_event_callback() -> None:
    """Test that coordinator registers review event callback with API client."""
    # Create mock objects
    mock_entry = Mock()
    mock_entry.data = {"token": "test_token", "host": "http://test.com"}

    mock_hass = Mock()
    mock_hass.bus = Mock()

    # Create coordinator
    coordinator = InceptionUpdateCoordinator(mock_hass, mock_entry)

    # Mock the API client
    with patch.object(coordinator, "api") as mock_api:
        mock_api.get_data = AsyncMock(return_value=Mock())
        mock_api.connect = AsyncMock()
        mock_api.register_data_callback = Mock()
        mock_api.register_review_event_callback = Mock()

        # Trigger the coordinator setup
        await coordinator._async_update_data()

        # Verify that the review event callback was registered
        mock_api.register_review_event_callback.assert_called_once_with(
            coordinator.review_event_callback
        )


@pytest.mark.asyncio
async def test_review_event_callback_handles_missing_fields() -> None:
    """Test that review event callback handles missing fields gracefully."""
    # Create mock objects
    mock_entry = Mock()
    mock_entry.data = {"token": "test_token", "host": "http://test.com"}

    mock_hass = Mock()
    mock_hass.bus = Mock()
    mock_hass.bus.async_fire = Mock()

    # Create coordinator
    coordinator = InceptionUpdateCoordinator(mock_hass, mock_entry)

    # Create minimal event data (some fields missing)
    event_data = {
        "ID": "event456",
        "Description": "Motion detected",
        # Missing most other fields
    }

    # Call the review event callback directly
    coordinator.review_event_callback(event_data)

    # Verify the Home Assistant event was fired with only available fields
    expected_event_data = {
        "event_id": "event456",
        "description": "Motion detected",
    }

    mock_hass.bus.async_fire.assert_called_once_with(
        event_type=EVENT_REVIEW_EVENT,
        event_data=expected_event_data,
    )


def test_review_event_callback_method_exists() -> None:
    """Test that the review event callback method exists."""
    assert hasattr(InceptionUpdateCoordinator, "review_event_callback")

    # Test method signature
    import inspect

    signature = inspect.signature(InceptionUpdateCoordinator.review_event_callback)
    params = list(signature.parameters.keys())
    assert "self" in params
    assert "event_data" in params
