from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.LIGHT, CameraUiLight)


class CameraUiLight(CameraUiSensorEntity, LightEntity):
    @property
    def _brightness(self) -> dict[str, Any] | None:
        # the server tells us whether this light dims and on what scale, and it may
        # only learn that after querying the hardware, so never cache it
        return self._semantics.get("brightness")

    @property
    def color_mode(self) -> ColorMode:
        return ColorMode.BRIGHTNESS if self._brightness else ColorMode.ONOFF

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        return {self.color_mode}

    @property
    def is_on(self) -> bool:
        return bool(self._properties.get(self._semantics.get("stateProperty", "")))

    @property
    def brightness(self) -> int | None:
        if not self._brightness:
            return None
        value = self._properties.get(self._brightness["property"])
        if value is None:
            return None
        return round(value / self._brightness["scale"] * 255)

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs and self._brightness:
            scaled = round(kwargs[ATTR_BRIGHTNESS] / 255 * self._brightness["scale"])
            await self.async_command(self._brightness["property"], scaled)
        await self.async_command(self._semantics["commandProperty"], True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], False)
