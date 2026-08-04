from __future__ import annotations

import logging
from typing import Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .api import CameraUiApiError
from .const import (
    DOMAIN,
    SIGNAL_SENSOR_ASSIGNED,
    SIGNAL_SENSOR_NEW,
    signal_sensor_remove,
    signal_sensor_update,
)
from .coordinator import CameraUiCoordinator
from .sensor_map import sensor_platform

_LOGGER = logging.getLogger(__name__)


class CameraUiSensorManager:
    def __init__(self, hass: HomeAssistant, coordinator: CameraUiCoordinator) -> None:
        self.hass = hass
        self._coordinator = coordinator
        self._client = coordinator.client
        self._sensors: dict[str, dict[str, Any]] = {}
        self._warned_old_server = False

    async def async_setup(self) -> None:
        self._client.on_sensor(self._handle_push)
        self._client.on_connection(self._handle_connection)
        await self._reconcile(emit_new=False)

    def sensors_for_platform(self, platform: Platform) -> list[dict[str, Any]]:
        return [sensor for sensor in self._sensors.values() if sensor_platform(sensor) is platform]

    def cameras_with_sensor_type(self, sensor_type: str) -> set[str]:
        return {
            camera_id
            for sensor in self._sensors.values()
            if sensor.get("type") == sensor_type
            for camera_id in sensor.get("assignedCameraIds", [])
        }

    def sensor_for_camera_type(self, camera_id: str, sensor_type: str) -> dict[str, Any] | None:
        return next(
            (
                s
                for s in self._sensors.values()
                if s.get("type") == sensor_type and camera_id in s.get("assignedCameraIds", [])
            ),
            None,
        )

    def get_sensor(self, sensor_id: str) -> dict[str, Any] | None:
        return self._sensors.get(sensor_id)

    def has_sensor(self, sensor_id: str) -> bool:
        return sensor_id in self._sensors

    async def async_command(self, sensor_id: str, property_name: str, value: Any) -> None:
        await self._client.command_sensor(sensor_id, property_name, value)

    async def _reconcile(self, emit_new: bool = True) -> None:
        try:
            fetched = await self._client.get_sensors()
        except CameraUiApiError as err:
            if err.status == 404 and not self._warned_old_server:
                self._warned_old_server = True
                _LOGGER.warning(
                    "The camera.ui server does not offer the sensors API yet; "
                    "sensor entities stay disabled until the server is updated"
                )
            else:
                _LOGGER.debug("Sensor fetch failed: %s", err)
            return

        current = {sensor["id"]: sensor for sensor in fetched if sensor.get("id") and sensor.get("exposed") and sensor.get("origin") != "homeassistant"}

        for sensor_id, sensor in current.items():
            existed = sensor_id in self._sensors
            self._sensors[sensor_id] = sensor
            if not existed and emit_new:
                async_dispatcher_send(self.hass, SIGNAL_SENSOR_NEW, sensor)
            elif existed:
                async_dispatcher_send(self.hass, signal_sensor_update(sensor_id))

        for sensor_id in [sensor_id for sensor_id in self._sensors if sensor_id not in current]:
            self._sensors.pop(sensor_id, None)
            self._remove_sensor(sensor_id)

    def _remove_sensor(self, sensor_id: str) -> None:
        async_dispatcher_send(self.hass, signal_sensor_remove(sensor_id))
        registry = dr.async_get(self.hass)
        device = registry.async_get_device(identifiers={(DOMAIN, f"sensor_{sensor_id}")})
        if device:
            registry.async_update_device(
                device.id,
                remove_config_entry_id=self._coordinator.config_entry.entry_id,
            )

    async def _add_sensor(self, sensor_id: str) -> None:
        sensor = await self._client.get_sensor(sensor_id)
        if not sensor or not sensor.get("exposed") or sensor.get("origin") == "homeassistant":
            return
        existed = sensor_id in self._sensors
        self._sensors[sensor_id] = sensor
        if existed:
            async_dispatcher_send(self.hass, signal_sensor_update(sensor_id))
        else:
            async_dispatcher_send(self.hass, SIGNAL_SENSOR_NEW, sensor)

    def _handle_push(self, message: dict[str, Any]) -> None:
        sensor_id = message.get("sensorId")
        if not sensor_id:
            return

        message_type = message.get("type")

        if message_type == "added":
            self.hass.async_create_task(self._add_sensor(sensor_id))
            return

        if message_type == "removed":
            if self._sensors.pop(sensor_id, None) is not None:
                self._remove_sensor(sensor_id)
            return

        sensor = self._sensors.get(sensor_id)
        if sensor is None:
            return

        if message_type == "changed":
            property_name = message.get("property")
            if property_name is None:
                return
            sensor.setdefault("properties", {})[property_name] = message.get("value")
        elif message_type == "meta":
            previous_assigned = set(sensor.get("assignedCameraIds", []))
            for key in (
                "displayName",
                "connected",
                "capabilities",
                "assignedCameraIds",
            ):
                if key in message:
                    sensor[key] = message[key]
            if set(sensor.get("assignedCameraIds", [])) - previous_assigned:
                async_dispatcher_send(self.hass, SIGNAL_SENSOR_ASSIGNED, sensor)
        else:
            return

        async_dispatcher_send(self.hass, signal_sensor_update(sensor_id))

    def _handle_connection(self, connected: bool) -> None:
        if not connected:
            return
        self.hass.async_create_task(self._reconcile())
