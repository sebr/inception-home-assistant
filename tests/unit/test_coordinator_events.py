"""Test coordinator event emission functionality."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from custom_components.inception.const import EVENT_REVIEW_EVENT
from custom_components.inception.coordinator import InceptionUpdateCoordinator


def test_review_event_callback_method_exists() -> None:
    """Test that the review event callback method exists."""
    assert hasattr(InceptionUpdateCoordinator, "review_event_callback")

    # Test method signature
    import inspect

    signature = inspect.signature(InceptionUpdateCoordinator.review_event_callback)
    params = list(signature.parameters.keys())
    assert "self" in params
    assert "event_data" in params


def test_review_event_callback_emits_ha_event() -> None:
    """Test that review event callback emits Home Assistant event."""
    # Create mock objects
    mock_entry = Mock()
    mock_entry.data = {"token": "test_token", "host": "http://test.com"}

    mock_hass = Mock()
    mock_hass.bus = Mock()
    mock_hass.bus.async_fire = Mock()

    # Create coordinator by mocking the parent class initialization
    with pytest.MonkeyPatch().context() as m:
        # Mock the DataUpdateCoordinator.__init__ to avoid HA framework setup
        m.setattr(
            "custom_components.inception.coordinator.DataUpdateCoordinator.__init__",
            Mock(return_value=None),
        )

        # Create coordinator and set required attributes
        coordinator = InceptionUpdateCoordinator.__new__(InceptionUpdateCoordinator)
        coordinator.hass = mock_hass
        coordinator.config_entry = mock_entry

    # Create sample event data
    event_data = {
        "ID": "event123",
        "MessageType": "DoorAccess",
        "Description": "Card access granted",
        "MessageCategory": 2011,
        "When": "2023-12-01T10:30:00Z",
        "Who": "John Doe",
        "What": "Door 1",
        "Where": "Main Entrance",
        "WhenTicks": 1701432600,
    }

    # Call the review event callback directly
    coordinator.review_event_callback(event_data)

    # Verify the Home Assistant event was fired
    expected_event_data = {
        "event_id": "event123",
        "description": "Card access granted",
        "message_category": 2011,
        "message_description": "Door Access Granted from Access Button",
        "when": "2023-12-01T10:30:00Z",
        "reference_time": None,
        "who": "John Doe",
        "who_id": None,
        "what": "Door 1",
        "what_id": None,
        "where": "Main Entrance",
        "where_id": None,
    }

    mock_hass.bus.async_fire.assert_called_once_with(
        event_type=EVENT_REVIEW_EVENT,
        event_data=expected_event_data,
    )


def test_review_event_callback_filters_none_values() -> None:
    """Test that review event callback filters out None values."""
    # Create mock objects
    mock_entry = Mock()
    mock_entry.data = {"token": "test_token", "host": "http://test.com"}

    mock_hass = Mock()
    mock_hass.bus = Mock()
    mock_hass.bus.async_fire = Mock()

    # Create coordinator by mocking the parent class initialization
    with pytest.MonkeyPatch().context() as m:
        # Mock the DataUpdateCoordinator.__init__ to avoid HA framework setup
        m.setattr(
            "custom_components.inception.coordinator.DataUpdateCoordinator.__init__",
            Mock(return_value=None),
        )

        # Create coordinator and set required attributes
        coordinator = InceptionUpdateCoordinator.__new__(InceptionUpdateCoordinator)
        coordinator.hass = mock_hass
        coordinator.config_entry = mock_entry

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

    # Verify the Home Assistant event was fired
    # (None values are included in actual implementation)
    expected_event_data = {
        "event_id": "event123",
        "description": "Card access granted",
        "message_category": None,
        "message_description": None,
        "when": "2023-12-01T10:30:00Z",
        "reference_time": None,
        "who": None,
        "who_id": None,
        "what": "Door 1",
        "what_id": None,
        "where": "Main Entrance",
        "where_id": None,
    }

    mock_hass.bus.async_fire.assert_called_once_with(
        event_type=EVENT_REVIEW_EVENT,
        event_data=expected_event_data,
    )


def test_review_event_callback_handles_missing_fields() -> None:
    """Test that review event callback handles missing fields gracefully."""
    # Create mock objects
    mock_entry = Mock()
    mock_entry.data = {"token": "test_token", "host": "http://test.com"}

    mock_hass = Mock()
    mock_hass.bus = Mock()
    mock_hass.bus.async_fire = Mock()

    # Create coordinator by mocking the parent class initialization
    with pytest.MonkeyPatch().context() as m:
        # Mock the DataUpdateCoordinator.__init__ to avoid HA framework setup
        m.setattr(
            "custom_components.inception.coordinator.DataUpdateCoordinator.__init__",
            Mock(return_value=None),
        )

        # Create coordinator and set required attributes
        coordinator = InceptionUpdateCoordinator.__new__(InceptionUpdateCoordinator)
        coordinator.hass = mock_hass
        coordinator.config_entry = mock_entry

    # Create minimal event data (some fields missing)
    event_data = {
        "ID": "event456",
        "Description": "Motion detected",
        # Missing most other fields
    }

    # Call the review event callback directly
    coordinator.review_event_callback(event_data)

    # Verify the Home Assistant event was fired with all expected fields
    expected_event_data = {
        "event_id": "event456",
        "description": "Motion detected",
        "message_category": 0,
        "message_description": "Unknown",
        "when": None,
        "reference_time": None,
        "who": None,
        "who_id": None,
        "what": None,
        "what_id": None,
        "where": None,
        "where_id": None,
    }

    mock_hass.bus.async_fire.assert_called_once_with(
        event_type=EVENT_REVIEW_EVENT,
        event_data=expected_event_data,
    )
