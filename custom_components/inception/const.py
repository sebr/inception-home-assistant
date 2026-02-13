"""Constants for inception."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "inception"
ATTRIBUTION = "Data provided by InnerRange Inception"
MANUFACTURER = "InnerRange"

# Events
EVENT_REVIEW_EVENT = f"{DOMAIN}_review_event"

# Options
CONF_REQUIRE_PIN_CODE = "require_pin_code"
CONF_REQUIRE_CODE_TO_ARM = "require_code_to_arm"
DEFAULT_REQUIRE_PIN_CODE = True
DEFAULT_REQUIRE_CODE_TO_ARM = False
