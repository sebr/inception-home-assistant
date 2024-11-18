"""DataUpdateCoordinator for inception."""

from __future__ import annotations

from ast import In
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import InceptionConfigEntry
    from .schema import Area, Door, Input, Output


@dataclass
class InceptionData:
    """Container for data fetched from the Inception API."""

    inputs: dict[str, Input] = field(default_factory=dict)
    doors: dict[str, Door] = field(default_factory=dict)
    areas: dict[str, Area] = field(default_factory=dict)
    outputs: dict[str, Output] = field(default_factory=dict)


class InceptionUpdateCoordinator(DataUpdateCoordinator[InceptionData]):
    """Class to manage fetching data from the API."""

    config_entry: InceptionConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
            always_update=False,
        )
        self._client = self.config_entry.runtime_data.client

    async def _async_setup(self) -> InceptionData:
        """Set up the data."""
        i_data = InceptionData()
        for i_input in await self._client.get_inputs():
            i_data.inputs[i_input.ID] = i_input
        for i_door in await self._client.get_doors():
            i_data.doors[i_door.ID] = i_door
        for i_area in await self._client.get_areas():
            i_data.areas[i_area.ID] = i_area

        return i_data

    async def _async_update_data(self) -> InceptionData:
        """Fetch data from the API."""
        r = self._client.monitor_updates()
        print(r)

        return InceptionData()
