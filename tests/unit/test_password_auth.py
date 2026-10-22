"""Tests for username/password (session cookie) authentication."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.inception.const import DOMAIN
from custom_components.inception.pyinception.api import (
    InceptionApiClient,
    InceptionApiClientAuthenticationError,
    InceptionApiClientError,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

LOGIN_URL = "http://h.test/api/v1/authentication/hashed-login"
PLAIN_LOGIN_URL = "http://h.test/api/v1/authentication/login"
LOGOUT_URL = "http://h.test/api/v1/authentication/logout"


class _Resp:
    """Minimal aiohttp response stand-in."""

    def __init__(self, status: int = 200, body: Any = None) -> None:
        self.status = status
        self._body = body if body is not None else {}

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise aiohttp.ClientResponseError(Mock(), (), status=self.status)

    async def json(self, content_type: Any = None) -> Any:  # noqa: ARG002
        return self._body


def _login_ok(session_id: str) -> _Resp:
    return _Resp(
        body={
            "Response": {"Result": "Success", "Message": "OK"},
            "UserID": session_id,
        }
    )


def _session(responses: list[_Resp]) -> Mock:
    """Return a mocked session whose request() yields ``responses`` in order."""
    session = Mock(spec=aiohttp.ClientSession)
    session.request = AsyncMock(side_effect=responses)
    return session


def _client(session: Mock) -> InceptionApiClient:
    return InceptionApiClient(
        token=None,
        host="http://h.test",
        session=session,
        username="ha",
        password="secret",
    )


class TestPasswordLogin:
    """The API client logs in and sends the session as a cookie."""

    def test_requires_token_or_username_and_password(self) -> None:
        """Constructing without any credentials is a programming error."""
        session = Mock(spec=aiohttp.ClientSession)
        with pytest.raises(ValueError, match="token or a username"):
            InceptionApiClient(token=None, host="http://h.test", session=session)
        with pytest.raises(ValueError, match="token or a username"):
            InceptionApiClient(
                token=None, host="http://h.test", session=session, username="ha"
            )

    async def test_logs_in_once_and_sends_cookie(self) -> None:
        """The first request logs in; later requests reuse the session."""
        session = _session([_login_ok("sess-1"), _Resp(), _Resp()])
        client = _client(session)

        await client.request(method="get", path="/control/input")
        await client.request(method="get", path="/control/door")

        calls = session.request.call_args_list
        assert len(calls) == 3
        assert calls[0].kwargs["url"] == LOGIN_URL
        # The hash of "ha:secret", base64-encoded.
        assert calls[0].kwargs["json"] == {
            "Username": "ha",
            "PasswordHash": "YTBF3c9aX3Xt0x5CGmuxSscxZ75sOy8uuRsu5pWFM+M=",
        }
        for call in calls[1:]:
            assert call.kwargs["cookies"] == {"LoginSessId": "sess-1"}
            assert "Authorization" not in call.kwargs["headers"]

    async def test_expired_session_relogs_in_and_retries(self) -> None:
        """A 401 logs out the rejected session, logs in again and retries."""
        session = _session(
            [
                _login_ok("sess-1"),
                _Resp(),
                _Resp(status=401),
                _Resp(),
                _login_ok("sess-2"),
                _Resp(body={"ok": True}),
            ]
        )
        client = _client(session)

        await client.request(method="get", path="/control/input")
        result = await client.request(method="get", path="/control/input")

        assert result == {"ok": True}
        calls = session.request.call_args_list
        assert calls[3].kwargs["url"] == LOGOUT_URL
        assert calls[3].kwargs["cookies"] == {"LoginSessId": "sess-1"}
        assert calls[4].kwargs["url"] == LOGIN_URL
        assert calls[5].kwargs["cookies"] == {"LoginSessId": "sess-2"}

    async def test_persistent_401_raises_auth_error(self) -> None:
        """If the retry is also rejected, surface an auth error."""
        session = _session(
            [
                _login_ok("sess-1"),
                _Resp(status=401),
                _Resp(),
                _login_ok("sess-2"),
                _Resp(401),
            ]
        )
        client = _client(session)

        with pytest.raises(InceptionApiClientAuthenticationError):
            await client.request(method="get", path="/control/input")

    async def test_failed_login_raises_auth_error(self) -> None:
        """A login response without a session ID means bad credentials."""
        session = _session(
            [
                _Resp(
                    body={
                        "Response": {
                            "Result": "Failure",
                            "Message": "Invalid credentials",
                        }
                    }
                )
            ]
        )
        client = _client(session)

        with pytest.raises(
            InceptionApiClientAuthenticationError, match="Invalid credentials"
        ):
            await client.request(method="get", path="/control/input")

    async def test_failed_login_with_nil_session_raises_auth_error(self) -> None:
        """Real firmware answers a bad login with HTTP 200 and a nil UserID."""
        session = _session(
            [
                _Resp(
                    body={
                        "Response": {
                            "Result": "Failure",
                            "Message": "Invalid credentials provided",
                            "FailureReason": 1,
                        },
                        "UserID": "00000000-0000-0000-0000-000000000000",
                    }
                )
            ]
        )
        client = _client(session)

        with pytest.raises(
            InceptionApiClientAuthenticationError,
            match="Invalid credentials provided",
        ):
            await client.request(method="get", path="/control/input")
        assert session.request.call_count == 1

    async def test_failed_login_is_not_repeated(self) -> None:
        """Concurrent requests share one failed login instead of each retrying."""
        session = _session(
            [_Resp(body={"Response": {"Result": "Failure", "Message": "Locked"}})]
        )
        client = _client(session)

        results = await asyncio.gather(
            *(client.request(method="get", path="/control/input") for _ in range(3)),
            return_exceptions=True,
        )

        assert all(
            isinstance(r, InceptionApiClientAuthenticationError) for r in results
        )
        assert session.request.call_count == 1

    async def test_falls_back_to_plain_login_without_hashed_login(self) -> None:
        """Firmware without hashed-login gets the plain endpoint from then on."""
        session = _session(
            [
                _Resp(status=404),
                _login_ok("sess-1"),
                _Resp(status=401),
                _Resp(),
                _login_ok("sess-2"),
                _Resp(),
            ]
        )
        client = _client(session)

        await client.request(method="get", path="/control/input")

        calls = session.request.call_args_list
        assert calls[0].kwargs["url"] == LOGIN_URL
        assert calls[1].kwargs["url"] == PLAIN_LOGIN_URL
        assert calls[1].kwargs["json"] == {"Username": "ha", "Password": "secret"}
        # The re-login after the 401 skips hashed-login.
        assert calls[4].kwargs["url"] == PLAIN_LOGIN_URL

    async def test_hashed_login_server_error_does_not_fall_back(self) -> None:
        """Only a missing endpoint falls back; other errors propagate."""
        session = _session([_Resp(status=500)])
        client = _client(session)

        with pytest.raises(InceptionApiClientError):
            await client.request(method="get", path="/control/input")
        assert session.request.call_count == 1

    async def test_malformed_login_response_raises_auth_error(self) -> None:
        """A non-dict ``Response`` is still reported as a failed login."""
        session = _session([_Resp(body={"Response": None})])
        client = _client(session)

        with pytest.raises(
            InceptionApiClientAuthenticationError, match="no session returned"
        ):
            await client.request(method="get", path="/control/input")

    async def test_protocol_version_does_not_log_in(self) -> None:
        """The unauthenticated version probe skips the login."""
        session = _session([_Resp(body={"ProtocolVersion": 16})])
        client = _client(session)

        assert await client.get_protocol_version() == 16

        (call,) = session.request.call_args_list
        assert call.kwargs["cookies"] is None

    async def test_no_login_after_close(self) -> None:
        """A request still running after close() cannot open a new session."""
        session = _session([_login_ok("sess-1"), _Resp(), _Resp()])
        client = _client(session)
        await client.request(method="get", path="/control/input")
        await client.close()

        with pytest.raises(InceptionApiClientError, match="closed"):
            await client.request(method="get", path="/control/input")
        assert session.request.call_count == 3

    async def test_close_logs_out(self) -> None:
        """Closing the client invalidates the panel session."""
        session = _session([_login_ok("sess-1"), _Resp(), _Resp()])
        client = _client(session)
        await client.request(method="get", path="/control/input")

        await client.close()

        last = session.request.call_args_list[-1]
        assert last.kwargs["url"] == LOGOUT_URL
        assert last.kwargs["cookies"] == {"LoginSessId": "sess-1"}

    async def test_token_mode_does_not_log_in(self) -> None:
        """Token auth is unchanged: no login call, no cookie."""
        session = _session([_Resp()])
        client = InceptionApiClient(token="t", host="http://h.test", session=session)

        await client.request(method="get", path="/control/input")
        await client.close()

        (call,) = session.request.call_args_list
        assert call.kwargs["headers"]["Authorization"] == "APIToken t"
        assert call.kwargs["cookies"] is None


@pytest.mark.usefixtures("enable_custom_integrations")
class TestConfigFlowCredentials:
    """The user step accepts either a token or a username and password."""

    @pytest.fixture(autouse=True)
    def _no_setup(self) -> Any:
        with patch("custom_components.inception.async_setup_entry", return_value=True):
            yield

    async def _submit(self, hass: HomeAssistant, user_input: dict[str, Any]) -> Any:
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        return await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input
        )

    async def test_missing_credentials_shows_error(self, hass: HomeAssistant) -> None:
        """Neither a token nor a full username/password is rejected."""
        with patch(
            "custom_components.inception.config_flow.InceptionFlowHandler._test_credentials"
        ) as test_credentials:
            result = await self._submit(
                hass, {"name": "Test", "host": "h.test", "username": "ha"}
            )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "missing_credentials"}
        test_credentials.assert_not_called()

    async def test_password_entry_created(self, hass: HomeAssistant) -> None:
        """Username/password creates an entry without a token."""
        with patch(
            "custom_components.inception.config_flow.InceptionFlowHandler._test_credentials"
        ) as test_credentials:
            result = await self._submit(
                hass,
                {
                    "name": "Test",
                    "host": "https://skytunnel.com.au/inception/IN1",
                    "username": "ha",
                    "password": "secret",
                },
            )

        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["data"] == {
            "name": "Test",
            "host": "https://skytunnel.com.au/inception/IN1",
            "username": "ha",
            "password": "secret",
        }
        test_credentials.assert_awaited_once_with(
            host="https://skytunnel.com.au/inception/IN1",
            token=None,
            username="ha",
            password="secret",
        )

    async def test_timeout_shows_connection_error(self, hass: HomeAssistant) -> None:
        """A timeout while testing credentials maps to the connection error."""
        with patch(
            "custom_components.inception.config_flow.InceptionFlowHandler._test_credentials",
            side_effect=TimeoutError,
        ):
            result = await self._submit(
                hass,
                {"name": "Test", "host": "h.test", "username": "ha", "password": "x"},
            )

        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "connection"}

    async def test_token_wins_over_password(self, hass: HomeAssistant) -> None:
        """When a token is given, username/password are not stored."""
        with patch(
            "custom_components.inception.config_flow.InceptionFlowHandler._test_credentials"
        ):
            result = await self._submit(
                hass,
                {
                    "name": "Test",
                    "host": "h.test",
                    "token": "t",
                    "username": "ha",
                    "password": "secret",
                },
            )

        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["data"] == {"name": "Test", "host": "http://h.test", "token": "t"}
