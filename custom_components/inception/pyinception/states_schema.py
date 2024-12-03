# ruff: noqa: E501


from enum import IntFlag


class InputPublicStates(IntFlag):
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
            InputPublicStates.ACTIVE: "Input is active/unsealed",
            InputPublicStates.TAMPER: "Input has been tampered with",
            InputPublicStates.ISOLATED: "Input is temporarily or permanently isolated from the system (bypassed)",
            InputPublicStates.MASK: "Input is being masked/blocked",
            InputPublicStates.LOW_BATTERY: "Input is reporting low battery (RF detector)",
            InputPublicStates.POLL_FAILED: "Failed to poll the input (RF detector)",
            InputPublicStates.SEALED: "Input is inactive/sealed",
            InputPublicStates.WIRELESS_DOOR_BATTERY_LOW: "Input is reporting low battery (Wireless Door)",
            InputPublicStates.WIRELESS_DOOR_LOCK_OFFLINE: "Input is reporting lock offline (Wireless Door)",
        }

        return [
            descriptions[state] for state in InputPublicStates if state_value & state
        ]

    @staticmethod
    def get_state(state_value: int) -> bool:
        """Get the state of the input."""
        return bool(state_value & InputPublicStates.ACTIVE)


class DoorPublicStates(IntFlag):
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
            DoorPublicStates.UNLOCKED: "Door is unlocked",
            DoorPublicStates.OPEN: "Door is open",
            DoorPublicStates.LOCKED_OUT: "Door is locked out",
            DoorPublicStates.FORCED: "Door has been forced open",
            DoorPublicStates.HELD_OPEN_WARNING: "Door has nearly been held open too long",
            DoorPublicStates.HELD_OPEN_TOO_LONG: "Door has been held open too long",
            DoorPublicStates.BREAKGLASS: "Door's breakglass detector has been triggered",
            DoorPublicStates.READER_TAMPER: "A reader connected to the door has been tampered with",
            DoorPublicStates.LOCKED: "Door is locked",
            DoorPublicStates.CLOSED: "Door is closed",
            DoorPublicStates.HELD_RESPONSE_MUTED: "Door's Held Open response has been muted by a user",
            DoorPublicStates.BATTERY_LOW: "Door Wireless Lock has Low Battery",
            DoorPublicStates.LOCK_OFFLINE: "Door Wireless Lock Offline",
        }

        return [
            descriptions[state] for state in DoorPublicStates if state_value & state
        ]


class OutputPublicStates(IntFlag):
    """Output public states."""

    ON = 0x001
    OFF = 0x002

    @staticmethod
    def get_state_description(state_value: int) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        descriptions = {
            OutputPublicStates.ON: "Output is active",
            OutputPublicStates.OFF: "Output is inactive",
        }

        return [
            descriptions[state] for state in OutputPublicStates if state_value & state
        ]


class AreaPublicStates(IntFlag):
    """Area public states."""

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
            AreaPublicStates.ARMED: "Area is armed",
            AreaPublicStates.ALARM: "Area is in alarm",
            AreaPublicStates.ENTRY_DELAY: "Area is in entry delay",
            AreaPublicStates.EXIT_DELAY: "Area is in exit delay",
            AreaPublicStates.ARM_WARNING: "Area is in arm warning",
            AreaPublicStates.DEFER_DISARMED: "Area has been defer disarmed (temporarily disarmed)",
            AreaPublicStates.DETECTING_ACTIVE_INPUTS: "One or more inputs in this area are currently unsealed",
            AreaPublicStates.WALK_TEST_ACTIVE: "A walk test is currently active for this area",
            AreaPublicStates.AWAY_ARM: "Area is armed in Full mode",
            AreaPublicStates.STAY_ARM: "Area is armed in Perimeter mode",
            AreaPublicStates.SLEEP_ARM: "Area is armed in Night mode",
            AreaPublicStates.DISARMED: "Area is disarmed",
            AreaPublicStates.ARM_READY: "Area is ready to arm (i.e. no active inputs)",
        }

        return [
            descriptions[state] for state in AreaPublicStates if state_value & state
        ]
