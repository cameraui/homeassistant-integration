from __future__ import annotations

from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import Entity
from pytest_homeassistant_custom_component.common import MockEntityPlatform

from custom_components.cameraui import (
    climate,
    cover,
    event,
    fan,
    humidifier,
    light,
    lock,
    number,
    scene,
    select,
    sensor,
    siren,
    switch,
    text,
    valve,
)
from custom_components.cameraui.const import DOMAIN
from custom_components.cameraui.coordinator import CameraUiCoordinator
from custom_components.cameraui.sensor_manager import CameraUiSensorManager
from custom_components.cameraui.sensor_map import DOMAIN_PLATFORM

from .helpers import FakeEventsClient, make_entry

PLATFORMS: dict[str, ModuleType] = {
    "sensor": sensor,
    "event": event,
    "text": text,
    "number": number,
    "select": select,
    "siren": siren,
    "light": light,
    "switch": switch,
    "lock": lock,
    "cover": cover,
    "climate": climate,
    "fan": fan,
    "valve": valve,
    "scene": scene,
    "humidifier": humidifier,
}

# every SensorDomain of the SDK
SENSOR_DOMAINS = [
    "binary",
    "measurement",
    "switch",
    "light",
    "siren",
    "lock",
    "cover",
    "climate",
    "fan",
    "valve",
    "scene",
    "humidifier",
    "alarm",
    "event",
    "text",
]

TONES = {
    "type": "string",
    "writable": True,
    "choices": [{"value": "r-1", "label": "Ding Dong"}, {"value": "r-2", "label": "Chirp"}],
}


def stored(sensor_id: str, sensor_type: str, semantics: dict[str, Any], **changes: Any) -> dict[str, Any]:
    return {
        "id": sensor_id,
        "type": sensor_type,
        "name": "Front",
        "displayName": "Front",
        "shortName": "Front",
        "primary": False,
        "pluginName": "UniFi Protect",
        "exposed": True,
        "connected": True,
        "assignedCameraIds": [],
        "properties": {},
        "capabilities": [],
        "propertySpecs": {},
        "semantics": semantics,
        **changes,
    }


class Setup:
    def __init__(self, hass: HomeAssistant, client: FakeEventsClient) -> None:
        self.hass = hass
        self.client = client
        self.entities: dict[tuple[str, str], Any] = {}

    def entity_id(self, domain: str, unique_id: str) -> str:
        entity_id = er.async_get(self.hass).async_get_entity_id(domain, DOMAIN, unique_id)
        assert entity_id, f"no {domain} entity {unique_id}"
        return entity_id

    def state(self, domain: str, unique_id: str) -> Any:
        state = self.hass.states.get(self.entity_id(domain, unique_id))
        assert state
        return state

    def has(self, domain: str, unique_id: str) -> bool:
        return er.async_get(self.hass).async_get_entity_id(domain, DOMAIN, unique_id) is not None

    async def push(self, message: dict[str, Any]) -> None:
        self.client.sensor(message)
        await self.hass.async_block_till_done()

    async def changed(self, sensor_id: str, property_name: str, value: Any) -> None:
        await self.push({"type": "changed", "sensorId": sensor_id, "property": property_name, "value": value})

    def entity(self, domain: str, unique_id: str) -> Any:
        return self.entities[(domain, unique_id)]


async def setup(hass: HomeAssistant, *sensors: dict[str, Any]) -> Setup:
    entry = make_entry()
    entry.add_to_hass(hass)
    client = FakeEventsClient()
    client.sensors = {item["id"]: item for item in sensors}
    coordinator = CameraUiCoordinator(hass, entry, client)  # type: ignore[arg-type]
    coordinator.data = {}
    manager = CameraUiSensorManager(hass, coordinator)
    await manager.async_setup()
    entry.runtime_data = SimpleNamespace(coordinator=coordinator, sensor_manager=manager)
    ha = Setup(hass, client)

    for domain, module in PLATFORMS.items():
        platform = MockEntityPlatform(hass, domain=domain, platform_name=DOMAIN)
        platform.config_entry = entry
        # real HA loads these with the platform, a reading takes its name from them
        await platform.platform_data.async_load_translations()

        def add(
            entities: list[Entity], platform: MockEntityPlatform = platform, domain: str = domain
        ) -> None:
            ha.entities.update({(domain, str(entity.unique_id)): entity for entity in entities})
            hass.async_create_task(platform.async_add_entities(entities))

        await module.async_setup_entry(hass, entry, add)
    await hass.async_block_till_done()
    return ha


