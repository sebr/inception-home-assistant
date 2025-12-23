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
            "door_123_forced",
            "door_123_dotl",
            "door_123_open",
            "door_123_tamper",
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
            "door_456_forced": "Forced",
            "door_456_dotl": "Held open too long",
            "door_456_open": "Sensor",
            "door_456_tamper": "Reader tamper",
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
        assert added_entities[0].entity_description.key == "input_789_sensor"

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

    @pytest.mark.asyncio
    async def test_input_matching_door_creates_sensor_with_suffix(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that inputs matching a door create sensors with the correct suffix."""
        # Create a mock door
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_123"
        mock_door.entity_info.name = "Front Door"
        mock_door.entity_info.reporting_id = "1"
        mock_door.public_state = DoorPublicState.OPEN

        # Create a mock input that matches the door with " - " separator
        mock_input = Mock()
        mock_input.entity_info = Mock()
        mock_input.entity_info.id = "input_456"
        mock_input.entity_info.name = "Front Door - Reed"
        mock_input.entity_info.reporting_id = "2"
        mock_input.entity_info.is_custom_input = False
        mock_input.public_state = InputPublicState.ACTIVE

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])
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

        # Should have 4 door sensors + 1 input sensor
        assert len(added_entities) == 5

        # Find the input sensor
        input_sensors = [
            e
            for e in added_entities
            if hasattr(e, "entity_description")
            and e.entity_description.key.startswith("input_")
        ]

        assert len(input_sensors) == 1
        input_sensor = input_sensors[0]

        # Verify the key uses the suffix
        assert input_sensor.entity_description.key == "input_456_reed"
        # Verify the name is the suffix
        assert input_sensor.entity_description.name == "Reed"

    @pytest.mark.asyncio
    async def test_input_matching_door_grouped_with_door_device(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that input sensors matching a door are grouped with the door device."""
        # Create a mock door
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_789"
        mock_door.entity_info.name = "Back Door"
        mock_door.entity_info.reporting_id = "3"
        mock_door.public_state = DoorPublicState.CLOSED

        # Create a mock input that matches the door with space separator
        mock_input = Mock()
        mock_input.entity_info = Mock()
        mock_input.entity_info.id = "input_999"
        mock_input.entity_info.name = "Back Door Reed"
        mock_input.entity_info.reporting_id = "4"
        mock_input.entity_info.is_custom_input = False
        mock_input.public_state = InputPublicState.SEALED

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])
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

        # Find the input sensor
        input_sensors = [
            e
            for e in added_entities
            if hasattr(e, "entity_description")
            and e.entity_description.key.startswith("input_")
        ]

        assert len(input_sensors) == 1
        input_sensor = input_sensors[0]

        # Verify it's grouped with the door device
        assert input_sensor._attr_device_info is not None
        assert ("inception", "door_789") in input_sensor._attr_device_info[
            "identifiers"
        ]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        assert input_sensor._attr_device_info["name"] == "Back Door"  # pyright: ignore[reportTypedDictNotRequiredAccess]

    @pytest.mark.asyncio
    async def test_input_matching_door_with_dash_separator(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test input matching door with dash separator creates correct key."""
        # Create a mock door
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_abc"
        mock_door.entity_info.name = "Side Door"
        mock_door.entity_info.reporting_id = "5"
        mock_door.public_state = DoorPublicState.OPEN

        # Create a mock input with " - " separator
        mock_input = Mock()
        mock_input.entity_info = Mock()
        mock_input.entity_info.id = "input_xyz"
        mock_input.entity_info.name = "Side Door - Contact"
        mock_input.entity_info.reporting_id = "6"
        mock_input.entity_info.is_custom_input = False
        mock_input.public_state = InputPublicState.ACTIVE

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])
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

        # Find the input sensor
        input_sensors = [
            e
            for e in added_entities
            if hasattr(e, "entity_description")
            and e.entity_description.key.startswith("input_")
        ]

        assert len(input_sensors) == 1
        # Verify key format: input_id_suffix
        assert input_sensors[0].entity_description.key == "input_xyz_contact"
        # Verify name is the suffix
        assert input_sensors[0].entity_description.name == "Contact"

    @pytest.mark.asyncio
    async def test_input_not_matching_door_creates_standalone_sensor(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that inputs not matching any door create standalone sensors."""
        # Create a mock door
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_111"
        mock_door.entity_info.name = "Main Door"
        mock_door.entity_info.reporting_id = "7"
        mock_door.public_state = DoorPublicState.OPEN

        # Create a mock input that does NOT match the door
        mock_input = Mock()
        mock_input.entity_info = Mock()
        mock_input.entity_info.id = "input_222"
        mock_input.entity_info.name = "PIR Motion Sensor"
        mock_input.entity_info.reporting_id = "8"
        mock_input.entity_info.is_custom_input = False
        mock_input.public_state = InputPublicState.ACTIVE

        # Set up coordinator data
        mock_coordinator.data.doors = Mock()
        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])
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

        # Find the input sensor
        input_sensors = [
            e
            for e in added_entities
            if hasattr(e, "entity_description")
            and e.entity_description.key.startswith("input_")
        ]

        assert len(input_sensors) == 1
        input_sensor = input_sensors[0]

        # Verify key format for standalone sensor: input_id_sensor
        assert input_sensor.entity_description.key == "input_222_sensor"
        # Verify name is "Sensor" for standalone
        assert input_sensor.entity_description.name == "Sensor"

        # Verify it has its own device (not grouped with door)
        assert input_sensor._attr_device_info is not None
        assert ("inception", "input_222") in input_sensor._attr_device_info[
            "identifiers"
        ]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        assert input_sensor._attr_device_info["name"] == "PIR Motion Sensor"  # pyright: ignore[reportTypedDictNotRequiredAccess]
