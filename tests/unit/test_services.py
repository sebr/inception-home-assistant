"""Tests for the Inception domain services."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.inception.const import DOMAIN
from custom_components.inception.services import (
    SERVICE_GET_REVIEW_EVENTS,
    _resolve_coordinator,
    async_register_services,
)


def _hass_with_coordinators(coordinators: dict[str, Any]) -> MagicMock:
    """Build a minimal hass stub that records service registrations."""
    hass = MagicMock()
    hass.data = {DOMAIN: coordinators} if coordinators else {}
    hass.services.has_service.return_value = False
    hass.services.async_register = MagicMock()
    hass.services.async_remove = MagicMock()
    return hass


class TestResolveCoordinator:
    """Test the entry-id resolution helper."""

    def test_raises_when_no_integrations(self) -> None:
        """No configured integrations is a user-facing validation error."""
        hass = _hass_with_coordinators({})
        with pytest.raises(ServiceValidationError):
            _resolve_coordinator(hass, None)

    def test_returns_single_coordinator_implicitly(self) -> None:
        """A single configured entry is selected without an entry_id."""
        coordinator = MagicMock()
        hass = _hass_with_coordinators({"only": coordinator})
        assert _resolve_coordinator(hass, None) is coordinator

    def test_requires_entry_id_when_multiple(self) -> None:
        """Multiple entries without entry_id raises a validation error."""
        hass = _hass_with_coordinators({"a": MagicMock(), "b": MagicMock()})
        with pytest.raises(ServiceValidationError):
            _resolve_coordinator(hass, None)

    def test_returns_named_entry(self) -> None:
        """Explicit entry_id resolves to the matching coordinator."""
        wanted = MagicMock()
        hass = _hass_with_coordinators({"a": MagicMock(), "b": wanted})
        assert _resolve_coordinator(hass, "b") is wanted

    def test_unknown_entry_id_raises(self) -> None:
        """An entry_id that doesn't match any configured entry is rejected."""
        hass = _hass_with_coordinators({"a": MagicMock()})
        with pytest.raises(ServiceValidationError):
            _resolve_coordinator(hass, "missing")


class TestAsyncRegisterServices:
    """Test the service registration entry point."""

    def test_registers_get_review_events_once(self) -> None:
        """async_register_services registers the get_review_events service."""
        hass = _hass_with_coordinators({"a": MagicMock()})
        async_register_services(hass)

        hass.services.async_register.assert_called_once()
        call_args = hass.services.async_register.call_args
        assert call_args.args[0] == DOMAIN
        assert call_args.args[1] == SERVICE_GET_REVIEW_EVENTS

    def test_skips_when_already_registered(self) -> None:
        """Re-invocation is a no-op so multiple entries don't double-register."""
        hass = _hass_with_coordinators({"a": MagicMock()})
        hass.services.has_service.return_value = True

        async_register_services(hass)

        hass.services.async_register.assert_not_called()

    @pytest.mark.asyncio
    async def test_handler_calls_api_and_returns_events(self) -> None:
        """The registered handler delegates to the coordinator's API client."""
        coordinator = MagicMock()
        coordinator.api.get_review_events = AsyncMock(
            return_value=[{"ID": "evt-1"}, {"ID": "evt-2"}]
        )
        hass = _hass_with_coordinators({"only": coordinator})

        async_register_services(hass)
        handler = hass.services.async_register.call_args.args[2]

        call = MagicMock()
        call.data = {
            "limit": 50,
            "direction": "desc",
            "category_filter": ["Access"],
        }

        response = await handler(call)

        coordinator.api.get_review_events.assert_awaited_once_with(
            limit=50,
            offset=None,
            direction="desc",
            start=None,
            end=None,
            category_filter=["Access"],
            message_type_id_filter=None,
            involved_entity_id_filter=None,
            reference_id=None,
            reference_time=None,
        )
        assert response == {
            "events": [{"ID": "evt-1"}, {"ID": "evt-2"}],
            "count": 2,
        }

    @pytest.mark.asyncio
    async def test_handler_wraps_api_errors(self) -> None:
        """Unexpected API errors surface as HomeAssistantError."""
        coordinator = MagicMock()
        coordinator.api.get_review_events = AsyncMock(side_effect=RuntimeError("boom"))
        hass = _hass_with_coordinators({"only": coordinator})

        async_register_services(hass)
        handler = hass.services.async_register.call_args.args[2]

        call = MagicMock()
        call.data = {}

        with pytest.raises(HomeAssistantError):
            await handler(call)
