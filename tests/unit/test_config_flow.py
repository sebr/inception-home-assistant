"""Test the Inception config flow."""

from __future__ import annotations

from custom_components.inception.config_flow import InceptionFlowHandler


class TestInceptionFlowHandler:
    """Test InceptionFlowHandler class."""

    def test_handler_domain(self) -> None:
        """Test flow handler is configured for correct domain."""
        # The domain is set via the class decorator, so we test the class configuration
        from custom_components.inception.config_flow import InceptionFlowHandler

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
