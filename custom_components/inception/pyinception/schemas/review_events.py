# ruff: noqa: ANN003, E501

"""Defines the schema for Inception review events responses."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ReviewEventRequest:
    """Request to monitor review events."""

    request_id: str
    time_since_last_update: int

    def __init__(
        self,
        request_id: str,
        time_since_last_update: int,
    ) -> None:
        """Initialize the object."""
        self.request_id = request_id
        self.time_since_last_update = time_since_last_update

    def get_request_payload(self) -> dict[str, Any]:
        """Return the payload for review events request."""
        return {
            "ID": self.request_id,
            "RequestType": "MonitorEvents",
            "InputData": {
                "timeSinceUpdate": self.time_since_last_update,
            },
        }


@dataclass
class ReviewEventResponse:
    """Individual review event response."""

    event_id: str
    event_type: str
    timestamp: str
    user_id: str | None
    area_id: str | None
    zone_id: str | None
    door_id: str | None
    description: str
    extra_fields: dict[str, Any]

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.event_id = kwargs.pop("EventID", "")
        self.event_type = kwargs.pop("EventType", "")
        self.timestamp = kwargs.pop("Timestamp", "")
        self.user_id = kwargs.pop("UserID", None)
        self.area_id = kwargs.pop("AreaID", None)
        self.zone_id = kwargs.pop("ZoneID", None)
        self.door_id = kwargs.pop("DoorID", None)
        self.description = kwargs.pop("Description", "")
        # Collect any extra fields
        self.extra_fields = kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"ReviewEvent(EventID={self.event_id!r}, EventType={self.event_type!r}, "
            f"Timestamp={self.timestamp!r}, Description={self.description!r})"
        )


@dataclass
class ReviewEventsResponse:
    """Review events response from the API."""

    update_time: int
    events: list[ReviewEventResponse]

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.update_time = kwargs.pop("updateTime", 0)
        events_data = kwargs.pop("events", [])
        self.events = [ReviewEventResponse(**event) for event in events_data]

    def __repr__(self) -> str:
        """Return string representation."""
        return f"ReviewEventsResponse(update_time={self.update_time}, events_count={len(self.events)})"
