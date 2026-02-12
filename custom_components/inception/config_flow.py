"""Adds config flow for Inception."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import OptionsFlow
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
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
    from homeassistant.config_entries import ConfigFlowResult


class InceptionFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Inception."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,  # noqa: ARG004
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
            try:
                await self._test_credentials(
                    token=cleaned_input[CONF_TOKEN],
                    host=cleaned_input[CONF_HOST],
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
                    vol.Required(
                        CONF_TOKEN,
                        default=(user_input or {}).get(CONF_TOKEN, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, token: str, host: str) -> None:
        """Validate credentials."""
        client = InceptionApiClient(
            token=token,
            host=host,
            session=async_create_clientsession(self.hass),
        )
        await client.authenticate()


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
