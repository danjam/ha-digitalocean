import logging

import voluptuous as vol
import yaml
from aiohttp import ClientError

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .api import DigitalOceanAPI, DigitalOceanAuthError
from .const import CONF_API_TOKEN, CONF_SECRET_KEY, DOMAIN

_LOGGER = logging.getLogger(__name__)


class DigitalOceanConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def _read_secret(self, key: str) -> str | None:
        secrets_path = self.hass.config.path("secrets.yaml")
        try:
            with open(secrets_path) as f:
                secrets = yaml.safe_load(f) or {}
            return secrets.get(key)
        except (FileNotFoundError, yaml.YAMLError):
            return None

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        errors = {}
        if user_input is not None:
            token = user_input[CONF_API_TOKEN]
            session = async_get_clientsession(self.hass)
            api = DigitalOceanAPI(token, session)
            try:
                account = await api.get_account()
            except DigitalOceanAuthError:
                errors["base"] = "invalid_auth"
            except (ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during setup")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(account["email"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=account["email"],
                    data={CONF_API_TOKEN: token},
                )

        default_token = ""
        if user_input is None:
            default_token = await self.hass.async_add_executor_job(
                self._read_secret, CONF_SECRET_KEY
            ) or ""

        schema = vol.Schema({
            vol.Required(CONF_API_TOKEN, default=default_token): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> ConfigFlowResult:
        errors = {}
        if user_input is not None:
            token = user_input[CONF_API_TOKEN]
            session = async_get_clientsession(self.hass)
            api = DigitalOceanAPI(token, session)
            try:
                await api.get_account()
            except DigitalOceanAuthError:
                errors["base"] = "invalid_auth"
            except (ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during reauth")
                errors["base"] = "unknown"
            else:
                entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
                self.hass.config_entries.async_update_entry(
                    entry, data={CONF_API_TOKEN: token}
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        schema = vol.Schema({
            vol.Required(CONF_API_TOKEN): TextSelector(
                TextSelectorConfig(type=TextSelectorType.PASSWORD)
            ),
        })

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=schema,
            errors=errors,
        )
