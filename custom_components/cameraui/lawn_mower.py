from __future__ import annotations

from homeassistant.components.lawn_mower import LawnMowerActivity, LawnMowerEntity, LawnMowerEntityFeature
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiCommandEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1

COMMAND_FEATURES = {
    "start": LawnMowerEntityFeature.START_MOWING,
    "pause": LawnMowerEntityFeature.PAUSE,
    "dock": LawnMowerEntityFeature.DOCK,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.LAWN_MOWER, CameraUiLawnMower)


class CameraUiLawnMower(CameraUiCommandEntity, LawnMowerEntity):
    @property
    def supported_features(self) -> LawnMowerEntityFeature:
        return self._command_features(COMMAND_FEATURES, LawnMowerEntityFeature(0))

    @property
    def activity(self) -> LawnMowerActivity | None:
        return LawnMowerActivity(self._state) if self._state else None

    async def async_start_mowing(self) -> None:
        await self._send("start")

    async def async_pause(self) -> None:
        await self._send("pause")

    async def async_dock(self) -> None:
        await self._send("dock")
