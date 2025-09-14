"""switch platform for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.storage import Store

from .const import DOMAIN, LOGGER
from .entity import InceptionEntity
from .pyinception.schemas.input import InputPublicState
from .pyinception.schemas.output import OutputPublicState

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schemas.entities import (
        InceptionSummaryEntry,
    )
    from .pyinception.schemas.input import (
        InputSummaryEntry,
    )
    from .pyinception.schemas.output import (
        OutputSummaryEntry,
    )


@dataclass(frozen=True, kw_only=True)
class InceptionSwitchDescription(SwitchEntityDescription):
    """Describes Inception switch entity."""

    name: str = ""
    value_fn: Callable[[InceptionSummaryEntry], bool]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[InceptionSwitch] = [
        InceptionOutputSwitch(
            coordinator=coordinator,
            entity_description=InceptionSwitchDescription(
                key=output.entity_info.id,
                device_class=SwitchDeviceClass.SWITCH,
                value_fn=lambda data: data.public_state is not None
                and bool(data.public_state & OutputPublicState.ON),
            ),
            data=output,
        )
        for output in coordinator.data.outputs.get_items()
    ]

    entities += [
        InceptionInputSwitch(
            coordinator=coordinator,
            entity_description=InceptionSwitchDescription(
                key=f"{i_input.entity_info.id}_isolated",
                device_class=SwitchDeviceClass.SWITCH,
                name="Isolated",
                has_entity_name=True,
                entity_registry_visible_default=False,
                value_fn=lambda data: data.public_state is not None
                and bool(data.public_state & InputPublicState.ISOLATED),
            ),
            data=i_input,
        )
        for i_input in coordinator.data.inputs.get_items()
    ]

    # Add review event control switches
    entities += [
        ReviewEventGlobalSwitch(coordinator=coordinator),
        ReviewEventCategorySwitch(coordinator=coordinator, category="System"),
        ReviewEventCategorySwitch(coordinator=coordinator, category="Audit"),
        ReviewEventCategorySwitch(coordinator=coordinator, category="Access"),
        ReviewEventCategorySwitch(coordinator=coordinator, category="Security"),
        ReviewEventCategorySwitch(coordinator=coordinator, category="Hardware"),
    ]

    async_add_entities(entities)


class InceptionSwitch(InceptionEntity, SwitchEntity):
    """inception switch class."""

    entity_description: InceptionSwitchDescription
    data: InceptionSummaryEntry

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionSwitchDescription,
        data: InceptionSummaryEntry,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description
        self.reporting_id = data.entity_info.reporting_id

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self.entity_description.value_fn(self.data)


class InceptionInputSwitch(InceptionSwitch, SwitchEntity):
    """inception switch class for Inputs."""

    entity_description: InceptionSwitchDescription
    data: InputSummaryEntry

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionSwitchDescription,
        data: InputSummaryEntry,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.entity_info.id)},
            name=data.entity_info.name,
        )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.entity_description.name

    async def async_turn_on(self) -> None:
        """Isolate the Input."""
        return await self.coordinator.api.control_input(
            input_id=self.data.entity_info.id,
            data={
                "Type": "ControlInput",
                "InputControlType": "Isolate",
            },
        )

    async def async_turn_off(self) -> None:
        """Deisolate the Input."""
        return await self.coordinator.api.control_input(
            input_id=self.data.entity_info.id,
            data={
                "Type": "ControlInput",
                "InputControlType": "Deisolate",
            },
        )


class InceptionOutputSwitch(InceptionSwitch, SwitchEntity):
    """inception switch class."""

    entity_description: InceptionSwitchDescription
    data: OutputSummaryEntry

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionSwitchDescription,
        data: OutputSummaryEntry,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)

    @property
    def icon(self) -> str:
        """Define device class from device name."""
        default_icon = "mdi:help-circle"
        icon_map = {
            "screamer": ("mdi:bullhorn", "mdi:bullhorn"),
            "siren": ("mdi:bullhorn", "mdi:bullhorn"),
            "strobe": ("mdi:alarm-light", "mdi:alarm-light-off"),
        }

        # Find the first matching device class or fallback to default_icon
        return next(
            (
                icon_map[device][0 if self.is_on else 1]
                for device in icon_map
                if device in self.name.lower()
            ),
            default_icon,
        )

    async def async_turn_on(self) -> None:
        """Turn on the Output."""
        return await self.coordinator.api.control_output(
            output_id=self.data.entity_info.id,
            data={
                "Type": "ControlOutput",
                "OutputControlType": "On",
            },
        )

    async def async_turn_off(self) -> None:
        """Turn off the Output."""
        return await self.coordinator.api.control_output(
            output_id=self.data.entity_info.id,
            data={
                "Type": "ControlOutput",
                "OutputControlType": "Off",
            },
        )


class ReviewEventGlobalSwitch(SwitchEntity):
    """Switch to control review event listener globally."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: InceptionUpdateCoordinator) -> None:
        """Initialize the global review event switch."""
        self.coordinator = coordinator
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_review_events_global"
        )
        self._attr_name = "Review Events"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Inception Integration",
            manufacturer="InnerRange",
            model="Inception",
        )

        # Initialize storage for persistent state
        self._store = Store(
            coordinator.hass,
            version=1,
            key=f"{DOMAIN}.{coordinator.config_entry.entry_id}.review_events",
        )

    async def async_added_to_hass(self) -> None:
        """Load the switch state when added to Home Assistant."""
        # Load stored state, default to False (disabled)
        stored_data = await self._store.async_load() or {}
        self._attr_is_on = stored_data.get("global_enabled", False)

        # If enabled, start the listener
        if self._attr_is_on:
            await self._start_review_listener()

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return getattr(self, "_attr_is_on", False)

    async def async_turn_on(self) -> None:
        """Turn on the global review event listener."""
        self._attr_is_on = True
        await self._save_state()
        await self._start_review_listener()
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn off the global review event listener."""
        self._attr_is_on = False
        await self._save_state()
        await self._stop_review_listener()
        self.async_write_ha_state()

    async def _start_review_listener(self) -> None:
        """Start the review event listener if categories are enabled."""
        # Check if any category switches are enabled by their entity IDs
        enabled_categories = []
        categories = ["System", "Audit", "Access", "Security", "Hardware"]

        for category in categories:
            entity_id = (
                f"switch.{self.coordinator.config_entry.entry_id}_review_events_"
                f"{category.lower()}"
            )
            state = self.hass.states.get(entity_id)
            if state and state.state == "on":
                enabled_categories.append(category)

        if not enabled_categories:
            LOGGER.warning(
                "Review event listener global switch is enabled but no categories are "
                "selected. Please enable at least one category (System, Audit, Access, "
                "Security, Hardware)."
            )
            return

        # Start the listener with enabled categories
        await self.coordinator.start_review_listener(enabled_categories)

    async def _stop_review_listener(self) -> None:
        """Stop the review event listener."""
        await self.coordinator.stop_review_listener()

    async def _save_state(self) -> None:
        """Save the current state to storage."""
        await self._store.async_save({"global_enabled": self._attr_is_on})


class ReviewEventCategorySwitch(SwitchEntity):
    """Switch to control review event listener for a specific category."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: InceptionUpdateCoordinator, category: str) -> None:
        """Initialize the category review event switch."""
        self.coordinator = coordinator
        self.category = category
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_review_events_{category.lower()}"
        )
        self._attr_name = f"Review Events {category}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Inception Integration",
            manufacturer="InnerRange",
            model="Inception",
        )

        # Initialize storage for persistent state
        self._store = Store(
            coordinator.hass,
            version=1,
            key=f"{DOMAIN}.{coordinator.config_entry.entry_id}.review_events",
        )

    async def async_added_to_hass(self) -> None:
        """Load the switch state when added to Home Assistant."""
        # Load stored state, default to False (disabled)
        stored_data = await self._store.async_load() or {}
        self._attr_is_on = stored_data.get(f"{self.category.lower()}_enabled", False)

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return getattr(self, "_attr_is_on", False)

    @property
    def available(self) -> bool:
        """Return if the switch is available (global switch must be on)."""
        # Check the global switch state by entity ID
        global_entity_id = (
            f"switch.{self.coordinator.config_entry.entry_id}_review_events_global"
        )
        global_state = self.hass.states.get(global_entity_id)
        return global_state is not None and global_state.state == "on"

    async def async_turn_on(self) -> None:
        """Turn on the category review event listener."""
        if not self.available:
            LOGGER.warning(
                "Cannot enable %s review events: global review events switch is "
                "disabled",
                self.category,
            )
            return

        self._attr_is_on = True
        await self._save_state()
        await self._update_review_listener()
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        """Turn off the category review event listener."""
        self._attr_is_on = False
        await self._save_state()
        await self._update_review_listener()
        self.async_write_ha_state()

    async def _update_review_listener(self) -> None:
        """Update the review listener with current category settings."""
        # Check the global switch state by entity ID
        global_entity_id = (
            f"switch.{self.coordinator.config_entry.entry_id}_review_events_global"
        )
        global_state = self.hass.states.get(global_entity_id)

        if not global_state or global_state.state != "on":
            return

        # Get all enabled categories by checking entity states
        enabled_categories = []
        categories = ["System", "Audit", "Access", "Security", "Hardware"]

        for category in categories:
            entity_id = (
                f"switch.{self.coordinator.config_entry.entry_id}_review_events_"
                f"{category.lower()}"
            )
            state = self.hass.states.get(entity_id)
            if state and state.state == "on":
                enabled_categories.append(category)

        if not enabled_categories:
            LOGGER.warning(
                "All review event categories are disabled. "
                "Please enable at least one category or disable the global switch."
            )
            await self.coordinator.stop_review_listener()
            return

        # Restart the listener with updated categories
        await self.coordinator.start_review_listener(enabled_categories)

    async def _save_state(self) -> None:
        """Save the current state to storage."""
        stored_data = await self._store.async_load() or {}
        stored_data[f"{self.category.lower()}_enabled"] = self._attr_is_on
        await self._store.async_save(stored_data)
