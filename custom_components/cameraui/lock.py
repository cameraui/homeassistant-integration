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
        return None if self._state is None else self._is("locked")

    @property
    def is_jammed(self) -> bool:
        return self._is("jammed")

    async def async_lock(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["locked"])

    async def async_unlock(self, **kwargs: Any) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["unlocked"])
