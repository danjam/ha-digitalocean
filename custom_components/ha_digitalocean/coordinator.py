import logging
from datetime import timedelta

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DigitalOceanAPI, DigitalOceanAuthError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class DigitalOceanCoordinator(DataUpdateCoordinator[dict[int, dict]]):
    def __init__(self, hass: HomeAssistant, api: DigitalOceanAPI, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=entry,
        )
        self.api = api

    async def _async_update_data(self) -> dict[int, dict]:
        try:
            droplets = await self.api.get_droplets()
        except DigitalOceanAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except ClientError as err:
            raise UpdateFailed(f"Failed to fetch droplets: {err}") from err
        return {d["id"]: d for d in droplets}
