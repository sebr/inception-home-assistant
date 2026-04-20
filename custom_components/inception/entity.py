"""Base classes for Inception entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER, MANUFACTURER
from .coordinator import InceptionUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription

    from .pyinception.schemas.entities import InceptionSummaryEntry


def panel_device_info(coordinator: InceptionUpdateCoordinator) -> DeviceInfo:
    """Build the DeviceInfo for the Inception controller (panel)."""
    entry = coordinator.config_entry
    protocol_version = coordinator.api.protocol_version
    system_info = coordinator.api.system_info
    name = (
        (system_info.system_name if system_info else "") or entry.title or "Inception"
    )
    serial_number = system_info.serial_number if system_info else None
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=name,
        manufacturer=MANUFACTURER,
        model="Inception",
        serial_number=serial_number or None,
        sw_version=(
            f"Protocol v{protocol_version}" if protocol_version is not None else None
        ),
        configuration_url=coordinator.api._host,
    )


def panel_identifiers(coordinator: InceptionUpdateCoordinator) -> tuple[str, str]:
    """Return the panel device identifier tuple used as via_device for children."""
    return (DOMAIN, coordinator.config_entry.entry_id)


class InceptionEntity(CoordinatorEntity[InceptionUpdateCoordinator]):
    """Entity class for Inception entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: EntityDescription,
        *,
        inception_object: InceptionSummaryEntry,
    ) -> None:
        """Initialize the Inception entity."""
        self.entity_description = entity_description
        self._attr_attribution = f"Data provided by {coordinator.api._host}"
        self._attr_unique_id = (
            f"{inception_object.entity_info.id}_{entity_description.key}"
        )
        self._inception_object = inception_object
        self._attr_extra_state_attributes = inception_object.extra_fields
        super().__init__(coordinator=coordinator)
        self._update_attrs()

        LOGGER.debug(
            "Creating %s: %s - %s",
            self.__class__.__name__,
            inception_object.entity_info.name,
            entity_description.name,
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._inception_object.entity_info.name

    def _update_attrs(self) -> None:
        """Update state attributes."""
        return  # pragma: no cover

    @callback
    def _handle_coordinator_update(self) -> None:
        """Get the latest data and updates the state."""
        self._update_attrs()
        super()._handle_coordinator_update()
