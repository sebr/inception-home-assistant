# ruff: noqa: E501 ANN003

"""Inception Input schemas."""

from dataclasses import dataclass
from enum import IntEnum

from .entities import (
    InceptionPublicState,
    InceptionSummary,
    InceptionSummaryEntry,
    ReportableShortEntity,
)


class InputType(IntEnum):
    """Inception input types."""

    UNKNOWN = 0
    DETECTOR = 1
    SWITCH = 2
    LOGICAL = 3
    ANALOG = 4
    RF_DEVICE = 5
    WIRELESS_DOOR_HEALTH = 6


class InputPublicState(InceptionPublicState):
    """Input public states."""

    ACTIVE = 0x001
    TAMPER = 0x002
    ISOLATED = 0x004
    MASK = 0x008
    LOW_BATTERY = 0x010
    POLL_FAILED = 0x020
    SEALED = 0x040
    WIRELESS_DOOR_BATTERY_LOW = 0x080
    WIRELESS_DOOR_LOCK_OFFLINE = 0x100

    @staticmethod
    def get_state_description(state_value: int) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        descriptions = {
            InputPublicState.ACTIVE: "Input is active/unsealed",
            InputPublicState.TAMPER: "Input has been tampered with",
            InputPublicState.ISOLATED: "Input is temporarily or permanently isolated from the system (bypassed)",
            InputPublicState.MASK: "Input is being masked/blocked",
            InputPublicState.LOW_BATTERY: "Input is reporting low battery (RF detector)",
            InputPublicState.POLL_FAILED: "Failed to poll the input (RF detector)",
            InputPublicState.SEALED: "Input is inactive/sealed",
            InputPublicState.WIRELESS_DOOR_BATTERY_LOW: "Input is reporting low battery (Wireless Door)",
            InputPublicState.WIRELESS_DOOR_LOCK_OFFLINE: "Input is reporting lock offline (Wireless Door)",
        }

        return [
            descriptions[state] for state in InputPublicState if state_value & state
        ]


@dataclass
class InputShortEntity(ReportableShortEntity):
    """Represents a short entity for an input."""

    input_type: InputType
    is_custom_input: bool

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        super().__init__(**kwargs)
        self.input_type = kwargs.pop("InputType", InputType.UNKNOWN)
        self.is_custom_input = kwargs.pop("IsCustomInput", False)


@dataclass
class InputSummaryEntry(InceptionSummaryEntry[InputPublicState]):
    """Represents a summary entry for an input."""

    entity_info: InputShortEntity

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.entity_info = InputShortEntity(**kwargs.pop("EntityInfo"))
        super().__init__(**kwargs)


@dataclass
class InputSummary(InceptionSummary[InputSummaryEntry]):
    """Represents a summary of inputs."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.items = {
            input_id: InputSummaryEntry(**data)
            for input_id, data in kwargs.pop("Inputs").items()
        }
        super().__init__(**kwargs)