BUTTON = {
    "domain": "event",
    "stateProperty": "press",
    "commandProperty": "press",
    "deviceClass": "button",
    "states": {"single": "single", "long": "long"},
}

ACCESS = {
    "domain": "event",
    "stateProperty": "result",
    "commandProperty": "result",
    "states": {"granted": "granted", "denied": "denied"},
}


async def test_a_button_fires_each_press_with_its_index(hass: HomeAssistant) -> None:
    ha = await setup(hass, stored("b-1", "button", BUTTON, properties={"press": "", "index": 2}))

    state = ha.state("event", "b-1")
    assert state.attributes["event_types"] == ["single", "long"]
    assert state.attributes["device_class"] == "button"

    await ha.changed("b-1", "press", "single")
    first = ha.state("event", "b-1")
    assert first.attributes["event_type"] == "single"
    assert first.attributes["index"] == 2

    await ha.changed("b-1", "press", "")
    await ha.push({"type": "meta", "sensorId": "b-1", "displayName": "Keyfob"})
    assert ha.state("event", "b-1").state == first.state

    await ha.changed("b-1", "press", "single")
    assert ha.state("event", "b-1").state != first.state


async def test_an_access_reader_fires_its_result_with_method_and_user(hass: HomeAssistant) -> None:
    ha = await setup(
        hass, stored("a-1", "access", ACCESS, properties={"result": "", "method": "", "user": ""})
    )

    await ha.changed("a-1", "method", "nfc")
    await ha.changed("a-1", "user", "Anna")
    await ha.changed("a-1", "result", "granted")

    state = ha.state("event", "a-1")
    assert state.attributes["event_type"] == "granted"
    assert state.attributes["method"] == "nfc"
    assert state.attributes["user"] == "Anna"


async def test_air_quality_shows_its_level_and_each_reading_it_has(hass: HomeAssistant) -> None:
    levels = {
        "excellent": "excellent",
        "good": "good",
        "fair": "fair",
        "inferior": "inferior",
        "poor": "poor",
    }
    semantics = {
        "domain": "measurement",
        "stateProperty": "level",
        "commandProperty": "level",
        "deviceClass": "enum",
        "states": levels,
        "readings": [{"property": "pm25", "deviceClass": "pm25", "unit": "μg/m³"}],
    }
    ha = await setup(hass, stored("q-1", "airQuality", semantics, properties={"level": "good", "pm25": 12.5}))

    level = ha.state("sensor", "q-1")
    assert level.state == "good"
    assert level.attributes["options"] == list(levels)
    assert "state_class" not in level.attributes

    pm25 = ha.state("sensor", "q-1_pm25")
    assert pm25.state == "12.5"
    assert pm25.attributes["unit_of_measurement"] == "μg/m³"
    assert pm25.attributes["friendly_name"] == "Front PM2.5"
    assert not ha.has("sensor", "q-1_voc")

    voc = {"property": "voc", "deviceClass": "volatile_organic_compounds", "unit": "μg/m³"}
    await ha.push(
        {
            "type": "meta",
            "sensorId": "q-1",
            "capabilities": ["pm25", "voc"],
            "semantics": {**semantics, "readings": [*semantics["readings"], voc]},
        }
    )
    await ha.changed("q-1", "voc", 80)
    assert ha.state("sensor", "q-1_voc").state == "80"


