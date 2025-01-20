"""The NIO Vehicle integration."""
from __future__ import annotations

import logging
import asyncio
from datetime import timedelta

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    CONF_VEHICLE_ID,
    CONF_ACCESS_TOKEN,
    CONF_APP_VERSION,
    CONF_DEVICE_ID,
    CONF_SIGN,
    CONF_TIMESTAMP,
    DEFAULT_SCAN_INTERVAL,
    API_HEADERS,
    API_BASE_URL,
    DEFAULT_APP_ID,
    DEFAULT_APP_VERSION,
    DEFAULT_LANGUAGE,
    DEFAULT_REGION,
    MANUFACTURER,
    MODEL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_VEHICLE_ID): str,
                vol.Required(CONF_ACCESS_TOKEN): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_SIGN): str,
                vol.Required(CONF_TIMESTAMP): str,
                vol.Optional(CONF_APP_VERSION, default=DEFAULT_APP_VERSION): str,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the NIO Vehicle component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NIO Vehicle from a config entry."""
    coordinator = NIOVehicleDataUpdateCoordinator(
        hass=hass,
        config_entry=entry,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class NIOVehicleDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NIO Vehicle data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"nio_vehicle_{config_entry.data[CONF_VEHICLE_ID]}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.config_entry = config_entry
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self):
        """Fetch data from NIO API."""
        headers = API_HEADERS.copy()
        headers["Authorization"] = f"Bearer {self.config_entry.data[CONF_ACCESS_TOKEN]}"
        headers["User-Agent"] = headers["User-Agent"].replace(
            DEFAULT_APP_VERSION, 
            self.config_entry.data.get(CONF_APP_VERSION, DEFAULT_APP_VERSION)
        )

        url = f"{API_BASE_URL}/{self.config_entry.data[CONF_VEHICLE_ID]}/status"
        
        params = {
            "field": [
                "soc", "door", "position", "connection", "exterior",
                "hvac", "window", "tyre", "maintain", "special",
                "fota", "heating", "offcar_mode_status", "light",
                "mix_auth", "remote_operate_status", "frdg",
                "nearby_car_ctrl", "trip_share_status",
                "offcar_power_swap_status"
            ],
            "timestamp": self.config_entry.data[CONF_TIMESTAMP],
            "device_id": self.config_entry.data[CONF_DEVICE_ID],
            "app_id": DEFAULT_APP_ID,
            "app_ver": self.config_entry.data.get(CONF_APP_VERSION, DEFAULT_APP_VERSION),
            "lang": DEFAULT_LANGUAGE,
            "region": DEFAULT_REGION,
            "sign": self.config_entry.data[CONF_SIGN]
        }

        try:
            # 构建完整的URL用于日志
            from urllib.parse import urlencode
            query_string = urlencode(params, doseq=True)
            full_url = f"{url}?{query_string}"
            _LOGGER.debug("Full request URL: %s", full_url)
            
            async with async_timeout.timeout(10):
                response = await self.session.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = await response.json()
                
                if data.get("result_code") != "success":
                    raise UpdateFailed("API request failed")
                
                return data

        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout error") from err
        except (aiohttp.ClientError, KeyError) as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

class NIOVehicleEntity(CoordinatorEntity):
    """Base class for NIO Vehicle entities."""

    def __init__(self, coordinator: NIOVehicleDataUpdateCoordinator, device_class: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_class = device_class
        self._attr_unique_id = f"{coordinator.config_entry.data[CONF_VEHICLE_ID]}_{device_class}"
        
        # Set up device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.data[CONF_VEHICLE_ID])},
            "name": f"NIO Vehicle ({coordinator.config_entry.data[CONF_VEHICLE_ID]})",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
        }