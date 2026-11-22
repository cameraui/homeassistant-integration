from __future__ import annotations

from typing import Any

from homeassistant.components.scene import Scene
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.SCENE, CameraUiScene)


class CameraUiScene(CameraUiSensorEntity, Scene):
    async def async_activate(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], True)
