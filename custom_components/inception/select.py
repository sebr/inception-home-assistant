"""Binary sensor platform for inception."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity

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

# Define possible unlock strategies and their descriptions
GRANT_ACCESS = "grant_access"
UNLOCK = "unlock"


DEFAULT_UNLOCK_STRATEGY = UNLOCK

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        InceptionUnlockStrategySelect(
            coordinator=coordinator,
            entity_description=InceptionSelectDescription(
                key=f"{door.entity_info.id}_unlock_mechanism",
                name="Unlock Strategy",
                options=[UNLOCK, GRANT_ACCESS],
                entity_category=EntityCategory.CONFIG,
                translation_key="unlock_strategy",
            ),
            data=door,
        )
        for door in coordinator.data.doors.get_items()
    ]

    async_add_entities(entities)


@dataclass(frozen=True, kw_only=True)
class InceptionSelectDescription(SelectEntityDescription):
    """Describes Inception select entity."""

    options: list[str] = field(default_factory=list)


class InceptionSelect(InceptionEntity, SelectEntity):
    """inception binary_sensor class."""

    data: InceptionSummaryEntry

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: SelectEntityDescription,
        data: InceptionSummaryEntry,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )
        self.data = data
        self.unique_id = entity_description.key
        self._device_id = data.entity_info.id


class InceptionUnlockStrategySelect(
    InceptionSelect,
    RestoreEntity,
):
    """inception select for Doors."""

    _attr_has_entity_name = True
    entity_description: InceptionSelectDescription

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionSelectDescription,
        data: DoorSummaryEntry,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.entity_info.id)},
            manufacturer=MANUFACTURER,
        )
        self._attr_current_option = None
        self.entity_description = entity_description
        self._attr_extra_state_attributes = {
            "type": "unlock_strategy",
        }

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "Unlock Strategy"

    async def async_added_to_hass(self) -> None:
        """Restore state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            try:
                self._attr_current_option = last_state.state
                if self._attr_current_option not in self.entity_description.options:
                    _LOGGER.warning(
                        "Restored unlock strategy '%s' is invalid. Using default.",
                        self._attr_current_option,
                    )
                    self._attr_current_option = DEFAULT_UNLOCK_STRATEGY
            except ValueError:
                _LOGGER.warning(
                    "Could not restore unlock strategy. Falling back to default."
                )
                self._attr_current_option = DEFAULT_UNLOCK_STRATEGY
        else:
            self._attr_current_option = (
                DEFAULT_UNLOCK_STRATEGY  # Set initial value if no history
            )

    async def async_select_option(self, option: str) -> None:
        """Handle selection of an unlock strategy."""
        if option not in self.entity_description.options:
            msg = f"Invalid unlock strategy: {option}"
            raise ValueError(msg)

        _LOGGER.debug("Setting unlock strategy to: %s", option)

        self._attr_current_option = option
        self.async_write_ha_state()

        # Now you can use the selected strategy in your lock platform:
        _LOGGER.debug("Unlock strategy set to: %s", self._attr_current_option)
