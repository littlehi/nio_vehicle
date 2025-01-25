"""Support for NIO Vehicle binary sensors."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from . import DOMAIN, NIOVehicleEntity

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NIO Vehicle binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        NIODoorLockSensor(coordinator),
        NIODoorSensor(coordinator, "front_left"),
        NIODoorSensor(coordinator, "front_right"),
        NIODoorSensor(coordinator, "rear_left"),
        NIODoorSensor(coordinator, "rear_right"),
        NIODoorSensor(coordinator, "trunk"),
        NIOChargingPortSensor(coordinator),
        NIOChargingSensor(coordinator),
    ]
    
    async_add_entities(sensors)

class NIODoorLockSensor(NIOVehicleEntity, BinarySensorEntity):
    """Representation of NIO Vehicle Lock sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "door_lock")
        self.entity_id = f"binary_sensor.{self.entity_id_prefix}_lock"
        self._attr_name = "车辆锁定状态 Door Lock"
        self._attr_device_class = BinarySensorDeviceClass.LOCK

    @property
    def is_on(self):
        """Return true if the vehicle is locked."""
        # vehicle_lock_status: 1 表示锁定, 返回 True 表示已锁定
        return self.coordinator.data["data"]["door_status"]["vehicle_lock_status"] != 1

class NIODoorSensor(NIOVehicleEntity, BinarySensorEntity):
    """Representation of NIO Door sensor."""

    def __init__(self, coordinator, position):
        """Initialize the sensor."""
        super().__init__(coordinator, f"door_{position}")
        self.position = position
        self.entity_id = f"binary_sensor.{self.entity_id_prefix}_door_{position}"
        self._attr_name = f"Door {position.replace('_', ' ').title()}"
        self._attr_device_class = BinarySensorDeviceClass.DOOR

        # 映射位置到API字段名称
        self._status_map = {
            "front_left": "door_ajar_front_left_status",
            "front_right": "door_ajar_front_right_status",
            "rear_left": "door_ajar_rear_left_status",
            "rear_right": "door_ajar_rear_right_status",
            "trunk": "tailgate_ajar_status",
        }

    @property
    def is_on(self):
        """Return true if the door is open."""
        # status: 1 表示关闭，所以需要反转状态
        # 返回 True 表示开启状态
        return self.coordinator.data["data"]["door_status"][self._status_map[self.position]] != 1

class NIOChargingPortSensor(NIOVehicleEntity, BinarySensorEntity):
    """Representation of NIO Charging Port sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "charging_port")
        self.entity_id = f"binary_sensor.{self.entity_id_prefix}_charging_port"
        self._attr_name = "充电口状态 Charging Port"
        self._attr_device_class = BinarySensorDeviceClass.DOOR

    @property
    def is_on(self):
        """Return true if the charging port is open."""
        # second_charge_port_ajar_status: 1 表示关闭，需要反转状态
        # 返回 True 表示开启状态
        return self.coordinator.data["data"]["door_status"]["second_charge_port_ajar_status"] != 1

class NIOChargingSensor(NIOVehicleEntity, BinarySensorEntity):
    """Representation of NIO Charging Status sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "charging")
        self.entity_id = f"binary_sensor.{self.entity_id_prefix}_charging"
        self._attr_name = "充电状态 Charging"
        self._attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    @property
    def is_on(self):
        """Return true if the vehicle is charging."""
        # charge_state: 1-4 表示正在充电的不同状态
        return self.coordinator.data["data"]["soc_status"]["charge_state"] > 0
