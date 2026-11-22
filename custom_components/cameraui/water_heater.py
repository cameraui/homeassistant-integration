from __future__ import annotations

from typing import Any

from homeassistant.components.water_heater import (
    ATTR_OPERATION_MODE,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import ATTR_TEMPERATURE, STATE_OFF, Platform, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.WATER_HEATER, CameraUiWaterHeater)


class CameraUiWaterHeater(CameraUiSensorEntity, WaterHeaterEntity):
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _block = "climate"

    @property
    def _target_spec(self) -> dict[str, Any]:
        return self._part_spec("target")

    @property
    def _turn_on_mode(self) -> str | None:
        # turning on needs a mode to go to, only obvious when off has a single counterpart
        modes = self.operation_list
        others = [mode for mode in modes if mode != STATE_OFF]
        return others[0] if STATE_OFF in modes and len(others) == 1 else None

    @property
    def supported_features(self) -> WaterHeaterEntityFeature:
        features = WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.OPERATION_MODE
        if self._turn_on_mode:
            features |= WaterHeaterEntityFeature.ON_OFF
        return features

    @property
    def operation_list(self) -> list[str]:
        return [str(mode) for mode in self._semantics.get("states", {}).values()]

    @property
    def current_operation(self) -> str | None:
        return self._read("mode")

    @property
    def current_temperature(self) -> float | None:
        return self._read("current")

    @property
    def target_temperature(self) -> float | None:
        return self._read("target")

    @property
    def target_temperature_step(self) -> float | None:
        return self._target_spec.get("step")

    @property
    def min_temp(self) -> float:
        return float(self._target_spec.get("min", super().min_temp))

    @property
    def max_temp(self) -> float:
        return float(self._target_spec.get("max", super().max_temp))

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_OPERATION_MODE in kwargs:
            await self.async_handle_set_operation_mode(kwargs[ATTR_OPERATION_MODE])
        await self.async_command(self._parts["target"], kwargs[ATTR_TEMPERATURE])

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        await self.async_command(self._parts["mode"], operation_mode)

    async def async_turn_on(self, **kwargs: Any) -> None:
        if mode := self._turn_on_mode:
            await self.async_set_operation_mode(mode)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_set_operation_mode(STATE_OFF)
