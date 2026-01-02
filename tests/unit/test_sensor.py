"""Test the sensor platform."""

from collections.abc import Iterable
from pathlib import Path
from unittest.mock import Mock

import pytest
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import Entity

from custom_components.inception.coordinator import InceptionUpdateCoordinator
from custom_components.inception.sensor import (
    InceptionLastReviewEventSensor,
    async_setup_entry,
)


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


class TestSensorEntityKeys:
    """Test sensor entity key generation."""

    @pytest.fixture
    def mock_coordinator(self, mock_hass: Mock) -> Mock:
        """Create a mock coordinator."""
        coordinator = Mock(spec=InceptionUpdateCoordinator)
        coordinator.config_entry = Mock()
        coordinator.config_entry.entry_id = "test_entry_id"
        coordinator.api = Mock()
        coordinator.api._host = "test.example.com"
        coordinator.data = Mock()
        coordinator.hass = mock_hass

        # Initialize all entity collections as empty
        coordinator.data.doors = Mock()
        coordinator.data.doors.get_items = Mock(return_value=[])
        coordinator.data.inputs = Mock()
        coordinator.data.inputs.get_items = Mock(return_value=[])
        coordinator.data.outputs = Mock()
        coordinator.data.outputs.get_items = Mock(return_value=[])
        coordinator.data.areas = Mock()
        coordinator.data.areas.get_items = Mock(return_value=[])

        coordinator.review_events_global_enabled = False

        return coordinator

    @pytest.fixture
    def mock_hass(self, tmp_path: Path) -> Mock:
        """Create a mock Home Assistant instance."""
        hass = Mock()
        hass.data = {}
        hass.bus = Mock()
        hass.bus.async_listen = Mock()
        hass.config = Mock()
        hass.config.config_dir = str(tmp_path)
        return hass

    @pytest.fixture
    def mock_entry(self) -> Mock:
        """Create a mock config entry."""
        entry = Mock()
        entry.entry_id = "test_entry_id"
        return entry

    def mock_async_add_entities(
        self,
        new_entities: Iterable[Entity],
        update_before_add: bool = False,  # noqa: FBT001, FBT002, ARG002
    ) -> None:
        """Mock entity addition callback."""
        self.added_entities.extend(new_entities)

    @pytest.mark.asyncio
    async def test_sensor_entity_keys(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that sensor entities have expected keys."""
        mock_coordinator.review_events_global_enabled = False

        self.added_entities = []
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        await async_setup_entry(mock_hass, mock_entry, self.mock_async_add_entities)

        # Verify sensor key (last review event)
        assert len(self.added_entities) == 1
        assert (
            self.added_entities[0]._attr_unique_id == "test_entry_id_last_review_event"
        )