async def test_a_chime_rings_and_sets_its_volume_and_tone(hass: HomeAssistant) -> None:
    semantics = {
        "domain": "siren",
        "stateProperty": "active",
        "commandProperty": "active",
        "icon": "mdi:bell-ring",
        "tone": {"property": "tone"},
        "volume": {"property": "volume", "scale": 100},
        "choices": ["tone"],
    }
    chime = stored(
        "c-1",
        "chime",
        semantics,
        properties={"active": False, "tone": "r-1", "volume": 60},
        capabilities=["volume"],
        propertySpecs={"tone": TONES},
    )
    ha = await setup(hass, chime)

    assert ha.state("siren", "c-1").attributes["icon"] == "mdi:bell-ring"
    assert ha.state("number", "c-1_volume").state == "60"
    tone = ha.state("select", "c-1_tone")
    assert tone.state == "Ding Dong"
    assert tone.attributes["options"] == ["Ding Dong", "Chirp"]
    assert tone.attributes["friendly_name"] == "Front Tone"

    await ha.entity("siren", "c-1").async_turn_on()
    await ha.entity("number", "c-1_volume").async_set_native_value(40)
    await ha.entity("select", "c-1_tone").async_select_option("Chirp")
    assert ha.client.commands == [("c-1", "active", True), ("c-1", "volume", 40), ("c-1", "tone", "r-2")]


async def test_a_light_offers_the_colors_it_has_and_shows_its_mode(hass: HomeAssistant) -> None:
    semantics = {
        "domain": "light",
        "stateProperty": "on",
        "commandProperty": "on",
        "color": {"temperature": "colorTemperature", "hueSaturation": "color", "mode": "colorMode"},
    }
    bulb = stored(
        "l-1",
        "light",
        semantics,
        properties={
            "on": True,
            "colorTemperature": 3000,
            "color": {"hue": 120, "saturation": 80},
            "colorMode": "temperature",
        },
        capabilities=["colorTemperature", "color"],
        propertySpecs={
            "colorTemperature": {"type": "number", "min": 2200, "max": 6500, "unit": "K", "writable": True}
        },
    )
    white = stored(
        "l-2",
        "light",
        {**semantics, "color": {"temperature": "colorTemperature"}},
        properties={"on": False, "colorTemperature": 2700},
    )
    ha = await setup(hass, bulb, white)

    state = ha.state("light", "l-1")
    assert set(state.attributes["supported_color_modes"]) == {"color_temp", "hs"}
    assert state.attributes["color_mode"] == "color_temp"
    assert state.attributes["color_temp_kelvin"] == 3000
    assert state.attributes["min_color_temp_kelvin"] == 2200
    assert state.attributes["max_color_temp_kelvin"] == 6500
    assert ha.state("light", "l-2").attributes["supported_color_modes"] == ["color_temp"]

    await ha.changed("l-1", "colorMode", "color")
    assert ha.state("light", "l-1").attributes["color_mode"] == "hs"
    assert ha.state("light", "l-1").attributes["hs_color"] == (120, 80)

    await ha.entity("light", "l-1").async_turn_on(color_temp_kelvin=4000)
    await ha.entity("light", "l-1").async_turn_on(hs_color=(30, 50))
    assert ha.client.commands == [
        ("l-1", "colorTemperature", 4000),
        ("l-1", "on", True),
        ("l-1", "color", {"hue": 30, "saturation": 50}),
        ("l-1", "on", True),
    ]


async def test_an_outlet_is_an_outlet_switch(hass: HomeAssistant) -> None:
    semantics = {"domain": "switch", "stateProperty": "on", "commandProperty": "on", "deviceClass": "outlet"}
    ha = await setup(hass, stored("o-1", "outlet", semantics, properties={"on": True}))

    state = ha.state("switch", "o-1")
    assert state.state == "on"
    assert state.attributes["device_class"] == "outlet"


