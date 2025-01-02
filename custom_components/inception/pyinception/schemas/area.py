# ruff: noqa: E501 ANN003

"""Inception Area schemas."""

from dataclasses import dataclass

from .entities import (
    InceptionPublicState,
    InceptionSummary,
    InceptionSummaryEntry,
    ReportableShortEntity,
)


class AreaPublicState(InceptionPublicState):
    """Area public state."""

    ARMED = 0x0001
    ALARM = 0x0002
    ENTRY_DELAY = 0x0004
    EXIT_DELAY = 0x0008
    ARM_WARNING = 0x0010
    DEFER_DISARMED = 0x0020
    DETECTING_ACTIVE_INPUTS = 0x0040
    WALK_TEST_ACTIVE = 0x0080
    AWAY_ARM = 0x0100
    STAY_ARM = 0x0200
    SLEEP_ARM = 0x0400
    DISARMED = 0x0800
    ARM_READY = 0x1000

    @staticmethod
    def get_state_description(state_value: int) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        descriptions = {
            AreaPublicState.ARMED: "Area is armed",
            AreaPublicState.ALARM: "Area is in alarm",
            AreaPublicState.ENTRY_DELAY: "Area is in entry delay",
            AreaPublicState.EXIT_DELAY: "Area is in exit delay",
            AreaPublicState.ARM_WARNING: "Area is in arm warning",
            AreaPublicState.DEFER_DISARMED: "Area has been defer disarmed (temporarily disarmed)",
            AreaPublicState.DETECTING_ACTIVE_INPUTS: "One or more inputs in this area are currently unsealed",
            AreaPublicState.WALK_TEST_ACTIVE: "A walk test is currently active for this area",
            AreaPublicState.AWAY_ARM: "Area is armed in Full mode",
            AreaPublicState.STAY_ARM: "Area is armed in Perimeter mode",
            AreaPublicState.SLEEP_ARM: "Area is armed in Night mode",
            AreaPublicState.DISARMED: "Area is disarmed",
            AreaPublicState.ARM_READY: "Area is ready to arm (i.e. no active inputs)",
        }

        return [descriptions[state] for state in AreaPublicState if state_value & state]


@dataclass
class ArmInfo:
    """Represents the arm info for an area."""

    entry_delay_secs: int = 0
    exit_delay_secs: int = 0
    defer_arm_delay_secs: int = 0
    area_warn_time_secs: int = 0
    multi_mode_arm_enabled: bool = False

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.entry_delay_secs = kwargs.pop("EntryDelaySecs", 0)
        self.exit_delay_secs = kwargs.pop("ExitDelaySecs", 0)
        self.defer_arm_delay_secs = kwargs.pop("DeferArmDelaySecs", 0)
        self.area_warn_time_secs = kwargs.pop("AreaWarnTimeSecs", 0)
        self.multi_mode_arm_enabled = kwargs.pop("MultiModeArmEnabled", False)

        super().__init__(**kwargs)


@dataclass
class AreaSummaryEntry(InceptionSummaryEntry[AreaPublicState]):
    """Represents a summary entry for an area."""

    arm_info: ArmInfo | None = None

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.entity_info = ReportableShortEntity(**kwargs.pop("EntityInfo"))
        self.arm_info = ArmInfo(**kwargs.pop("ArmInfo", 0))
        super().__init__(**kwargs)


@dataclass
class AreaSummary(InceptionSummary[AreaSummaryEntry]):
    """Represents a summary of areas."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.items = {
            area_id: AreaSummaryEntry(**data)
            for area_id, data in kwargs.pop("Areas").items()
        }
        super().__init__(**kwargs)
