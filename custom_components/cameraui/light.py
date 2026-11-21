from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    DEFAULT_MAX_KELVIN,
    DEFAULT_MIN_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1

# the light's colorMode while it shows a color instead of a white
COLOR_MODE_COLOR = "color"


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
    def _color(self) -> dict[str, str]:
        return self._semantics.get("color") or {}

    @property
    def color_mode(self) -> ColorMode:
        temperature, hue_saturation = self._color.get("temperature"), self._color.get("hueSaturation")
        if temperature and hue_saturation:
            mode = self._properties.get(self._color.get("mode", ""))
            return ColorMode.HS if mode == COLOR_MODE_COLOR else ColorMode.COLOR_TEMP
        if temperature:
            return ColorMode.COLOR_TEMP
        if hue_saturation:
            return ColorMode.HS
        return ColorMode.BRIGHTNESS if self._brightness else ColorMode.ONOFF

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        modes = set()
        if self._color.get("temperature"):
            modes.add(ColorMode.COLOR_TEMP)
        if self._color.get("hueSaturation"):
            modes.add(ColorMode.HS)
        return modes or {self.color_mode}

    @property
    def color_temp_kelvin(self) -> int | None:
        temperature = self._color.get("temperature")
        return self._properties.get(temperature) if temperature else None

    @property
    def min_color_temp_kelvin(self) -> int:
        return int(self._temperature_spec.get("min", DEFAULT_MIN_KELVIN))

    @property
    def max_color_temp_kelvin(self) -> int:
        return int(self._temperature_spec.get("max", DEFAULT_MAX_KELVIN))

    @property
    def hs_color(self) -> tuple[float, float] | None:
        hue_saturation = self._color.get("hueSaturation")
        color = self._properties.get(hue_saturation) if hue_saturation else None
        return (color["hue"], color["saturation"]) if color else None

    @property
    def _temperature_spec(self) -> dict[str, Any]:
        specs = (self._sensor or {}).get("propertySpecs") or {}
        return specs.get(self._color.get("temperature", "")) or {}

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
        if ATTR_COLOR_TEMP_KELVIN in kwargs and (temperature := self._color.get("temperature")):
            await self.async_command(temperature, kwargs[ATTR_COLOR_TEMP_KELVIN])
        if ATTR_HS_COLOR in kwargs and (hue_saturation := self._color.get("hueSaturation")):
            hue, saturation = kwargs[ATTR_HS_COLOR]
            await self.async_command(hue_saturation, {"hue": hue, "saturation": saturation})
        await self.async_command(self._semantics["commandProperty"], True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], False)
