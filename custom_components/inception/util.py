"""Utility functions for inception."""

from __future__ import annotations


def extract_door_name_from_input(input_name: str) -> tuple[str | None, str | None]:
    """
    Extract door name from input name if it matches a known pattern.

    Patterns:
    - "{Door Name} - {Event Type}" -> returns ("Door Name", "Event Type")
    - "{Door Name} {Suffix}" -> returns ("Door Name", "Suffix")

    Returns:
        Tuple of (door_name, suffix) or (None, None) if no pattern matches

    """
    # Check for pattern with dash separator
    if " - " in input_name:
        parts = input_name.split(" - ", 1)
        return (parts[0], parts[1])

    # Check for known suffix patterns (case-insensitive)
    door_input_suffixes = [" Reed"]
    for suffix in door_input_suffixes:
        if input_name.lower().endswith(suffix.lower()):
            door_name = input_name[: -len(suffix)]
            # Return the actual suffix from the original case (strip leading space)
            return (door_name, suffix.strip())

    return (None, None)
