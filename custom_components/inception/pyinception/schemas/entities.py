# ruff: noqa: E501 ANN003

"""Defines the schema for various Inception objects and responses."""

from abc import abstractmethod
from enum import IntFlag
from typing import Any, TypeVar

"""https://skytunnel.com.au/Inception/API_SAMPLE/ApiModelDoc"""


class InceptionPublicState(IntFlag):
    """Inception public states."""

    @staticmethod
    @abstractmethod
    def get_state_description(_state_value: int) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        return []

    def state_description(self) -> list[str]:
        """Get the list of state descriptions for the given state value."""
        return self.get_state_description(self.value)

    def __str__(self) -> str:
        """Return the name or value of the state."""
        if self.name is None:
            return str(self.value)
        return self.name.replace("_", " ").capitalize()


class ReportableShortEntity:
    """Represents a short entity for a reportable."""

    id: str
    name: str
    reporting_id: str

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.id = kwargs.pop("ID", "")
        self.name = kwargs.pop("Name", "")
        self.reporting_id = kwargs.pop("ReportingID", "")


StateType = TypeVar("StateType", bound=InceptionPublicState)


class InceptionSummaryEntry[StateType]:
    """Inception SummaryEntry schema."""

    entity_info: ReportableShortEntity
    public_state: StateType
    last_state_change_time: int = 0
    extra_fields: dict[str, Any]

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.last_state_change_time = kwargs.pop("LastStateChangeTime", 0)
        self.set_state(kwargs.pop("CurrentState", 0))
        # Collect any extra fields
        self.extra_fields = kwargs

    def set_state(self, state: StateType) -> None:
        """Set the public state."""
        self.public_state = state


SummaryType = TypeVar("SummaryType", bound=InceptionSummaryEntry)


class InceptionSummary[SummaryType]:
    """Inception Entity Summary schema."""

    items: dict[str, SummaryType]

    def get_items(self) -> list[SummaryType]:
        """Return the items."""
        return [] if self.items is None else list(self.items.values())


class InceptionObject:
    """An inception object."""

    id: str
    name: str
    reporting_id: str
    extra_fields: dict[str, Any]
    public_state: InceptionPublicState | None

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.id = kwargs.pop("ID", "")
        self.name = kwargs.pop("Name", "")
        self.reporting_id = kwargs.pop("ReportingID", "")
        # Collect any extra fields
        self.extra_fields = kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Input(ID={self.id!r}, Name={self.name!r}, "
            f"ReportingID={self.reporting_id!r}, extra_fields={self.extra_fields!r})"
        )


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


class MonitorStateResponse:
    """State Response from update monitor."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.id = kwargs.pop("ID", "")
        self.reporting_id = kwargs.pop("ReportingID", "")
        self.state_value = kwargs.pop("stateValue", "")
        self.public_state = kwargs.pop("PublicState", "")
        # Collect any extra fields
        self.extra_fields = kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Input(ID={self.id!r}, ReportingID={self.reporting_id!r}, "
            f"stateValue={self.state_value!r}, extra_fields={self.extra_fields!r})"
        )
