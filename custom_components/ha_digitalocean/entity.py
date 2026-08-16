from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DigitalOceanCoordinator


class DigitalOceanEntity(CoordinatorEntity[DigitalOceanCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: DigitalOceanCoordinator, droplet_id: int) -> None:
        super().__init__(coordinator)
        self._droplet_id = droplet_id

    @property
    def droplet(self) -> dict | None:
        return self.coordinator.data.get(self._droplet_id)

    @property
    def available(self) -> bool:
        return super().available and self.droplet is not None

    @property
    def device_info(self) -> DeviceInfo:
        droplet = self.droplet or {}
        image = droplet.get("image") or {}
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._droplet_id))},
            name=droplet.get("name", f"Droplet {self._droplet_id}"),
            manufacturer="DigitalOcean",
            model=droplet.get("size_slug", "droplet"),
            sw_version=image.get("description", ""),
        )
