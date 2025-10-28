"""Binary sensor platform for inception."""

from __future__ import annotations

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
    """Define device class from device name."""
    device_classes = {
        "motion": BinarySensorDeviceClass.MOTION,
        "pir": BinarySensorDeviceClass.MOTION,
        "pe beam": BinarySensorDeviceClass.MOTION,
        "louvre": BinarySensorDeviceClass.WINDOW,
        "shock": BinarySensorDeviceClass.VIBRATION,
        "button": BinarySensorDeviceClass.CONNECTIVITY,
        "rex": BinarySensorDeviceClass.DOOR,
        "opening": BinarySensorDeviceClass.OPENING,
        "power": BinarySensorDeviceClass.POWER,
        "smoke": BinarySensorDeviceClass.SMOKE,
        "vibration": BinarySensorDeviceClass.VIBRATION,
        "cold": BinarySensorDeviceClass.COLD,
        "light": BinarySensorDeviceClass.LIGHT,
        "moisture": BinarySensorDeviceClass.MOISTURE,
        "break": BinarySensorDeviceClass.VIBRATION,
        "glass": BinarySensorDeviceClass.WINDOW,
        "side door": BinarySensorDeviceClass.DOOR,
        "hallway door": BinarySensorDeviceClass.DOOR,
        "garage": BinarySensorDeviceClass.GARAGE_DOOR,
        "gate": BinarySensorDeviceClass.DOOR,
        "window": BinarySensorDeviceClass.WINDOW,
        "door": BinarySensorDeviceClass.DOOR,
        "heat": BinarySensorDeviceClass.HEAT,
    }

    # Find the first matching device class or default to 'opening'
    return next(
        (device_classes[device] for device in device_classes if device in name.lower()),
        BinarySensorDeviceClass.OPENING,
    )


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


def is_entity_registry_enabled_default(name: str) -> bool:
    """Disables these sensors by default."""
    return not name.lower().endswith("- forced") and not name.lower().endswith(
        "- held open"
    )


def extract_door_name_from_input(input_name: str) -> str | None:
    """
    Extract door name from input name if it matches a known pattern.

    Patterns:
    - "{Door Name} - {Event Type}" -> returns "Door Name"
    - "{Door Name} {Suffix}" where Suffix is a known suffix -> returns "Door Name"
    """
    # Check for pattern with dash separator
    if " - " in input_name:
        return input_name.split(" - ")[0]

    # Check for known suffix patterns (case-insensitive)
    door_input_suffixes = [" Reed"]
    for suffix in door_input_suffixes:
        if input_name.lower().endswith(suffix.lower()):
            return input_name[: -len(suffix)]

    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create door binary sensors
    entities: list[InceptionBinarySensor] = [
        InceptionDoorBinarySensor(
            coordinator=coordinator,
            entity_description=InceptionBinarySensorDescription(
                key=f"{door.entity_info.id}_{state.value}",
                device_class=get_device_class_for_state(state),
                name=f"{state}",
                has_entity_name=True,
                value_fn=lambda data, state=state: data.public_state is not None
                and bool(data.public_state & state),
            ),
            data=door,
        )
        for state in [
            DoorPublicState.FORCED,
            DoorPublicState.HELD_OPEN_TOO_LONG,
            DoorPublicState.OPEN,
            DoorPublicState.READER_TAMPER,
        ]
        for door in coordinator.data.doors.get_items()
    ]

    # Create input binary sensors, skipping inputs that match door patterns
    door_dict = {
        door.entity_info.name: door for door in coordinator.data.doors.get_items()
    }

    for i_input in coordinator.data.inputs.get_items():
        input_name = i_input.entity_info.name

        # Check if input matches a door pattern
        door_name = extract_door_name_from_input(input_name)
        if door_name and door_dict.get(door_name):
            # Skip inputs that match doors (handled by switch.py for isolation)
            continue

        # Create binary sensor for all other inputs
        entities.append(
            InceptionInputBinarySensor(
                coordinator=coordinator,
                entity_description=InceptionBinarySensorDescription(
                    key=i_input.entity_info.id,
                    device_class=get_device_class_for_name(i_input.entity_info.name),
                    name="Sensor",
                    value_fn=lambda data: data.public_state is not None
                    and bool(data.public_state & InputPublicState.ACTIVE),
                    entity_registry_enabled_default=is_entity_registry_enabled_default(
                        i_input.entity_info.name
                    ),
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
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description
        self.unique_id = entity_description.key
        self.reporting_id = data.entity_info.reporting_id

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
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)

        self.data = data
        self.entity_description = entity_description
        self.reporting_id = data.entity_info.reporting_id
        self._device_id = data.entity_info.id
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
