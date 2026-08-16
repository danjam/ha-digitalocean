import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DigitalOceanAPI
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class DigitalOceanCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api: DigitalOceanAPI) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> dict:
        try:
            droplets = await self.api.get_droplets()
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch droplets: {err}") from err
        return {d["id"]: d for d in droplets}
