"""Binary sensor platform for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .entity import InceptionEntity
from .pyinception.states_schema import InputPublicStates

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schema import Input

INPUT_BINARY_SENSOR: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="inception",
        name="Inception Input",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


@dataclass(frozen=True, kw_only=True)
class InceptionBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Inception binary sensor entity."""

    value_fn: Callable[[Input], bool]


def get_device_class(name: str) -> BinarySensorDeviceClass:
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
        InceptionBinarySensor(
            coordinator=coordinator,
            entity_description=InceptionBinarySensorEntityDescription(
                key=inception_input.ID,
                device_class=get_device_class(inception_input.Name),
                value_fn=lambda data: data.PublicState is not None
                and bool(data.PublicState & InputPublicStates.ACTIVE),
                entity_registry_enabled_default=is_entity_registry_enabled_default(
                    inception_input.Name
                ),
            ),
            data=inception_input,
        )
        for inception_input in coordinator.data.inputs.values()
    ]

    async_add_entities(entities)


class InceptionBinarySensor(InceptionEntity, BinarySensorEntity):
    """inception binary_sensor class."""

    entity_description: InceptionBinarySensorEntityDescription
    data: Input

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionBinarySensorEntityDescription,
        data: Input,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(
            coordinator, description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description
        self.unique_id = data.ID
        self.name = data.Name
        self.reportingId = data.ReportingID

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        return self.entity_description.value_fn(self.data)
