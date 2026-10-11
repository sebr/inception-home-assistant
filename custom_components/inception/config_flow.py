"""Adds config flow for Inception."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import OptionsFlow
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    CONF_REQUIRE_CODE_TO_ARM,
    CONF_REQUIRE_PIN_CODE,
    DEFAULT_REQUIRE_CODE_TO_ARM,
    DEFAULT_REQUIRE_PIN_CODE,
    DOMAIN,
    LOGGER,
)
from .pyinception.api import (
    InceptionApiClient,
    InceptionApiClientAuthenticationError,
    InceptionApiClientCommunicationError,
    InceptionApiClientError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.config_entries import ConfigFlowResult


class InceptionFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Inception."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: config_entries.ConfigEntry,
    ) -> InceptionOptionsFlowHandler:
        """Get the options flow for this handler."""
        return InceptionOptionsFlowHandler()

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            cleaned_input = {
                **user_input,
                CONF_HOST: f"http://{user_input[CONF_HOST]}"
                if not user_input[CONF_HOST].startswith(("http://", "https://"))
                else user_input[CONF_HOST],
            }
            # Keep only the credentials in use, so the entry's auth mode is
            # unambiguous: a token, or a username and password.
            if cleaned_input.get(CONF_TOKEN):
                cleaned_input.pop(CONF_USERNAME, None)
                cleaned_input.pop(CONF_PASSWORD, None)
            else:
                cleaned_input.pop(CONF_TOKEN, None)
            try:
                if not cleaned_input.get(CONF_TOKEN) and not (
                    cleaned_input.get(CONF_USERNAME)
                    and cleaned_input.get(CONF_PASSWORD)
                ):
                    _errors["base"] = "missing_credentials"
                else:
                    await self._test_credentials(
                        host=cleaned_input[CONF_HOST],
                        token=cleaned_input.get(CONF_TOKEN),
                        username=cleaned_input.get(CONF_USERNAME),
                        password=cleaned_input.get(CONF_PASSWORD),
                    )
            except InceptionApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except InceptionApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except InceptionApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                if not _errors:
                    return self.async_create_entry(
                        title=cleaned_input[CONF_NAME],
                        data=cleaned_input,
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NAME,
                        default=(user_input or {}).get(CONF_NAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                        ),
                    ),
                    vol.Optional(
                        CONF_TOKEN,
                        default=(user_input or {}).get(CONF_TOKEN, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                    vol.Optional(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                            autocomplete="username",
                        ),
                    ),
                    vol.Optional(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                            autocomplete="current-password",
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(
        self,
        host: str,
        token: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Validate credentials."""
        client = InceptionApiClient(
            token=token,
            host=host,
            session=async_create_clientsession(self.hass),
            username=username,
            password=password,
        )
        try:
            await client.authenticate()
        finally:
            await client.close()

    async def async_step_reauth(
        self,
        _entry_data: Mapping[str, Any],
    ) -> ConfigFlowResult:
        """Triggered when HA requests re-authentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Prompt the user to supply new credentials for the existing entry."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        uses_password = not entry.data.get(CONF_TOKEN)

        if user_input is not None:
            try:
                await self._test_credentials(
                    host=entry.data[CONF_HOST],
                    token=user_input.get(CONF_TOKEN),
                    username=user_input.get(CONF_USERNAME),
                    password=user_input.get(CONF_PASSWORD),
                )
            except InceptionApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                errors["base"] = "auth"
            except InceptionApiClientCommunicationError as exception:
                LOGGER.error(exception)
                errors["base"] = "connection"
            except InceptionApiClientError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=user_input,
                )

        password_selector = selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
        )
        if uses_password:
            schema = vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME, default=entry.data.get(CONF_USERNAME)
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): password_selector,
                },
            )
        else:
            schema = vol.Schema({vol.Required(CONF_TOKEN): password_selector})

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=schema,
            description_placeholders={"name": entry.title},
            errors=errors,
        )


class InceptionOptionsFlowHandler(OptionsFlow):
    """Handle options flow for Inception."""

    async def async_step_init(
        self,
        user_input: dict | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_REQUIRE_PIN_CODE,
                        default=self.config_entry.options.get(
                            CONF_REQUIRE_PIN_CODE,
                            DEFAULT_REQUIRE_PIN_CODE,
                        ),
                    ): selector.BooleanSelector(
                        selector.BooleanSelectorConfig(),
                    ),
                    vol.Required(
                        CONF_REQUIRE_CODE_TO_ARM,
                        default=self.config_entry.options.get(
                            CONF_REQUIRE_CODE_TO_ARM,
                            DEFAULT_REQUIRE_CODE_TO_ARM,
                        ),
                    ): selector.BooleanSelector(
                        selector.BooleanSelectorConfig(),
                    ),
                },
            ),
        )
