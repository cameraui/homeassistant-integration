from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass

from awesomeversion import AwesomeVersion
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntry

from .api import CameraUiApiError, CameraUiClient
from .clips import ClipCache
from .const import (
    CLIP_QUALITY_LOW,
    CONF_CLIP_QUALITY,
    CONF_PROXY_SECRET,
    CONF_TOKEN,
    DOMAIN,
    MIN_SERVER_VERSION,
)
from .coordinator import CameraUiCoordinator
from .panel import async_register_panel, async_register_panel_static, async_unregister_panel
from .ptz import async_setup_ptz_service
from .resources import async_register_cards_bundle, async_unregister_cards_bundle
from .rpc import CameraUiRpc
from .sensor_manager import CameraUiSensorManager
from .sensor_map import SENSOR_PLATFORMS
from .views import (
    CameraUiAuthProxyView,
    CameraUiCardsAssetView,
    CameraUiCardsFontView,
    CameraUiMediaView,
    CameraUiProxyView,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.CAMERA, Platform.UPDATE, *SENSOR_PLATFORMS]

DATA_GLOBAL_SETUP = f"{DOMAIN}_global_setup"


@dataclass
class CameraUiRuntimeData:
    coordinator: CameraUiCoordinator
    sensor_manager: CameraUiSensorManager
    rpc: CameraUiRpc
    clips: ClipCache


type CameraUiConfigEntry = ConfigEntry[CameraUiRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: CameraUiConfigEntry) -> bool:
    if not hass.data.get(DATA_GLOBAL_SETUP):
        hass.data[DATA_GLOBAL_SETUP] = True
        hass.http.register_view(CameraUiProxyView)
        hass.http.register_view(CameraUiAuthProxyView)
        hass.http.register_view(CameraUiCardsAssetView)
        hass.http.register_view(CameraUiCardsFontView)
        hass.http.register_view(CameraUiMediaView)
        async_setup_ptz_service(hass)
        await async_register_panel_static(hass)

    session = async_get_clientsession(hass, verify_ssl=False)
    client = CameraUiClient(entry.data[CONF_HOST], entry.data[CONF_PORT], entry.data[CONF_TOKEN], session)

    coordinator = CameraUiCoordinator(hass, entry, client)

    await coordinator.async_config_entry_first_refresh()

    try:
        info = await client.get_info()
        _async_check_server_version(hass, entry, str(info.get("version", "0")))
        tag = await client.cards_bundle_tag()
        if tag:
            await async_register_cards_bundle(hass, entry.entry_id, f"{info.get('version', '0')}-{tag}")
        else:
            _LOGGER.info(
                "camera.ui at %s does not ship the dashboard cards bundle, skipping", entry.data[CONF_HOST]
            )
            await async_unregister_cards_bundle(hass, entry.entry_id)
    except CameraUiApiError as err:
        _LOGGER.warning("Cards bundle not registered: %s", err)

    try:
        await client.connect_events()
    except CameraUiApiError as err:
        raise ConfigEntryNotReady(f"Event socket unavailable: {err}") from err

    sensor_manager = CameraUiSensorManager(hass, coordinator)
    await sensor_manager.async_setup()

    rpc = CameraUiRpc(entry.data[CONF_HOST], entry.data[CONF_PORT], entry.data[CONF_TOKEN])
    clips = ClipCache(
        hass, entry.entry_id, rpc, client.base_url, entry.options.get(CONF_CLIP_QUALITY, CLIP_QUALITY_LOW)
    )
    await clips.wipe()

    entry.runtime_data = CameraUiRuntimeData(coordinator, sensor_manager, rpc, clips)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    secret = entry.data.get(CONF_PROXY_SECRET)
    if not secret:
        secret = secrets.token_urlsafe(24)
        hass.config_entries.async_update_entry(entry, data={**entry.data, CONF_PROXY_SECRET: secret})
    async_register_panel(hass, entry, secret)
    return True


# older servers keep their entities, the parts they lack (cards, panel auto-login) are named in a repair
def _async_check_server_version(hass: HomeAssistant, entry: CameraUiConfigEntry, version: str) -> None:
    issue_id = f"server_outdated_{entry.entry_id}"
    try:
        outdated = AwesomeVersion(version) < AwesomeVersion(MIN_SERVER_VERSION)
    except Exception:  # noqa: BLE001
        outdated = False
    if outdated:
        ir.async_create_issue(
            hass,
            DOMAIN,
            issue_id,
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="server_outdated",
            translation_placeholders={
                "host": entry.data[CONF_HOST],
                "version": version,
                "min_version": MIN_SERVER_VERSION,
            },
        )
    else:
        ir.async_delete_issue(hass, DOMAIN, issue_id)


async def _async_options_updated(hass: HomeAssistant, entry: CameraUiConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: CameraUiConfigEntry) -> bool:
    async_unregister_panel(hass, entry)
    await entry.runtime_data.coordinator.client.disconnect_events()
    await entry.runtime_data.rpc.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: CameraUiConfigEntry, device: DeviceEntry
) -> bool:
    cameras = entry.runtime_data.coordinator.data
    sensors = entry.runtime_data.sensor_manager
    for domain, ident in device.identifiers:
        if domain != DOMAIN:
            continue
        if ident in cameras:
            return False
        if ident.startswith("sensor_") and sensors.has_sensor(ident.removeprefix("sensor_")):
            return False
        if ident.startswith("server_"):
            return False
    return True
