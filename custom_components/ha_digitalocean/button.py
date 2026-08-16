import logging

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DigitalOceanCoordinator
from .entity import DigitalOceanEntity

_LOGGER = logging.getLogger(__name__)

BUTTONS = [
    ("reboot", "Reboot", ButtonDeviceClass.RESTART),
    ("power_cycle", "Power cycle", None),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DigitalOceanCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for droplet_id in coordinator.data:
        for action, name, device_class in BUTTONS:
            entities.append(
                DropletActionButton(coordinator, droplet_id, action, name, device_class)
            )
    async_add_entities(entities)


class DropletActionButton(DigitalOceanEntity, ButtonEntity):
    def __init__(
        self,
        coordinator: DigitalOceanCoordinator,
        droplet_id: int,
        action: str,
        name: str,
        device_class: ButtonDeviceClass | None,
    ) -> None:
        super().__init__(coordinator, droplet_id)
        self._action = action
        self._attr_unique_id = f"{droplet_id}_{action}"
        self._attr_device_class = device_class
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def async_press(self) -> None:
        try:
            await self.coordinator.api.droplet_action(self._droplet_id, self._action)
        except Exception as err:
            raise HomeAssistantError(f"Failed to {self._action}: {err}") from err
        await self.coordinator.async_request_refresh()
