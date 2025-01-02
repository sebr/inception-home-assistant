# ruff: noqa: E501 ANN003

"""Inception Output schemas."""

from dataclasses import dataclass

from .entities import (
    InceptionPublicState,
    InceptionSummary,
    InceptionSummaryEntry,
    ReportableShortEntity,
)


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


@dataclass
class OutputSummaryEntry(InceptionSummaryEntry[OutputPublicState]):
    """Represents a summary entry for an output."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.entity_info = ReportableShortEntity(**kwargs.pop("EntityInfo"))
        super().__init__(**kwargs)


@dataclass
class OutputSummary(InceptionSummary[OutputSummaryEntry]):
    """Represents a summary of outputs."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.items = {
            output_id: OutputSummaryEntry(**data)
            for output_id, data in kwargs.pop("Outputs").items()
        }
        super().__init__(**kwargs)
