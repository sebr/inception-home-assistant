from custom_components.inception.pyinception.states_schema import (
    AreaPublicStates,
    DoorPublicStates,
    InputPublicStates,
    OutputPublicStates,
)


class InceptionObject:
    """An inception object."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the object."""
        self.ID = kwargs.pop("ID", "")
        self.Name = kwargs.pop("Name", "")
        self.ReportingID = kwargs.pop("ReportingID", "")
        # Collect any extra fields
        self.extra_fields = kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Input(ID={self.ID!r}, Name={self.Name!r}, "
            f"ReportingID={self.ReportingID!r}, extra_fields={self.extra_fields!r})"
        )


class Input(InceptionObject):
    """An inception Input."""

    InputType: str = ""
    PublicState: InputPublicStates | None = None

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the object."""
        self.InputType = kwargs.pop("InputType", 0)
        super().__init__(**kwargs)


class Output(InceptionObject):
    """An inception Output."""

    PublicState: OutputPublicStates | None = None


class Door(InceptionObject):
    """An inception Door."""

    PublicState: DoorPublicStates | None = None


class Area(InceptionObject):
    """An inception Area."""

    PublicState: AreaPublicStates | None = None


class LiveReviewEventsResult:
    """Live Review Events Result from update monitor."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the object."""
        self.ID = kwargs.pop("ID", "")
        self.Description = kwargs.pop("Description", "")
        self.MessageCategory = kwargs.pop("MessageCategory", "")
        self.What = kwargs.pop("What", "")
        self.Who = kwargs.pop("Who", "")
        self.Where = kwargs.pop("Where", "")
        self.WhenTicks = kwargs.pop("WhenTicks", "")
        # Collect any extra fields
        self.extra_fields = kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Input(ID={self.ID!r}, Name={self.Description!r}, "
            f"What={self.What!r}, Who={self.Who!r}, extra_fields={self.extra_fields!r})"
        )


class MonitorStateResponse:
    """State Response from update monitor."""

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the object."""
        self.ID = kwargs.pop("ID", "")
        self.ReportingID = kwargs.pop("ReportingID", "")
        self.stateValue = kwargs.pop("stateValue", "")
        self.PublicState = kwargs.pop("PublicState", "")
        # Collect any extra fields
        self.extra_fields = kwargs

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Input(ID={self.ID!r}, ReportingID={self.ReportingID!r}, "
            f"stateValue={self.stateValue!r}, extra_fields={self.extra_fields!r})"
        )
