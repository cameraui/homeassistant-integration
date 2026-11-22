from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.FAN, CameraUiFan)


class CameraUiFan(CameraUiSensorEntity, FanEntity):
    _block = "fan"

    @property
    def supported_features(self) -> FanEntityFeature:
        features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        if self._parts.get("speed"):
            features |= FanEntityFeature.SET_SPEED
        if self._parts.get("oscillating"):
            features |= FanEntityFeature.OSCILLATE
        if self._parts.get("direction"):
            features |= FanEntityFeature.DIRECTION
        return features

    @property
    def is_on(self) -> bool:
        return bool(self._state)

    @property
    def percentage(self) -> int | None:
        return self._read("speed")

    @property
    def speed_count(self) -> int:
        step = self._part_spec("speed").get("step")
        return round(100 / step) if step else 100

    @property
    def oscillating(self) -> bool | None:
        return self._read("oscillating")

    @property
    def current_direction(self) -> str | None:
        return self._read("direction")

    async def async_turn_on(
        self, percentage: int | None = None, preset_mode: str | None = None, **kwargs: Any
    ) -> None:
        if percentage and (speed := self._parts.get("speed")):
            await self.async_command(speed, percentage)
        await self.async_command(self._semantics["commandProperty"], True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], False)

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage == 0:
            await self.async_turn_off()
        elif self.is_on:
            await self.async_command(self._parts["speed"], percentage)
        else:
            await self.async_turn_on(percentage)

    async def async_oscillate(self, oscillating: bool) -> None:
        await self.async_command(self._parts["oscillating"], oscillating)

    async def async_set_direction(self, direction: str) -> None:
        await self.async_command(self._parts["direction"], direction)
