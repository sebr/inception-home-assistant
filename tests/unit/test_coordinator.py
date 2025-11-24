"""Test the Inception data update coordinator."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from custom_components.inception.coordinator import InceptionUpdateCoordinator


class TestInceptionUpdateCoordinator:
    """Test InceptionUpdateCoordinator class."""

    def test_coordinator_class_exists(self) -> None:
        """Test that coordinator class exists and has expected structure."""
        # Test that the class exists and has expected methods
        assert hasattr(InceptionUpdateCoordinator, "__init__")
        assert hasattr(InceptionUpdateCoordinator, "async_config_entry_first_refresh")

        # Test that it's a proper class
        assert isinstance(InceptionUpdateCoordinator, type)

    def test_coordinator_inheritance(self) -> None:
        """Test coordinator inheritance."""
        # Test inheritance
        assert issubclass(InceptionUpdateCoordinator, DataUpdateCoordinator)
