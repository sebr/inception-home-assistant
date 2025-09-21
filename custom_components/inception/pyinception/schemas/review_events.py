# ruff: noqa: ANN003, E501

"""Defines the schema for Inception review events responses."""

from dataclasses import dataclass
from typing import Any


@dataclass
class LiveReviewEventsRequest:
    """Request to monitor live review events via monitor-updates."""

    request_id: str
    reference_id: str
    reference_time: int
    category_filter: list[str] | None = None
    message_type_id_filter: str | None = None

    def __init__(
        self,
        request_id: str,
        reference_id: str,
        reference_time: int,
        category_filter: list[str] | None = None,
        message_type_id_filter: str | None = None,
    ) -> None:
        """Initialize the object."""
        self.request_id = request_id
        self.reference_id = reference_id
        self.reference_time = reference_time
        self.category_filter = category_filter
        self.message_type_id_filter = message_type_id_filter

    def get_request_payload(self) -> dict[str, Any]:
        """Return the payload for live review events request."""
        input_data = {
            "referenceId": self.reference_id,
            "referenceTime": self.reference_time,
        }

        if self.category_filter:
            input_data["categoryFilter"] = self.category_filter

        if self.message_type_id_filter:
            input_data["messageTypeIdFilter"] = self.message_type_id_filter

        return {
            "ID": self.request_id,
            "RequestType": "LiveReviewEvents",
            "InputData": input_data,
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
