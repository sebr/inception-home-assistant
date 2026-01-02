"""Base classes for Inception entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import LOGGER
from .coordinator import InceptionUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription

    from .pyinception.schemas.entities import InceptionSummaryEntry


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
