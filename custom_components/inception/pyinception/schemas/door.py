# ruff: noqa: E501 ANN003

"""Inception Door schemas."""

from dataclasses import dataclass
from enum import Enum

from .entities import (
    InceptionPublicState,
    InceptionSummary,
    InceptionSummaryEntry,
    ReportableShortEntity,
)


class DoorControlType(Enum):
    """Inception door control types."""

    LOCK = 0
    UNLOCK = 1
    OPEN = 2
    TIMED_UNLOCK = 3
    LOCKOUT = 4
    REINSTATE = 5


class DoorPublicState(InceptionPublicState):
    """Door public states."""

    UNLOCKED = 0x001
    OPEN = 0x002
    LOCKED_OUT = 0x004
    FORCED = 0x008
    HELD_OPEN_WARNING = 0x010
    HELD_OPEN_TOO_LONG = 0x020
    BREAKGLASS = 0x040
    READER_TAMPER = 0x080
    LOCKED = 0x100
    CLOSED = 0x200
    HELD_RESPONSE_MUTED = 0x400
    BATTERY_LOW = 0x800
    LOCK_OFFLINE = 0x1000

    @staticmethod
    def get_state_description(state_value: int) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        descriptions = {
            DoorPublicState.UNLOCKED: "Door is unlocked",
            DoorPublicState.OPEN: "Door is open",
            DoorPublicState.LOCKED_OUT: "Door is locked out",
            DoorPublicState.FORCED: "Door has been forced open",
            DoorPublicState.HELD_OPEN_WARNING: "Door has nearly been held open too long",
            DoorPublicState.HELD_OPEN_TOO_LONG: "Door has been held open too long",
            DoorPublicState.BREAKGLASS: "Door's breakglass detector has been triggered",
            DoorPublicState.READER_TAMPER: "A reader connected to the door has been tampered with",
            DoorPublicState.LOCKED: "Door is locked",
            DoorPublicState.CLOSED: "Door is closed",
            DoorPublicState.HELD_RESPONSE_MUTED: "Door's Held Open response has been muted by a user",
            DoorPublicState.BATTERY_LOW: "Door Wireless Lock has Low Battery",
            DoorPublicState.LOCK_OFFLINE: "Door Wireless Lock Offline",
        }

        return [descriptions[state] for state in DoorPublicState if state_value & state]


@dataclass
class DoorSummaryEntry(InceptionSummaryEntry[DoorPublicState]):
    """Represents a summary entry for an input."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.entity_info = ReportableShortEntity(**kwargs.pop("EntityInfo"))
        super().__init__(**kwargs)


@dataclass
class DoorSummary(InceptionSummary[DoorSummaryEntry]):
    """Represents a summary of doors."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.items = {
            door_id: DoorSummaryEntry(**data)
            for door_id, data in kwargs.pop("Doors").items()
        }
        super().__init__(**kwargs)
