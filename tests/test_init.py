"""Test the Inception integration setup and unload."""

from __future__ import annotations

from custom_components.inception import PLATFORMS
from custom_components.inception.const import DOMAIN


class TestInceptionIntegration:
    """Test Inception integration setup and teardown."""

    def test_platforms_list(self) -> None:
        """Test that all required platforms are included."""
        from homeassistant.const import Platform

        expected_platforms = [
            Platform.ALARM_CONTROL_PANEL,
            Platform.BINARY_SENSOR,
            Platform.LOCK,
            Platform.NUMBER,
            Platform.SELECT,
            Platform.SWITCH,
        ]

        assert set(PLATFORMS) == set(expected_platforms)

    def test_domain_constant(self) -> None:
        """Test domain constant is correct."""
        assert DOMAIN == "inception"

    def test_integration_functions_exist(self) -> None:
        """Test that integration functions exist."""
        from custom_components.inception import (
            async_reload_entry,
            async_setup_entry,
            async_unload_entry,
        )

        # Test that functions exist and are callable
        assert callable(async_setup_entry)
        assert callable(async_unload_entry)
        assert callable(async_reload_entry)
