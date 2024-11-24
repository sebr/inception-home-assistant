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

    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        """Initialize the object."""
        self.InputType = kwargs.pop("InputType", 0)
        super().__init__(**kwargs)


class Output(InceptionObject):
    """An inception Output."""


class Door(InceptionObject):
    """An inception Door."""


class Area(InceptionObject):
    """An inception Area."""
