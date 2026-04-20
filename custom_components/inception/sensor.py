"""Sensor platform for inception."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EVENT_REVIEW_EVENT
from .coordinator import InceptionUpdateCoordinator
from .entity import panel_device_info

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.device_registry import DeviceInfo

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
        """Subscribe to review events when the entity is added to HA."""
        await super().async_added_to_hass()
        self._event_listener_remove = self.hass.bus.async_listen(
            EVENT_REVIEW_EVENT,
            self._handle_review_event,
        )

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from review events when the entity is removed."""
        if self._event_listener_remove is not None:
            self._event_listener_remove()
            self._event_listener_remove = None
        await super().async_will_remove_from_hass()

    @callback
    def _handle_review_event(self, event: Any) -> None:
        """Handle incoming review events."""
        self._last_event_data = event.data
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """
        Reflect the global review-events switch.

        We previously toggled `disabled_by` on the registry entry to hide the
        sensor when review events were off, but that re-added the entity to
        the platform and triggered a "duplicate unique IDs" error. Using
        `available` is the idiomatic HA pattern for "exists, but no data
        right now" and avoids touching the registry at runtime.
        """
        coordinator = cast("InceptionUpdateCoordinator", self.coordinator)
        return coordinator.review_events_global_enabled

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
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        coordinator = cast("InceptionUpdateCoordinator", self.coordinator)
        return panel_device_info(coordinator)
