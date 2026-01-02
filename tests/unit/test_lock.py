"""Test the Inception lock entity."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from homeassistant.components.lock import LockEntity, LockEntityDescription

from custom_components.inception.coordinator import InceptionUpdateCoordinator
from custom_components.inception.entity import InceptionEntity
from custom_components.inception.lock import (
    InceptionDoorEntityDescription,
    InceptionLock,
    async_setup_entry,
)
from custom_components.inception.pyinception.schemas.door import DoorPublicState

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from homeassistant.helpers.entity import Entity


class TestInceptionLock:
    """Test InceptionLock entity."""

    def test_lock_class_exists(self) -> None:
        """Test that lock class exists and has expected structure."""
        # Test that the class exists and has expected methods
        assert hasattr(InceptionLock, "__init__")
        assert hasattr(InceptionLock, "async_lock")
        assert hasattr(InceptionLock, "async_unlock")

        # Test that it's a proper class
        assert isinstance(InceptionLock, type)

    def test_lock_inheritance(self) -> None:
        """Test lock entity inheritance."""
        # Test inheritance
        assert issubclass(InceptionLock, LockEntity)
        assert issubclass(InceptionLock, InceptionEntity)

    def test_entity_description_class(self) -> None:
        """Test entity description class exists."""
        # Test that entity description exists and inherits properly
        assert hasattr(InceptionDoorEntityDescription, "__init__")
        assert issubclass(InceptionDoorEntityDescription, LockEntityDescription)


class TestLockEntityKeys:
    """Test lock entity key generation."""

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
    async def test_lock_entity_keys(
        self, mock_coordinator: Mock, mock_hass: Mock, mock_entry: Mock
    ) -> None:
        """Test that lock entities have expected keys."""
        # Create mock doors
        mock_door1 = Mock()
        mock_door1.entity_info = Mock()
        mock_door1.entity_info.id = "door_1"
        mock_door1.entity_info.name = "Front Door"
        mock_door1.public_state = DoorPublicState.OPEN

        mock_door2 = Mock()
        mock_door2.entity_info = Mock()
        mock_door2.entity_info.id = "door_2"
        mock_door2.entity_info.name = "Back Door"
        mock_door2.public_state = DoorPublicState.CLOSED

        mock_coordinator.data.doors.get_items = Mock(
            return_value=[mock_door1, mock_door2]
        )

        self.added_entities = []
        mock_hass.data = {"inception": {mock_entry.entry_id: mock_coordinator}}

        # Mock the entity_platform module
        with patch(
            "custom_components.inception.lock.entity_platform.async_get_current_platform"
        ) as mock_get_platform:
            mock_platform = Mock()
            mock_get_platform.return_value = mock_platform
            await async_setup_entry(mock_hass, mock_entry, self.mock_async_add_entities)

        # Verify lock keys
        assert len(self.added_entities) == 2
        keys = [entity._attr_unique_id for entity in self.added_entities]
        assert sorted(keys) == ["door_1_door_lock", "door_2_door_lock"]
