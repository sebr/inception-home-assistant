"""
Trigger platform for the Inception integration.

Exposes an ``inception`` trigger that fires on ``inception_review_event``
events emitted by the integration's coordinator. Optional filter fields
narrow the trigger to specific event categories or entities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.const import CONF_PLATFORM
from homeassistant.core import CALLBACK_TYPE, HassJob, HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, EVENT_REVIEW_EVENT

if TYPE_CHECKING:
    from homeassistant.core import Event
    from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
    from homeassistant.helpers.typing import ConfigType

CONF_EVENT_TYPE = "type"
CONF_MESSAGE_CATEGORY = "message_category"
CONF_MESSAGE_VALUE = "message_value"
CONF_WHO_ID = "who_id"
CONF_WHAT_ID = "what_id"
CONF_WHERE_ID = "where_id"

TRIGGER_REVIEW_EVENT = "review_event"

MESSAGE_CATEGORIES = ["System", "Audit", "Access", "Security", "Hardware"]

TRIGGER_SCHEMA = cv.TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_PLATFORM): DOMAIN,
        vol.Required(CONF_EVENT_TYPE, default=TRIGGER_REVIEW_EVENT): vol.In(
            [TRIGGER_REVIEW_EVENT]
        ),
        vol.Optional(CONF_MESSAGE_CATEGORY): vol.All(
            cv.ensure_list, [vol.In(MESSAGE_CATEGORIES)]
        ),
        vol.Optional(CONF_MESSAGE_VALUE): vol.All(cv.ensure_list, [vol.Coerce(int)]),
        vol.Optional(CONF_WHO_ID): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_WHAT_ID): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_WHERE_ID): vol.All(cv.ensure_list, [cv.string]),
    }
)


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Listen for inception_review_event events matching the configured filters."""
    trigger_data = trigger_info["trigger_data"]

    categories: set[str] | None = (
        set(config[CONF_MESSAGE_CATEGORY]) if CONF_MESSAGE_CATEGORY in config else None
    )
    message_values: set[int] | None = (
        set(config[CONF_MESSAGE_VALUE]) if CONF_MESSAGE_VALUE in config else None
    )
    who_ids: set[str] | None = (
        set(config[CONF_WHO_ID]) if CONF_WHO_ID in config else None
    )
    what_ids: set[str] | None = (
        set(config[CONF_WHAT_ID]) if CONF_WHAT_ID in config else None
    )
    where_ids: set[str] | None = (
        set(config[CONF_WHERE_ID]) if CONF_WHERE_ID in config else None
    )

    job = HassJob(action)

    async def handle_event(event: Event) -> None:
        data = event.data
        if categories is not None and data.get("message_category") not in categories:
            return
        if (
            message_values is not None
            and data.get("message_value") not in message_values
        ):
            return
        if who_ids is not None and data.get("who_id") not in who_ids:
            return
        if what_ids is not None and data.get("what_id") not in what_ids:
            return
        if where_ids is not None and data.get("where_id") not in where_ids:
            return

        task = hass.async_run_hass_job(
            job,
            {
                "trigger": {
                    **trigger_data,
                    "platform": DOMAIN,
                    "event": event,
                    "description": (
                        f"Inception review event: {data.get('description', '')}"
                    ),
                }
            },
            event.context,
        )
        if task:
            await task

    return hass.bus.async_listen(EVENT_REVIEW_EVENT, handle_event)
