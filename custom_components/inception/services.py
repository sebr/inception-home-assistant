"""Service handlers for the Inception integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from .coordinator import InceptionUpdateCoordinator

SERVICE_GET_REVIEW_EVENTS = "get_review_events"

ATTR_ENTRY_ID = "entry_id"
ATTR_LIMIT = "limit"
ATTR_OFFSET = "offset"
ATTR_DIRECTION = "direction"
ATTR_START = "start"
ATTR_END = "end"
ATTR_CATEGORY_FILTER = "category_filter"
ATTR_MESSAGE_TYPE_ID_FILTER = "message_type_id_filter"
ATTR_INVOLVED_ENTITY_ID_FILTER = "involved_entity_id_filter"
ATTR_REFERENCE_ID = "reference_id"
ATTR_REFERENCE_TIME = "reference_time"

REVIEW_CATEGORIES = ["System", "Audit", "Access", "Security", "Hardware"]

GET_REVIEW_EVENTS_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_LIMIT): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
        vol.Optional(ATTR_OFFSET): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(ATTR_DIRECTION): vol.In(["asc", "desc"]),
        vol.Optional(ATTR_START): cv.string,
        vol.Optional(ATTR_END): cv.string,
        vol.Optional(ATTR_CATEGORY_FILTER): vol.All(
            cv.ensure_list, [vol.In(REVIEW_CATEGORIES)]
        ),
        vol.Optional(ATTR_MESSAGE_TYPE_ID_FILTER): vol.All(
            cv.ensure_list, [vol.Coerce(int)]
        ),
        vol.Optional(ATTR_INVOLVED_ENTITY_ID_FILTER): vol.All(
            cv.ensure_list, [cv.string]
        ),
        vol.Optional(ATTR_REFERENCE_ID): cv.string,
        vol.Optional(ATTR_REFERENCE_TIME): vol.All(vol.Coerce(int), vol.Range(min=0)),
    }
)


def _resolve_coordinator(
    hass: HomeAssistant, entry_id: str | None
) -> InceptionUpdateCoordinator:
    """Return the coordinator for ``entry_id`` (or the only loaded one)."""
    coordinators: dict[str, InceptionUpdateCoordinator] = hass.data.get(DOMAIN, {})

    if not coordinators:
        msg = "No Inception integrations are configured."
        raise ServiceValidationError(msg)

    if entry_id is not None:
        coordinator = coordinators.get(entry_id)
        if coordinator is None:
            msg = f"No Inception integration found for entry_id '{entry_id}'."
            raise ServiceValidationError(msg)
        return coordinator

    if len(coordinators) > 1:
        msg = (
            "Multiple Inception integrations are configured; "
            "provide 'entry_id' to select one."
        )
        raise ServiceValidationError(msg)

    return next(iter(coordinators.values()))


@callback
def async_register_services(hass: HomeAssistant) -> None:
    """Register Inception domain services. Safe to call multiple times."""
    if hass.services.has_service(DOMAIN, SERVICE_GET_REVIEW_EVENTS):
        return

    async def async_get_review_events(call: ServiceCall) -> ServiceResponse:
        """Query historical review events from the Inception controller."""
        coordinator = _resolve_coordinator(hass, call.data.get(ATTR_ENTRY_ID))

        kwargs: dict[str, Any] = {
            "limit": call.data.get(ATTR_LIMIT),
            "offset": call.data.get(ATTR_OFFSET),
            "direction": call.data.get(ATTR_DIRECTION),
            "start": call.data.get(ATTR_START),
            "end": call.data.get(ATTR_END),
            "category_filter": call.data.get(ATTR_CATEGORY_FILTER),
            "message_type_id_filter": call.data.get(ATTR_MESSAGE_TYPE_ID_FILTER),
            "involved_entity_id_filter": call.data.get(ATTR_INVOLVED_ENTITY_ID_FILTER),
            "reference_id": call.data.get(ATTR_REFERENCE_ID),
            "reference_time": call.data.get(ATTR_REFERENCE_TIME),
        }

        try:
            events = await coordinator.api.get_review_events(**kwargs)
        except Exception as err:
            LOGGER.exception("Failed to fetch review events")
            msg = f"Failed to fetch review events: {err}"
            raise HomeAssistantError(msg) from err

        return {"events": events, "count": len(events)}

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_REVIEW_EVENTS,
        async_get_review_events,
        schema=GET_REVIEW_EVENTS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


@callback
def async_unregister_services(hass: HomeAssistant) -> None:
    """Remove Inception domain services when the last entry unloads."""
    if hass.data.get(DOMAIN):
        return
    hass.services.async_remove(DOMAIN, SERVICE_GET_REVIEW_EVENTS)
