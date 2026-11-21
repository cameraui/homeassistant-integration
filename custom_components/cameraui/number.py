from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorSetting, async_setup_sensor_settings
from .sensor_manager import CameraUiSensorManager
from .sensor_map import sensor_semantics

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_settings(hass, entry, async_add_entities, volume_entities)


def volume_entities(manager: CameraUiSensorManager, sensor: dict[str, Any]) -> list[CameraUiVolume]:
    volume = sensor_semantics(sensor).get("volume")
    # HA's siren takes a volume only together with turning on, so it is a setting of its own
    return [CameraUiVolume(manager, sensor, volume["property"])] if volume else []


class CameraUiVolume(CameraUiSensorSetting, NumberEntity):
    _attr_native_min_value = 0
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER

    @property
    def icon(self) -> str | None:
        return "mdi:volume-high"

    @property
    def available(self) -> bool:
        return super().available and "volume" in self._semantics

    @property
    def native_max_value(self) -> float:
        return float(self._semantics.get("volume", {}).get("scale", 100))

    @property
    def native_value(self) -> float | None:
        value = self._value
        return value if isinstance(value, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        await self.async_command(self._property, round(value))
