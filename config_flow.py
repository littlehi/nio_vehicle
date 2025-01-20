"""Config flow for NIO Vehicle integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_VEHICLE_ID,
    CONF_ACCESS_TOKEN,
    CONF_APP_VERSION,
    CONF_DEVICE_ID,
    CONF_SIGN,
    CONF_TIMESTAMP,
    API_HEADERS,
    API_BASE_URL,
    DEFAULT_APP_ID,
    DEFAULT_APP_VERSION,
    DEFAULT_LANGUAGE,
    DEFAULT_REGION,
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NIO Vehicle."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await self._validate_input(user_input)
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show the form to the user
        data_schema = vol.Schema({
            vol.Required(CONF_VEHICLE_ID): str,
            vol.Required(CONF_ACCESS_TOKEN): str,
            vol.Required(CONF_DEVICE_ID): str,
            vol.Required(CONF_SIGN): str,
            vol.Required(CONF_TIMESTAMP): str,
            vol.Optional(CONF_APP_VERSION, default=DEFAULT_APP_VERSION): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def _validate_input(self, data: dict) -> dict:
        """Validate the user input allows us to connect."""
        headers = API_HEADERS.copy()
        headers["Authorization"] = f"Bearer {data[CONF_ACCESS_TOKEN]}"
        headers["User-Agent"] = headers["User-Agent"].replace(DEFAULT_APP_VERSION, data[CONF_APP_VERSION])

        url = f"{API_BASE_URL}/{data[CONF_VEHICLE_ID]}/status"
        
        params = {
            "field": [
                "soc", "door", "position", "connection", "exterior",
                "hvac", "window", "tyre", "maintain", "special",
                "fota", "heating", "offcar_mode_status", "light",
                "mix_auth", "remote_operate_status", "frdg",
                "nearby_car_ctrl", "trip_share_status",
                "offcar_power_swap_status"
            ],
            "timestamp": data[CONF_TIMESTAMP],
            "device_id": data[CONF_DEVICE_ID],
            "app_id": DEFAULT_APP_ID,
            "app_ver": data[CONF_APP_VERSION],
            "lang": DEFAULT_LANGUAGE,
            "region": DEFAULT_REGION,
            "sign": data[CONF_SIGN]
        }

        try:
            session = async_get_clientsession(self.hass)
            
            # 构建完整的URL用于日志
            from urllib.parse import urlencode
            query_string = urlencode(params, doseq=True)
            full_url = f"{url}?{query_string}"
            _LOGGER.debug("Validation request URL: %s", full_url)
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    raise CannotConnect
                response_data = await response.json()
                if response_data.get("result_code") != "success":
                    raise InvalidAuth
                
                return {"title": f"NIO Vehicle ({data[CONF_VEHICLE_ID]})"}
        except aiohttp.ClientError:
            raise CannotConnect
        except Exception as ex:
            _LOGGER.error("Validation error: %s", ex)
            raise CannotConnect from ex


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""