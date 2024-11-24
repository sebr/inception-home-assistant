"""DataUpdateCoordinator for inception."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.inception.api import InceptionApiClient

from .const import DOMAIN, LOGGER
from .data import InceptionApiData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import InceptionConfigEntry

_LOGGER = logging.getLogger(__name__)


class InceptionUpdateCoordinator(DataUpdateCoordinator[InceptionApiData]):
    """Class to manage fetching data from the API."""

    config_entry: InceptionConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: InceptionConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
            always_update=False,
        )
        self.config_entry = entry
        self._client = InceptionApiClient(
            token=entry.data[CONF_TOKEN],
            host=entry.data[CONF_HOST],
            session=async_get_clientsession(hass),
        )

        self.monitor_connected: bool = False

    async def _async_update_data(self) -> InceptionApiData:
        """Fetch data from the API."""
        if not self.monitor_connected:
            _LOGGER.debug(
                "Connecting to Inception",
            )
            await self._client.connect()
            self._client.register_data_callback(self.callback)
            self.monitor_connected = True
        try:
            data = await self._client.get_status()
            _LOGGER.debug("Data fetched: %s", data)
            return data
        except Exception as err:
            _LOGGER.debug("Failed to fetch data: %s", err)
            raise UpdateFailed(err) from err

    @callback
    def callback(self, data: InceptionApiData) -> None:
        """Process long-poll callbacks and write them to the DataUpdateCoordinator."""
        _LOGGER.debug(
            "Long poll update: %s",
            data,
        )
        self.async_set_updated_data(data)
