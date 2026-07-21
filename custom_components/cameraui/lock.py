from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.LOCK, CameraUiLock)


class CameraUiLock(CameraUiSensorEntity, LockEntity):
    @property
    def is_locked(self) -> bool | None:
        # reads currentState but commands targetState, hence the two properties
        current = self._properties.get(self._semantics.get("stateProperty", ""))
        locked = self._semantics.get("states", {}).get("locked")
        if current is None or locked is None:
            return None
        return current == locked

    async def async_lock(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["locked"])

    async def async_unlock(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["unlocked"])
