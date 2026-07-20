from __future__ import annotations

import logging
from typing import Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .api import CameraUiApiError
from .const import SIGNAL_SENSOR_NEW, signal_sensor_remove, signal_sensor_update
from .coordinator import CameraUiCoordinator
from .sensor_map import sensor_platform

_LOGGER = logging.getLogger(__name__)


class CameraUiSensorManager:
    def __init__(self, hass: HomeAssistant, coordinator: CameraUiCoordinator) -> None:
        self.hass = hass
        self._coordinator = coordinator
        self._client = coordinator.client
        self._sensors: dict[str, dict[str, Any]] = {}

    async def async_setup(self) -> None:
        self._client.on_sensor(self._handle_push)
        self._client.on_connection(self._handle_connection)
        for camera in self._coordinator.data.values():
            await self._reconcile_camera(camera, emit_new=False)

    def sensors_for_platform(self, platform: Platform) -> list[dict[str, Any]]:
        return [sensor for sensor in self._sensors.values() if sensor_platform(sensor) is platform]

    def cameras_with_sensor_type(self, sensor_type: str) -> set[str]:
        return {sensor["camera_id"] for sensor in self._sensors.values() if sensor.get("type") == sensor_type}

    def sensor_for_camera_type(self, camera_id: str, sensor_type: str) -> dict[str, Any] | None:
        return next(
            (
                s
                for s in self._sensors.values()
                if s["camera_id"] == camera_id and s.get("type") == sensor_type
            ),
            None,
        )

    def get_sensor(self, global_id: str) -> dict[str, Any] | None:
        return self._sensors.get(global_id)

    async def async_command(self, global_id: str, property_name: str, value: Any) -> None:
        sensor = self._sensors.get(global_id)
        if not sensor:
            return
        await self._client.command_sensor(sensor["camera_name"], sensor["stableId"], property_name, value)

    async def _reconcile_camera(self, camera: dict[str, Any], emit_new: bool = True) -> None:
        camera_id = camera.get("_id")
        camera_name = camera.get("name")
        if not camera_id or not camera_name:
            return

        try:
            fetched = await self._client.get_sensors(camera_name)
        except CameraUiApiError as err:
            _LOGGER.debug("Sensor fetch for %s failed: %s", camera_name, err)
            return

        current: dict[str, dict[str, Any]] = {}
        for sensor in fetched:
            global_id = sensor.get("globalId")
            if not global_id:
                continue
            current[global_id] = {**sensor, "camera_id": camera_id, "camera_name": camera_name}

        for global_id, sensor in current.items():
            existed = global_id in self._sensors
            self._sensors[global_id] = sensor
            if not existed and emit_new:
                async_dispatcher_send(self.hass, SIGNAL_SENSOR_NEW, sensor)
            elif existed:
                async_dispatcher_send(self.hass, signal_sensor_update(global_id))

        stale = [
            global_id
            for global_id, sensor in self._sensors.items()
            if sensor.get("camera_id") == camera_id and global_id not in current
        ]
        for global_id in stale:
            self._sensors.pop(global_id, None)
            async_dispatcher_send(self.hass, signal_sensor_remove(global_id))

    def _handle_push(self, message: dict[str, Any]) -> None:
        global_id = message.get("globalId")
        if not global_id:
            return

        if message.get("type") == "changed":
            sensor = self._sensors.get(global_id)
            property_name = message.get("property")
            if sensor is not None and property_name is not None:
                sensor.setdefault("properties", {})[property_name] = message.get("value")
                async_dispatcher_send(self.hass, signal_sensor_update(global_id))
            return

        # added/removed carry no full sensor data, so reconcile the whole camera
        camera = self._coordinator.data.get(message.get("cameraId", ""))
        if camera:
            self.hass.async_create_task(self._reconcile_camera(camera))

    def _handle_connection(self, connected: bool) -> None:
        if not connected:
            return
        for camera in self._coordinator.data.values():
            self.hass.async_create_task(self._reconcile_camera(camera))
