from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SIGNAL_CONNECTION,
    SIGNAL_SENSOR_ASSIGNED,
    SIGNAL_SENSOR_NEW,
    signal_sensor_remove,
    signal_sensor_update,
)
from .coordinator import CameraUiCoordinator
from .sensor_manager import CameraUiSensorManager
from .sensor_map import sensor_platform

if TYPE_CHECKING:
    from . import CameraUiConfigEntry


class CameraUiEntity(CoordinatorEntity[CameraUiCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: CameraUiCoordinator, camera_id: str) -> None:
        super().__init__(coordinator)
        self._camera_id = camera_id
        self._connected = True
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, camera_id)},
            name=self.camera_data.get("name", camera_id),
            manufacturer="camera.ui",
            configuration_url=coordinator.client.base_url,
        )

    @property
    def camera_data(self) -> dict[str, Any]:
        return self.coordinator.data.get(self._camera_id, {})

    @property
    def available(self) -> bool:
        return super().available and self._connected and self._camera_id in self.coordinator.data

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_CONNECTION, self._handle_connection))

    @callback
    def _handle_connection(self, connected: bool) -> None:
        self._connected = connected
        self.async_write_ha_state()


class CameraUiSensorEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, manager: CameraUiSensorManager, sensor: dict[str, Any]) -> None:
        self._manager = manager
        self._sensor_id = sensor["id"]
        self._connected = True
        self._attr_unique_id = self._sensor_id

        assigned = sensor.get("assignedCameraIds", [])
        # camera hardware sits on the camera device; everything else is its own
        # device, linked below the camera when there is exactly one
        self._own_device = not (sensor.get("assignmentLocked") and len(assigned) == 1)
        if self._own_device:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"sensor_{self._sensor_id}")},
                name=sensor.get("displayName") or sensor.get("name"),
                manufacturer="camera.ui",
                model=sensor.get("pluginName"),
            )
            if len(assigned) == 1:
                self._attr_device_info["via_device"] = (DOMAIN, assigned[0])
        else:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, assigned[0])},
                manufacturer="camera.ui",
            )

    @property
    def _sensor(self) -> dict[str, Any] | None:
        return self._manager.get_sensor(self._sensor_id)

    @property
    def name(self) -> str | None:
        # a single-entity device carries the name; live for camera-device
        # sensors, so a rename in the UI lands on the existing entity
        if self._own_device:
            return None
        sensor = self._sensor
        return (sensor.get("displayName") if sensor else None) or None

    @property
    def _semantics(self) -> dict[str, Any]:
        sensor = self._sensor
        return (sensor.get("semantics") or {}) if sensor else {}

    @property
    def _properties(self) -> dict[str, Any]:
        sensor = self._sensor
        return sensor.get("properties", {}) if sensor else {}

    @property
    def available(self) -> bool:
        sensor = self._sensor
        return self._connected and sensor is not None and sensor.get("connected", True)

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal_sensor_update(self._sensor_id), self._handle_update)
        )
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal_sensor_remove(self._sensor_id), self._handle_remove)
        )
        self.async_on_remove(async_dispatcher_connect(self.hass, SIGNAL_CONNECTION, self._handle_connection))

    @callback
    def _handle_update(self) -> None:
        if self._own_device:
            self._sync_device_name()
        self.async_write_ha_state()

    @callback
    def _sync_device_name(self) -> None:
        sensor = self._sensor
        if not sensor:
            return
        registry = dr.async_get(self.hass)
        device = registry.async_get_device(identifiers={(DOMAIN, f"sensor_{self._sensor_id}")})
        name = sensor.get("displayName") or sensor.get("name")
        if device and name and device.name != name:
            registry.async_update_device(device.id, name=name)

    @callback
    def _handle_connection(self, connected: bool) -> None:
        self._connected = connected
        self.async_write_ha_state()

    async def _handle_remove(self) -> None:
        # drop from the registry too, else HA keeps it as an unavailable ghost
        registry = er.async_get(self.hass)
        if self.entity_id and registry.async_get(self.entity_id):
            registry.async_remove(self.entity_id)
        else:
            await self.async_remove(force_remove=True)

    async def async_command(self, property_name: str, value: Any) -> None:
        await self._manager.async_command(self._sensor_id, property_name, value)


def async_setup_sensor_platform(
    hass: HomeAssistant,
    entry: CameraUiConfigEntry,
    async_add_entities: AddEntitiesCallback,
    platform: Platform,
    factory: Callable[[CameraUiSensorManager, dict[str, Any]], CameraUiSensorEntity],
) -> None:
    manager = entry.runtime_data.sensor_manager

    @callback
    def add_sensor(sensor: dict[str, Any]) -> None:
        if sensor_platform(sensor) is platform:
            async_add_entities([factory(manager, sensor)])

    for sensor in manager.sensors_for_platform(platform):
        add_sensor(sensor)

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_SENSOR_NEW, add_sensor))


def async_setup_detection_entities(
    hass: HomeAssistant,
    entry: CameraUiConfigEntry,
    async_add_entities: AddEntitiesCallback,
    sensor_type: str,
    factory: Callable[[str], Sequence[Entity]],
) -> None:
    manager = entry.runtime_data.sensor_manager
    coordinator = entry.runtime_data.coordinator
    created: set[str] = set()

    @callback
    def add_for(camera_id: str) -> None:
        if camera_id in created or camera_id not in coordinator.data:
            return
        created.add(camera_id)
        async_add_entities(factory(camera_id))

    for camera_id in manager.cameras_with_sensor_type(sensor_type):
        add_for(camera_id)

    @callback
    def on_new(sensor: dict[str, Any]) -> None:
        if sensor.get("type") == sensor_type:
            for camera_id in sensor.get("assignedCameraIds", []):
                add_for(camera_id)

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_SENSOR_NEW, on_new))
    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_SENSOR_ASSIGNED, on_new))
