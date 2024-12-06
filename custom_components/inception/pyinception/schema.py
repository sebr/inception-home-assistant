"""Defines the schema for various Inception objects and responses."""

from typing import Any

from custom_components.inception.pyinception.states_schema import (
    AreaPublicState,
    DoorPublicState,
    InceptionPublicState,
    InputPublicState,
    InputType,
    OutputPublicState,
)


class InceptionObject:
    """An inception object."""

    id: str
    name: str
    reporting_id: str
    extra_fields: dict[str, Any]
    public_state: InceptionPublicState | None

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
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


class Input(InceptionObject):
    """An inception Input."""

    input_type: InputType = InputType.UNKNOWN
    public_state: InputPublicState | None = None

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the object."""
        self.input_type = kwargs.pop("InputType", InputType.UNKNOWN)
        super().__init__(**kwargs)


class Output(InceptionObject):
    """An inception Output."""

    public_state: OutputPublicState | None = None


class Door(InceptionObject):
    """An inception Door."""

    public_state: DoorPublicState | None = None


class Area(InceptionObject):
    """An inception Area."""

    public_state: AreaPublicState | None = None


class LiveReviewEventsResult:
    """Live Review Events Result from update monitor."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
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

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
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
