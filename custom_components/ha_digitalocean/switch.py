import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DigitalOceanCoordinator
from .entity import DigitalOceanEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DigitalOceanCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DropletPowerSwitch(coordinator, droplet_id)
        for droplet_id in coordinator.data
    )


class DropletPowerSwitch(DigitalOceanEntity, SwitchEntity):
    def __init__(self, coordinator: DigitalOceanCoordinator, droplet_id: int) -> None:
        super().__init__(coordinator, droplet_id)
        self._attr_unique_id = f"{droplet_id}_power"

    @property
    def name(self) -> str:
        return "Power"

    @property
    def is_on(self) -> bool | None:
        if self.droplet is None:
            return None
        return self.droplet.get("status") == "active"

    async def async_turn_on(self, **kwargs) -> None:
        try:
            await self.coordinator.api.droplet_action(self._droplet_id, "power_on")
        except Exception as err:
            raise HomeAssistantError(f"Failed to power on: {err}") from err
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        try:
            await self.coordinator.api.droplet_action(self._droplet_id, "shutdown")
        except Exception as err:
            raise HomeAssistantError(f"Failed to shut down: {err}") from err
        self._attr_is_on = False
        self.async_write_ha_state()
