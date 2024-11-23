"""DataUpdateCoordinator for inception."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER
from .data import InceptionApiData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import InceptionConfigEntry


class InceptionUpdateCoordinator(DataUpdateCoordinator[InceptionApiData]):
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
        self.monitor_connected: bool = False

    async def _async_setup(self) -> InceptionApiData:
        """Set up the data."""
        i_data = InceptionApiData()
        for i_input in await self._client.get_inputs():
            i_data.inputs[i_input.ID] = i_input
        for i_door in await self._client.get_doors():
            i_data.doors[i_door.ID] = i_door
        for i_area in await self._client.get_areas():
            i_data.areas[i_area.ID] = i_area

        return i_data

    async def _async_update_data(self) -> None:
        """Fetch data from the API."""
        if not self.monitor_connected:
            await self._client.monitor_updates()
            self._client.register_monitor_callback(self.callback)

    @callback
    def callback(self, data: InceptionApiData) -> None:
        """Process websocket callbacks and write them to the DataUpdateCoordinator."""
        self.async_set_updated_data(data)
