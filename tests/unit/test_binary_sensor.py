"""Test the binary_sensor platform."""

from collections.abc import Iterable
from unittest.mock import Mock

import pytest
from homeassistant.helpers.entity import Entity

from custom_components.inception.binary_sensor import async_setup_entry
from custom_components.inception.coordinator import InceptionUpdateCoordinator
from custom_components.inception.pyinception.schemas.door import DoorPublicState
from custom_components.inception.pyinception.schemas.input import InputPublicState


class TestBinarySensorKeys:
    """Test binary sensor entity key generation."""

    @pytest.fixture
    def mock_coordinator(self) -> Mock:
        """Create a mock coordinator."""
        coordinator = Mock(spec=InceptionUpdateCoordinator)

        # Mock config_entry
        coordinator.config_entry = Mock()
        coordinator.config_entry.entry_id = "test_entry_id"

        # Mock api
        coordinator.api = Mock()
        coordinator.api._host = "test.example.com"

        # Mock data
        coordinator.data = Mock()
        coordinator.data.inputs = Mock()
        coordinator.data.inputs.get_items = Mock(return_value=[])

        return coordinator

    @pytest.fixture
    def mock_hass(self) -> Mock:
        """Create a mock Home Assistant instance."""
        hass = Mock()
        hass.data = {}
        return hass

    @pytest.fixture
    def mock_entry(self) -> Mock:
        """Create a mock config entry."""
        entry = Mock()
        entry.entry_id = "test_entry_id"
        return entry

    @pytest.mark.asyncio
    async def test_door_binary_sensor_keys(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that door binary sensors have expected keys."""
        # Create a mock door
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_123"
        mock_door.entity_info.name = "Front Door"
        mock_door.entity_info.reporting_id = "1"
        mock_door.public_state = DoorPublicState.OPEN

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])

        # Mock async_add_entities
        added_entities = []

        def mock_async_add_entities(
            new_entities: Iterable[Entity],
            update_before_add: bool = False,  # noqa: FBT001, FBT002, ARG001
        ) -> None:
            added_entities.extend(new_entities)

        # Set up HASS data
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Call async_setup_entry
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Verify the expected keys were created
        # Should have 4 binary sensors for each door state
        assert len(added_entities) == 4

        # Keys are formatted as {door_id}_{key_suffix}
        expected_keys = [
            "door_123_8",  # FORCED = 0x008
            "door_123_32",  # Door Open Too Long
            "door_123_2",
            "door_123_128",
        ]

        actual_keys = [entity.entity_description.key for entity in added_entities]
        assert sorted(actual_keys) == sorted(expected_keys)

    @pytest.mark.asyncio
    async def test_door_binary_sensor_names(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that door binary sensors have human-readable names."""
        # Create a mock door
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_456"
        mock_door.entity_info.name = "Back Door"
        mock_door.entity_info.reporting_id = "2"
        mock_door.public_state = DoorPublicState.OPEN

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])

        # Mock async_add_entities
        added_entities = []

        def mock_async_add_entities(
            new_entities: Iterable[Entity],
            update_before_add: bool = False,  # noqa: FBT001, FBT002, ARG001
        ) -> None:
            added_entities.extend(new_entities)

        # Set up HASS data
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Call async_setup_entry
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Verify the expected human-readable names
        assert len(added_entities) == 4

        # Create a mapping of keys to expected names
        expected_names = {
            "door_456_8": "Forced",
            "door_456_32": "Held open too long",
            "door_456_2": "Sensor",
            "door_456_128": "Reader tamper",
        }

        for entity in added_entities:
            key = entity.entity_description.key
            expected_name = expected_names[key]
            actual_name = entity.entity_description.name
            assert actual_name == expected_name, (
                f"Expected '{expected_name}' for '{key}', got '{actual_name}'"
            )

    @pytest.mark.asyncio
    async def test_regular_input_binary_sensor_key(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that regular input binary sensors have expected keys."""
        # Create a mock regular input
        mock_input = Mock()
        mock_input.entity_info = Mock()
        mock_input.entity_info.id = "input_789"
        mock_input.entity_info.name = "Motion Sensor"
        mock_input.entity_info.reporting_id = "3"
        mock_input.entity_info.is_custom_input = False
        mock_input.public_state = InputPublicState.ACTIVE

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(return_value=[])
        mock_coordinator.data.inputs.get_items = Mock(return_value=[mock_input])

        # Mock async_add_entities
        added_entities = []

        def mock_async_add_entities(
            new_entities: Iterable[Entity],
            update_before_add: bool = False,  # noqa: FBT001, FBT002, ARG001
        ) -> None:
            added_entities.extend(new_entities)

        # Set up HASS data
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Call async_setup_entry
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Verify one binary sensor was created with the input's ID as the key
        assert len(added_entities) == 1
        assert added_entities[0].entity_description.key == "input_789"

    @pytest.mark.asyncio
    async def test_custom_input_no_binary_sensor(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that custom inputs do not create binary sensors."""
        # Create a mock custom input
        mock_custom_input = Mock()
        mock_custom_input.entity_info = Mock()
        mock_custom_input.entity_info.id = "custom_input_100"
        mock_custom_input.entity_info.name = "Custom Logical Input"
        mock_custom_input.entity_info.reporting_id = "4"
        mock_custom_input.entity_info.is_custom_input = True
        mock_custom_input.public_state = InputPublicState.ACTIVE

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(return_value=[])
        mock_coordinator.data.inputs.get_items = Mock(return_value=[mock_custom_input])

        # Mock async_add_entities
        added_entities = []

        def mock_async_add_entities(
            new_entities: Iterable[Entity],
            update_before_add: bool = False,  # noqa: FBT001, FBT002, ARG001
        ) -> None:
            added_entities.extend(new_entities)

        # Set up HASS data
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Call async_setup_entry
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Verify no binary sensors were created for custom inputs
        assert len(added_entities) == 0

    @pytest.mark.asyncio
    async def test_multiple_doors_create_multiple_sensors(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that multiple doors create the correct number of binary sensors."""
        # Create two mock doors
        mock_door1 = Mock()
        mock_door1.entity_info = Mock()
        mock_door1.entity_info.id = "door_1"
        mock_door1.entity_info.name = "Door 1"
        mock_door1.entity_info.reporting_id = "1"
        mock_door1.public_state = DoorPublicState.OPEN

        mock_door2 = Mock()
        mock_door2.entity_info = Mock()
        mock_door2.entity_info.id = "door_2"
        mock_door2.entity_info.name = "Door 2"
        mock_door2.entity_info.reporting_id = "2"
        mock_door2.public_state = DoorPublicState.FORCED

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(
            return_value=[mock_door1, mock_door2]
        )

        # Mock async_add_entities
        added_entities = []

        def mock_async_add_entities(
            new_entities: Iterable[Entity],
            update_before_add: bool = False,  # noqa: FBT001, FBT002, ARG001
        ) -> None:
            added_entities.extend(new_entities)

        # Set up HASS data
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Call async_setup_entry
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Verify 8 binary sensors were created (4 states x 2 doors)
        assert len(added_entities) == 8

        # Verify keys for door 1
        door1_keys = [
            e.entity_description.key
            for e in added_entities
            if "door_1_" in e.entity_description.key
        ]
        assert len(door1_keys) == 4

        # Verify keys for door 2
        door2_keys = [
            e.entity_description.key
            for e in added_entities
            if "door_2_" in e.entity_description.key
        ]
        assert len(door2_keys) == 4
