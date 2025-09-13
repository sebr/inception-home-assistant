"""Global test configuration for Inception integration tests."""

from __future__ import annotations

from typing import Any

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture
def mock_config_entry_data() -> dict[str, Any]:
    """Return mock config entry data."""
    return {
        "host": "https://test.example.com",
        "token": "test-token-123",
        "name": "Test Inception",
    }
