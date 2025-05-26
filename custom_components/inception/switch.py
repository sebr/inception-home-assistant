"""switch platform for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
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
