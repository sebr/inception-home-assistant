"""Test the Inception trigger platform schema."""

import pytest
import voluptuous as vol

from custom_components.inception.trigger import (
    CONF_MESSAGE_CATEGORY,
    CONF_MESSAGE_VALUE,
    CONF_WHAT_ID,
    CONF_WHERE_ID,
    CONF_WHO_ID,
    TRIGGER_REVIEW_EVENT,
    TRIGGER_SCHEMA,
)


class TestTriggerSchema:
    """Validate TRIGGER_SCHEMA accepts the documented shapes."""

    def test_minimal_config(self) -> None:
        """Platform alone (with defaulted type) is valid."""
        config = TRIGGER_SCHEMA({"platform": "inception"})
        assert config["platform"] == "inception"
        assert config["type"] == TRIGGER_REVIEW_EVENT

    def test_all_filter_fields_accepted(self) -> None:
        """All optional filter fields coerce to lists."""
        config = TRIGGER_SCHEMA(
            {
                "platform": "inception",
                "type": TRIGGER_REVIEW_EVENT,
                CONF_MESSAGE_CATEGORY: "Access",
                CONF_MESSAGE_VALUE: 2011,
                CONF_WHO_ID: "user_1",
                CONF_WHAT_ID: ["door_1", "door_2"],
                CONF_WHERE_ID: "area_1",
            }
        )
        assert config[CONF_MESSAGE_CATEGORY] == ["Access"]
        assert config[CONF_MESSAGE_VALUE] == [2011]
        assert config[CONF_WHO_ID] == ["user_1"]
        assert config[CONF_WHAT_ID] == ["door_1", "door_2"]
        assert config[CONF_WHERE_ID] == ["area_1"]

    def test_invalid_category_rejected(self) -> None:
        """Categories outside the allowed set must fail validation."""
        with pytest.raises(vol.Invalid):
            TRIGGER_SCHEMA(
                {
                    "platform": "inception",
                    CONF_MESSAGE_CATEGORY: "Bogus",
                }
            )

    def test_invalid_type_rejected(self) -> None:
        """Unknown trigger types must fail validation."""
        with pytest.raises(vol.Invalid):
            TRIGGER_SCHEMA({"platform": "inception", "type": "not_a_trigger"})

    def test_message_value_coerces_strings(self) -> None:
        """String message IDs are coerced to ints."""
        config = TRIGGER_SCHEMA(
            {"platform": "inception", CONF_MESSAGE_VALUE: ["5505", "5506"]}
        )
        assert config[CONF_MESSAGE_VALUE] == [5505, 5506]
