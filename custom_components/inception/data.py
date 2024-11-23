"""Custom types for inception."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .schema import Area, Door, Input, Output

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import InceptionApiClient
    from .coordinator import InceptionUpdateCoordinator


type InceptionConfigEntry = ConfigEntry[InceptionData]


@dataclass
class InceptionData:
    """Data for the Inception integration."""

    client: InceptionApiClient
    coordinator: InceptionUpdateCoordinator
    integration: Integration


@dataclass
class InceptionApiData:
    """Container for data fetched from the Inception API."""

    inputs: dict[str, Input] = field(default_factory=dict)
    doors: dict[str, Door] = field(default_factory=dict)
    areas: dict[str, Area] = field(default_factory=dict)
    outputs: dict[str, Output] = field(default_factory=dict)
