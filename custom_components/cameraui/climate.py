from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, Platform, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1

# the modes Home Assistant's own turn on falls back to
TURN_ON_MODES = (HVACMode.HEAT_COOL, HVACMode.HEAT, HVACMode.COOL)


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.CLIMATE, CameraUiClimate)


class CameraUiClimate(CameraUiSensorEntity, ClimateEntity):
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def _climate(self) -> dict[str, str]:
        return self._semantics.get("climate") or {}

    @property
    def _target_spec(self) -> dict[str, Any]:
        specs = (self._sensor or {}).get("propertySpecs") or {}
        return specs.get(self._climate.get("target", "")) or {}

    def _read(self, key: str) -> Any:
        property_name = self._climate.get(key)
        return self._properties.get(property_name) if property_name else None

    @property
    def supported_features(self) -> ClimateEntityFeature:
        features = ClimateEntityFeature.TARGET_TEMPERATURE
        if self._climate.get("targetLow") and self._climate.get("targetHigh"):
            features |= ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        modes = self.hvac_modes
        if HVACMode.OFF in modes:
            features |= ClimateEntityFeature.TURN_OFF
        if (len(modes) == 2 and HVACMode.OFF in modes) or any(mode in modes for mode in TURN_ON_MODES):
            features |= ClimateEntityFeature.TURN_ON
        return features

    @property
    def hvac_modes(self) -> list[HVACMode]:
        return [HVACMode(mode) for mode in self._semantics.get("states", {}).values()]

    @property
    def hvac_mode(self) -> HVACMode | None:
        mode = self._read("mode")
        return HVACMode(mode) if mode else None

    @property
    def hvac_action(self) -> HVACAction | None:
        action = self._read("action")
        return HVACAction(action) if action else None

    @property
    def current_temperature(self) -> float | None:
        return self._read("current")

    @property
    def target_temperature(self) -> float | None:
        return self._read("target")

    @property
    def target_temperature_low(self) -> float | None:
        return self._read("targetLow")

    @property
    def target_temperature_high(self) -> float | None:
        return self._read("targetHigh")

    @property
    def target_temperature_step(self) -> float | None:
        return self._target_spec.get("step")

    @property
    def min_temp(self) -> float:
        return float(self._target_spec.get("min", super().min_temp))

    @property
    def max_temp(self) -> float:
        return float(self._target_spec.get("max", super().max_temp))

    @property
    def current_humidity(self) -> float | None:
        return self._read("humidity")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self.async_command(self._climate["mode"], str(hvac_mode))

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_HVAC_MODE in kwargs:
            await self.async_set_hvac_mode(kwargs[ATTR_HVAC_MODE])
        if ATTR_TEMPERATURE in kwargs:
            await self.async_command(self._climate["target"], kwargs[ATTR_TEMPERATURE])
        for attribute, key in ((ATTR_TARGET_TEMP_LOW, "targetLow"), (ATTR_TARGET_TEMP_HIGH, "targetHigh")):
            if attribute in kwargs and (property_name := self._climate.get(key)):
                await self.async_command(property_name, kwargs[attribute])
