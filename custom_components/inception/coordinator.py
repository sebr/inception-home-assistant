"""DataUpdateCoordinator for inception."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_HOST, CONF_TOKEN, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, EVENT_REVIEW_EVENT, LOGGER
from .pyinception.api import InceptionApiClient
from .pyinception.data import InceptionApiData
from .pyinception.message_categories import get_message_description

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
            await self.api.connect()
            self.api.register_data_callback(self.data_callback)
            self.api.register_review_event_callback(self.review_event_callback)
            self.monitor_connected = True

        return data

    @callback
    def data_callback(self, data: InceptionApiData) -> None:
        """Process long-poll callbacks and write them to the DataUpdateCoordinator."""
        self.async_set_updated_data(data)

    @callback
    def review_event_callback(self, event_data: dict[str, Any]) -> None:
        """Process review event callbacks and emit Home Assistant events."""
        # Get message description from MessageID
        message_category = event_data.get("MessageCategory", 0)
        message_description = get_message_description(message_category)

        # Create a clean event data structure for Home Assistant
        event_payload = {
            "event_id": event_data.get("ID"),
            "event_type": event_data.get("MessageType"),
            "description": event_data.get("Description"),
            "message_category": message_category,
            "message_description": message_description,
            "when": event_data.get("When"),
            "who": event_data.get("Who"),
            "what": event_data.get("What"),
            "where": event_data.get("Where"),
            "when_ticks": event_data.get("WhenTicks"),
        }

        # Remove None values to keep the event clean
        event_payload = {k: v for k, v in event_payload.items() if v is not None}

        # Fire the Home Assistant event
        self.hass.bus.async_fire(
            event_type=EVENT_REVIEW_EVENT,
            event_data=event_payload,
        )

        LOGGER.debug(
            "Emitted %s event: %s - %s",
            EVENT_REVIEW_EVENT,
            event_payload.get("event_type", "Unknown"),
            event_payload.get("description", "No description"),
        )

    async def start_review_listener(self, categories: list[str]) -> None:
        """Start the review event listener with specific categories."""
        try:
            LOGGER.debug(
                "Starting review event listener for categories: %s", categories
            )
            await self.api.start_review_listener(categories)
            LOGGER.info("Review event listener started for categories: %s", categories)
        except Exception as err:
            LOGGER.error("Failed to start review event listener: %s", err)
            raise

    async def stop_review_listener(self) -> None:
        """Stop the review event listener."""
        try:
            LOGGER.debug("Stopping review event listener")
            await self.api.stop_review_listener()
            LOGGER.info("Review event listener stopped")
        except Exception as err:
            LOGGER.error("Failed to stop review event listener: %s", err)
            raise

    async def update_review_listener_from_switches(self) -> None:
        """Update review listener based on current switch states."""
        # Check if global switch is enabled
        if not getattr(self, "_review_events_global_enabled", False):
            LOGGER.debug("Global review events switch is disabled, stopping listener")
            await self.stop_review_listener()
            return

        # Get enabled categories from storage
        enabled_categories = await self._get_enabled_categories_from_storage()

        if not enabled_categories:
            LOGGER.warning(
                "Review event listener global switch is enabled but no categories are "
                "selected. Please enable at least one category (System, Audit, Access, "
                "Security, Hardware)."
            )
            await self.stop_review_listener()
            return

        # Start/update the listener with enabled categories
        await self.start_review_listener(enabled_categories)

    async def _get_enabled_categories_from_storage(self) -> list[str]:
        """Get enabled categories from storage."""
        from homeassistant.helpers.storage import Store

        store = Store(
            self.hass,
            version=1,
            key=f"{DOMAIN}.{self.config_entry.entry_id}.review_events",
        )

        stored_data = await store.async_load() or {}
        categories = ["System", "Audit", "Access", "Security", "Hardware"]

        return [
            category
            for category in categories
            if stored_data.get(f"{category.lower()}_enabled", False)
        ]
