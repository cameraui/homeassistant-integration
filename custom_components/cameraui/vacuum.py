from __future__ import annotations

from typing import Any

from homeassistant.components.vacuum import StateVacuumEntity, VacuumActivity, VacuumEntityFeature
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiCommandEntity, async_setup_sensor_platform, choice_value

PARALLEL_UPDATES = 1

COMMAND_FEATURES = {
    "start": VacuumEntityFeature.START,
    "pause": VacuumEntityFeature.PAUSE,
    "stop": VacuumEntityFeature.STOP,
    "dock": VacuumEntityFeature.RETURN_HOME,
    "locate": VacuumEntityFeature.LOCATE,
    "spot": VacuumEntityFeature.CLEAN_SPOT,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.VACUUM, CameraUiVacuum)


class CameraUiVacuum(CameraUiCommandEntity, StateVacuumEntity):
    @property
    def _fan_speed_property(self) -> str:
        return (self._semantics.get("fanSpeed") or {}).get("property", "")

    @property
    def _fan_speeds(self) -> list[dict[str, Any]]:
        choices: list[dict[str, Any]] = self._spec(self._fan_speed_property).get("choices", [])
        return choices

    @property
    def supported_features(self) -> VacuumEntityFeature:
        features = self._command_features(COMMAND_FEATURES, VacuumEntityFeature.STATE)
        if self._fan_speed_property:
            features |= VacuumEntityFeature.FAN_SPEED
        return features

    @property
    def activity(self) -> VacuumActivity | None:
        return VacuumActivity(self._state) if self._state else None

    @property
    def fan_speed_list(self) -> list[str]:
        return [choice["label"] for choice in self._fan_speeds]

    @property
    def fan_speed(self) -> str | None:
        value = self._properties.get(self._fan_speed_property)
        return next((choice["label"] for choice in self._fan_speeds if choice["value"] == value), None)

    async def async_start(self) -> None:
        await self._send("start")

    async def async_pause(self) -> None:
        await self._send("pause")

    async def async_stop(self, **kwargs: Any) -> None:
        await self._send("stop")

    async def async_return_to_base(self, **kwargs: Any) -> None:
        await self._send("dock")

    async def async_locate(self, **kwargs: Any) -> None:
        await self._send("locate")

    async def async_clean_spot(self, **kwargs: Any) -> None:
        await self._send("spot")

    async def async_set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        await self.async_command(
            self._fan_speed_property, choice_value(self._fan_speeds, fan_speed, "fan speed")
        )
