"""Constants for inception."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "inception"
ATTRIBUTION = "Data provided by InnerRange Inception"
MANUFACTURER = "InnerRange"

# Events
EVENT_REVIEW_EVENT = f"{DOMAIN}_review_event"
