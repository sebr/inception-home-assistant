# ruff: noqa: ANN003

"""Schema for the Inception SystemInfoDto from /api/v1/system-info."""

from __future__ import annotations


class SystemInfo:
    """Inception SystemInfoDto."""

    serial_number: str
    system_name: str

    def __init__(self, **kwargs) -> None:
        """Initialize the object."""
        self.serial_number = kwargs.pop("SerialNumber", "") or ""
        self.system_name = kwargs.pop("SystemName", "") or ""
