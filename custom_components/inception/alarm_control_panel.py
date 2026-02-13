"""Binary sensor platform for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityDescription,
)
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
    CodeFormat,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform

from .const import (
    CONF_REQUIRE_CODE_TO_ARM,
    CONF_REQUIRE_PIN_CODE,
    DEFAULT_REQUIRE_CODE_TO_ARM,
    DEFAULT_REQUIRE_PIN_CODE,
    DOMAIN,
)
from .entity import InceptionEntity
from .pyinception.schemas.area import AreaPublicState

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry
    from .pyinception.schemas.area import AreaSummaryEntry

SERVICE_AREA_ARM = "area_arm"


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
                key="area_alarm",
                name=area.entity_info.name,
            ),
            data=area,
        )
        for area in coordinator.data.areas.get_items()
    ]

    async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_AREA_ARM,
        {
            vol.Optional("exit_delay"): cv.boolean,
            vol.Optional("seal_check"): cv.boolean,
            vol.Optional("code"): cv.string,
        },
        "area_arm_service",
    )


class InceptionAlarm(InceptionEntity, AlarmControlPanelEntity):
    """inception alarm class."""

    entity_description: InceptionAlarmDescription
    data: AreaSummaryEntry

    def __init__(
        self,
        coordinator: InceptionUpdateCoordinator,
        entity_description: InceptionAlarmDescription,
        data: AreaSummaryEntry,
    ) -> None:
        """Initialize the alarm class."""
        super().__init__(
            coordinator, entity_description=entity_description, inception_object=data
        )
        self.data = data
        self.entity_description = entity_description

        options = coordinator.config_entry.options
        require_pin = options.get(CONF_REQUIRE_PIN_CODE, DEFAULT_REQUIRE_PIN_CODE)
        require_code_to_arm = options.get(
            CONF_REQUIRE_CODE_TO_ARM, DEFAULT_REQUIRE_CODE_TO_ARM
        )

        # If PIN entry is disabled, do not require a code to arm to avoid
        # an inconsistent configuration where the UI cannot supply a code.
        if not require_pin:
            require_code_to_arm = False

        self._attr_code_format = CodeFormat.NUMBER if require_pin else None
        self._attr_code_arm_required = require_code_to_arm
        self._attr_supported_features = (
            AlarmControlPanelEntityFeature.ARM_AWAY
            | AlarmControlPanelEntityFeature.TRIGGER
        )
        if data.arm_info.multi_mode_arm_enabled:
            self._attr_supported_features |= (
                AlarmControlPanelEntityFeature.ARM_HOME
                | AlarmControlPanelEntityFeature.ARM_NIGHT
            )

    @property
    def alarm_state(self) -> AlarmControlPanelState | None:
        """Return the state of the alarm."""
        if self.data.public_state is None:
            return None

        state_mappings = {
            # Order here matters:
            # 1. Triggered
            AreaPublicState.ALARM: AlarmControlPanelState.TRIGGERED,
            # 2. Pending
            AreaPublicState.ENTRY_DELAY: AlarmControlPanelState.PENDING,
            AreaPublicState.EXIT_DELAY: AlarmControlPanelState.PENDING,
            # 3. Arming
            AreaPublicState.ARM_WARNING: AlarmControlPanelState.ARMING,
            # 4. Armed (Perimiter)
            AreaPublicState.STAY_ARM: AlarmControlPanelState.ARMED_HOME,
            # 5. Armed (Sleep)
            AreaPublicState.SLEEP_ARM: AlarmControlPanelState.ARMED_NIGHT,
            # 6. Armed (Full)
            AreaPublicState.AWAY_ARM: AlarmControlPanelState.ARMED_AWAY,
            AreaPublicState.ARMED: AlarmControlPanelState.ARMED_AWAY,
            # 7. Disarmed
            AreaPublicState.DISARMED: AlarmControlPanelState.DISARMED,
        }

        for area_state, alarm_state in state_mappings.items():
            if bool(self.data.public_state & area_state):
                return alarm_state

        return None

    async def _alarm_control(
        self,
        control_type: str,
        code: str | None = None,
        *,
        exit_delay: bool | None = None,
        seal_check: bool | None = None,
    ) -> None:
        """Control the switch."""
        data = {
            "Type": "ControlArea",
            "AreaControlType": control_type,
        }

        if code:
            data["ExecuteAsOtherUser"] = "true"
            data["OtherUserPIN"] = code

        # Only add optional parameters if explicitly provided
        if exit_delay is not None:
            data["ExitDelay"] = str(exit_delay).lower()
        if seal_check is not None:
            data["SealCheck"] = str(seal_check).lower()

        return await self.coordinator.api.request(
            method="post",
            path=f"/control/area/{self.data.entity_info.id}/activity",
            data=data,
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

    async def area_arm_service(
        self,
        *,
        exit_delay: bool | None = None,
        seal_check: bool | None = None,
        code: str | None = None,
    ) -> None:
        """Arm the area with custom exit delay and seal check settings."""
        return await self._alarm_control(
            "Arm", code, exit_delay=exit_delay, seal_check=seal_check
        )
