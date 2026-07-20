from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.service import async_extract_referenced_entity_ids

from .const import DOMAIN

SERVICE_PTZ = "ptz"

ATTR_ACTION = "action"
ATTR_PAN = "pan"
ATTR_TILT = "tilt"
ATTR_ZOOM = "zoom"
ATTR_PRESET = "preset"

ACTIONS = ("continuous", "stop", "move", "absolute", "preset", "home")

PTZ_SCHEMA = vol.Schema(
    {
        **cv.ENTITY_SERVICE_FIELDS,
        vol.Required(ATTR_ACTION): vol.In(ACTIONS),
        vol.Optional(ATTR_PAN): vol.Coerce(float),
        vol.Optional(ATTR_TILT): vol.Coerce(float),
        vol.Optional(ATTR_ZOOM): vol.Coerce(float),
        vol.Optional(ATTR_PRESET): cv.string,
    }
)


def _resolve_command(data: dict[str, Any]) -> tuple[str, Any]:
    action = data[ATTR_ACTION]
    pan = data.get(ATTR_PAN, 0.0)
    tilt = data.get(ATTR_TILT, 0.0)
    zoom = data.get(ATTR_ZOOM, 0.0)

    if action == "continuous":
        return "velocity", {"panSpeed": pan, "tiltSpeed": tilt, "zoomSpeed": zoom}
    if action == "stop":
        return "velocity", {"panSpeed": 0.0, "tiltSpeed": 0.0, "zoomSpeed": 0.0}
    if action == "move":
        return "relativeMove", {"panDelta": pan, "tiltDelta": tilt, "zoomDelta": zoom}
    if action == "absolute":
        return "position", {"pan": pan, "tilt": tilt, "zoom": zoom}
    if action == "home":
        return "home", True

    preset = data.get(ATTR_PRESET)
    if not preset:
        raise ServiceValidationError("A preset name is required for the 'preset' action")
    return "targetPreset", preset


def async_setup_ptz_service(hass: HomeAssistant) -> None:
    async def handle_ptz(call: ServiceCall) -> None:
        registry = er.async_get(hass)
        referenced = async_extract_referenced_entity_ids(hass, call)
        prop, value = _resolve_command(call.data)

        commanded = 0
        for entity_id in referenced.referenced | referenced.indirectly_referenced:
            entity = registry.async_get(entity_id)
            if (
                not entity
                or entity.platform != DOMAIN
                or entity.domain != "camera"
                or not entity.config_entry_id
            ):
                continue
            entry = hass.config_entries.async_get_entry(entity.config_entry_id)
            if not entry or not (runtime_data := getattr(entry, "runtime_data", None)):
                continue

            manager = runtime_data.sensor_manager
            sensor = manager.sensor_for_camera_type(entity.unique_id, "ptz")
            if not sensor:
                continue
            await manager.async_command(sensor["globalId"], prop, value)
            commanded += 1

        if commanded == 0:
            raise ServiceValidationError("No targeted camera has a PTZ sensor")

    hass.services.async_register(DOMAIN, SERVICE_PTZ, handle_ptz, schema=PTZ_SCHEMA)
