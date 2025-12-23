"""Tests for the utility functions of the Inception integration."""

from unittest.mock import Mock

import pytest

from custom_components.inception.util import find_matching_door


def create_mock_door(name: str, door_id: str = "") -> Mock:
    """Create a mock DoorSummaryEntry object for testing."""
    door = Mock()
    door.entity_info = Mock()
    door.entity_info.name = name
    door.entity_info.id = door_id
    return door


@pytest.mark.parametrize(
    ("input_name", "doors", "expected_door_name", "expected_suffix"),
    [
        # Basic match with " - "
        ("Front Door - Reed", [create_mock_door("Front Door")], "Front Door", "Reed"),
        # Basic match with " "
        ("Garage Door Reed", [create_mock_door("Garage Door")], "Garage Door", "Reed"),
        # No match
        ("Living Room Motion", [create_mock_door("Front Door")], None, None),
        # Multiple doors, correct match
        (
            "Back Door - Tamper",
            [create_mock_door("Front Door"), create_mock_door("Back Door")],
            "Back Door",
            "Tamper",
        ),
        # No separator, should not match
        ("FrontDoorReed", [create_mock_door("Front Door")], None, None),
        # Partial match but not at the start
        ("Main Front Door - Reed", [create_mock_door("Front Door")], None, None),
        # Empty input string
        ("", [create_mock_door("Front Door")], None, None),
        # Empty doors list
        ("Front Door - Reed", [], None, None),
        # Door name with special characters
        (
            "Door (Main) - Sensor",
            [create_mock_door("Door (Main)")],
            "Door (Main)",
            "Sensor",
        ),
        # Suffix contains separator
        (
            "Side Door - Part 1 - Part 2",
            [create_mock_door("Side Door")],
            "Side Door",
            "Part 1 - Part 2",
        ),
        # Suffix with only a space
        ("Side Door ", [create_mock_door("Side Door")], "Side Door", ""),
    ],
)
def test_find_matching_door(
    input_name: str,
    doors: list[Mock],
    expected_door_name: str | None,
    expected_suffix: str | None,
) -> None:
    """Test find_matching_door with various scenarios."""
    matched_door, suffix = find_matching_door(input_name, doors)

    if expected_door_name is None:
        assert matched_door is None
        assert suffix is None
    else:
        assert matched_door is not None
        assert matched_door.entity_info.name == expected_door_name
        assert suffix == expected_suffix


def test_find_matching_door_prefix_ambiguity() -> None:
    """
    Test the case where one door name is a prefix of another.

    This test highlights that the current implementation's result depends on the
    order of doors in the list, and it doesn't find the longest match.
    """
    door_short = create_mock_door("Front")
    door_long = create_mock_door("Front Door")
    input_name = "Front Door - Reed"

    # Case 1: Short name comes first, leading to an incorrect greedy match.
    doors_short_first = [door_short, door_long]
    matched_door, suffix = find_matching_door(input_name, doors_short_first)

    assert matched_door.entity_info.name == "Front"
    assert suffix == "Door - Reed"

    # Case 2: Long name comes first, leading to a correct match.
    doors_long_first = [door_long, door_short]
    matched_door_rev, suffix_rev = find_matching_door(input_name, doors_long_first)

    assert matched_door_rev.entity_info.name == "Front Door"
    assert suffix_rev == "Reed"
