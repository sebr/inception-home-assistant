"""Test review events schemas and functionality."""

from custom_components.inception.pyinception.schemas.review_events import (
    LiveReviewEventsRequest,
    ReviewEventResponse,
    ReviewEventsResponse,
)


class TestLiveReviewEventsRequest:
    """Test LiveReviewEventsRequest class."""

    def test_live_review_events_request_creation_minimal(self) -> None:
        """Test LiveReviewEventsRequest can be created with minimal parameters."""
        request = LiveReviewEventsRequest(
            request_id="LiveReviewEventsRequest",
            reference_id="ref123",
            reference_time=1234567890,
        )
        assert request.request_id == "LiveReviewEventsRequest"
        assert request.reference_id == "ref123"
        assert request.reference_time == 1234567890
        assert request.category_filter is None
        assert request.message_type_id_filter is None

    def test_live_review_events_request_creation_with_filters(self) -> None:
        """Test LiveReviewEventsRequest with filters."""
        request = LiveReviewEventsRequest(
            request_id="LiveReviewEventsRequest",
            reference_id="ref456",
            reference_time=9876543210,
            category_filter=["Access", "Alarm"],
            message_type_id_filter="5501",
        )
        assert request.request_id == "LiveReviewEventsRequest"
        assert request.reference_id == "ref456"
        assert request.reference_time == 9876543210
        assert request.category_filter == ["Access", "Alarm"]
        assert request.message_type_id_filter == "5501"

    def test_get_request_payload_minimal(self) -> None:
        """Test get_request_payload returns correct structure with minimal data."""
        request = LiveReviewEventsRequest(
            request_id="LiveReviewEventsRequest",
            reference_id="ref123",
            reference_time=1234567890,
        )
        payload = request.get_request_payload()

        expected_payload = {
            "ID": "LiveReviewEventsRequest",
            "RequestType": "LiveReviewEvents",
            "InputData": {
                "referenceId": "ref123",
                "referenceTime": 1234567890,
            },
        }
        assert payload == expected_payload

    def test_get_request_payload_with_filters(self) -> None:
        """Test get_request_payload with filters."""
        request = LiveReviewEventsRequest(
            request_id="LiveReviewEventsRequest",
            reference_id="ref456",
            reference_time=9876543210,
            category_filter=["Access", "Alarm"],
            message_type_id_filter="5501",
        )
        payload = request.get_request_payload()

        expected_payload = {
            "ID": "LiveReviewEventsRequest",
            "RequestType": "LiveReviewEvents",
            "InputData": {
                "referenceId": "ref456",
                "referenceTime": 9876543210,
                "categoryFilter": ["Access", "Alarm"],
                "messageTypeIdFilter": "5501",
            },
        }
        assert payload == expected_payload


class TestReviewEventResponse:
    """Test ReviewEventResponse class."""

    def test_review_event_response_creation_minimal(self) -> None:
        """Test ReviewEventResponse can be created with minimal data."""
        event = ReviewEventResponse()
        assert event.event_id == ""
        assert event.event_type == ""
        assert event.timestamp == ""
        assert event.user_id is None
        assert event.area_id is None
        assert event.zone_id is None
        assert event.door_id is None
        assert event.description == ""
        assert event.extra_fields == {}

    def test_review_event_response_creation_full(self) -> None:
        """Test ReviewEventResponse with full data."""
        data = {
            "EventID": "event123",
            "EventType": "DoorAccess",
            "Timestamp": "2023-12-01T10:30:00Z",
            "UserID": "user456",
            "AreaID": "area789",
            "ZoneID": "zone012",
            "DoorID": "door345",
            "Description": "Card access granted",
            "ExtraField1": "value1",
            "ExtraField2": "value2",
        }

        event = ReviewEventResponse(**data)
        assert event.event_id == "event123"
        assert event.event_type == "DoorAccess"
        assert event.timestamp == "2023-12-01T10:30:00Z"
        assert event.user_id == "user456"
        assert event.area_id == "area789"
        assert event.zone_id == "zone012"
        assert event.door_id == "door345"
        assert event.description == "Card access granted"
        assert event.extra_fields == {"ExtraField1": "value1", "ExtraField2": "value2"}

    def test_review_event_response_repr(self) -> None:
        """Test ReviewEventResponse string representation."""
        event = ReviewEventResponse(
            EventID="test123",
            EventType="Access",
            Timestamp="2023-12-01T10:30:00Z",
            Description="Test event",
        )
        repr_str = repr(event)
        assert "ReviewEvent(" in repr_str
        assert "EventID='test123'" in repr_str
        assert "EventType='Access'" in repr_str
        assert "Timestamp='2023-12-01T10:30:00Z'" in repr_str
        assert "Description='Test event'" in repr_str


