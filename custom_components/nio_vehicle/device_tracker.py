"""Support for tracking NIO vehicles."""
from __future__ import annotations

from homeassistant.components.device_tracker import (
    SourceType,
    TrackerEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, NIOVehicleEntity
from .const import CONF_VEHICLE_ID

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the NIO tracker from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([NIODeviceTracker(coordinator)])

class NIODeviceTracker(NIOVehicleEntity, TrackerEntity):
    """NIO device tracker."""

    def __init__(self, coordinator):
        """Initialize the tracker."""
        super().__init__(coordinator, "location")
        self.entity_id = f"device_tracker.{self.entity_id_prefix}_location"
        self._attr_name = "位置 Location"
        self._attr_unique_id = f"{coordinator.config_entry.data[CONF_VEHICLE_ID]}_location"

    @property
    def source_type(self) -> SourceType:
        """Return the source type of the device."""
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        try:
            return self.coordinator.data["data"]["position_status"]["latitude"]
        except KeyError:
            return None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        try:
            return self.coordinator.data["data"]["position_status"]["longitude"]
        except KeyError:
            return None
