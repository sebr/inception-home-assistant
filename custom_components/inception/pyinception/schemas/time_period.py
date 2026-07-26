# ruff: noqa: ANN003

"""Inception Time Period schemas."""

from dataclasses import dataclass

from .entities import (
    InceptionPublicState,
    InceptionSummary,
    InceptionSummaryEntry,
    ReportableShortEntity,
)


class TimePeriodPublicState(InceptionPublicState):
    """
    Time Period public states.

    A Time Period is Inception's scheduling primitive (e.g. "Business Hours").
    At any moment it is either active or inactive; the ``ACTIVE`` bit is the
    one that matters for a binary sensor. The flag values mirror the Output
    schema's active/inactive convention.
    """

    ACTIVE = 0x001
    INACTIVE = 0x002

    @staticmethod
    def get_state_description(state_value: int) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        descriptions = {
            TimePeriodPublicState.ACTIVE: "Time period is currently active",
            TimePeriodPublicState.INACTIVE: "Time period is currently inactive",
        }

        return [
            descriptions[state]
            for state in TimePeriodPublicState
            if state_value & state
        ]


@dataclass
class TimePeriodSummaryEntry(InceptionSummaryEntry[TimePeriodPublicState]):
    """Represents a summary entry for a time period."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.entity_info = ReportableShortEntity(**kwargs.pop("EntityInfo"))
        super().__init__(**kwargs)


@dataclass
class TimePeriodSummary(InceptionSummary[TimePeriodSummaryEntry]):
    """Represents a summary of time periods."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.items = {
            time_period_id: TimePeriodSummaryEntry(**data)
            for time_period_id, data in kwargs.pop("TimePeriods").items()
        }
        super().__init__(**kwargs)
