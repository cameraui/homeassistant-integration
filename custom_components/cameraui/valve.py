from __future__ import annotations

from homeassistant.components.valve import ValveDeviceClass, ValveEntity, ValveEntityFeature
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiOpenCloseEntity, async_setup_sensor_platform

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.VALVE, CameraUiValve)


class CameraUiValve(CameraUiOpenCloseEntity, ValveEntity):
    @property
    def supported_features(self) -> ValveEntityFeature:
        features = ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE
        if self._semantics.get("position"):
            features |= ValveEntityFeature.SET_POSITION
        return features

    @property
    def device_class(self) -> ValveDeviceClass | None:
        device_class = self._semantics.get("deviceClass")
        if not device_class:
            return None
        # HA knows water and gas valves only
        return ValveDeviceClass.GAS if device_class == ValveDeviceClass.GAS else ValveDeviceClass.WATER

    @property
    def reports_position(self) -> bool:
        return bool(self._semantics.get("position"))

    @property
    def current_valve_position(self) -> int | None:
        position = self._semantics.get("position")
        return self._properties.get(position["current"]) if position else None

    async def async_open_valve(self) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["open"])

    async def async_close_valve(self) -> None:
        await self.async_command(self._semantics["commandProperty"], self._semantics["states"]["closed"])

    async def async_set_valve_position(self, position: int) -> None:
        await self.async_command(self._semantics["position"]["target"], position)
