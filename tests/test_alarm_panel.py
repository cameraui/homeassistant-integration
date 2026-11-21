from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from homeassistant.components.alarm_control_panel import AlarmControlPanelEntityFeature
from homeassistant.const import ATTR_SUPPORTED_FEATURES, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockEntityPlatform

from custom_components.cameraui.alarm_control_panel import CameraUiAlarmControlPanel
from custom_components.cameraui.const import DOMAIN
from custom_components.cameraui.coordinator import CameraUiCoordinator
from custom_components.cameraui.sensor_manager import CameraUiSensorManager

from .helpers import FakeEventsClient, make_entry

STATES = {"armed_home": 0, "armed_away": 1, "armed_night": 2, "disarmed": 3, "triggered": 4}


def alarm(**changes: Any) -> dict[str, Any]:
    return {
        "id": "s-alarm",
        "type": "securitySystem",
        "name": "Alarm",
        "displayName": "Alarm",
        "shortName": "Alarm",
        "primary": False,
        "exposed": True,
        "connected": True,
        "assignedCameraIds": [],
        "properties": {"currentState": 3, "targetState": 3},
        "semantics": {
            "domain": "alarm",
            "stateProperty": "currentState",
            "commandProperty": "targetState",
            "states": STATES,
        },
        **changes,
    }


async def setup(hass: HomeAssistant, sensor: dict[str, Any]) -> tuple[FakeEventsClient, str]:
    entry = make_entry()
    entry.add_to_hass(hass)
    client = FakeEventsClient()
    client.sensors = {sensor["id"]: sensor}
    coordinator = CameraUiCoordinator(hass, entry, client)  # type: ignore[arg-type]
    coordinator.data = {}
    manager = CameraUiSensorManager(hass, coordinator)
    await manager.async_setup()
    entry.runtime_data = SimpleNamespace(coordinator=coordinator, sensor_manager=manager)

    platform = MockEntityPlatform(hass, domain="alarm_control_panel", platform_name=DOMAIN)
    platform.config_entry = entry
    await platform.async_add_entities(
        [
            CameraUiAlarmControlPanel(manager, item)
            for item in manager.sensors_for_platform(Platform.ALARM_CONTROL_PANEL)
        ]
    )
    await hass.async_block_till_done()
    entity_id = er.async_get(hass).async_get_entity_id("alarm_control_panel", DOMAIN, sensor["id"])
    assert entity_id
    return client, entity_id


def features(hass: HomeAssistant, entity_id: str) -> AlarmControlPanelEntityFeature:
    state = hass.states.get(entity_id)
    assert state
    return AlarmControlPanelEntityFeature(state.attributes[ATTR_SUPPORTED_FEATURES])


async def test_an_alarm_without_specs_offers_every_mode(hass: HomeAssistant) -> None:
    _, entity_id = await setup(hass, alarm())

    assert features(hass, entity_id) == (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.ARM_NIGHT
    )


async def test_an_alarm_offers_only_the_modes_of_its_system(hass: HomeAssistant) -> None:
    no_night = {
        "targetState": {
            "type": "enum",
            "values": {"stay_arm": 0, "away_arm": 1, "disarmed": 3},
            "writable": True,
        }
    }
    client, entity_id = await setup(hass, alarm(propertySpecs=no_night))

    assert (
        features(hass, entity_id)
        == AlarmControlPanelEntityFeature.ARM_HOME | AlarmControlPanelEntityFeature.ARM_AWAY
    )

    away_only = {"targetState": {"type": "enum", "values": {"away_arm": 1, "disarmed": 3}, "writable": True}}
    client.sensor({"type": "meta", "sensorId": "s-alarm", "propertySpecs": away_only})
    await hass.async_block_till_done()
    assert features(hass, entity_id) == AlarmControlPanelEntityFeature.ARM_AWAY

    client.sensor({"type": "meta", "sensorId": "s-alarm", "propertySpecs": {}})
    await hass.async_block_till_done()
    assert AlarmControlPanelEntityFeature.ARM_NIGHT in features(hass, entity_id)
