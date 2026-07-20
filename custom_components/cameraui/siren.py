from __future__ import annotations

from typing import Any

from homeassistant.components.siren import SirenEntity, SirenEntityFeature
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.SIREN, CameraUiSiren)


class CameraUiSiren(CameraUiSensorEntity, SirenEntity):
    _attr_supported_features = SirenEntityFeature.TURN_ON | SirenEntityFeature.TURN_OFF

    @property
    def is_on(self) -> bool:
        return bool(self._properties.get(self._semantics.get("stateProperty", "")))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], False)
