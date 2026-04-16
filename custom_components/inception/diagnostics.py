"""Diagnostics support for Inception."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_HOST, CONF_TOKEN

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .coordinator import InceptionUpdateCoordinator
    from .data import InceptionConfigEntry

TO_REDACT = {CONF_TOKEN, CONF_HOST}


def _summary_to_dict(summary: Any) -> dict[str, Any]:
    """Render a schema container to JSON-safe primitives."""
    if summary is None:
        return {}

    items = getattr(summary, "items", None)
    if not isinstance(items, dict):
        return {}

    rendered: dict[str, Any] = {}
    for item_id, item in items.items():
        entry: dict[str, Any] = {}
        entity_info = getattr(item, "entity_info", None)
        if entity_info is not None and is_dataclass(entity_info):
            entry["entity_info"] = asdict(entity_info)
        public_state = getattr(item, "public_state", None)
        if public_state is not None:
            entry["public_state"] = int(public_state)
        extra_fields = getattr(item, "extra_fields", None)
        if extra_fields is not None:
            entry["extra_fields"] = dict(extra_fields)
        rendered[str(item_id)] = entry
    return rendered


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: InceptionConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: InceptionUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    api_data = coordinator.data

    return {
        "entry": {
            "title": entry.title,
            "version": entry.version,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": dict(entry.options),
        },
        "coordinator": {
            "monitor_connected": coordinator.monitor_connected,
            "review_events_global_enabled": coordinator.review_events_global_enabled,
            "last_update_success": coordinator.last_update_success,
        },
        "api_data": {
            "inputs": _summary_to_dict(getattr(api_data, "inputs", None)),
            "doors": _summary_to_dict(getattr(api_data, "doors", None)),
            "areas": _summary_to_dict(getattr(api_data, "areas", None)),
            "outputs": _summary_to_dict(getattr(api_data, "outputs", None)),
        },
    }
