"""Custom types for inception."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

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
