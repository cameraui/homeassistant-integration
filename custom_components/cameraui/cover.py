from __future__ import annotations

from typing import Any

from homeassistant.components.cover import CoverDeviceClass, CoverEntity, CoverEntityFeature
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.COVER, CameraUiCover)


class CameraUiCover(CameraUiSensorEntity, CoverEntity):
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

    @property
    def device_class(self) -> CoverDeviceClass | None:
        device_class = self._semantics.get("deviceClass")
        return CoverDeviceClass(device_class) if device_class else None

    @property
    def _state(self) -> Any:
        return self._properties.get(self._semantics.get("stateProperty", ""))

    def _is(self, name: str) -> bool:
        expected = self._semantics.get("states", {}).get(name)
        return expected is not None and self._state == expected

    @property
    def is_closed(self) -> bool | None:
        return None if self._state is None else self._is("closed")

    @property
    def is_opening(self) -> bool:
        return self._is("opening")

    @property
    def is_closing(self) -> bool:
        return self._is("closing")

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["open"])

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["closed"])
