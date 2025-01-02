"""Contains data classes for the Inception API."""

from dataclasses import dataclass

from .schemas.area import AreaSummary
from .schemas.door import DoorSummary
from .schemas.input import InputSummary
from .schemas.output import OutputSummary


@dataclass
class InceptionApiData:
    """Container for data fetched from the Inception API."""

    inputs: InputSummary
    doors: DoorSummary
    areas: AreaSummary
    outputs: OutputSummary
