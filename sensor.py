"""Support for NIO Vehicle sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfPressure,
    UnitOfTemperature,  # 使用新的温度单位常量
)

from . import DOMAIN, NIOVehicleDataUpdateCoordinator, NIOVehicleEntity

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NIO Vehicle sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        NIOBatterySensor(coordinator),
        NIORemainRangeSensor(coordinator),
        NIOActualRemainRangeSensor(coordinator),  # 添加实际续航里程传感器
        NIOTyrePressureSensor(coordinator, "front_left"),
        NIOTyrePressureSensor(coordinator, "front_right"),
        NIOTyrePressureSensor(coordinator, "rear_left"),
        NIOTyrePressureSensor(coordinator, "rear_right"),
        NIOTemperatureSensor(coordinator),
    ]
    
    async_add_entities(sensors)

class NIOBatterySensor(NIOVehicleEntity, SensorEntity):
    """Representation of NIO Battery sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "battery")
        self._attr_name = "电池电量 Battery Level"
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data["data"]["soc_status"]["soc"]

class NIORemainRangeSensor(NIOVehicleEntity, SensorEntity):
    """Representation of NIO Remaining Range sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "range")
        self._attr_name = "预估续航里程 Remaining Range"
        self._attr_device_class = SensorDeviceClass.DISTANCE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfLength.KILOMETERS

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data["data"]["soc_status"]["remaining_range"]

class NIOTyrePressureSensor(NIOVehicleEntity, SensorEntity):
    """Representation of NIO Tyre Pressure sensor."""

    def __init__(self, coordinator, position):
        """Initialize the sensor."""
        super().__init__(coordinator, f"tyre_pressure_{position}")
        
        # 映射位置到中文名称
        self._name_map = {
            "front_left": "前左轮胎压力 Front Left Tyre",
            "front_right": "前右轮胎压力 Front Right Tyre",
            "rear_left": "后左轮胎压力 Rear Left Tyre",
            "rear_right": "后右轮胎压力 Rear Right Tyre",
        }
        
        self.position = position
        self._attr_name = self._name_map[position]
        self._attr_device_class = SensorDeviceClass.PRESSURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfPressure.BAR

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data["data"]["tyre_status"][f"{self.position}_wheel_press_bar"]

class NIOActualRemainRangeSensor(NIOVehicleEntity, SensorEntity):
    """Representation of NIO Actual Remaining Range sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "actual_range")
        self._attr_name = "实际续航里程 Actual Range"
        self._attr_device_class = SensorDeviceClass.DISTANCE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfLength.KILOMETERS

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data["data"]["soc_status"]["remaining_actual_range"]

class NIOTemperatureSensor(NIOVehicleEntity, SensorEntity):
    """Representation of NIO Temperature sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator, "temperature")
        self._attr_name = "车外温度 Outside Temperature"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS  # 使用新的温度单位常量

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data["data"]["hvac_status"]["outside_temperature"]