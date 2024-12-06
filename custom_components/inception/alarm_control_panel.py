"""Binary sensor platform for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityDescription,
)
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)

from .const import DOMAIN
from .entity import InceptionEntity
from .pyinception.states_schema import AreaPublicState

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schema import Area


@dataclass(frozen=True, kw_only=True)
class InceptionAlarmDescription(AlarmControlPanelEntityDescription):
    """Describes Inception switch entity."""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the alarm platform."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[InceptionAlarm] = [
        InceptionAlarm(
            coordinator=coordinator,
            entity_description=InceptionAlarmDescription(
                key=area.id,
            ),
            data=area,
        )
        for area in coordinator.data.areas.values()
    ]

    async_add_entities(entities)


class InceptionAlarm(InceptionEntity, AlarmControlPanelEntity):
    """inception alarm class."""

    entity_description: InceptionAlarmDescription
    data: Area

    _attr_code_arm_required: bool = False
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_NIGHT
        | AlarmControlPanelEntityFeature.TRIGGER
    )

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionAlarmDescription,
        data: Area,
    ) -> None:
        """Initialize the alarm class."""
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description
        self.unique_id = data.id
        self.reportingId = data.reporting_id

    @property
    def alarm_state(self) -> AlarmControlPanelState | None:
        """Return the state of the alarm."""
        if self.data.public_state is None:
            return None

        state_mapping = {
            AreaPublicState.ALARM: AlarmControlPanelState.TRIGGERED,
            AreaPublicState.DISARMED: AlarmControlPanelState.DISARMED,
            AreaPublicState.STAY_ARM: AlarmControlPanelState.ARMED_HOME,
            AreaPublicState.AWAY_ARM: AlarmControlPanelState.ARMED_AWAY,
            AreaPublicState.SLEEP_ARM: AlarmControlPanelState.ARMED_NIGHT,
            AreaPublicState.ARM_WARNING: AlarmControlPanelState.ARMING,
            AreaPublicState.ENTRY_DELAY: AlarmControlPanelState.PENDING,
            AreaPublicState.EXIT_DELAY: AlarmControlPanelState.PENDING,
        }

        for area_state, alarm_state in state_mapping.items():
            if bool(self.data.public_state & area_state):
                return alarm_state

        return None

    async def _alarm_control(self, control_type: str, _code: str | None = None) -> None:
        """Control the switch."""
        return await self.coordinator.api.request(
            method="post",
            path=f"/control/area/{self.data.id}/activity",
            data={
                "Type": "ControlArea",
                "AreaControlType": control_type,
            },
        )

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        return await self._alarm_control("Arm", code)

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm home command."""
        return await self._alarm_control("ArmStay", code)

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Disarm."""
        return await self._alarm_control("Disarm", code)

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        """Send arm night command."""
        return await self._alarm_control("ArmSleep", code)
