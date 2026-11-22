from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import partial
from typing import TYPE_CHECKING, Any, cast

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
    signal_connection,
    signal_sensor_assigned,
    signal_sensor_new,
    signal_sensor_remove,
    signal_sensor_semantics,
    signal_sensor_update,
)
from .coordinator import CameraUiCoordinator
from .devices import async_get_device, async_remove_device_if_empty, async_set_via_device
from .sensor_manager import CameraUiSensorManager
from .sensor_map import sensor_platform

if TYPE_CHECKING:
    from . import CameraUiConfigEntry

DEVICE_FIELDS = ("name", "manufacturer", "model", "sw_version", "serial_number")


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
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal_connection(self.coordinator.config_entry.entry_id), self._handle_connection
            )
        )

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
        # camera hardware sits on the camera device
        self._camera_id: str | None = (
            assigned[0] if sensor.get("assignmentLocked") and len(assigned) == 1 else None
        )
        self._attr_device_info = self._device_info(sensor)

    @property
    def _sensor(self) -> dict[str, Any] | None:
        return self._manager.get_sensor(self._sensor_id)

    @property
    def name(self) -> str | None:
        # None takes the device name, live so a rename in the UI lands on the existing entity
        sensor = self._sensor
        if not sensor:
            return None
        if self._camera_id:
            return sensor.get("displayName") or None
        if sensor.get("device") and not sensor.get("primary"):
            return sensor.get("shortName") or sensor.get("displayName") or None
        return None

    @property
    def icon(self) -> str | None:
        return self._semantics.get("icon")

    @property
    def _semantics(self) -> dict[str, Any]:
        sensor = self._sensor
        return (sensor.get("semantics") or {}) if sensor else {}

    @property
    def _properties(self) -> dict[str, Any]:
        sensor = self._sensor
        return sensor.get("properties", {}) if sensor else {}

    @property
    def _state(self) -> Any:
        return self._properties.get(self._semantics.get("stateProperty", ""))

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
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal_connection(self._manager.entry_id), self._handle_connection
            )
        )

    @callback
    def _handle_update(self) -> None:
        if not self._camera_id:
            self._sync_device()
        self.async_write_ha_state()

    def _device_info(self, sensor: dict[str, Any]) -> DeviceInfo:
        if self._camera_id:
            return DeviceInfo(identifiers={(DOMAIN, self._camera_id)}, manufacturer="camera.ui")
        if device := sensor.get("device"):
            return DeviceInfo(
                identifiers={(DOMAIN, f"device_{device['id']}")},
                name=device.get("name"),
                manufacturer=device.get("manufacturer") or "camera.ui",
                model=device.get("model") or sensor.get("pluginName"),
                sw_version=device.get("firmware"),
                serial_number=device.get("serialNumber"),
            )
        info = DeviceInfo(
            identifiers={(DOMAIN, f"sensor_{self._sensor_id}")},
            name=sensor.get("displayName") or sensor.get("name"),
            manufacturer="camera.ui",
            model=sensor.get("pluginName"),
        )
        # linked below the camera when there is exactly one
        assigned = sensor.get("assignedCameraIds", [])
        if len(assigned) == 1:
            async_set_via_device(self._manager.hass, info, (DOMAIN, assigned[0]), self._manager.entry_id)
        return info

    @callback
    def _sync_device(self) -> None:
        sensor = self._sensor
        entry = self.registry_entry
        if not sensor or not entry:
            return
        info = self._device_info(sensor)
        device = async_get_device(self.hass, next(iter(info["identifiers"])), self._manager.entry_id)
        if device is None or device.id != entry.device_id:
            self._move_to_device(info, entry.device_id)
            return
        fields = cast("dict[str, Any]", info)
        changes = {
            key: fields[key] for key in DEVICE_FIELDS if key in fields and getattr(device, key) != fields[key]
        }
        if changes:
            dr.async_get(self.hass).async_update_device(device.id, **changes)

    @callback
    def _move_to_device(self, info: DeviceInfo, previous_device_id: str | None) -> None:
        device = dr.async_get(self.hass).async_get_or_create(config_entry_id=self._manager.entry_id, **info)
        er.async_get(self.hass).async_update_entity(self.entity_id, device_id=device.id)
        if previous_device_id:
            async_remove_device_if_empty(self.hass, previous_device_id)

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

    def _is(self, name: str) -> bool:
        expected = self._semantics.get("states", {}).get(name)
        return expected is not None and self._state == expected

    def _spec(self, property_name: str) -> dict[str, Any]:
        specs = (self._sensor or {}).get("propertySpecs") or {}
        return specs.get(property_name) or {}

    async def async_command(self, property_name: str, value: Any) -> None:
        await self._manager.async_command(self._sensor_id, property_name, value)


class CameraUiOpenCloseEntity(CameraUiSensorEntity):
    @property
    def is_closed(self) -> bool | None:
        return None if self._state is None else self._is("closed")

    @property
    def is_opening(self) -> bool:
        return self._is("opening")

    @property
    def is_closing(self) -> bool:
        return self._is("closing")


class CameraUiSensorSetting(CameraUiSensorEntity):
    def __init__(self, manager: CameraUiSensorManager, sensor: dict[str, Any], property_name: str) -> None:
        super().__init__(manager, sensor)
        self._property = property_name
        self._attr_unique_id = f"{self._sensor_id}_{property_name}"

    @property
    def name(self) -> str | None:
        base = super().name
        label = self._property.capitalize()
        return f"{base} {label}" if base else label

    @property
    def icon(self) -> str | None:
        return None

    @property
    def _value(self) -> Any:
        return self._properties.get(self._property)


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

    entry.async_on_unload(async_dispatcher_connect(hass, signal_sensor_new(entry.entry_id), add_sensor))


def async_setup_sensor_settings(
    hass: HomeAssistant,
    entry: CameraUiConfigEntry,
    async_add_entities: AddEntitiesCallback,
    factory: Callable[[CameraUiSensorManager, dict[str, Any]], Sequence[CameraUiSensorSetting]],
) -> None:
    manager = entry.runtime_data.sensor_manager
    created: set[str] = set()

    # a setting can show up after its sensor, when the plugin reports what the device has
    @callback
    def add_for(sensor: dict[str, Any]) -> None:
        entities = [entity for entity in factory(manager, sensor) if entity.unique_id not in created]
        for entity in entities:
            unique_id = str(entity.unique_id)
            created.add(unique_id)
            entity.async_on_remove(partial(created.discard, unique_id))
        if entities:
            async_add_entities(entities)

    for sensor in manager.sensors:
        add_for(sensor)

    entry.async_on_unload(async_dispatcher_connect(hass, signal_sensor_new(entry.entry_id), add_for))
    entry.async_on_unload(async_dispatcher_connect(hass, signal_sensor_semantics(entry.entry_id), add_for))


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

    entry.async_on_unload(async_dispatcher_connect(hass, signal_sensor_new(entry.entry_id), on_new))
    entry.async_on_unload(async_dispatcher_connect(hass, signal_sensor_assigned(entry.entry_id), on_new))
