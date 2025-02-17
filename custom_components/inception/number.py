"""Binary sensor platform for inception."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
    RestoreNumber,
)
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MANUFACTURER
from .entity import InceptionEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schemas.door import (
        DoorSummaryEntry,
    )
    from .pyinception.schemas.entities import (
        InceptionSummaryEntry,
    )

_LOGGER = logging.getLogger(__name__)
DEFAULT_TIMED_UNLOCK_DURATION = 5


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        InceptionTimedUnlockNumber(
            coordinator=coordinator,
            entity_description=InceptionNumberDescription(
                key=f"{door.entity_info.id}_timed_unlock_time",
                name="Timed Unlock Duration",
                entity_category=EntityCategory.CONFIG,
                translation_key="timed_unlock_duration",
                device_class=NumberDeviceClass.DURATION,
                native_unit_of_measurement="s",
                native_step=1,
                mode=NumberMode.BOX,
            ),
            data=door,
        )
        for door in coordinator.data.doors.get_items()
    ]

    async_add_entities(entities)


@dataclass(frozen=True, kw_only=True)
class InceptionNumberDescription(NumberEntityDescription):
    """Describes Inception number entity."""


class InceptionNumber(InceptionEntity, NumberEntity):
    """inception number class."""

    data: InceptionSummaryEntry

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: NumberEntityDescription,
        data: InceptionSummaryEntry,
    ) -> None:
        """Initialize the number class."""
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )
        self.data = data
        self.unique_id = entity_description.key
        self._device_id = data.entity_info.id


class InceptionTimedUnlockNumber(
    InceptionNumber,
    RestoreNumber,
):
    """inception select for Doors."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    entity_description: InceptionNumberDescription

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionNumberDescription,
        data: DoorSummaryEntry,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.entity_info.id)},
            manufacturer=MANUFACTURER,
        )
        self.entity_description = entity_description
        self._attr_current_option = None
        self._attr_native_min_value = 1
        self._attr_extra_state_attributes = {
            "type": "timed_unlock_duration",
        }

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "Timed Unlock Duration"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()
        if (
            (last_state := await self.async_get_last_state())
            and (last_number_data := await self.async_get_last_number_data())
            and last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE)
        ):
            self._attr_native_value = last_number_data.native_value
        else:
            self._attr_native_value = DEFAULT_TIMED_UNLOCK_DURATION
