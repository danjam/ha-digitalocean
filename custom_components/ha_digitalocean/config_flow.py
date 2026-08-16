import logging

import voluptuous as vol
import yaml

from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DigitalOceanAPI
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

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            token = user_input[CONF_API_TOKEN]
            session = async_get_clientsession(self.hass)
            api = DigitalOceanAPI(token, session)
            if await api.validate():
                account = await api.get_account()
                await self.async_set_unique_id(account["email"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=account["email"],
                    data={CONF_API_TOKEN: token},
                )
            errors["base"] = "auth_failed"

        default_token = ""
        if user_input is None:
            default_token = await self.hass.async_add_executor_job(
                self._read_secret, CONF_SECRET_KEY
            ) or ""

        schema = vol.Schema({
            vol.Required(CONF_API_TOKEN, default=default_token): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
