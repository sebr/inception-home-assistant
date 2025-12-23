"""Utility functions for inception."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pyinception.schemas.door import DoorSummaryEntry


def find_matching_door(
    value: str, doors: list[DoorSummaryEntry]
) -> tuple[DoorSummaryEntry | None, str | None]:
    """
    Find a matching door for an input based on its name.

    Patterns:
    - "{Door Name} - {Suffix}"
    - "{Door Name} {Suffix}"

    Returns:
        Tuple of (DoorSummaryEntry, suffix) or (None, None) if no match.

    """
    for door in doors:
        door_name = door.entity_info.name
        if value.startswith(door_name):
            # Check for " - " separator
            if value.startswith(f"{door_name} - "):
                suffix = value[len(door_name) + 3 :]
                return door, suffix
            # Check for space separator
            if value.startswith(f"{door_name} "):
                suffix = value[len(door_name) + 1 :]
                return door, suffix
    return None, None
