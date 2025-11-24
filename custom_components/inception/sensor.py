"""Sensor platform for inception."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.entity_registry import RegistryEntryDisabler, async_get
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EVENT_REVIEW_EVENT
from .coordinator import InceptionUpdateCoordinator

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant

    from .data import InceptionConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: Any,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        InceptionLastReviewEventSensor(
            coordinator=coordinator,
            entity_description=SensorEntityDescription(
                key="last_review_event",
                name="Last Review Event",
                entity_category=EntityCategory.DIAGNOSTIC,
                icon="mdi:math-log",
            ),
        )
    ]

    async_add_entities(entities)


class InceptionLastReviewEventSensor(
    CoordinatorEntity[InceptionUpdateCoordinator], SensorEntity
):
    """Sensor that shows the last review event message description."""

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = entity_description
        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        )
        self._last_event_data: dict[str, Any] | None = None
        self._event_listener_remove: Callable[[], None] | None = None

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to Home Assistant."""
        await super().async_added_to_hass()

        # Start event listener
        self._start_event_listener()

        # Update enabled state based on current switch state
        await self._update_entity_enabled_state()

        # Listen for entity registry updates to handle manual enable/disable
        self.async_on_remove(
            self.hass.bus.async_listen(
                "entity_registry_updated",
                self._handle_entity_registry_update,
            )
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed from Home Assistant."""
        # Clean up event listener
        self._stop_event_listener()

        await super().async_will_remove_from_hass()

    async def _update_entity_enabled_state(self) -> None:
        """Update the entity's enabled state based on review events switch."""
        coordinator = cast("InceptionUpdateCoordinator", self.coordinator)
        entity_registry = async_get(self.hass)

        if entity_entry := entity_registry.async_get(self.entity_id):
            should_be_enabled = coordinator.review_events_global_enabled
            if entity_entry.disabled_by is None and not should_be_enabled:
                # Stop the event listener before disabling
                self._stop_event_listener()
                # Disable the entity
                entity_registry.async_update_entity(
                    self.entity_id, disabled_by=RegistryEntryDisabler.INTEGRATION
                )
            elif (
                entity_entry.disabled_by == RegistryEntryDisabler.INTEGRATION
                and should_be_enabled
            ):
                # Enable the entity
                entity_registry.async_update_entity(self.entity_id, disabled_by=None)
                # Start the event listener after enabling
                self._start_event_listener()

    def _start_event_listener(self) -> None:
        """Start the event listener if not already running and entity is enabled."""
        if (
            self._event_listener_remove is None
            and self.hass is not None
            and self._is_entity_enabled()
        ):
            self._event_listener_remove = self.hass.bus.async_listen(
                EVENT_REVIEW_EVENT,
                self._handle_review_event,
            )

    def _stop_event_listener(self) -> None:
        """Stop the event listener if running."""
        if self._event_listener_remove is not None:
            self._event_listener_remove()
            self._event_listener_remove = None

    def _is_entity_enabled(self) -> bool:
        """Check if the entity is currently enabled."""
        if self.entity_id is None or self.hass is None:
            return False

        entity_registry = async_get(self.hass)
        if entity_entry := entity_registry.async_get(self.entity_id):
            return entity_entry.disabled_by is None
        return True  # If not in registry yet, assume enabled

    @callback
    def _handle_entity_registry_update(self, event: Any) -> None:
        """Handle entity registry updates to manage event listener state."""
        # Check if this update is for our entity and disabled_by changed
        if (
            event.data.get("action") == "update"
            and event.data.get("entity_id") == self.entity_id
            and "disabled_by" in event.data.get("changes", {})
        ):
            if self._is_entity_enabled():
                # Entity was enabled, start listener
                self._start_event_listener()
            else:
                # Entity was disabled, stop listener
                self._stop_event_listener()

    @callback
    def _handle_review_event(self, event: Any) -> None:
        """Handle incoming review events."""
        self._last_event_data = event.data
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self._last_event_data is None:
            return None
        return self._last_event_data.get("message_description", "Unknown")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes."""
        if self._last_event_data is None:
            return None

        return {
            "event_id": self._last_event_data.get("event_id"),
            "description": self._last_event_data.get("description"),
            "message_value": self._last_event_data.get("message_value"),
            "message_category": self._last_event_data.get("message_category"),
            "when": self._last_event_data.get("when"),
            "reference_time": self._last_event_data.get("reference_time"),
            "who": self._last_event_data.get("who"),
            "who_id": self._last_event_data.get("who_id"),
            "what": self._last_event_data.get("what"),
            "what_id": self._last_event_data.get("what_id"),
            "where": self._last_event_data.get("where"),
            "where_id": self._last_event_data.get("where_id"),
        }

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if entity should be enabled when first added to registry."""
        coordinator = cast("InceptionUpdateCoordinator", self.coordinator)
        return coordinator.review_events_global_enabled

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information about this entity."""
        coordinator = cast("InceptionUpdateCoordinator", self.coordinator)
        return {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": "Inception Security System",
            "manufacturer": "InnerRange",
            "model": "Inception",
        }