async def test_a_display_takes_text_and_offers_presets_once_it_has_them(hass: HomeAssistant) -> None:
    semantics = {"domain": "text", "stateProperty": "message", "commandProperty": "message"}
    specs = {
        "message": {"type": "string", "writable": True, "maxLength": 30},
        "preset": {"type": "string", "writable": True, "choices": [{"value": "AWAY", "label": "Away"}]},
    }
    ha = await setup(
        hass, stored("d-1", "display", semantics, properties={"message": "Hi"}, propertySpecs=specs)
    )

    message = ha.state("text", "d-1")
    assert message.state == "Hi"
    assert message.attributes["max"] == 30
    assert not ha.has("select", "d-1_preset")

    await ha.entity("text", "d-1").async_set_value("Back soon")
    assert ha.client.commands == [("d-1", "message", "Back soon")]

    await ha.push(
        {
            "type": "meta",
            "sensorId": "d-1",
            "capabilities": ["presets"],
            "semantics": {**semantics, "choices": ["preset"]},
        }
    )
    assert ha.state("select", "d-1_preset").attributes["options"] == ["Away"]


def test_every_sensor_domain_has_a_platform() -> None:
    assert sorted(DOMAIN_PLATFORM) == sorted(SENSOR_DOMAINS)


COVER = {
    "domain": "cover",
    "stateProperty": "currentState",
    "commandProperty": "targetState",
    "deviceClass": "blind",
    "states": {"open": 0, "closed": 1, "opening": 2, "closing": 3, "stopped": 4},
}


async def test_a_cover_moves_to_a_position_tilts_and_stops_when_it_can(hass: HomeAssistant) -> None:
    blind = stored(
        "c-1",
        "cover",
        {
            **COVER,
            "position": {"current": "currentPosition", "target": "targetPosition"},
            "tilt": {"current": "currentTilt", "target": "targetTilt"},
            "stop": {"property": "stop"},
        },
        properties={"currentState": 0, "currentPosition": 40, "currentTilt": 50},
    )
    door = stored("c-2", "cover", {**COVER, "deviceClass": "door"}, properties={"currentState": 1})
    ha = await setup(hass, blind, door)

    state = ha.state("cover", "c-1")
    assert state.state == "open"
    assert state.attributes["device_class"] == "blind"
    assert state.attributes["current_position"] == 40
    assert state.attributes["current_tilt_position"] == 50
    # open, close, set position, stop and set tilt position
    assert state.attributes["supported_features"] == 1 | 2 | 4 | 8 | 128

    door_state = ha.state("cover", "c-2")
    assert door_state.state == "closed"
    assert door_state.attributes["supported_features"] == 1 | 2
    assert "current_position" not in door_state.attributes

    await ha.changed("c-1", "currentState", 3)
    assert ha.state("cover", "c-1").state == "closing"

    entity = ha.entity("cover", "c-1")
    await entity.async_set_cover_position(position=70)
    await entity.async_set_cover_tilt_position(tilt_position=20)
    await entity.async_stop_cover()
    await ha.entity("cover", "c-2").async_open_cover()
    assert ha.client.commands == [
        ("c-1", "targetPosition", 70),
        ("c-1", "targetTilt", 20),
        ("c-1", "stop", True),
        ("c-2", "targetState", 0),
    ]


CLIMATE = {
    "domain": "climate",
    "stateProperty": "mode",
    "commandProperty": "mode",
    "states": {"off": "off", "heat": "heat", "cool": "cool", "heat_cool": "heat_cool"},
    "climate": {"current": "currentTemperature", "target": "targetTemperature", "mode": "mode"},
}


