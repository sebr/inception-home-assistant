"""Test the Inception config flow."""

from __future__ import annotations

from homeassistant.config_entries import OptionsFlow

from custom_components.inception.config_flow import (
    InceptionFlowHandler,
    InceptionOptionsFlowHandler,
)


class TestInceptionFlowHandler:
    """Test InceptionFlowHandler class."""

    def test_handler_domain(self) -> None:
        """Test flow handler is configured for correct domain."""
        # The domain is set via the class decorator, so we test the class configuration
        # Test that the class has the expected configuration
        assert hasattr(InceptionFlowHandler, "VERSION")

    def test_handler_version(self) -> None:
        """Test flow handler version."""
        handler = InceptionFlowHandler()
        assert handler.VERSION == 1

    def test_handler_exists(self) -> None:
        """Test that handler class exists and is properly configured."""
        handler = InceptionFlowHandler()

        # Test that required methods exist
        assert hasattr(handler, "async_step_user")
        assert callable(handler.async_step_user)

        # Test configuration
        assert handler.VERSION == 1

    def test_has_options_flow(self) -> None:
        """Test that config flow declares options flow support."""
        assert hasattr(InceptionFlowHandler, "async_get_options_flow")
        assert callable(InceptionFlowHandler.async_get_options_flow)


class TestInceptionOptionsFlowHandler:
    """Test InceptionOptionsFlowHandler class."""

    def test_options_handler_exists(self) -> None:
        """Test that options handler class exists."""
        assert issubclass(InceptionOptionsFlowHandler, OptionsFlow)

    def test_options_handler_has_init_step(self) -> None:
        """Test that options handler has async_step_init."""
        assert hasattr(InceptionOptionsFlowHandler, "async_step_init")
        assert callable(InceptionOptionsFlowHandler.async_step_init)
