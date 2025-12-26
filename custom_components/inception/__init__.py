"""
Custom integration to integrate InnerRange Inception with Home Assistant.

For more details about this integration, please refer to
https://github.com/sebr/inception-home-assistant
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.storage import Store

from .const import DOMAIN
from .coordinator import InceptionUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import InceptionConfigEntry

PLATFORMS: list[Platform] = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.LOCK,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = InceptionUpdateCoordinator(
        hass=hass,
        entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    # Unload platforms first
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False

    # Clean up the coordinator
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_unload()

    # Remove the coordinator from hass.data
    hass.data[DOMAIN].pop(entry.entry_id)

    return True


async def async_remove_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
) -> None:
    """Handle removal of an entry (when deleted by user)."""
    # Clean up stored review events settings
    store = Store(
        hass,
        version=1,
        key=f"{DOMAIN}.{entry.entry_id}.review_events",
    )
    await store.async_remove()


async def async_reload_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