async def test_a_thermostat_shows_its_modes_range_and_readings(hass: HomeAssistant) -> None:
    full = stored(
        "t-1",
        "thermostat",
        {
            **CLIMATE,
            "climate": {
                **CLIMATE["climate"],
                "targetLow": "targetTemperatureLow",
                "targetHigh": "targetTemperatureHigh",
                "action": "action",
                "humidity": "currentHumidity",
            },
            "choices": ["preset"],
        },
        properties={
            "mode": "heat",
            "action": "heating",
            "currentTemperature": 19.5,
            "targetTemperature": 21,
            "targetTemperatureLow": 18,
            "targetTemperatureHigh": 24,
            "currentHumidity": 45,
            "preset": "eco",
        },
        propertySpecs={
            "targetTemperature": {
                "type": "number",
                "min": 10,
                "max": 30,
                "step": 0.5,
                "unit": "°C",
                "writable": True,
            },
            "preset": {
                "type": "string",
                "writable": True,
                "choices": [{"value": "eco", "label": "eco"}, {"value": "comfort", "label": "comfort"}],
            },
        },
    )
    simple = stored(
        "t-2",
        "thermostat",
        {**CLIMATE, "states": {"heat": "heat"}},
        properties={"mode": "heat", "currentTemperature": 20, "targetTemperature": 20},
    )
    ha = await setup(hass, full, simple)

    state = ha.state("climate", "t-1")
    assert state.state == "heat"
    assert state.attributes["hvac_modes"] == ["off", "heat", "cool", "heat_cool"]
    assert state.attributes["hvac_action"] == "heating"
    assert state.attributes["current_temperature"] == 19.5
    assert state.attributes["temperature"] == 21
    assert state.attributes["min_temp"] == 10
    assert state.attributes["max_temp"] == 30
    assert state.attributes["target_temp_step"] == 0.5
    assert state.attributes["current_humidity"] == 45
    # target temperature, range, turn off and turn on
    assert state.attributes["supported_features"] == 1 | 2 | 128 | 256
    assert ha.state("select", "t-1_preset").state == "eco"

    simple_state = ha.state("climate", "t-2")
    assert simple_state.attributes["supported_features"] == 1 | 256
    assert simple_state.attributes["min_temp"] == 7
    assert "hvac_action" not in simple_state.attributes

    await ha.changed("t-1", "mode", "heat_cool")
    state = ha.state("climate", "t-1")
    assert state.state == "heat_cool"
    assert state.attributes["target_temp_low"] == 18
    assert state.attributes["target_temp_high"] == 24

    entity = ha.entity("climate", "t-1")
    await entity.async_set_temperature(target_temp_low=17, target_temp_high=25)
    await entity.async_set_temperature(temperature=22, hvac_mode="heat")
    await entity.async_turn_off()
    assert ha.client.commands == [
        ("t-1", "targetTemperatureLow", 17),
        ("t-1", "targetTemperatureHigh", 25),
        ("t-1", "mode", "heat"),
        ("t-1", "targetTemperature", 22),
        ("t-1", "mode", "off"),
    ]


async def test_a_thermostat_sets_its_target_humidity(hass: HomeAssistant) -> None:
    humidifier = stored(
        "t-1",
        "thermostat",
        {**CLIMATE, "climate": {**CLIMATE["climate"], "targetHumidity": "targetHumidity"}},
        properties={"mode": "heat", "currentTemperature": 20, "targetTemperature": 21, "targetHumidity": 45},
        capabilities=["targetHumidity"],
        propertySpecs={
            "targetHumidity": {"type": "number", "min": 30, "max": 80, "unit": "%", "writable": True}
        },
    )
    ha = await setup(hass, humidifier)

    state = ha.state("climate", "t-1")
    assert state.attributes["humidity"] == 45
    assert state.attributes["min_humidity"] == 30
    assert state.attributes["max_humidity"] == 80
    # target temperature, target humidity, turn off and turn on
    assert state.attributes["supported_features"] == 1 | 4 | 128 | 256

    await ha.entity("climate", "t-1").async_set_humidity(50)
    assert ha.client.commands == [("t-1", "targetHumidity", 50)]


LOCK = {
    "domain": "lock",
    "stateProperty": "currentState",
    "commandProperty": "targetState",
    "states": {"locked": 0, "unlocked": 1, "jammed": 3},
}


async def test_a_lock_shows_when_it_is_jammed(hass: HomeAssistant) -> None:
    ha = await setup(hass, stored("k-1", "lock", LOCK, properties={"currentState": 0}))
    assert ha.state("lock", "k-1").state == "locked"

    await ha.changed("k-1", "currentState", 3)
    assert ha.state("lock", "k-1").state == "jammed"

    await ha.changed("k-1", "currentState", 1)
    assert ha.state("lock", "k-1").state == "unlocked"

    await ha.entity("lock", "k-1").async_lock()
    assert ha.client.commands == [("k-1", "targetState", 0)]


