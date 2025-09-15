"""Test message categories functionality."""

from __future__ import annotations

from custom_components.inception.pyinception.message_categories import (
    get_message_description,
    get_message_info,
    get_message_string_value,
)


def test_get_message_info_known_message() -> None:
    """Test getting info for a known message ID."""
    info = get_message_info(2006)
    assert info == ("Access_DoorUserAccessGranted", "Door Access Granted for User")


def test_get_message_info_unknown_message() -> None:
    """Test getting info for an unknown message ID."""
    info = get_message_info(99999)
    assert info is None


def test_get_message_info_none() -> None:
    """Test getting info for None message ID."""
    info = get_message_info(None)
    assert info is None


def test_get_message_description_known_message() -> None:
    """Test getting description for a known message ID."""
    description = get_message_description(5001)
    assert description == "Area Armed With Exit Delay by User"


def test_get_message_description_unknown_message() -> None:
    """Test getting description for an unknown message ID."""
    description = get_message_description(99999)
    assert description is None


def test_get_message_description_none() -> None:
    """Test getting description for None message ID."""
    description = get_message_description(None)
    assert description is None


def test_get_message_string_value_known_message() -> None:
    """Test getting string value for a known message ID."""
    string_value = get_message_string_value(3001)
    assert string_value == "Access_CardReadSuccessful"


def test_get_message_string_value_unknown_message() -> None:
    """Test getting string value for an unknown message ID."""
    string_value = get_message_string_value(99999)
    assert string_value is None


def test_get_message_string_value_none() -> None:
    """Test getting string value for None message ID."""
    string_value = get_message_string_value(None)
    assert string_value is None


def test_message_categories_coverage() -> None:
    """Test that we have good coverage of message categories."""
    # Test some key categories are present
    assert get_message_description(0) == "Unknown"
    assert get_message_description(1) == "System Started"
    assert get_message_description(1500) == "Item Created"  # Audit
    assert get_message_description(2000) == "Door Unlocked"  # Access
    assert get_message_description(3001) == "Credential Read Successful"  # Card
    assert get_message_description(5000) == "Area Armed by User"  # Security
    assert get_message_description(10000) == "LAN Module Discovered"  # Hardware
