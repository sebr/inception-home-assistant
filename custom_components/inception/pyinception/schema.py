"""Defines the schema for various Inception objects and responses."""


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
