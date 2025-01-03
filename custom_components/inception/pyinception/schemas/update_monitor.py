# ruff: noqa: ANN003, E501

"""Defines the schema for various Inception objects and responses."""

from dataclasses import dataclass
from typing import TypeVar

from .entities import InceptionPublicState


@dataclass
class LiveReviewEventsResult:
    """Live Review Events Result from update monitor."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.id = kwargs.pop("ID", "")
        self.description = kwargs.pop("Description", "")
        self.message_category = kwargs.pop("MessageCategory", "")
        self.what = kwargs.pop("What", "")
        self.who = kwargs.pop("Who", "")
        self.where = kwargs.pop("Where", "")
        self.when_ticks = kwargs.pop("WhenTicks", "")
        # Collect any extra fields
        self.extra_fields = kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Input(ID={self.id!r}, Name={self.description!r}, "
            f"What={self.what!r}, Who={self.who!r}, extra_fields={self.extra_fields!r})"
        )


StateType = TypeVar("StateType", bound=InceptionPublicState)


@dataclass
class UpdateMonitorRequest:
    """Request to update monitor."""

    request_id: str
    request_type: str
    state_type: str
    public_state_type: InceptionPublicState
    api_data: str
    time_since_last_update: int

    def __init__(  # noqa: PLR0913
        self,
        request_id: str,
        request_type: str,
        state_type: str,
        public_state_type: InceptionPublicState,
        api_data: str,
        time_since_last_update: int,
    ) -> None:
        """Initialize the object."""
        self.request_id = request_id
        self.request_type = request_type
        self.state_type = state_type
        self.public_state_type = public_state_type
        self.api_data = api_data
        self.time_since_last_update = time_since_last_update

    def get_request_payload(self) -> dict:
        """Return the payload."""
        return {
            "ID": self.request_id,
            "RequestType": self.request_type,
            "InputData": {
                "stateType": self.state_type,
                "timeSinceUpdate": self.time_since_last_update,
            },
        }


class MonitorEntityStatesRequest(UpdateMonitorRequest):
    """Request to update monitor."""

    def __init__(
        self,
        request_id: str,
        state_type: str,
        public_state_type: InceptionPublicState,
        api_data: str,
        time_since_last_update: int,
    ) -> None:
        """Initialize the object."""
        super().__init__(
            request_id,
            "MonitorEntityStates",
            state_type,
            public_state_type,
            api_data,
            time_since_last_update,
        )


@dataclass
class UpdateMonitorEntityResponse[StateType]:
    """State Response from update monitor."""

    id: str
    reporting_id: str
    public_state: StateType

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.id = kwargs.pop("ID")
        self.reporting_id = kwargs.pop("ReportingID")
        self.public_state = kwargs.pop("PublicState")
        # stateValue is internal only - remove it
        kwargs.pop("stateValue", "")
        # Collect any extra fields
        self.extra_fields = kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Input(ID={self.id!r}, ReportingID={self.reporting_id!r}, "
            f"extra_fields={self.extra_fields!r})"
        )


@dataclass
class UpdateMonitorResponse[StateType]:
    """UpdateMonitorResponse objects are returned by the server whenever there is a new event available."""

    update_time: int
    state_data: list[UpdateMonitorEntityResponse[StateType]]

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.update_time = kwargs.pop("updateTime")
        self.state_data = [
            UpdateMonitorEntityResponse[StateType](**state)
            for state in kwargs.pop("stateData")
        ]


@dataclass
class UpdateMonitorRequestResult[StateType]:
    """UpdateMonitorRequestResult objects are returned by the server whenever there is a new event available."""

    id: str
    result: UpdateMonitorResponse[StateType]

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.id = kwargs.pop("ID")
        self.result = UpdateMonitorResponse[StateType](**kwargs)
