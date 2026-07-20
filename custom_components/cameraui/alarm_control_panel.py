from __future__ import annotations

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform

STATE_MAP: dict[str, AlarmControlPanelState] = {
    "armed_home": AlarmControlPanelState.ARMED_HOME,
    "armed_away": AlarmControlPanelState.ARMED_AWAY,
    "armed_night": AlarmControlPanelState.ARMED_NIGHT,
    "disarmed": AlarmControlPanelState.DISARMED,
    "triggered": AlarmControlPanelState.TRIGGERED,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(
        hass, entry, async_add_entities, Platform.ALARM_CONTROL_PANEL, CameraUiAlarmControlPanel
    )


class CameraUiAlarmControlPanel(CameraUiSensorEntity, AlarmControlPanelEntity):
    _attr_code_arm_required = False
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_NIGHT
    )

    @property
    def alarm_state(self) -> AlarmControlPanelState | None:
        current = self._properties.get(self._semantics.get("stateProperty", ""))
        for name, value in self._semantics.get("states", {}).items():
            if value == current:
                return STATE_MAP.get(name)
        return None

    async def _async_arm(self, name: str) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"][name])

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        await self._async_arm("disarmed")

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        await self._async_arm("armed_home")

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        await self._async_arm("armed_away")

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        await self._async_arm("armed_night")
