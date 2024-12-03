"""Binary sensor platform for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.lock import (
    LockEntity,
    LockEntityDescription,
    LockEntityFeature,
)

from .const import DOMAIN
from .entity import InceptionEntity
from .pyinception.states_schema import DoorPublicStates

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schema import Door


@dataclass(frozen=True, kw_only=True)
class InceptionDoorEntityDescription(LockEntityDescription):
    """Describes Inception binary sensor entity."""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[InceptionLock] = [
        InceptionLock(
            coordinator=coordinator,
            entity_description=InceptionDoorEntityDescription(
                key=door.ID,
            ),
            data=door,
        )
        for door in coordinator.data.doors.values()
    ]

    async_add_entities(entities)


class InceptionLock(InceptionEntity, LockEntity):
    """inception binary_sensor class."""

    entity_description: InceptionDoorEntityDescription
    data: Door

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionDoorEntityDescription,
        data: Door,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(
            coordinator, description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description
        self.unique_id = data.ID
        self.reportingId = data.ReportingID

        # TODO(sebr): Check lock support
        self._attr_supported_features = LockEntityFeature.OPEN

    @property
    def is_locked(self) -> bool | None:
        """Return true if device is locked."""
        if self.data.PublicState is None:
            return None
        return bool(self.data.PublicState & DoorPublicStates.LOCKED)

    async def _door_control(self, data: Any | None = None) -> None:
        """Control the door."""
        return await self.coordinator.api.request(
            method="post", path=f"/control/door/{self.data.ID}/activity", data=data
        )

    async def async_lock(self) -> None:
        """Lock the device."""
        return await self._door_control(
            data={
                "Type": "ControlDoor",
                "DoorControlType": "Lock",
            },
        )

    async def async_unlock(self) -> None:
        """Unlock the device."""
        return await self._door_control(
            data={
                "Type": "ControlDoor",
                "DoorControlType": "Unlock",
            },
        )

    async def async_open(self) -> None:
        """Unlock the device."""
        return await self._door_control(
            data={
                "Type": "ControlDoor",
                "DoorControlType": "Open",
            },
        )
