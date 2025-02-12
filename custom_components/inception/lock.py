"""Binary sensor platform for inception."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.components.lock import (
    LockEntity,
    LockEntityDescription,
)
from homeassistant.helpers import entity_platform
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MANUFACTURER
from .entity import InceptionEntity
from .pyinception.schemas.door import (
    DoorControlType,
    DoorPublicState,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schemas.door import DoorSummaryEntry

SERVICE_UNLOCK = "unlock"


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
                key=door.entity_info.id, name="Lock"
            ),
            data=door,
        )
        for door in coordinator.data.doors.get_items()
    ]

    async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_UNLOCK,
        {
            vol.Optional("time_secs"): vol.All(
                vol.Coerce(int), vol.Range(min=0, max=86399)
            ),
        },
        "unlock_service",
    )


class InceptionLock(InceptionEntity, LockEntity):
    """inception binary_sensor class."""

    entity_description: InceptionDoorEntityDescription
    data: DoorSummaryEntry

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionDoorEntityDescription,
        data: DoorSummaryEntry,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description
        self.unique_id = data.entity_info.id
        self.reporting_id = data.entity_info.reporting_id
        self._device_id = data.entity_info.id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=re.sub(
                r"[^a-zA-Z\s]*(Lock|Strike)", "", data.entity_info.name
            ).strip(),
            manufacturer=MANUFACTURER,
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "Lock"

    @property
    def is_locked(self) -> bool | None:
        """Return true if device is locked."""
        if self.data.public_state is None:
            return None
        return bool(self.data.public_state & DoorPublicState.LOCKED)

    async def _door_control(self, data: Any | None = None) -> None:
        """Control the door."""
        return await self.coordinator.api.request(
            method="post",
            path=f"/control/door/{self.data.entity_info.id}/activity",
            data=data,
        )

    async def async_lock(self) -> None:
        """Lock the device."""
        return await self._door_control(
            data={
                "Type": "ControlDoor",
                "DoorControlType": DoorControlType.LOCK,
            },
        )

    async def async_unlock(self) -> None:
        """Unlock the device."""
        return await self._door_control(
            data={
                "Type": "ControlDoor",
                "DoorControlType": DoorControlType.UNLOCK,  # Unlock is a permanent open
            },
        )

    async def unlock_service(self, time_secs: int | None) -> None:
        """Unlock the device. If a time is provided, the device will issue a timed unlock."""  # noqa: E501
        if time_secs is None:
            return await self._door_control(
                data={
                    "Type": "ControlDoor",
                    "DoorControlType": DoorControlType.UNLOCK,
                },
            )

        return await self._door_control(
            data={
                "Type": "ControlDoor",
                "DoorControlType": DoorControlType.TIMED_UNLOCK,
                "TimeSecs": time_secs,
            },
        )
