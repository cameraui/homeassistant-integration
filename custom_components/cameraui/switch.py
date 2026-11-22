from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import (
    CameraUiSensorEntity,
    CameraUiSensorSetting,
    async_setup_sensor_platform,
    async_setup_sensor_settings,
)
from .sensor_manager import CameraUiSensorManager
from .sensor_map import sensor_semantics

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.SWITCH, CameraUiSwitch)
    async_setup_sensor_settings(hass, entry, async_add_entities, toggle_entities)


def toggle_entities(manager: CameraUiSensorManager, sensor: dict[str, Any]) -> list[CameraUiToggle]:
    return [CameraUiToggle(manager, sensor, name) for name in sensor_semantics(sensor).get("toggles", [])]


class CameraUiSwitch(CameraUiSensorEntity, SwitchEntity):
    @property
    def device_class(self) -> SwitchDeviceClass | None:
        device_class = self._semantics.get("deviceClass")
        return SwitchDeviceClass(device_class) if device_class else None

    @property
    def is_on(self) -> bool:
        return bool(self._properties.get(self._semantics.get("stateProperty", "")))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], False)


class CameraUiToggle(CameraUiSensorSetting, SwitchEntity):
    @property
    def available(self) -> bool:
        return super().available and self._property in self._semantics.get("toggles", [])

    @property
    def is_on(self) -> bool:
        return bool(self._value)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_command(self._property, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_command(self._property, False)
