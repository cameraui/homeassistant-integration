from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .const import SIGNAL_DETECTION
from .coordinator import CameraUiCoordinator
from .entity import (
    CameraUiEntity,
    CameraUiSensorEntity,
    async_setup_detection_entities,
    async_setup_sensor_platform,
)

PARALLEL_UPDATES = 0

# camera.ui detector type -> entity key / translation_key
DETECTION_VALUE_SENSORS = [
    ("face", "face"),
    ("licensePlate", "license_plate"),
    ("classifier", "classification"),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data.coordinator
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.SENSOR, CameraUiMeasurement)

    def make_factory(kind: str) -> Callable[[str], list[CameraUiDetectionValueSensor]]:
        def factory(camera_id: str) -> list[CameraUiDetectionValueSensor]:
            return [CameraUiDetectionValueSensor(coordinator, camera_id, kind)]

        return factory

    for sensor_type, kind in DETECTION_VALUE_SENSORS:
        async_setup_detection_entities(hass, entry, async_add_entities, sensor_type, make_factory(kind))


class CameraUiMeasurement(CameraUiSensorEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_class(self) -> SensorDeviceClass | None:
        raw = self._semantics.get("deviceClass")
        if not raw:
            return None
        try:
            return SensorDeviceClass(raw)
        except ValueError:
            return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self._semantics.get("unit")

    @property
    def entity_category(self) -> EntityCategory | None:
        return EntityCategory.DIAGNOSTIC if self._semantics.get("diagnostic") else None

    @property
    def native_value(self) -> float | None:
        value = self._properties.get(self._semantics.get("stateProperty", ""))
        return value if isinstance(value, (int, float)) else None


class CameraUiDetectionValueSensor(CameraUiEntity, SensorEntity):
    def __init__(self, coordinator: CameraUiCoordinator, camera_id: str, kind: str) -> None:
        super().__init__(coordinator, camera_id)
        self._kind = kind
        self._attr_unique_id = f"{camera_id}_{kind}"
        self._attr_translation_key = kind
        self._detections: list[dict[str, Any]] = []

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{SIGNAL_DETECTION}_{self._camera_id}", self._handle_detection
            )
        )

    def _matches(self, attribute_type: str | None) -> bool:
        if self._kind == "face":
            return attribute_type == "face"
        if self._kind == "license_plate":
            return attribute_type == "license_plate"
        return attribute_type not in ("face", "license_plate")

    @callback
    def _handle_detection(self, message: dict[str, Any]) -> None:
        self._detections = [a for a in message.get("attributes", []) if self._matches(a.get("type"))]
        self.async_write_ha_state()

    @property
    def native_value(self) -> str | None:
        return ", ".join(a["label"] for a in self._detections) or None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"detections": self._detections}
