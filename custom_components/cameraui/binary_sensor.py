from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .const import OBJECT_DETECTION_LABELS, SIGNAL_DETECTION
from .coordinator import CameraUiCoordinator
from .entity import (
    CameraUiEntity,
    CameraUiSensorEntity,
    async_setup_detection_entities,
    async_setup_sensor_platform,
)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data.coordinator

    # motion is universal; object-label sensors appear per camera that has object detection
    async_add_entities(CameraUiMotionSensor(coordinator, camera_id) for camera_id in coordinator.data)
    async_setup_detection_entities(
        hass,
        entry,
        async_add_entities,
        "object",
        lambda camera_id: [
            CameraUiObjectSensor(coordinator, camera_id, label) for label in OBJECT_DETECTION_LABELS
        ],
    )
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.BINARY_SENSOR, CameraUiBinarySensor)


class CameraUiMotionSensor(CameraUiEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_translation_key = "motion"

    def __init__(self, coordinator: CameraUiCoordinator, camera_id: str) -> None:
        super().__init__(coordinator, camera_id)
        self._attr_unique_id = f"{camera_id}_motion"
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{SIGNAL_DETECTION}_{self._camera_id}", self._handle_detection
            )
        )

    @callback
    def _handle_detection(self, message: dict[str, Any]) -> None:
        event = message.get("event", {})
        self._attr_is_on = event.get("state") == "active"
        self._attr_extra_state_attributes = {
            "event_id": event.get("id"),
            "detection_types": event.get("types", []),
        }
        self.async_write_ha_state()


class CameraUiObjectSensor(CameraUiEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(self, coordinator: CameraUiCoordinator, camera_id: str, label: str) -> None:
        super().__init__(coordinator, camera_id)
        self._label = label
        self._attr_unique_id = f"{camera_id}_object_{label}"
        self._attr_translation_key = f"object_{label}"
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{SIGNAL_DETECTION}_{self._camera_id}", self._handle_detection
            )
        )

    @callback
    def _handle_detection(self, message: dict[str, Any]) -> None:
        self._attr_is_on = self._label in message.get("labels", [])
        self.async_write_ha_state()


class CameraUiBinarySensor(CameraUiSensorEntity, BinarySensorEntity):
    @property
    def device_class(self) -> BinarySensorDeviceClass | None:
        device_class = self._semantics.get("deviceClass")
        return BinarySensorDeviceClass(device_class) if device_class else None

    @property
    def icon(self) -> str | None:
        return self._semantics.get("icon")

    @property
    def is_on(self) -> bool:
        return bool(self._properties.get(self._semantics.get("stateProperty", "")))
