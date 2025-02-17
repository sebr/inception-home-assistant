"""
Custom integration to integrate InnerRange Inception with Home Assistant.

For more details about this integration, please refer to
https://github.com/sebr/inception-home-assistant
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform

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
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
