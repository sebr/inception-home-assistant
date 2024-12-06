# ruff: noqa: E501  # noqa: D100

from abc import abstractmethod
from enum import Enum, IntFlag

"""https://skytunnel.com.au/Inception/API_SAMPLE/ApiModelDoc"""


class InputType(Enum):
    """Inception input types."""

    UNKNOWN = 0
    DETECTOR = 1
    SWITCH = 2
    LOGICAL = 3
    ANALOG = 4
    RF_DEVICE = 5
    WIRELESS_DOOR_HEALTH = 6


class DoorControlType(Enum):
    """Inception door control types."""

    LOCK = 0
    UNLOCK = 1
    OPEN = 2
    TIMED_UNLOCK = 3
    LOCKOUT = 4
    REINSTATE = 5


class InceptionPublicState(IntFlag):
    """Inception public states."""

    @staticmethod
    @abstractmethod
    def get_state_description(_state_value: int) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        return []

    def __str__(self) -> str:
        """Return the name or value of the state."""
        if self.name is None:
            return str(self.value)
        return self.name.replace("_", " ").capitalize()


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


class OutputPublicState(InceptionPublicState):
    """Output public states."""

    ON = 0x001
    OFF = 0x002

    @staticmethod
    def get_state_description(state_value: int) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        descriptions = {
            OutputPublicState.ON: "Output is active",
            OutputPublicState.OFF: "Output is inactive",
        }

        return [
            descriptions[state] for state in OutputPublicState if state_value & state
        ]


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
