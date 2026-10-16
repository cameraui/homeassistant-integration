from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er

from custom_components.cameraui.const import DOMAIN
from custom_components.cameraui.ptz import SERVICE_PTZ, async_setup_ptz_service

from .helpers import make_entry


async def test_ptz_service_commands_the_ptz_sensor_of_a_targeted_camera(hass: HomeAssistant) -> None:
    entry = make_entry()
    entry.add_to_hass(hass)
    commands: list[tuple[str, str, Any]] = []

    class Manager:
        def sensor_for_camera_type(self, camera_id: str, sensor_type: str) -> dict[str, Any] | None:
            return {"id": f"ptz_{camera_id}"} if sensor_type == "ptz" else None

        async def async_command(self, sensor_id: str, prop: str, value: Any) -> None:
            commands.append((sensor_id, prop, value))

    entry.runtime_data = SimpleNamespace(sensor_manager=Manager())
    camera = er.async_get(hass).async_get_or_create("camera", DOMAIN, "cam1", config_entry=entry)
    async_setup_ptz_service(hass)

    await hass.services.async_call(
        DOMAIN, SERVICE_PTZ, {"entity_id": camera.entity_id, "action": "home"}, blocking=True
    )
    assert commands == [("ptz_cam1", "home", True)]


async def test_ptz_service_without_a_ptz_camera_is_rejected(hass: HomeAssistant) -> None:
    async_setup_ptz_service(hass)
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN, SERVICE_PTZ, {"entity_id": "camera.nothing", "action": "stop"}, blocking=True
        )