class TestReviewEventsResponse:
    """Test ReviewEventsResponse class."""

    def test_review_events_response_creation_empty(self) -> None:
        """Test ReviewEventsResponse with no events."""
        response = ReviewEventsResponse()
        assert response.update_time == 0
        assert response.events == []

    def test_review_events_response_creation_with_data(self) -> None:
        """Test ReviewEventsResponse with event data."""
        data = {
            "updateTime": 1234567890,
            "events": [
                {
                    "EventID": "event1",
                    "EventType": "DoorAccess",
                    "Timestamp": "2023-12-01T10:30:00Z",
                    "Description": "Access granted",
                },
                {
                    "EventID": "event2",
                    "EventType": "AlarmTriggered",
                    "Timestamp": "2023-12-01T10:31:00Z",
                    "Description": "Motion detected",
                    "AreaID": "area123",
                },
            ],
        }

        response = ReviewEventsResponse(**data)
        assert response.update_time == 1234567890
        assert len(response.events) == 2

        # Check first event
        event1 = response.events[0]
        assert event1.event_id == "event1"
        assert event1.event_type == "DoorAccess"
        assert event1.description == "Access granted"

        # Check second event
        event2 = response.events[1]
        assert event2.event_id == "event2"
        assert event2.event_type == "AlarmTriggered"
        assert event2.description == "Motion detected"
        assert event2.area_id == "area123"

    def test_review_events_response_repr(self) -> None:
        """Test ReviewEventsResponse string representation."""
        data = {
            "updateTime": 9876543210,
            "events": [
                {"EventID": "event1", "EventType": "Test"},
                {"EventID": "event2", "EventType": "Test"},
                {"EventID": "event3", "EventType": "Test"},
            ],
        }

        response = ReviewEventsResponse(**data)
        repr_str = repr(response)
        assert "ReviewEventsResponse(" in repr_str
        assert "update_time=9876543210" in repr_str
        assert "events_count=3" in repr_str


class TestReviewEventsIntegration:
    """Test integration between review events classes."""

    def test_full_workflow(self) -> None:
        """Test complete workflow from request to response processing."""
        # Create live review events request
        request = LiveReviewEventsRequest(
            request_id="LiveReviewEventsRequest",
            reference_id="ref123",
            reference_time=1701432600,
            category_filter=["Access"],
        )

        # Verify request payload
        payload = request.get_request_payload()
        assert payload["ID"] == "LiveReviewEventsRequest"
        assert payload["RequestType"] == "LiveReviewEvents"
        assert payload["InputData"]["referenceId"] == "ref123"
        assert payload["InputData"]["referenceTime"] == 1701432600
        assert payload["InputData"]["categoryFilter"] == ["Access"]

        # Simulate API response
        api_response_data = {
            "updateTime": 1701432600,
            "events": [
                {
                    "EventID": "evt_001",
                    "EventType": "CardAccess",
                    "Timestamp": "2023-12-01T10:30:00Z",
                    "UserID": "user_123",
                    "DoorID": "door_456",
                    "Description": "Employee card access",
                    "AccessResult": "Granted",
                },
            ],
        }

        # Parse response
        response = ReviewEventsResponse(**api_response_data)

        # Verify response structure
        assert response.update_time == 1701432600
        assert len(response.events) == 1

        event = response.events[0]
        assert event.event_id == "evt_001"
        assert event.event_type == "CardAccess"
        assert event.user_id == "user_123"
        assert event.door_id == "door_456"
        assert event.description == "Employee card access"
        assert event.extra_fields["AccessResult"] == "Granted"