FAN = {"domain": "fan", "stateProperty": "on", "commandProperty": "on"}


async def test_a_fan_offers_speed_direction_and_swing_when_it_has_them(hass: HomeAssistant) -> None:
    ceiling = stored(
        "f-1",
        "fan",
        {
            **FAN,
            "fan": {"speed": "speed", "direction": "direction", "oscillating": "oscillating"},
            "choices": ["preset"],
        },
        properties={
            "on": True,
            "speed": 50,
            "direction": "forward",
            "oscillating": False,
            "preset": "breeze",
        },
        capabilities=["speed", "direction", "oscillation", "preset"],
        propertySpecs={
            "speed": {"type": "number", "min": 0, "max": 100, "step": 25, "unit": "%", "writable": True},
            "preset": {
                "type": "string",
                "writable": True,
                "choices": [{"value": "breeze", "label": "Breeze"}, {"value": "sleep", "label": "Sleep"}],
            },
        },
    )
    plain = stored("f-2", "fan", FAN, properties={"on": False})
    ha = await setup(hass, ceiling, plain)

    state = ha.state("fan", "f-1")
    assert state.state == "on"
    assert state.attributes["percentage"] == 50
    assert state.attributes["percentage_step"] == 25
    assert state.attributes["direction"] == "forward"
    assert state.attributes["oscillating"] is False
    # set speed, oscillate, direction, turn off and turn on
    assert state.attributes["supported_features"] == 1 | 2 | 4 | 16 | 32
    assert ha.state("select", "f-1_preset").state == "Breeze"

    plain_state = ha.state("fan", "f-2")
    assert plain_state.state == "off"
    assert plain_state.attributes["supported_features"] == 16 | 32
    assert "percentage" not in plain_state.attributes

    entity = ha.entity("fan", "f-1")
    await entity.async_set_percentage(75)
    await entity.async_oscillate(True)
    await entity.async_set_direction("reverse")
    await ha.entity("select", "f-1_preset").async_select_option("Sleep")
    await entity.async_set_percentage(0)
    await ha.changed("f-1", "on", False)
    await entity.async_set_percentage(25)
    await ha.entity("fan", "f-2").async_turn_on()
    assert ha.client.commands == [
        ("f-1", "speed", 75),
        ("f-1", "oscillating", True),
        ("f-1", "direction", "reverse"),
        ("f-1", "preset", "sleep"),
        ("f-1", "on", False),
        ("f-1", "speed", 25),
        ("f-1", "on", True),
        ("f-2", "on", True),
    ]


VALVE = {
    "domain": "valve",
    "stateProperty": "currentState",
    "commandProperty": "targetState",
    "states": {"open": 0, "closed": 1, "opening": 2, "closing": 3},
}


async def test_a_valve_opens_and_closes_or_moves_to_a_position(hass: HomeAssistant) -> None:
    sprinkler = stored("v-1", "valve", {**VALVE, "deviceClass": "irrigation"}, properties={"currentState": 1})
    gas = stored(
        "v-2",
        "valve",
        {
            **VALVE,
            "deviceClass": "gas",
            "position": {"current": "currentPosition", "target": "targetPosition"},
        },
        properties={"currentState": 0, "currentPosition": 40},
        capabilities=["position"],
    )
    ha = await setup(hass, sprinkler, gas)

    state = ha.state("valve", "v-1")
    assert state.state == "closed"
    assert state.attributes["device_class"] == "water"
    assert state.attributes["supported_features"] == 1 | 2
    assert "current_position" not in state.attributes

    gas_state = ha.state("valve", "v-2")
    assert gas_state.state == "open"
    assert gas_state.attributes["device_class"] == "gas"
    assert gas_state.attributes["current_position"] == 40
    # open, close and set position
    assert gas_state.attributes["supported_features"] == 1 | 2 | 4

    await ha.changed("v-1", "currentState", 2)
    assert ha.state("valve", "v-1").state == "opening"
    await ha.changed("v-2", "currentPosition", 0)
    assert ha.state("valve", "v-2").state == "closed"

    await ha.entity("valve", "v-1").async_handle_close_valve()
    await ha.entity("valve", "v-2").async_handle_open_valve()
    await ha.entity("valve", "v-2").async_set_valve_position(30)
    assert ha.client.commands == [
        ("v-1", "targetState", 1),
        ("v-2", "targetPosition", 100),
        ("v-2", "targetPosition", 30),
    ]


