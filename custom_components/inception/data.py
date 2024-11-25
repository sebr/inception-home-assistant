"""Custom types for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import InceptionUpdateCoordinator
    from .pyinception.api import InceptionApiClient


type InceptionConfigEntry = ConfigEntry[InceptionEntryData]


@dataclass
class InceptionEntryData:
    """Data for the Inception integration."""

    client: InceptionApiClient
    coordinator: InceptionUpdateCoordinator
    integration: Integration
