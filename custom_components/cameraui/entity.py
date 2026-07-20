from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SIGNAL_SENSOR_NEW, signal_sensor_remove, signal_sensor_update
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
        return super().available and self._camera_id in self.coordinator.data


class CameraUiSensorEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, manager: CameraUiSensorManager, sensor: dict[str, Any]) -> None:
        self._manager = manager
        self._global_id = sensor["globalId"]
        self._camera_id = sensor["camera_id"]
        # never stableId: it repeats across cameras, HA would drop the duplicate
        self._attr_unique_id = self._global_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._camera_id)},
            manufacturer="camera.ui",
        )

    @property
    def _sensor(self) -> dict[str, Any] | None:
        return self._manager.get_sensor(self._global_id)

    @property
    def name(self) -> str | None:
        # live, not cached: a rename in the UI must land on the existing entity
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
        return self._sensor is not None

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal_sensor_update(self._global_id), self._handle_update)
        )
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal_sensor_remove(self._global_id), self._handle_remove)
        )

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()

    async def _handle_remove(self) -> None:
        # drop from the registry too, else HA keeps it as an unavailable ghost
        registry = er.async_get(self.hass)
        if self.entity_id and registry.async_get(self.entity_id):
            registry.async_remove(self.entity_id)
        else:
            await self.async_remove(force_remove=True)

    async def async_command(self, property_name: str, value: Any) -> None:
        await self._manager.async_command(self._global_id, property_name, value)


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
            add_for(sensor["camera_id"])

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_SENSOR_NEW, on_new))
