# ruff: noqa: E501

# class AreaPublicStates:
#     ARMED = 0x001
#     DETECTING_ACTIVE_INPUTS = 0x040
#     STAY_ARM = 0x200

#     @staticmethod
#     def get_active_states(state_value):
#         active_states = []
#         if state_value & AreaPublicStates.ARMED:
#             active_states.append("Armed")
#         if state_value & AreaPublicStates.DETECTING_ACTIVE_INPUTS:
#             active_states.append("DetectingActiveInputs")
#         if state_value & AreaPublicStates.STAY_ARM:
#             active_states.append("StayArm")
#         return active_states


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
