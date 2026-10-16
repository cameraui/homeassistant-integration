from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cameraui.binary_sensor import CameraUiMotionSensor
from custom_components.cameraui.coordinator import CameraUiCoordinator
from custom_components.cameraui.entity import async_setup_detection_entities, async_setup_sensor_platform
from custom_components.cameraui.sensor_manager import CameraUiSensorManager

from .helpers import FakeEventsClient, make_entry


def add_server(hass: HomeAssistant) -> tuple[MockConfigEntry, FakeEventsClient, CameraUiCoordinator]:
    entry = make_entry()
    entry.add_to_hass(hass)
    client = FakeEventsClient()
    coordinator = CameraUiCoordinator(hass, entry, client)  # type: ignore[arg-type]
    coordinator.data = {f"cam_{entry.entry_id}": {"name": "Cam"}}
    return entry, client, coordinator


async def test_one_server_losing_its_socket_leaves_the_other_available(hass: HomeAssistant) -> None:
    entry_a, client_a, coordinator_a = add_server(hass)
    entry_b, _, coordinator_b = add_server(hass)

    sensors = []
    for entry, coordinator in ((entry_a, coordinator_a), (entry_b, coordinator_b)):
        sensor = CameraUiMotionSensor(coordinator, f"cam_{entry.entry_id}")
        sensor.hass = hass
        sensor.entity_id = f"binary_sensor.motion_{entry.entry_id}"
        sensor.async_write_ha_state = Mock()  # type: ignore[method-assign]
        await sensor.async_added_to_hass()
        sensors.append(sensor)

    client_a.connection(False)
    await hass.async_block_till_done()

    assert not sensors[0].available
    assert sensors[1].available
    for sensor in sensors:
        for remove in sensor._on_remove or []:
            remove()
    await coordinator_a.async_shutdown()
    await coordinator_b.async_shutdown()


async def test_new_sensor_is_added_only_by_its_own_server(hass: HomeAssistant) -> None:
    added: dict[str, list[Any]] = {}
    clients: dict[str, FakeEventsClient] = {}
    for _ in range(2):
        entry, client, coordinator = add_server(hass)
        manager = CameraUiSensorManager(hass, coordinator)
        await manager.async_setup()
        entry.runtime_data = SimpleNamespace(sensor_manager=manager, coordinator=coordinator)
        added[entry.entry_id] = []
        clients[entry.entry_id] = client
        bucket = added[entry.entry_id]
        async_setup_sensor_platform(
            hass,
            entry,  # type: ignore[arg-type]
            lambda entities, bucket=bucket: bucket.extend(entities),
            Platform.BINARY_SENSOR,
            lambda manager, sensor: ("binary", sensor["id"]),
        )
        async_setup_detection_entities(
            hass,
            entry,  # type: ignore[arg-type]
            lambda entities, bucket=bucket: bucket.extend(entities),
            "object",
            lambda camera_id: [("object", camera_id)],
        )

    entry_a, entry_b = list(added)
    camera_b = f"cam_{entry_b}"
    clients[entry_b].sensors["s1"] = {
        "id": "s1",
        "exposed": True,
        "type": "object",
        "assignedCameraIds": [camera_b],
        "semantics": {"domain": "binary"},
    }
    clients[entry_b].sensor({"sensorId": "s1", "type": "added"})
    await hass.async_block_till_done()

    assert added[entry_a] == []
    assert sorted(added[entry_b]) == [("binary", "s1"), ("object", camera_b)]
