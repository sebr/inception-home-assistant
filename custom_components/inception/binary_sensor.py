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

from .const import DOMAIN, LOGGER, MANUFACTURER
from .entity import InceptionEntity
from .pyinception.states_schema import DoorPublicState, InputPublicState, InputType

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.inception.pyinception.schema import (
        Door,
        InceptionObject,
        Input,
    )

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry


@dataclass(frozen=True, kw_only=True)
class InceptionBinarySensorDescription(BinarySensorEntityDescription):
    """Describes Inception binary sensor entity."""

    name: str = ""
    value_fn: Callable[[InceptionObject], bool]


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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[InceptionBinarySensor] = [
        InceptionInputBinarySensor(
            coordinator=coordinator,
            entity_description=InceptionBinarySensorDescription(
                key=inception_input.id,
                device_class=get_device_class_for_name(inception_input.name),
                name="Sensor",
                value_fn=lambda data: data.public_state is not None
                and bool(data.public_state & InputPublicState.ACTIVE),
                entity_registry_enabled_default=is_entity_registry_enabled_default(
                    inception_input.name
                ),
            ),
            data=inception_input,
        )
        for inception_input in coordinator.data.inputs.values()
        if inception_input.input_type != InputType.LOGICAL
    ]

    entities += [
        InceptionDoorBinarySensor(
            coordinator=coordinator,
            entity_description=InceptionBinarySensorDescription(
                key=f"{door.id}_{state.value}",
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
        for door in coordinator.data.doors.values()
    ]

    async_add_entities(entities)


class InceptionBinarySensor(InceptionEntity, BinarySensorEntity):
    """inception binary_sensor class."""

    entity_description: InceptionBinarySensorDescription
    data: InceptionObject

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionBinarySensorDescription,
        data: InceptionObject,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description
        self.unique_id = entity_description.key
        self.reporting_id = data.reporting_id

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

    entity_description: InceptionBinarySensorDescription
    data: Input

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionBinarySensorDescription,
        data: Input,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)

        self.data = data
        self.entity_description = entity_description
        self.reporting_id = data.reporting_id
        self._device_id = data.id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=data.name,
            manufacturer=MANUFACTURER,
        )

        LOGGER.debug("Input Binary Sensor: %s %s", data.name, data.input_type)


class InceptionDoorBinarySensor(
    InceptionBinarySensor,
):
    """inception binary_sensor for Doors."""

    entity_description: InceptionBinarySensorDescription
    data: Door

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionBinarySensorDescription,
        data: Door,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description=entity_description, data=data)

        self.data = data
        self.entity_description = entity_description
        self.reporting_id = data.reporting_id
        self._device_id = data.id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=data.name,
        )
