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
SERVICE_BADGE_CREDENTIAL = "badge_credential"
SERVICE_SEND_PIN = "send_pin"
SERVICE_GET_ATTACHED_READERS = "get_attached_readers"

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
ATTR_READER_ID = "reader_id"
ATTR_DOOR_ID = "door_id"
ATTR_CREDENTIAL_TEMPLATE = "credential_template"
ATTR_CARD_NUMBER = "card_number"
ATTR_PIN = "pin"

REVIEW_CATEGORIES = ["System", "Audit", "Access", "Security", "Hardware"]

BADGE_CREDENTIAL_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_READER_ID): cv.string,
        vol.Required(ATTR_CREDENTIAL_TEMPLATE): cv.string,
        vol.Required(ATTR_CARD_NUMBER): cv.string,
    }
)

SEND_PIN_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_READER_ID): cv.string,
        vol.Required(ATTR_PIN): cv.string,
    }
)

GET_ATTACHED_READERS_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Required(ATTR_DOOR_ID): cv.string,
    }
)

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

    async def async_badge_credential(call: ServiceCall) -> ServiceResponse:
        """Virtually badge a credential at a door reader."""
        coordinator = _resolve_coordinator(hass, call.data.get(ATTR_ENTRY_ID))

        try:
            activity_id = await coordinator.api.badge_credential_at_reader(
                reader_id=call.data[ATTR_READER_ID],
                credential_template=call.data[ATTR_CREDENTIAL_TEMPLATE],
                card_number=call.data[ATTR_CARD_NUMBER],
            )
        except Exception as err:
            LOGGER.exception("Failed to submit badge credential activity")
            msg = f"Failed to submit badge credential activity: {err}"
            raise HomeAssistantError(msg) from err

        return {"activity_id": activity_id}

    async def async_send_pin(call: ServiceCall) -> ServiceResponse:
        """Virtually present a User PIN at a door reader."""
        coordinator = _resolve_coordinator(hass, call.data.get(ATTR_ENTRY_ID))

        try:
            activity_id = await coordinator.api.send_pin_to_reader(
                reader_id=call.data[ATTR_READER_ID],
                pin=call.data[ATTR_PIN],
            )
        except Exception as err:
            LOGGER.exception("Failed to submit PIN activity")
            msg = f"Failed to submit PIN activity: {err}"
            raise HomeAssistantError(msg) from err

        return {"activity_id": activity_id}

    async def async_get_attached_readers(call: ServiceCall) -> ServiceResponse:
        """List readers attached to a door."""
        coordinator = _resolve_coordinator(hass, call.data.get(ATTR_ENTRY_ID))

        try:
            readers = await coordinator.api.get_attached_readers(
                door_id=call.data[ATTR_DOOR_ID],
            )
        except Exception as err:
            LOGGER.exception("Failed to fetch attached readers")
            msg = f"Failed to fetch attached readers: {err}"
            raise HomeAssistantError(msg) from err

        return {"readers": readers, "count": len(readers)}

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
    hass.services.async_register(
        DOMAIN,
        SERVICE_BADGE_CREDENTIAL,
        async_badge_credential,
        schema=BADGE_CREDENTIAL_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_PIN,
        async_send_pin,
        schema=SEND_PIN_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_ATTACHED_READERS,
        async_get_attached_readers,
        schema=GET_ATTACHED_READERS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


@callback
def async_unregister_services(hass: HomeAssistant) -> None:
    """Remove Inception domain services when the last entry unloads."""
    if hass.data.get(DOMAIN):
        return
    hass.services.async_remove(DOMAIN, SERVICE_GET_REVIEW_EVENTS)
    hass.services.async_remove(DOMAIN, SERVICE_BADGE_CREDENTIAL)
    hass.services.async_remove(DOMAIN, SERVICE_SEND_PIN)
    hass.services.async_remove(DOMAIN, SERVICE_GET_ATTACHED_READERS)
