from __future__ import annotations

from typing import Any

from homeassistant.components.humidifier import (
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.HUMIDIFIER, CameraUiHumidifier)


class CameraUiHumidifier(CameraUiSensorEntity, HumidifierEntity):
    @property
    def _humidifier(self) -> dict[str, str]:
        return self._semantics.get("humidifier") or {}

    def _read(self, key: str) -> Any:
        property_name = self._humidifier.get(key)
        return self._properties.get(property_name) if property_name else None

    def _humidifier_spec(self, key: str) -> dict[str, Any]:
        return self._spec(self._humidifier.get(key, ""))

    @property
    def _modes(self) -> list[dict[str, Any]]:
        choices: list[dict[str, Any]] = self._humidifier_spec("mode").get("choices", [])
        return choices

    @property
    def supported_features(self) -> HumidifierEntityFeature:
        if self._humidifier.get("mode"):
            return HumidifierEntityFeature.MODES
        return HumidifierEntityFeature(0)

    @property
    def device_class(self) -> HumidifierDeviceClass | None:
        device_class = self._semantics.get("deviceClass")
        return HumidifierDeviceClass(device_class) if device_class else None

    @property
    def is_on(self) -> bool:
        return bool(self._state)

    @property
    def action(self) -> HumidifierAction | None:
        action = self._read("action")
        return HumidifierAction(action) if action else None

    @property
    def current_humidity(self) -> float | None:
        return self._read("current")

    @property
    def target_humidity(self) -> float | None:
        return self._read("target")

    @property
    def target_humidity_step(self) -> float | None:
        return self._humidifier_spec("target").get("step")

    @property
    def min_humidity(self) -> float:
        return float(self._humidifier_spec("target").get("min", super().min_humidity))

    @property
    def max_humidity(self) -> float:
        return float(self._humidifier_spec("target").get("max", super().max_humidity))

    @property
    def available_modes(self) -> list[str]:
        return [choice["label"] for choice in self._modes]

    @property
    def mode(self) -> str | None:
        value = self._read("mode")
        return next((choice["label"] for choice in self._modes if choice["value"] == value), None)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], False)

    async def async_set_humidity(self, humidity: int) -> None:
        await self.async_command(self._humidifier["target"], humidity)

    async def async_set_mode(self, mode: str) -> None:
        # the set_mode service takes any string, HA does not check it against available_modes
        value = next((choice["value"] for choice in self._modes if choice["label"] == mode), None)
        if value is None:
            raise ServiceValidationError(f"Unknown mode {mode}, available: {', '.join(self.available_modes)}")
        await self.async_command(self._humidifier["mode"], value)
