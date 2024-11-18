from dataclasses import dataclass


@dataclass
class InceptionObject:
    """An inception object."""

    ID: str = ""
    Name: str = ""
    ReportingID: str = ""


@dataclass
class Input(InceptionObject):
    """An inception Input."""

    InputType: str = ""


@dataclass
class Output(InceptionObject):
    """An inception Output."""


@dataclass
class Door(InceptionObject):
    """An inception Door."""


@dataclass
class Area(InceptionObject):
    """An inception Area."""
