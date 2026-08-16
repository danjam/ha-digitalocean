from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DigitalOceanCoordinator
from .entity import DigitalOceanEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DigitalOceanCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for droplet_id in coordinator.data:
        entities.extend([
            DropletSensor(coordinator, droplet_id, "vcpus", "vCPUs", None, lambda d: d.get("vcpus")),
            DropletSensor(coordinator, droplet_id, "memory", "Memory", UnitOfInformation.MEGABYTES, lambda d: d.get("memory")),
            DropletSensor(coordinator, droplet_id, "disk", "Disk", UnitOfInformation.GIGABYTES, lambda d: d.get("disk")),
            DropletSensor(coordinator, droplet_id, "region", "Region", None, lambda d: d.get("region", {}).get("name")),
            DropletSensor(coordinator, droplet_id, "image", "Image", None, lambda d: d.get("image", {}).get("distribution", "") + " " + d.get("image", {}).get("name", "")),
            DropletSensor(coordinator, droplet_id, "ipv4", "IPv4", None, _get_public_ipv4),
            DropletSensor(coordinator, droplet_id, "monthly_cost", "Monthly cost", "USD", lambda d: d.get("size", {}).get("price_monthly")),
        ])
    async_add_entities(entities)


def _get_public_ipv4(droplet: dict) -> str | None:
    for net in droplet.get("networks", {}).get("v4", []):
        if net.get("type") == "public":
            return net.get("ip_address")
    return None


class DropletSensor(DigitalOceanEntity, SensorEntity):
    def __init__(
        self,
        coordinator: DigitalOceanCoordinator,
        droplet_id: int,
        key: str,
        name: str,
        unit: str | None,
        value_fn,
    ) -> None:
        super().__init__(coordinator, droplet_id)
        self._attr_unique_id = f"{droplet_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._name = name
        self._value_fn = value_fn

    @property
    def name(self) -> str:
        return self._name

    @property
    def native_value(self):
        if self.droplet is None:
            return None
        return self._value_fn(self.droplet)
