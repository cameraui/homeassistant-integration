from __future__ import annotations

from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiOpenCloseEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.COVER, CameraUiCover)


class CameraUiCover(CameraUiOpenCloseEntity, CoverEntity):
    @property
    def supported_features(self) -> CoverEntityFeature:
        features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE
        if self._semantics.get("position"):
            features |= CoverEntityFeature.SET_POSITION
        if self._semantics.get("stop"):
            features |= CoverEntityFeature.STOP
        if self._semantics.get("tilt"):
            features |= CoverEntityFeature.SET_TILT_POSITION
        return features

    @property
    def device_class(self) -> CoverDeviceClass | None:
        device_class = self._semantics.get("deviceClass")
        return CoverDeviceClass(device_class) if device_class else None

    @property
    def current_cover_position(self) -> int | None:
        position = self._semantics.get("position")
        return self._properties.get(position["current"]) if position else None

    @property
    def current_cover_tilt_position(self) -> int | None:
        tilt = self._semantics.get("tilt")
        return self._properties.get(tilt["current"]) if tilt else None

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["open"])

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["closed"])

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["position"]["target"], kwargs[ATTR_POSITION])

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["tilt"]["target"], kwargs[ATTR_TILT_POSITION])

    async def async_stop_cover(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["stop"]["property"], True)
