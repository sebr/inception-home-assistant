"""Test the Inception switch entity."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock

import pytest
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription

from custom_components.inception.coordinator import InceptionUpdateCoordinator
from custom_components.inception.entity import InceptionEntity
from custom_components.inception.pyinception.schemas.input import (
    InputPublicState,
    InputShortEntity,
    InputSummaryEntry,
    InputType,
)
from custom_components.inception.pyinception.schemas.output import OutputPublicState
from custom_components.inception.switch import (
    InceptionLogicalInputSwitch,
    InceptionSwitch,
    InceptionSwitchDescription,
    async_setup_entry,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from homeassistant.helpers.entity import Entity


class TestInceptionSwitch:
    """Test InceptionSwitch entity."""

    def test_switch_class_exists(self) -> None:
        """Test that switch class exists and has expected structure."""
        # Test that the class exists and has expected methods
        assert hasattr(InceptionSwitch, "__init__")
        assert hasattr(InceptionSwitch, "is_on")

        # Test that it's a proper class
        assert isinstance(InceptionSwitch, type)

    def test_switch_inheritance(self) -> None:
        """Test switch entity inheritance."""
        # Test inheritance
        assert issubclass(InceptionSwitch, SwitchEntity)
        assert issubclass(InceptionSwitch, InceptionEntity)

    def test_entity_description_class(self) -> None:
        """Test entity description class exists."""
        # Test that entity description exists and inherits properly
        assert hasattr(InceptionSwitchDescription, "__init__")
        assert issubclass(InceptionSwitchDescription, SwitchEntityDescription)

    def test_switch_unique_id_assignment(self) -> None:
        """Test that unique_id is assigned from entity_description.key."""
        # Create mock objects
        mock_coordinator = MagicMock()
        mock_coordinator.data = MagicMock()
        mock_coordinator.api = MagicMock()
        mock_coordinator.api._host = "test.example.com"

        # Create a mock InputSummaryEntry
        mock_input_data = MagicMock(spec=InputSummaryEntry)
        mock_input_data.entity_info = MagicMock()
        mock_input_data.entity_info.id = "input_123"
        mock_input_data.entity_info.name = "Test Input"
        mock_input_data.entity_info.reporting_id = "REP_123"
        mock_input_data.extra_fields = {}

        # Create entity description
        entity_description = InceptionSwitchDescription(
            key="test_unique_key_456",
            value_fn=lambda _data: True,
        )

        # Create the switch
        switch = InceptionSwitch(
            coordinator=mock_coordinator,
            entity_description=entity_description,
            data=mock_input_data,
        )

        # Assert that unique_id is set from entity_description.key
        assert switch.unique_id == "test_unique_key_456"


class TestInceptionLogicalInputSwitch:
    """Test InceptionLogicalInputSwitch entity."""

    def test_logical_input_switch_with_door(self) -> None:
        """Test InceptionLogicalInputSwitch groups with a door when provided."""
        # Create mock coordinator
        mock_coordinator = MagicMock()
        mock_coordinator.data = MagicMock()
        mock_coordinator.api = MagicMock()
        mock_coordinator.api._host = "test.example.com"

        # Create mock InputSummaryEntry with door pattern
        mock_input_data = MagicMock(spec=InputSummaryEntry)
        mock_input_data.entity_info = MagicMock()
        mock_input_data.entity_info.id = "input_456"
        mock_input_data.entity_info.name = "Front Door - Reed"
        mock_input_data.entity_info.reporting_id = "REP_456"
        mock_input_data.extra_fields = {}

        entity_description = InceptionSwitchDescription(
            key="input_456_isolated",
            value_fn=lambda _data: True,
        )

        # Create mock door
        mock_door = MagicMock()
        mock_door.entity_info = MagicMock()
        mock_door.entity_info.id = "door_789"
        mock_door.entity_info.name = "Front Door"

        # Create the switch WITH a door
        switch = InceptionLogicalInputSwitch(
            coordinator=mock_coordinator,
            entity_description=entity_description,
            data=mock_input_data,
            door=mock_door,
        )

        # Assert device_info is set to group with door device
        assert switch._attr_device_info is not None
        assert ("inception", "door_789") in switch._attr_device_info["identifiers"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        assert switch._attr_device_info["name"] == "Front Door"  # pyright: ignore[reportTypedDictNotRequiredAccess]

    def test_logical_input_switch_without_door(self) -> None:
        """Test InceptionLogicalInputSwitch creates its own device when no door is provided."""
        # Create mock coordinator
        mock_coordinator = MagicMock()
        mock_coordinator.data = MagicMock()
        mock_coordinator.api = MagicMock()
        mock_coordinator.api._host = "test.example.com"

        # Create mock InputSummaryEntry without door pattern
        mock_input_data = MagicMock(spec=InputSummaryEntry)
        mock_input_data.entity_info = MagicMock()
        mock_input_data.entity_info.id = "input_999"
        mock_input_data.entity_info.name = "Standalone Input"
        mock_input_data.entity_info.reporting_id = "REP_999"
        mock_input_data.entity_info.input_type = InputType.LOGICAL
        mock_input_data.extra_fields = {}

        entity_description = InceptionSwitchDescription(
            key="input_999_isolated",
            value_fn=lambda _data: True,
        )

        # Create the switch WITHOUT a door
        switch = InceptionLogicalInputSwitch(
            coordinator=mock_coordinator,
            entity_description=entity_description,
            data=mock_input_data,
            door=None,
        )

        # Assert device_info is set to its own device (from parent InceptionInputSwitch)
        assert switch._attr_device_info is not None
        assert ("inception", "input_999") in switch._attr_device_info["identifiers"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        assert switch._attr_device_info["name"] == "Standalone Input"  # pyright: ignore[reportTypedDictNotRequiredAccess]


class TestAsyncSetupEntry:
    """Test async_setup_entry for custom input switches."""

    @pytest.mark.asyncio
    async def test_custom_input_creates_active_switch(self) -> None:
        """Test that custom inputs create an 'Active' switch entity."""
        # Create mock hass and entry
        mock_hass = MagicMock()
        mock_entry = MagicMock()
        mock_entry.entry_id = "test_entry_123"

        # Create mock coordinator with custom input
        mock_coordinator = MagicMock()
        mock_coordinator.config_entry = mock_entry
        mock_coordinator.api = MagicMock()
        mock_coordinator.api._host = "test.example.com"

        # Create mock custom input
        mock_custom_input = MagicMock(spec=InputSummaryEntry)
        mock_custom_input.entity_info = MagicMock(spec=InputShortEntity)
        mock_custom_input.entity_info.id = "custom_input_001"
        mock_custom_input.entity_info.name = "Custom Input 1"
        mock_custom_input.entity_info.reporting_id = "CI_001"
        mock_custom_input.entity_info.input_type = InputType.LOGICAL
        mock_custom_input.entity_info.is_custom_input = True
        mock_custom_input.public_state = InputPublicState.ACTIVE
        mock_custom_input.extra_fields = {}

        # Create mock data
        mock_data = MagicMock()
        mock_data.inputs = MagicMock()
        mock_data.inputs.get_items = MagicMock(return_value=[mock_custom_input])
        mock_data.outputs = MagicMock()
        mock_data.outputs.get_items = MagicMock(return_value=[])
        mock_data.doors = MagicMock()
        mock_data.doors.get_items = MagicMock(return_value=[])

        mock_coordinator.data = mock_data

        # Set up hass.data
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Mock async_add_entities
        mock_async_add_entities = MagicMock()

        # Call async_setup_entry
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Verify async_add_entities was called
        assert mock_async_add_entities.called
        entities = mock_async_add_entities.call_args[0][0]

        # Find the "Active" switch in the created entities
        active_switches = [
            e
            for e in entities
            if hasattr(e, "entity_description")
            and e.entity_description.key == "custom_input_001_active"
        ]

        # Assert the Active switch was created
        assert len(active_switches) == 1
        active_switch = active_switches[0]

        # Verify the entity description properties
        assert active_switch.entity_description.name == "Active"
        assert active_switch.entity_description.has_entity_name is True
        assert active_switch.entity_description.entity_registry_visible_default is True

        # Verify turn_on_data and turn_off_data
        assert active_switch.entity_description.turn_on_data == {
            "Type": "ControlCustomInput",
            "CustomInputControlType": "Activate",
        }
        assert active_switch.entity_description.turn_off_data == {
            "Type": "ControlCustomInput",
            "CustomInputControlType": "Deactivate",
        }

    @pytest.mark.asyncio
    async def test_non_custom_input_no_active_switch(self) -> None:
        """Test that non-custom inputs do NOT create an 'Active' switch entity."""
        # Create mock hass and entry
        mock_hass = MagicMock()
        mock_entry = MagicMock()
        mock_entry.entry_id = "test_entry_456"

        # Create mock coordinator with regular input
        mock_coordinator = MagicMock()
        mock_coordinator.config_entry = mock_entry
        mock_coordinator.api = MagicMock()
        mock_coordinator.api._host = "test.example.com"

        # Create mock regular input (not custom)
        mock_regular_input = MagicMock(spec=InputSummaryEntry)
        mock_regular_input.entity_info = MagicMock(spec=InputShortEntity)
        mock_regular_input.entity_info.id = "regular_input_001"
        mock_regular_input.entity_info.name = "Regular Input"
        mock_regular_input.entity_info.reporting_id = "RI_001"
        mock_regular_input.entity_info.is_custom_input = False
        mock_regular_input.entity_info.input_type = InputType.LOGICAL
        mock_regular_input.public_state = InputPublicState.SEALED
        mock_regular_input.extra_fields = {}

        # Create mock data
        mock_data = MagicMock()
        mock_data.inputs = MagicMock()
        mock_data.inputs.get_items = MagicMock(return_value=[mock_regular_input])
        mock_data.outputs = MagicMock()
        mock_data.outputs.get_items = MagicMock(return_value=[])
        mock_data.doors = MagicMock()
        mock_data.doors.get_items = MagicMock(return_value=[])

        mock_coordinator.data = mock_data

        # Set up hass.data
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Mock async_add_entities
        mock_async_add_entities = MagicMock()

        # Call async_setup_entry
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Verify async_add_entities was called
        assert mock_async_add_entities.called
        entities = mock_async_add_entities.call_args[0][0]

        # Find the "Active" switch in the created entities
        active_switches = [
            e
            for e in entities
            if hasattr(e, "entity_description")
            and e.entity_description.key == "regular_input_001_active"
        ]

        # Assert the Active switch was NOT created for regular inputs
        assert len(active_switches) == 0

        # But the "Isolated" switch should still be created
        isolated_switches = [
            e
            for e in entities
            if hasattr(e, "entity_description")
            and e.entity_description.key == "regular_input_001_isolated"
        ]
        assert len(isolated_switches) == 1

    @pytest.mark.asyncio
    async def test_isolated_switch_uses_logical_input_switch_class(self) -> None:
        """Test that all isolated switches use InceptionLogicalInputSwitch class."""
        # Create mock hass and entry
        mock_hass = MagicMock()
        mock_entry = MagicMock()
        mock_entry.entry_id = "test_entry_789"

        # Create mock coordinator
        mock_coordinator = MagicMock()
        mock_coordinator.config_entry = mock_entry
        mock_coordinator.api = MagicMock()
        mock_coordinator.api._host = "test.example.com"

        # Create mock input
        mock_input = MagicMock(spec=InputSummaryEntry)
        mock_input.entity_info = MagicMock(spec=InputShortEntity)
        mock_input.entity_info.id = "input_test"
        mock_input.entity_info.name = "Test Input"
        mock_input.entity_info.reporting_id = "TI_001"
        mock_input.entity_info.is_custom_input = False
        mock_input.entity_info.input_type = InputType.LOGICAL
        mock_input.public_state = InputPublicState.SEALED
        mock_input.extra_fields = {}

        # Create mock data
        mock_data = MagicMock()
        mock_data.inputs = MagicMock()
        mock_data.inputs.get_items = MagicMock(return_value=[mock_input])
        mock_data.outputs = MagicMock()
        mock_data.outputs.get_items = MagicMock(return_value=[])
        mock_data.doors = MagicMock()
        mock_data.doors.get_items = MagicMock(return_value=[])

        mock_coordinator.data = mock_data

        # Set up hass.data
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Mock async_add_entities
        mock_async_add_entities = MagicMock()

        # Call async_setup_entry
        await async_setup_entry(mock_hass, mock_entry, mock_async_add_entities)

        # Verify async_add_entities was called
        assert mock_async_add_entities.called
        entities = mock_async_add_entities.call_args[0][0]

        # Find the isolated switch
        isolated_switches = [
            e
            for e in entities
            if hasattr(e, "entity_description")
            and e.entity_description.key == "input_test_isolated"
        ]

        assert len(isolated_switches) == 1
        isolated_switch = isolated_switches[0]

        # Verify it's an instance of InceptionLogicalInputSwitch
        assert isinstance(isolated_switch, InceptionLogicalInputSwitch)


class TestSwitchEntityKeys:
    """Test switch entity key generation."""

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
    async def test_switch_output_keys(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that output switch entities have expected keys."""
        mock_output = Mock()
        mock_output.entity_info = Mock()
        mock_output.entity_info.id = "output_1"
        mock_output.entity_info.name = "Siren"
        mock_output.public_state = OutputPublicState.ON

        mock_coordinator.data.outputs.get_items = Mock(return_value=[mock_output])
        mock_coordinator.review_events_global_enabled = False

        self.added_entities = []
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        await async_setup_entry(mock_hass, mock_entry, self.mock_async_add_entities)

        # Find output switch (exclude review event switches)
        output_switches = [
            e for e in self.added_entities if hasattr(e, "entity_description")
        ]
        output_switch_keys = [
            e.entity_description.key
            for e in output_switches
            if not e.entity_description.key.startswith("review_")
        ]

        assert "output_1" in output_switch_keys

    @pytest.mark.asyncio
    async def test_switch_input_isolated_keys(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that input isolated switch entities have expected keys."""
        mock_input = Mock()
        mock_input.entity_info = Mock()
        mock_input.entity_info.id = "input_1"
        mock_input.entity_info.name = "PIR Sensor"
        mock_input.entity_info.is_custom_input = False
        mock_input.public_state = InputPublicState.ACTIVE

        mock_coordinator.data.inputs.get_items = Mock(return_value=[mock_input])
        mock_coordinator.review_events_global_enabled = False

        self.added_entities = []
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        await async_setup_entry(mock_hass, mock_entry, self.mock_async_add_entities)

        # Find isolated switch
        isolated_switches = [
            e
            for e in self.added_entities
            if hasattr(e, "entity_description")
            and e.entity_description.key.endswith("_isolated")
        ]

        assert len(isolated_switches) == 1
        assert isolated_switches[0].entity_description.key == "input_1_isolated"

    @pytest.mark.asyncio
    async def test_switch_custom_input_active_keys(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that custom input active switch entities have expected keys."""
        mock_custom_input = Mock()
        mock_custom_input.entity_info = Mock()
        mock_custom_input.entity_info.id = "custom_input_1"
        mock_custom_input.entity_info.name = "Custom Trigger"
        mock_custom_input.entity_info.is_custom_input = True
        mock_custom_input.public_state = InputPublicState.ACTIVE

        mock_coordinator.data.inputs.get_items = Mock(return_value=[mock_custom_input])
        mock_coordinator.review_events_global_enabled = False

        self.added_entities = []
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        await async_setup_entry(mock_hass, mock_entry, self.mock_async_add_entities)

        # Find active switch
        active_switches = [
            e
            for e in self.added_entities
            if hasattr(e, "entity_description")
            and e.entity_description.key.endswith("_active")
        ]

        assert len(active_switches) == 1
        assert active_switches[0].entity_description.key == "custom_input_1_active"

        # Also verify isolated switch exists
        isolated_switches = [
            e
            for e in self.added_entities
            if hasattr(e, "entity_description")
            and e.entity_description.key.endswith("_isolated")
        ]
        assert len(isolated_switches) == 1
        assert isolated_switches[0].entity_description.key == "custom_input_1_isolated"
