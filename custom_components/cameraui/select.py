from __future__ import annotations

from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorSetting, async_setup_sensor_settings
from .sensor_manager import CameraUiSensorManager
from .sensor_map import sensor_semantics

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_settings(hass, entry, async_add_entities, choice_entities)


def choice_entities(manager: CameraUiSensorManager, sensor: dict[str, Any]) -> list[CameraUiChoice]:
    return [CameraUiChoice(manager, sensor, name) for name in sensor_semantics(sensor).get("choices", [])]


class CameraUiChoice(CameraUiSensorSetting, SelectEntity):
    @property
    def _choices(self) -> list[dict[str, Any]]:
        specs = (self._sensor or {}).get("propertySpecs") or {}
        choices: list[dict[str, Any]] = specs.get(self._property, {}).get("choices", [])
        return choices

    @property
    def available(self) -> bool:
        return super().available and self._property in self._semantics.get("choices", [])

    @property
    def options(self) -> list[str]:
        return [choice["label"] for choice in self._choices]

    @property
    def current_option(self) -> str | None:
        value = self._value
        return next((choice["label"] for choice in self._choices if choice["value"] == value), None)

    async def async_select_option(self, option: str) -> None:
        value = next(choice["value"] for choice in self._choices if choice["label"] == option)
        await self.async_command(self._property, value)
