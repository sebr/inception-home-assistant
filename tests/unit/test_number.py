"""Test the Inception number entity."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from custom_components.inception.coordinator import InceptionUpdateCoordinator
from custom_components.inception.number import async_setup_entry as number_setup
from custom_components.inception.pyinception.schemas.door import DoorPublicState
from custom_components.inception.select import async_setup_entry as select_setup

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from homeassistant.helpers.entity import Entity


class TestNumberEntityKeys:
    """Test number entity key generation."""

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
    async def test_number_entity_keys(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that number entities have expected keys."""
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_123"
        mock_door.entity_info.name = "Main Door"

        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])

        self.added_entities = []
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        await number_setup(mock_hass, mock_entry, self.mock_async_add_entities)

        # Verify number entity key (timed unlock duration)
        assert len(self.added_entities) == 1
        assert (
            self.added_entities[0].entity_description.key
            == "door_123_timed_unlock_time"
        )

    @pytest.mark.asyncio
    async def test_door_entities_consistent_id_prefix(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that all door-related entities share the same ID prefix."""
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_test"
        mock_door.entity_info.name = "Test Door"
        mock_door.public_state = DoorPublicState.OPEN

        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Test number
        self.added_entities = []
        await number_setup(mock_hass, mock_entry, self.mock_async_add_entities)
        assert self.added_entities[0].entity_description.key.startswith("door_test")
        assert "timed_unlock_time" in self.added_entities[0].entity_description.key

        # Test select
        self.added_entities = []
        await select_setup(mock_hass, mock_entry, self.mock_async_add_entities)
        assert self.added_entities[0].entity_description.key.startswith("door_test")
        assert "unlock_mechanism" in self.added_entities[0].entity_description.key
