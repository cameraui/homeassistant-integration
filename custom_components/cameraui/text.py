from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.TEXT, CameraUiText)


class CameraUiText(CameraUiSensorEntity, TextEntity):
    _attr_mode = TextMode.TEXT

    @property
    def native_max(self) -> int:
        max_length = self._spec(self._semantics.get("commandProperty", "")).get("maxLength")
        return int(max_length) if max_length else super().native_max

    @property
    def native_value(self) -> str | None:
        value = self._properties.get(self._semantics.get("stateProperty", ""))
        return value if isinstance(value, str) else None

    async def async_set_value(self, value: str) -> None:
        await self.async_command(self._semantics["commandProperty"], value)
