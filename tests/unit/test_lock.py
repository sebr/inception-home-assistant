"""Test the Inception lock entity."""

from __future__ import annotations

from custom_components.inception.lock import (
    InceptionDoorEntityDescription,
    InceptionLock,
)


class TestInceptionLock:
    """Test InceptionLock entity."""

    def test_lock_class_exists(self) -> None:
        """Test that lock class exists and has expected structure."""
        # Test that the class exists and has expected methods
        assert hasattr(InceptionLock, "__init__")
        assert hasattr(InceptionLock, "async_lock")
        assert hasattr(InceptionLock, "async_unlock")

        # Test that it's a proper class
        assert isinstance(InceptionLock, type)

    def test_lock_inheritance(self) -> None:
        """Test lock entity inheritance."""
        from homeassistant.components.lock import LockEntity

        from custom_components.inception.entity import InceptionEntity

        # Test inheritance
        assert issubclass(InceptionLock, LockEntity)
        assert issubclass(InceptionLock, InceptionEntity)

    def test_entity_description_class(self) -> None:
        """Test entity description class exists."""
        from homeassistant.components.lock import LockEntityDescription

        # Test that entity description exists and inherits properly
        assert hasattr(InceptionDoorEntityDescription, "__init__")
        assert issubclass(InceptionDoorEntityDescription, LockEntityDescription)
