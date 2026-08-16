from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DigitalOceanCoordinator
from .entity import DigitalOceanEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DigitalOceanCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DropletStatusSensor(coordinator, droplet_id)
        for droplet_id in coordinator.data
    )


class DropletStatusSensor(DigitalOceanEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, coordinator: DigitalOceanCoordinator, droplet_id: int) -> None:
        super().__init__(coordinator, droplet_id)
        self._attr_unique_id = f"{droplet_id}_status"

    @property
    def name(self) -> str:
        return "Status"

    @property
    def is_on(self) -> bool | None:
        if self.droplet is None:
            return None
        return self.droplet.get("status") == "active"
