"""Test the Inception diagnostics support."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from custom_components.inception import diagnostics
from custom_components.inception.const import DOMAIN


@dataclass
class _FakeEntityInfo:
    """Minimal dataclass matching the shape used in summary entries."""

    ID: str
    Name: str
    ReportingID: int


def _fake_summary(entries: dict[str, Any] | None) -> SimpleNamespace:
    """Build a SimpleNamespace that quacks like a schema summary container."""
    return SimpleNamespace(items=entries or {})


class TestSummaryToDict:
    """Test the _summary_to_dict helper."""

    def test_none_summary_returns_empty(self) -> None:
        """None in yields empty dict out."""
        assert diagnostics._summary_to_dict(None) == {}

    def test_container_without_items_dict(self) -> None:
        """A container whose .items is not a dict should be ignored."""
        broken = SimpleNamespace(items="not a dict")
        assert diagnostics._summary_to_dict(broken) == {}

    def test_entry_serialised_with_all_fields(self) -> None:
        """Entity info, public state and extra fields are rendered."""
        entry = SimpleNamespace(
            entity_info=_FakeEntityInfo(ID="abc", Name="Front Door", ReportingID=1),
            public_state=2048,
            extra_fields={"LastStateChangeTime": "2026-04-16T00:00:00"},
        )
        summary = _fake_summary({"abc": entry})

        rendered = diagnostics._summary_to_dict(summary)

        assert rendered == {
            "abc": {
                "entity_info": {"ID": "abc", "Name": "Front Door", "ReportingID": 1},
                "public_state": 2048,
                "extra_fields": {"LastStateChangeTime": "2026-04-16T00:00:00"},
            },
        }

    def test_entry_with_missing_optional_fields(self) -> None:
        """An entry without public_state/extra_fields still renders."""
        entry = SimpleNamespace(
            entity_info=_FakeEntityInfo(ID="x", Name="X", ReportingID=0),
            public_state=None,
            extra_fields=None,
        )
        summary = _fake_summary({"x": entry})

        rendered = diagnostics._summary_to_dict(summary)

        assert rendered == {
            "x": {"entity_info": {"ID": "x", "Name": "X", "ReportingID": 0}}
        }


class TestAsyncGetConfigEntryDiagnostics:
    """Test the diagnostics entry point."""

    @pytest.mark.asyncio
    async def test_redacts_sensitive_fields(self) -> None:
        """Token and host are redacted; non-sensitive fields pass through."""
        coordinator = SimpleNamespace(
            data=SimpleNamespace(inputs=None, doors=None, areas=None, outputs=None),
            monitor_connected=True,
            review_events_global_enabled=False,
            last_update_success=True,
        )
        entry = SimpleNamespace(
            entry_id="entry-1",
            title="Test Inception",
            version=1,
            data={
                "host": "https://inception.example.com",
                "token": "supersecret",
                "name": "Test Inception",
            },
            options={"require_pin_code": True},
        )
        hass = SimpleNamespace(data={DOMAIN: {"entry-1": coordinator}})

        # async_redact_data is sync, but the function is async; call directly.
        result = await diagnostics.async_get_config_entry_diagnostics(
            hass,  # type: ignore[arg-type]
            entry,  # type: ignore[arg-type]
        )

        assert result["entry"]["data"]["token"] == "**REDACTED**"
        assert result["entry"]["data"]["host"] == "**REDACTED**"
        assert result["entry"]["data"]["name"] == "Test Inception"
        assert result["entry"]["options"] == {"require_pin_code": True}

    @pytest.mark.asyncio
    async def test_renders_coordinator_state_and_api_data(self) -> None:
        """Coordinator flags and API summaries are included."""
        door = SimpleNamespace(
            entity_info=_FakeEntityInfo(ID="d1", Name="Front", ReportingID=1),
            public_state=1,
            extra_fields={},
        )
        coordinator = SimpleNamespace(
            data=SimpleNamespace(
                inputs=_fake_summary(None),
                doors=_fake_summary({"d1": door}),
                areas=_fake_summary(None),
                outputs=_fake_summary(None),
            ),
            monitor_connected=False,
            review_events_global_enabled=True,
            last_update_success=False,
        )
        entry = SimpleNamespace(
            entry_id="entry-2",
            title="T",
            version=1,
            data={"host": "h", "token": "t", "name": "n"},
            options={},
        )
        hass = SimpleNamespace(data={DOMAIN: {"entry-2": coordinator}})

        result = await diagnostics.async_get_config_entry_diagnostics(
            hass,  # type: ignore[arg-type]
            entry,  # type: ignore[arg-type]
        )

        assert result["coordinator"] == {
            "monitor_connected": False,
            "review_events_global_enabled": True,
            "last_update_success": False,
        }
        assert "d1" in result["api_data"]["doors"]
        assert result["api_data"]["doors"]["d1"]["public_state"] == 1
        assert result["api_data"]["inputs"] == {}

    @pytest.mark.asyncio
    async def test_handles_missing_coordinator_data(self) -> None:
        """A coordinator with data=None should not crash the diagnostics call."""
        coordinator = SimpleNamespace(
            data=None,
            monitor_connected=False,
            review_events_global_enabled=False,
            last_update_success=True,
        )
        # AsyncMock here ensures accidental awaits on coordinator don't break the test.
        coordinator.async_refresh = AsyncMock()
        entry = SimpleNamespace(
            entry_id="entry-3",
            title="T",
            version=1,
            data={"host": "h", "token": "t"},
            options={},
        )
        hass = SimpleNamespace(data={DOMAIN: {"entry-3": coordinator}})

        result = await diagnostics.async_get_config_entry_diagnostics(
            hass,  # type: ignore[arg-type]
            entry,  # type: ignore[arg-type]
        )

        assert result["api_data"] == {
            "inputs": {},
            "doors": {},
            "areas": {},
            "outputs": {},
        }
