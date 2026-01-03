"""Binary sensor platform for inception."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, MANUFACTURER
from .entity import InceptionEntity
from .pyinception.schemas.door import DoorPublicState
from .pyinception.schemas.input import InputPublicState
from .util import find_matching_door

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schemas.door import DoorSummaryEntry
    from .pyinception.schemas.entities import (
        InceptionSummaryEntry,
    )
    from .pyinception.schemas.input import InputSummaryEntry


@dataclass(frozen=True, kw_only=True)
class InceptionBinarySensorDescription(BinarySensorEntityDescription):
    """Describes Inception binary sensor entity."""

    name: str = ""
    value_fn: Callable[[InceptionSummaryEntry], bool]


def get_device_class_for_name(name: str) -> BinarySensorDeviceClass:
    """
    Define device class from device name.

    Device classes are ordered from most specific to least specific to ensure
    accurate matching. For example, "garage door" should match before "door".
    """
    # Ordered list of (keyword, device_class) tuples
    # More specific patterns first to avoid false positives
    device_class_patterns = [
        # Specific door types (must come before generic "door")
        ("side door", BinarySensorDeviceClass.DOOR),
        ("hallway door", BinarySensorDeviceClass.DOOR),
        ("garage door", BinarySensorDeviceClass.GARAGE_DOOR),
        ("garage", BinarySensorDeviceClass.GARAGE_DOOR),
        # Motion and presence detection
        ("pe beam", BinarySensorDeviceClass.MOTION),
        ("pir", BinarySensorDeviceClass.MOTION),
        ("motion", BinarySensorDeviceClass.MOTION),
        ("beam", BinarySensorDeviceClass.MOTION),
        # Safety and security
        ("duress", BinarySensorDeviceClass.SAFETY),
        ("panic", BinarySensorDeviceClass.SAFETY),
        ("tamper", BinarySensorDeviceClass.TAMPER),
        # Glass and window detection
        ("glass break", BinarySensorDeviceClass.VIBRATION),
        ("glass", BinarySensorDeviceClass.WINDOW),
        ("louvre", BinarySensorDeviceClass.WINDOW),
        ("window", BinarySensorDeviceClass.WINDOW),
        # Environmental sensors
        ("smoke", BinarySensorDeviceClass.SMOKE),
        ("gas", BinarySensorDeviceClass.GAS),
        ("heat", BinarySensorDeviceClass.HEAT),
        ("cold", BinarySensorDeviceClass.COLD),
        ("moisture", BinarySensorDeviceClass.MOISTURE),
        # Vibration and shock
        ("shock", BinarySensorDeviceClass.VIBRATION),
        ("vibration", BinarySensorDeviceClass.VIBRATION),
        ("break", BinarySensorDeviceClass.VIBRATION),
        # Access control
        ("rex", BinarySensorDeviceClass.CONNECTIVITY),
        ("exit", BinarySensorDeviceClass.CONNECTIVITY),
        ("button", BinarySensorDeviceClass.CONNECTIVITY),
        # Generic types
        ("contact", BinarySensorDeviceClass.OPENING),
        ("door", BinarySensorDeviceClass.DOOR),
        ("gate", BinarySensorDeviceClass.DOOR),
        ("opening", BinarySensorDeviceClass.OPENING),
        ("power", BinarySensorDeviceClass.POWER),
        ("light", BinarySensorDeviceClass.LIGHT),
    ]

    name_lower = name.lower()

    # Find the first matching device class or default to 'opening'
    for keyword, device_class in device_class_patterns:
        if keyword in name_lower:
            return device_class

    return BinarySensorDeviceClass.OPENING


def get_device_class_for_state(state: DoorPublicState) -> BinarySensorDeviceClass:
    """Define device class from device state."""
    device_classes = {
        DoorPublicState.FORCED: BinarySensorDeviceClass.PROBLEM,
        DoorPublicState.HELD_OPEN_TOO_LONG: BinarySensorDeviceClass.PROBLEM,
        DoorPublicState.OPEN: BinarySensorDeviceClass.DOOR,
        DoorPublicState.READER_TAMPER: BinarySensorDeviceClass.TAMPER,
    }

    # Find the first matching device class or default to 'opening'
    return device_classes.get(state, BinarySensorDeviceClass.OPENING)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create door binary sensors
    # Define states with human-readable names and key suffixes
    door_states = [
        (DoorPublicState.FORCED, "Forced", "forced"),
        (DoorPublicState.HELD_OPEN_TOO_LONG, "Held open too long", "dotl"),
        (DoorPublicState.OPEN, "Sensor", "open"),
        (DoorPublicState.READER_TAMPER, "Reader tamper", "tamper"),
    ]

    all_doors = coordinator.data.doors.get_items()

    entities: list[InceptionBinarySensor] = []

    for door in all_doors:
        for state, name, key_suffix in door_states:
            # For the "open" sensor, use door name to determine device class
            # (e.g., garage door vs regular door)
            # For other states, use the state-based device class
            if state == DoorPublicState.OPEN:
                device_class = get_device_class_for_name(door.entity_info.name)
            else:
                device_class = get_device_class_for_state(state)

            entities.append(
                InceptionDoorBinarySensor(
                    coordinator=coordinator,
                    entity_description=InceptionBinarySensorDescription(
                        key=f"door_{key_suffix}",
                        device_class=device_class,
                        name=name,
                        has_entity_name=True,
                        value_fn=lambda data, state=state: data.public_state is not None
                        and bool(data.public_state & state),
                        entity_registry_enabled_default=key_suffix
                        not in ["forced", "dotl"],
                    ),
                    data=door,
                )
            )

    # Create input binary sensors
    # Skip inputs that match door standard states (forced, held, open, tamper)
    # But create sensors for other door-related inputs (REX, button, etc.)

    # Define regex pattern for standard door state suffixes that are already handled
    # This matches: forced, held open, dotl, open, sensor, contact,
    # reed (contact/sensor), tamper, reader tamper
    standard_door_suffix_pattern = re.compile(
        r"^(forced|held\s+open(\s+too\s+long)?|dotl|open|sensor|contact|"
        r"reed(\s+contact)?(\s+sensor)?|reader\s+tamper|tamper)$",
        re.IGNORECASE,
    )

    for i_input in coordinator.data.inputs.get_items():
        input_entity = i_input.entity_info

        if input_entity.is_custom_input:
            # Skip custom inputs (they are a switch)
            continue

        matching_door, suffix = find_matching_door(input_entity.name, all_doors)

        if matching_door is not None and suffix:
            # Input matches a door - check if it's a standard state or additional input
            if standard_door_suffix_pattern.match(suffix):
                # Skip - this is already handled by door binary sensors
                continue

            # Create sensor for non-standard door input (REX, button, etc.)
            # Group it with the door device
            key_suffix = suffix.lower()
            entities.append(
                InceptionInputBinarySensor(
                    coordinator=coordinator,
                    entity_description=InceptionBinarySensorDescription(
                        key=f"input_{key_suffix}",
                        device_class=get_device_class_for_name(input_entity.name),
                        name=suffix,
                        has_entity_name=True,
                        value_fn=lambda data: data.public_state is not None
                        and bool(data.public_state & InputPublicState.ACTIVE),
                    ),
                    data=i_input,
                    door=matching_door,
                )
            )
        else:
            # Create standalone binary sensor for inputs that don't match any door
            entities.append(
                InceptionInputBinarySensor(
                    coordinator=coordinator,
                    entity_description=InceptionBinarySensorDescription(
                        key="sensor",
                        device_class=get_device_class_for_name(input_entity.name),
                        name="Sensor",
                        value_fn=lambda data: data.public_state is not None
                        and bool(data.public_state & InputPublicState.ACTIVE),
                    ),
                    data=i_input,
                )
            )

    async_add_entities(entities)


class InceptionBinarySensor(InceptionEntity, BinarySensorEntity):
    """inception binary_sensor class."""

    entity_description: InceptionBinarySensorDescription
    data: InceptionSummaryEntry

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionBinarySensorDescription,
        data: InceptionSummaryEntry,
    ) -> None:
        """Initialize the binary_sensor class."""
        self.entity_description = entity_description
        self.data = data
        self.unique_id = entity_description.key
        self.reporting_id = data.entity_info.reporting_id
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        return self.entity_description.value_fn(self.data)

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self.entity_description.name


class InceptionInputBinarySensor(
    InceptionBinarySensor,
):
    """inception binary_sensor for Inputs."""

    data: InputSummaryEntry

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionBinarySensorDescription,
        data: InputSummaryEntry,
        door: DoorSummaryEntry | None = None,
    ) -> None:
        """Initialize the binary_sensor class."""
        self.entity_description = entity_description
        super().__init__(coordinator, entity_description=entity_description, data=data)

        self.data = data
        self.reporting_id = data.entity_info.reporting_id
        self._device_id = data.entity_info.id

        # Override device_info to group with door device instead of creating own device
        if door is not None:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, door.entity_info.id)},
                name=door.entity_info.name,
            )
        else:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, self._device_id)},
                name=data.entity_info.name,
                manufacturer=MANUFACTURER,
            )


class InceptionDoorBinarySensor(
    InceptionBinarySensor,
):
    """inception binary_sensor for Doors."""

    data: DoorSummaryEntry

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionBinarySensorDescription,
        data: DoorSummaryEntry,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)

        self.data = data
        self._device_id = data.entity_info.id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=data.entity_info.name,
            manufacturer=MANUFACTURER,
        )
