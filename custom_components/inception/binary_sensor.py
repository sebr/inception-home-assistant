"""Binary sensor platform for inception."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from sqlalchemy import desc

from .const import DOMAIN
from .entity import InceptionEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .schema import InceptionObject

INPUT_BINARY_SENSOR: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="inception",
        name="Inception Input",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


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
            entity_description=BinarySensorEntityDescription(
                key=inception_input.ID,
                name=inception_input.Name,
                device_class=get_device_class(inception_input.Name),
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

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
        data: InceptionObject,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(
            coordinator, description=entity_description, inception_object=data
        )
        self.entity_description = entity_description
        self.unique_id = data.ID
        self.name = data.Name
        self.reportingId = data.ReportingID

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return True
