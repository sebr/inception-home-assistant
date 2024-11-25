from dataclasses import dataclass, field

from .schema import Area, Door, Input, Output


@dataclass
class InceptionApiData:
    """Container for data fetched from the Inception API."""

    inputs: dict[str, Input] = field(default_factory=dict)
    doors: dict[str, Door] = field(default_factory=dict)
    areas: dict[str, Area] = field(default_factory=dict)
    outputs: dict[str, Output] = field(default_factory=dict)
