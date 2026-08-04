from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .api import CameraUiApiError, CameraUiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_SCAN_INTERVAL = timedelta(hours=6)


class CameraUiUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: Any, client: CameraUiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_updates",
            update_interval=UPDATE_SCAN_INTERVAL,
            config_entry=entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        info = await self.client.get_info()
        versions = await self.client.get_server_versions()
        latest = (versions.get("dist-tags") or {}).get("latest")

        plugins: dict[str, dict[str, Any]] = {}
        for plugin in await self.client.get_plugins():
            name = plugin.get("pluginName")
            installed = plugin.get("installedVersion")
            if not name or not installed or plugin.get("private"):
                continue
            state = await self.client.get_plugin_update(name) or {}
            plugins[name] = {
                "display_name": plugin.get("displayName") or name,
                "installed": installed,
                "latest": state.get("latestVersion") or installed,
            }

        return {
            "server": {
                "installed": info.get("installedVersion") or info.get("version"),
                "latest": latest or info.get("installedVersion"),
            },
            "plugins": plugins,
        }


async def async_setup_entry(hass: HomeAssistant, entry: Any, async_add_entities: AddEntitiesCallback) -> None:
    client = entry.runtime_data.coordinator.client
    coordinator = CameraUiUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    device = _server_device(entry)

    # the registry does not reliably pick up a changed name from device_info
    # on existing devices — rename explicitly (name_by_user still wins)
    registry = dr.async_get(hass)
    if (
        existing := registry.async_get_device(identifiers={(DOMAIN, f"server_{entry.entry_id}")})
    ) and existing.name != device["name"]:
        registry.async_update_device(existing.id, name=device["name"])

    entities: list[UpdateEntity] = [CameraUiServerUpdateEntity(coordinator, entry, device)]
    known_plugins: set[str] = set()

    @callback
    def _sync_plugin_entities() -> None:
        fresh = [
            CameraUiPluginUpdateEntity(coordinator, entry, device, name)
            for name in coordinator.data["plugins"]
            if name not in known_plugins
        ]
        known_plugins.update(coordinator.data["plugins"])
        if fresh:
            async_add_entities(fresh)

    known_plugins.update(coordinator.data["plugins"])
    entities.extend(CameraUiPluginUpdateEntity(coordinator, entry, device, name) for name in known_plugins)
    async_add_entities(entities)

    entry.async_on_unload(coordinator.async_add_listener(_sync_plugin_entities))


def _server_device(entry: Any) -> DeviceInfo:
    # HA composes every display name as "<device> <entity>", so the device
    # carries the short brand name; renaming the device once (multi-server)
    # cascades into all update entity names
    return DeviceInfo(
        identifiers={(DOMAIN, f"server_{entry.entry_id}")},
        name="camera.ui",
        manufacturer="camera.ui",
        model="Server",
    )


class CameraUiServerUpdateEntity(CoordinatorEntity[CameraUiUpdateCoordinator], UpdateEntity):
    _attr_has_entity_name = True
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES
    _attr_title = "camera.ui"
    # main entity of the device: display name is just the device name
    _attr_name = None

    def __init__(self, coordinator: CameraUiUpdateCoordinator, entry: Any, device: DeviceInfo) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_server_update"
        self._attr_device_info = device

    @property
    def installed_version(self) -> str | None:
        return self.coordinator.data["server"]["installed"]

    @property
    def latest_version(self) -> str | None:
        return self.coordinator.data["server"]["latest"]

    async def async_release_notes(self) -> str | None:
        version = self.latest_version
        if not version:
            return None
        return await self.coordinator.client.get_server_changelog(version)

    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        target = version or self.latest_version
        if not target:
            return
        self._attr_in_progress = True
        self.async_write_ha_state()
        try:
            await self.coordinator.client.update_server(target)
            # the update only stages the new version, the restart applies it
            await self.coordinator.client.restart_server()
        finally:
            self._attr_in_progress = False
            self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class CameraUiPluginUpdateEntity(CoordinatorEntity[CameraUiUpdateCoordinator], UpdateEntity):
    _attr_has_entity_name = True
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES

    def __init__(
        self,
        coordinator: CameraUiUpdateCoordinator,
        entry: Any,
        device: DeviceInfo,
        plugin_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._plugin_name = plugin_name
        self._attr_unique_id = f"{entry.entry_id}_plugin_update_{plugin_name}"
        self._attr_device_info = device
        display = self._plugin.get("display_name", plugin_name)
        self._attr_title = display
        self._attr_name = display

    @property
    def _plugin(self) -> dict[str, Any]:
        return self.coordinator.data["plugins"].get(self._plugin_name, {})

    @property
    def available(self) -> bool:
        return super().available and self._plugin_name in self.coordinator.data["plugins"]

    @property
    def installed_version(self) -> str | None:
        return self._plugin.get("installed")

    @property
    def latest_version(self) -> str | None:
        return self._plugin.get("latest")

    async def async_release_notes(self) -> str | None:
        return await self.coordinator.client.get_plugin_changelog(self._plugin_name, self.latest_version)

    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        target = version or self.latest_version
        if not target:
            return
        self._attr_in_progress = True
        self.async_write_ha_state()
        try:
            await self.coordinator.client.install_plugin(self._plugin_name, target)
        except CameraUiApiError as err:
            _LOGGER.warning("Plugin update for %s failed: %s", self._plugin_name, err)
            raise
        finally:
            self._attr_in_progress = False
            self.async_write_ha_state()
        await self.coordinator.async_request_refresh()
