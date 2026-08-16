import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DigitalOceanCoordinator
from .entity import DigitalOceanEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DigitalOceanCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for droplet_id in coordinator.data:
        entities.extend([
            DropletActionButton(coordinator, droplet_id, "reboot", "Reboot"),
            DropletActionButton(coordinator, droplet_id, "power_cycle", "Power cycle"),
        ])
    async_add_entities(entities)


class DropletActionButton(DigitalOceanEntity, ButtonEntity):
    def __init__(
        self,
        coordinator: DigitalOceanCoordinator,
        droplet_id: int,
        action: str,
        name: str,
    ) -> None:
        super().__init__(coordinator, droplet_id)
        self._action = action
        self._attr_unique_id = f"{droplet_id}_{action}"
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def async_press(self) -> None:
        await self.coordinator.api.droplet_action(self._droplet_id, self._action)
        await self.coordinator.async_request_refresh()
