from __future__ import annotations

from typing import Any

from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiSensorEntity, async_setup_sensor_platform
from .sensor_manager import CameraUiSensorManager

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.EVENT, CameraUiEvent)


class CameraUiEvent(CameraUiSensorEntity, EventEntity):
    def __init__(self, manager: CameraUiSensorManager, sensor: dict[str, Any]) -> None:
        super().__init__(manager, sensor)
        self._last = self._value

    @property
    def device_class(self) -> EventDeviceClass | None:
        try:
            return EventDeviceClass(self._semantics.get("deviceClass", ""))
        except ValueError:
            return None

    @property
    def event_types(self) -> list[str]:
        return [str(value) for value in self._semantics.get("states", {}).values()]

    @property
    def _value(self) -> Any:
        return self._properties.get(self._semantics.get("stateProperty", ""))

    @callback
    def _handle_update(self) -> None:
        value = self._value
        # the property is empty between two events, so a repeat arrives as a change too
        if value and value != self._last and str(value) in self.event_types:
            state_property = self._semantics.get("stateProperty")
            details = {
                name: detail
                for name, detail in self._properties.items()
                if name != state_property and detail not in ("", None)
            }
            self._trigger_event(str(value), details)
        self._last = value
        super()._handle_update()
