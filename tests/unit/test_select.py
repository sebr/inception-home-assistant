"""Test the Inception select entity."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from custom_components.inception.coordinator import InceptionUpdateCoordinator
from custom_components.inception.select import async_setup_entry

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from homeassistant.helpers.entity import Entity


class TestSelectEntityKeys:
    """Test select entity key generation."""

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
    async def test_select_entity_keys(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that select entities have expected keys."""
        mock_door = Mock()
        mock_door.entity_info = Mock()
        mock_door.entity_info.id = "door_456"
        mock_door.entity_info.name = "Side Door"

        mock_coordinator.data.doors.get_items = Mock(return_value=[mock_door])

        self.added_entities = []
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        await async_setup_entry(mock_hass, mock_entry, self.mock_async_add_entities)

        # Verify select entity key (unlock strategy)
        assert len(self.added_entities) == 1
        assert (
            self.added_entities[0]._attr_unique_id == "door_456_door_unlock_mechanism"
        )
