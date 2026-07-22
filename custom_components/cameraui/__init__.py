from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntry

from .api import CameraUiApiError, CameraUiClient
from .const import CONF_PROXY_SECRET, CONF_TOKEN, DOMAIN
from .coordinator import CameraUiCoordinator
from .panel import async_register_panel, async_register_panel_static, async_unregister_panel
from .ptz import async_setup_ptz_service
from .resources import async_register_card
from .sensor_manager import CameraUiSensorManager
from .sensor_map import SENSOR_PLATFORMS
from .views import CameraUiProbeView, CameraUiProxyView, CameraUiSnapshotView, CameraUiWsProxyView

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CAMERA, *SENSOR_PLATFORMS]

DATA_GLOBAL_SETUP = f"{DOMAIN}_global_setup"


@dataclass
class CameraUiRuntimeData:
    coordinator: CameraUiCoordinator
    sensor_manager: CameraUiSensorManager


type CameraUiConfigEntry = ConfigEntry[CameraUiRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: CameraUiConfigEntry) -> bool:
    if not hass.data.get(DATA_GLOBAL_SETUP):
        hass.data[DATA_GLOBAL_SETUP] = True
        hass.http.register_view(CameraUiWsProxyView)
        hass.http.register_view(CameraUiSnapshotView)
        hass.http.register_view(CameraUiProbeView)
        hass.http.register_view(CameraUiProxyView)
        async_setup_ptz_service(hass)
        await async_register_card(hass)
        await async_register_panel_static(hass)

    session = async_get_clientsession(hass, verify_ssl=False)
    client = CameraUiClient(entry.data[CONF_HOST], entry.data[CONF_PORT], entry.data[CONF_TOKEN], session)

    coordinator = CameraUiCoordinator(hass, entry, client)

    await coordinator.async_config_entry_first_refresh()

    try:
        await client.connect_events()
    except CameraUiApiError as err:
        raise ConfigEntryNotReady(f"Event socket unavailable: {err}") from err

    sensor_manager = CameraUiSensorManager(hass, coordinator)
    await sensor_manager.async_setup()

    entry.runtime_data = CameraUiRuntimeData(coordinator, sensor_manager)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    secret = entry.data.get(CONF_PROXY_SECRET)
    if not secret:
        secret = secrets.token_urlsafe(24)
        hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_PROXY_SECRET: secret})
    async_register_panel(hass, entry, secret)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: CameraUiConfigEntry) -> bool:
    async_unregister_panel(hass, entry)
    await entry.runtime_data.coordinator.client.disconnect_events()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: CameraUiConfigEntry, device: DeviceEntry
) -> bool:
    cameras = entry.runtime_data.coordinator.data
    return not any(domain == DOMAIN and ident in cameras for domain, ident in device.identifiers)