async def test_a_scene_runs_when_activated(hass: HomeAssistant) -> None:
    semantics = {"domain": "scene", "stateProperty": "active", "commandProperty": "active"}
    ha = await setup(hass, stored("s-1", "scene", semantics, properties={"active": False}))

    assert ha.state("scene", "s-1").state == "unknown"

    await ha.entity("scene", "s-1").async_activate()
    assert ha.client.commands == [("s-1", "active", True)]


HUMIDIFIER = {"domain": "humidifier", "stateProperty": "on", "commandProperty": "on"}


async def test_a_humidifier_offers_its_range_modes_and_readings(hass: HomeAssistant) -> None:
    bedroom = stored(
        "h-1",
        "humidifier",
        {
            **HUMIDIFIER,
            "deviceClass": "humidifier",
            "humidifier": {
                "target": "targetHumidity",
                "current": "currentHumidity",
                "action": "action",
                "mode": "mode",
            },
        },
        properties={
            "on": True,
            "targetHumidity": 45,
            "currentHumidity": 38,
            "action": "humidifying",
            "mode": "m-1",
        },
        capabilities=["humidity", "action", "mode"],
        propertySpecs={
            "targetHumidity": {
                "type": "number",
                "min": 30,
                "max": 80,
                "step": 5,
                "unit": "%",
                "writable": True,
            },
            "mode": {
                "type": "string",
                "writable": True,
                "choices": [{"value": "m-1", "label": "Eco"}, {"value": "m-2", "label": "Sleep"}],
            },
        },
    )
    basement = stored(
        "h-2",
        "humidifier",
        {**HUMIDIFIER, "deviceClass": "dehumidifier", "humidifier": {"target": "targetHumidity"}},
        properties={"on": False, "targetHumidity": 50},
    )
    ha = await setup(hass, bedroom, basement)

    state = ha.state("humidifier", "h-1")
    assert state.state == "on"
    assert state.attributes["device_class"] == "humidifier"
    assert state.attributes["humidity"] == 45
    assert state.attributes["current_humidity"] == 38
    assert state.attributes["action"] == "humidifying"
    assert state.attributes["min_humidity"] == 30
    assert state.attributes["max_humidity"] == 80
    assert state.attributes["target_humidity_step"] == 5
    assert state.attributes["available_modes"] == ["Eco", "Sleep"]
    assert state.attributes["mode"] == "Eco"
    # modes
    assert state.attributes["supported_features"] == 1
    assert not ha.has("select", "h-1_mode")

    basement_state = ha.state("humidifier", "h-2")
    assert basement_state.state == "off"
    assert basement_state.attributes["device_class"] == "dehumidifier"
    assert basement_state.attributes["supported_features"] == 0
    assert basement_state.attributes["min_humidity"] == 0
    assert basement_state.attributes["max_humidity"] == 100
    for attribute in ("available_modes", "mode", "action", "current_humidity", "target_humidity_step"):
        assert attribute not in basement_state.attributes

    await ha.changed("h-1", "on", False)
    assert ha.state("humidifier", "h-1").attributes["action"] == "off"

    entity = ha.entity("humidifier", "h-1")
    await entity.async_set_humidity(50)
    await entity.async_set_mode("Sleep")
    await entity.async_turn_off()
    await ha.entity("humidifier", "h-2").async_turn_on()
    assert ha.client.commands == [
        ("h-1", "targetHumidity", 50),
        ("h-1", "mode", "m-2"),
        ("h-1", "on", False),
        ("h-2", "on", True),
    ]

    with pytest.raises(ServiceValidationError):
        await entity.async_set_mode("Turbo")
