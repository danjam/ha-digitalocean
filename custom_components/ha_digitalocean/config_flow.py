import voluptuous as vol
from aiohttp import ClientSession

from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DigitalOceanAPI
from .const import CONF_API_TOKEN, DOMAIN


class DigitalOceanConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = DigitalOceanAPI(user_input[CONF_API_TOKEN], session)
            if await api.validate():
                account = await api.get_account()
                await self.async_set_unique_id(account["email"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=account["email"],
                    data=user_input,
                )
            errors["base"] = "auth_failed"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_TOKEN): str}),
            errors=errors,
        )
