"""switch platform for inception."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_registry import async_get
from homeassistant.helpers.storage import Store

from .const import DOMAIN, LOGGER
from .entity import InceptionEntity
from .pyinception.schemas.input import InputPublicState, InputType
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

    # Handle all input switches, treating logical inputs specially
    door_dict = {
        door.entity_info.name: door for door in coordinator.data.doors.get_items()
    }

    for i_input in coordinator.data.inputs.get_items():
        # Check if this is a logical input that matches a door pattern
        input_name = i_input.entity_info.name
        if i_input.entity_info.input_type == InputType.LOGICAL and " - " in input_name:
            [door_name, event_type] = input_name.split(" - ")
            matching_door = door_dict.get(door_name)
            if matching_door:
                # Create isolated switch grouped with door device
                entities.append(
                    InceptionLogicalInputSwitch(
                        coordinator=coordinator,
                        entity_description=InceptionSwitchDescription(
                            key=f"{i_input.entity_info.id}_isolated",
                            device_class=SwitchDeviceClass.SWITCH,
                            name=f"{event_type} Isolated",
                            has_entity_name=True,
                            entity_registry_visible_default=False,
                            value_fn=lambda data: data.public_state is not None
                            and bool(data.public_state & InputPublicState.ISOLATED),
                        ),
                        data=i_input,
                        door_device_id=matching_door.entity_info.id,
                    )
                )
                continue

        # Create isolated switch with its own device for all other inputs
        entities.append(
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
        )

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


class InceptionLogicalInputSwitch(InceptionSwitch, SwitchEntity):
    """inception switch class for Logical Inputs grouped with Door devices."""

    entity_description: InceptionSwitchDescription
    data: InputSummaryEntry

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionSwitchDescription,
        data: InputSummaryEntry,
        door_device_id: str,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)
        # Extract door name from the input name (remove " - {Event Type}")
        door_name = (
            data.entity_info.name.split(" - ")[0]
            if " - " in data.entity_info.name
            else data.entity_info.name
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, door_device_id)},
            name=door_name,
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

        # Store the global state in the coordinator for other switches to access
        self.coordinator.review_events_global_enabled = self._attr_is_on or False

        # Schedule a deferred startup check to allow all entities to load first
        if self._attr_is_on:
            self.hass.async_create_task(self._deferred_startup_check())

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
        # Update category switches availability
        await self._update_category_switches_availability()

    async def async_turn_off(self) -> None:
        """Turn off the global review event listener."""
        self._attr_is_on = False
        await self._save_state()
        await self._stop_review_listener()
        self.async_write_ha_state()
        # Update category switches availability
        await self._update_category_switches_availability()

    async def _start_review_listener(self) -> None:
        """Start the review event listener if categories are enabled."""
        await self.coordinator.update_review_listener_from_switches()

    async def _stop_review_listener(self) -> None:
        """Stop the review event listener."""
        await self.coordinator.stop_review_listener()

    async def _save_state(self) -> None:
        """Save the current state to storage."""
        await self._store.async_save({"global_enabled": self._attr_is_on})

    async def _update_category_switches_availability(self) -> None:
        """Update the availability of all category switches."""
        # Store the global state in the coordinator for other switches to access
        self.coordinator.review_events_global_enabled = self._attr_is_on or False

        # Force update of all entities by asking Home Assistant to refresh them
        entity_registry = async_get(self.hass)
        categories = ["system", "audit", "access", "security", "hardware"]

        for category in categories:
            unique_id = (
                f"{self.coordinator.config_entry.entry_id}_review_events_{category}"
            )
            entity_id = entity_registry.async_get_entity_id("switch", DOMAIN, unique_id)

            if entity_id:
                # Schedule a state update
                self.hass.async_create_task(
                    self.hass.services.async_call(
                        "homeassistant",
                        "update_entity",
                        {"entity_id": entity_id},
                        blocking=False,
                    )
                )

    async def _deferred_startup_check(self) -> None:
        """Check if we should start the listener after all entities are loaded."""
        # Wait a bit for all entities to be loaded
        await asyncio.sleep(2)

        # Now check if we should start the listener
        if self._attr_is_on:
            await self._start_review_listener()


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
        # Check the global state stored in the coordinator
        return getattr(self.coordinator, "_review_events_global_enabled", False)

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
        await self.coordinator.update_review_listener_from_switches()

    async def _save_state(self) -> None:
        """Save the current state to storage."""
        stored_data = await self._store.async_load() or {}
        stored_data[f"{self.category.lower()}_enabled"] = self._attr_is_on
        await self._store.async_save(stored_data)
