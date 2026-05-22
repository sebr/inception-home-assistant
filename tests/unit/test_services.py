"""Tests for the Inception domain services."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from custom_components.inception.const import DOMAIN
from custom_components.inception.services import (
    SERVICE_BADGE_CREDENTIAL,
    SERVICE_GET_ATTACHED_READERS,
    SERVICE_GET_REVIEW_EVENTS,
    SERVICE_SEND_PIN,
    _resolve_coordinator,
    async_register_services,
)


def _registered_handler(hass: MagicMock, service_name: str) -> Any:
    """Return the handler that was registered under ``service_name``."""
    for call_args in hass.services.async_register.call_args_list:
        if call_args.args[1] == service_name:
            return call_args.args[2]
    msg = f"Service {service_name} not registered"
    raise AssertionError(msg)


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

    def test_registers_all_services(self) -> None:
        """async_register_services registers every Inception domain service."""
        hass = _hass_with_coordinators({"a": MagicMock()})
        async_register_services(hass)

        registered = [
            call_args.args[1]
            for call_args in hass.services.async_register.call_args_list
        ]
        assert SERVICE_GET_REVIEW_EVENTS in registered
        assert SERVICE_BADGE_CREDENTIAL in registered
        assert SERVICE_SEND_PIN in registered
        assert SERVICE_GET_ATTACHED_READERS in registered

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
        handler = _registered_handler(hass, SERVICE_GET_REVIEW_EVENTS)

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
        handler = _registered_handler(hass, SERVICE_GET_REVIEW_EVENTS)

        call = MagicMock()
        call.data = {}

        with pytest.raises(HomeAssistantError):
            await handler(call)


class TestBadgeCredentialService:
    """Tests for the inception.badge_credential service handler."""

    @pytest.mark.asyncio
    async def test_handler_delegates_to_api(self) -> None:
        """Required fields are forwarded to badge_credential_at_reader."""
        coordinator = MagicMock()
        coordinator.api.badge_credential_at_reader = AsyncMock(
            return_value="activity-1"
        )
        hass = _hass_with_coordinators({"only": coordinator})

        async_register_services(hass)
        handler = _registered_handler(hass, SERVICE_BADGE_CREDENTIAL)

        call = MagicMock()
        call.data = {
            "reader_id": "reader-1",
            "credential_template": "template-1",
            "card_number": "0000123",
        }

        response = await handler(call)

        coordinator.api.badge_credential_at_reader.assert_awaited_once_with(
            reader_id="reader-1",
            credential_template="template-1",
            card_number="0000123",
        )
        assert response == {"activity_id": "activity-1"}

    @pytest.mark.asyncio
    async def test_handler_wraps_api_errors(self) -> None:
        """API failures surface as HomeAssistantError."""
        coordinator = MagicMock()
        coordinator.api.badge_credential_at_reader = AsyncMock(
            side_effect=RuntimeError("boom")
        )
        hass = _hass_with_coordinators({"only": coordinator})

        async_register_services(hass)
        handler = _registered_handler(hass, SERVICE_BADGE_CREDENTIAL)

        call = MagicMock()
        call.data = {
            "reader_id": "reader-1",
            "credential_template": "template-1",
            "card_number": "0000123",
        }

        with pytest.raises(HomeAssistantError):
            await handler(call)


class TestSendPinService:
    """Tests for the inception.send_pin service handler."""

    @pytest.mark.asyncio
    async def test_handler_delegates_to_api(self) -> None:
        """Required fields are forwarded to send_pin_to_reader."""
        coordinator = MagicMock()
        coordinator.api.send_pin_to_reader = AsyncMock(return_value="activity-2")
        hass = _hass_with_coordinators({"only": coordinator})

        async_register_services(hass)
        handler = _registered_handler(hass, SERVICE_SEND_PIN)

        call = MagicMock()
        call.data = {"reader_id": "reader-1", "pin": "1234"}

        response = await handler(call)

        coordinator.api.send_pin_to_reader.assert_awaited_once_with(
            reader_id="reader-1",
            pin="1234",
        )
        assert response == {"activity_id": "activity-2"}

    @pytest.mark.asyncio
    async def test_handler_wraps_api_errors(self) -> None:
        """API failures surface as HomeAssistantError."""
        coordinator = MagicMock()
        coordinator.api.send_pin_to_reader = AsyncMock(side_effect=RuntimeError("boom"))
        hass = _hass_with_coordinators({"only": coordinator})

        async_register_services(hass)
        handler = _registered_handler(hass, SERVICE_SEND_PIN)

        call = MagicMock()
        call.data = {"reader_id": "reader-1", "pin": "1234"}

        with pytest.raises(HomeAssistantError):
            await handler(call)


class TestGetAttachedReadersService:
    """Tests for the inception.get_attached_readers service handler."""

    @pytest.mark.asyncio
    async def test_handler_returns_readers(self) -> None:
        """Door ID is forwarded and the reader list is returned with a count."""
        coordinator = MagicMock()
        coordinator.api.get_attached_readers = AsyncMock(
            return_value=[{"ID": "reader-1"}, {"ID": "reader-2"}]
        )
        hass = _hass_with_coordinators({"only": coordinator})

        async_register_services(hass)
        handler = _registered_handler(hass, SERVICE_GET_ATTACHED_READERS)

        call = MagicMock()
        call.data = {"door_id": "door-1"}

        response = await handler(call)

        coordinator.api.get_attached_readers.assert_awaited_once_with(
            door_id="door-1",
        )
        assert response == {
            "readers": [{"ID": "reader-1"}, {"ID": "reader-2"}],
            "count": 2,
        }

    @pytest.mark.asyncio
    async def test_handler_wraps_api_errors(self) -> None:
        """API failures surface as HomeAssistantError."""
        coordinator = MagicMock()
        coordinator.api.get_attached_readers = AsyncMock(
            side_effect=RuntimeError("boom")
        )
        hass = _hass_with_coordinators({"only": coordinator})

        async_register_services(hass)
        handler = _registered_handler(hass, SERVICE_GET_ATTACHED_READERS)

        call = MagicMock()
        call.data = {"door_id": "door-1"}

        with pytest.raises(HomeAssistantError):
            await handler(call)
