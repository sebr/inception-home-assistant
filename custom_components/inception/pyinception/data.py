"""Contains data classes for the Inception API."""

from dataclasses import dataclass, field

from .schemas.area import AreaSummary
from .schemas.door import DoorSummary
from .schemas.input import InputSummary
from .schemas.output import OutputSummary
from .schemas.time_period import TimePeriodSummary


@dataclass
class InceptionApiData:
    """Container for data fetched from the Inception API."""

    inputs: InputSummary
    doors: DoorSummary
    areas: AreaSummary
    outputs: OutputSummary
    # Time periods are only present on controllers whose firmware exposes the
    # `/control/time-period/summary` endpoint; default to an empty summary so
    # the other entity types keep working when it is absent.
    time_periods: TimePeriodSummary = field(
        default_factory=lambda: TimePeriodSummary(TimePeriods={})
    )
