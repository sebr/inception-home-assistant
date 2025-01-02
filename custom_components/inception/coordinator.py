"""DataUpdateCoordinator for inception."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_HOST, CONF_TOKEN, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.inception.pyinception.api import InceptionApiClient

from .const import DOMAIN, LOGGER
from .pyinception.data import InceptionApiData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import InceptionConfigEntry


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
            always_update=False,
        )
        self.config_entry = entry
        self.api = InceptionApiClient(
            token=entry.data[CONF_TOKEN],
            host=entry.data[CONF_HOST],
            session=async_get_clientsession(hass),
        )

        self.monitor_connected: bool = False

    async def _async_setup(self) -> None:
        self._shutdown_remove_listener = self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_STOP, self._async_shutdown
        )

        return await super()._async_setup()

    async def _async_shutdown(self, _event: Any) -> None:
        """Call from Homeassistant shutdown event."""
        # unset remove listener otherwise calling it would raise an exception
        self._shutdown_remove_listener = None
        await self.async_unload()

    async def async_unload(self) -> None:
        """Stop the update monitor."""
        if self._shutdown_remove_listener:
            self._shutdown_remove_listener()

        await self.api.close()
        self.monitor_connected = False

    async def _async_update_data(self) -> InceptionApiData:
        """Fetch data from the API."""
        try:
            data = await self.api.get_data()
        except Exception as err:
            LOGGER.debug("Failed to fetch data: %s", err)
            LOGGER.exception("Error fetching data from Inception")
            raise UpdateFailed(err) from err

        if not self.monitor_connected:
            LOGGER.debug(
                "Connecting to Inception Monitor",
            )
            # await self.api.connect()
            # self.api.register_data_callback(self.callback)
            self.monitor_connected = True

        return data

    @callback
    def callback(self, data: InceptionApiData) -> None:
        """Process long-poll callbacks and write them to the DataUpdateCoordinator."""
        self.async_set_updated_data(data)
