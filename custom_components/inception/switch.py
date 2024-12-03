"""switch platform for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)

from .const import DOMAIN
from .entity import InceptionEntity
from .pyinception.states_schema import OutputPublicStates

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schema import Output


@dataclass(frozen=True, kw_only=True)
class InceptionSwitchDescription(SwitchEntityDescription):
    """Describes Inception switch entity."""

    value_fn: Callable[[Output], bool]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[InceptionSwitch] = [
        InceptionSwitch(
            coordinator=coordinator,
            entity_description=InceptionSwitchDescription(
                key=output.ID,
                device_class=SwitchDeviceClass.SWITCH,
                value_fn=lambda data: data.PublicState is not None
                and bool(data.PublicState & OutputPublicStates.ON),
            ),
            data=output,
        )
        for output in coordinator.data.outputs.values()
    ]

    async_add_entities(entities)


class InceptionSwitch(InceptionEntity, SwitchEntity):
    """inception switch class."""

    entity_description: InceptionSwitchDescription
    data: Output

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionSwitchDescription,
        data: Output,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(
            coordinator, description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description
        self.unique_id = data.ID
        self.reportingId = data.ReportingID

    @property
    def is_on(self) -> bool:
        """Return the state of the switch."""
        return self.entity_description.value_fn(self.data)

    @property
    def icon(self) -> str:
        """Define device class from device name."""
        default_icon = "mdi:help-circle"
        icon_map = {
            "screamer": ("mdi:bullhorn", "mdi:bullhorn"),
            "siren": ("mdi:bullhorn", "mdi:bullhorn"),
            "strobe": ("mdi:alarm-light", "mdi:alarm-light-off"),
        }

        # Find the first matching device class or default to 'opening'
        return next(
            (
                icon_map[device][0 if self.is_on else 1]
                for device in icon_map
                if device in self.name.lower()
            ),
            default_icon,
        )

    async def _switch_control(self, data: Any | None = None) -> None:
        """Control the switch."""
        return await self.coordinator.api.request(
            method="post", path=f"/control/output/{self.data.ID}/activity", data=data
        )

    async def async_turn_on(self) -> None:
        """Unlock the device."""
        return await self._switch_control(
            data={
                "Type": "ControlOutput",
                "OutputControlType": "On",
            },
        )

    async def async_turn_off(self) -> None:
        """Unlock the device."""
        return await self._switch_control(
            data={
                "Type": "ControlOutput",
                "OutputControlType": "Off",
            },
        )
