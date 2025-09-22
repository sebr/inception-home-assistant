"""Test the sensor platform."""

from unittest.mock import Mock

import pytest
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import EntityCategory

from custom_components.inception.coordinator import InceptionUpdateCoordinator
from custom_components.inception.sensor import InceptionLastReviewEventSensor


class TestInceptionLastReviewEventSensor:
    """Test the InceptionLastReviewEventSensor."""

    @pytest.fixture
    def mock_coordinator(self) -> Mock:
        """Create a mock coordinator."""
        coordinator = Mock(spec=InceptionUpdateCoordinator)
        coordinator.review_events_global_enabled = False

        # Mock config_entry
        coordinator.config_entry = Mock()
        coordinator.config_entry.entry_id = "test_entry_id"

        # Mock hass
        coordinator.hass = Mock()
        coordinator.hass.bus = Mock()
        coordinator.hass.bus.async_listen = Mock()

        return coordinator

    @pytest.fixture
    def sensor(self, mock_coordinator: Mock) -> InceptionLastReviewEventSensor:
        """Create a sensor instance."""
        entity_description = SensorEntityDescription(
            key="last_review_event",
            name="Last Review Event",
            entity_category=EntityCategory.DIAGNOSTIC,
            icon="mdi:security",
        )
        sensor = InceptionLastReviewEventSensor(
            coordinator=mock_coordinator,
            entity_description=entity_description,
        )
        # Mock the async_on_remove method and async_write_ha_state
        sensor.async_on_remove = Mock()
        sensor.async_write_ha_state = Mock()
        return sensor

    def test_initial_state(self, sensor: InceptionLastReviewEventSensor) -> None:
        """Test the sensor starts with no value."""
        assert sensor.native_value is None
        assert sensor.extra_state_attributes is None

    def test_entity_registry_enabled_default_when_disabled(
        self, sensor: InceptionLastReviewEventSensor, mock_coordinator: Mock
    ) -> None:
        """Test sensor registry enabled default when review events are disabled."""
        mock_coordinator.review_events_global_enabled = False
        assert not sensor.entity_registry_enabled_default

    def test_entity_registry_enabled_default_when_enabled(
        self, sensor: InceptionLastReviewEventSensor, mock_coordinator: Mock
    ) -> None:
        """Test sensor registry enabled default when review events are enabled."""
        mock_coordinator.review_events_global_enabled = True
        assert sensor.entity_registry_enabled_default

    def test_handle_review_event(self, sensor: InceptionLastReviewEventSensor) -> None:
        """Test handling a review event."""
        # Create a mock event
        event = Mock()
        event.data = {
            "event_id": "123",
            "description": "Test event",
            "message_value": 1000,
            "message_category": "Access",
            "message_description": "Card Access Granted",
            "when": "2023-01-01T12:00:00Z",
            "reference_time": "2023-01-01T12:00:00Z",
            "who": "John Doe",
            "who_id": "456",
            "what": "Card 123",
            "what_id": "789",
            "where": "Front Door",
            "where_id": "101",
        }

        # Handle the event
        sensor._handle_review_event(event)

        # Check the sensor state
        assert sensor.native_value == "Card Access Granted"
        assert sensor.extra_state_attributes == {
            "event_id": "123",
            "description": "Test event",
            "message_value": 1000,
            "message_category": "Access",
            "when": "2023-01-01T12:00:00Z",
            "reference_time": "2023-01-01T12:00:00Z",
            "who": "John Doe",
            "who_id": "456",
            "what": "Card 123",
            "what_id": "789",
            "where": "Front Door",
            "where_id": "101",
        }

    def test_handle_review_event_unknown_message(
        self, sensor: InceptionLastReviewEventSensor
    ) -> None:
        """Test handling a review event with unknown message."""
        # Create a mock event with unknown message
        event = Mock()
        event.data = {
            "event_id": "123",
            "description": "Test event",
            "message_value": 9999,
            "message_category": "Unknown",
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

        # Handle the event
        sensor._handle_review_event(event)

        # Check the sensor state shows unknown
        assert sensor.native_value == "Unknown"

        # Check all attributes are present
        attributes = sensor.extra_state_attributes
        assert attributes is not None
        assert attributes["message_category"] == "Unknown"
