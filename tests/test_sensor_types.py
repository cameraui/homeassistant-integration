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
    lawn_mower,
    light,
    lock,
    media_player,
    number,
    scene,
    select,
    sensor,
    siren,
    switch,
    text,
    vacuum,
    valve,
    water_heater,
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
    "water_heater": water_heater,
    "vacuum": vacuum,
    "lawn_mower": lawn_mower,
    "media_player": media_player,
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
    "airPurifier",
    "waterHeater",
    "vacuum",
    "lawnMower",
    "mediaPlayer",
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


PURIFIER = {"domain": "airPurifier", "stateProperty": "on", "commandProperty": "on"}


async def test_an_air_purifier_is_a_fan_with_its_presets_toggles_and_filter(hass: HomeAssistant) -> None:
    bedroom = stored(
        "p-1",
        "airPurifier",
        {
            **PURIFIER,
            "fan": {"speed": "speed"},
            "choices": ["preset"],
            "toggles": ["auto", "childLock"],
            "readings": [{"property": "filterLife", "unit": "%"}],
        },
        properties={
            "on": True,
            "speed": 60,
            "auto": False,
            "childLock": True,
            "preset": "sleep",
            "filterLife": 35,
        },
        capabilities=["speed", "auto", "preset", "childLock", "filter"],
        propertySpecs={
            "speed": {"type": "number", "min": 0, "max": 100, "step": 1, "unit": "%", "writable": True},
            "preset": {
                "type": "string",
                "writable": True,
                "choices": [{"value": "sleep", "label": "Sleep"}, {"value": "turbo", "label": "Turbo"}],
            },
        },
    )
    hallway = stored("p-2", "airPurifier", {**PURIFIER, "readings": []}, properties={"on": False})
    ha = await setup(hass, bedroom, hallway)

    state = ha.state("fan", "p-1")
    assert state.state == "on"
    assert state.attributes["percentage"] == 60
    assert state.attributes["percentage_step"] == 1
    # set speed, turn off and turn on
    assert state.attributes["supported_features"] == 1 | 16 | 32
    assert ha.state("select", "p-1_preset").state == "Sleep"

    filter_life = ha.state("sensor", "p-1_filterLife")
    assert filter_life.state == "35"
    assert filter_life.attributes["unit_of_measurement"] == "%"
    assert filter_life.attributes["friendly_name"] == "Front Filter life"

    assert ha.state("switch", "p-1_auto").state == "off"
    child_lock = ha.state("switch", "p-1_childLock")
    assert child_lock.state == "on"
    assert child_lock.attributes["friendly_name"] == "Front Child lock"

    hallway_state = ha.state("fan", "p-2")
    assert hallway_state.state == "off"
    assert hallway_state.attributes["supported_features"] == 16 | 32
    assert "percentage" not in hallway_state.attributes
    for domain, unique_id in (("switch", "p-2_auto"), ("select", "p-2_preset"), ("sensor", "p-2_filterLife")):
        assert not ha.has(domain, unique_id)

    await ha.entity("fan", "p-1").async_set_percentage(40)
    await ha.entity("select", "p-1_preset").async_select_option("Turbo")
    await ha.entity("switch", "p-1_auto").async_turn_on()
    await ha.entity("switch", "p-1_childLock").async_turn_off()
    await ha.entity("fan", "p-2").async_turn_on()
    assert ha.client.commands == [
        ("p-1", "speed", 40),
        ("p-1", "preset", "turbo"),
        ("p-1", "auto", True),
        ("p-1", "childLock", False),
        ("p-2", "on", True),
    ]

    await ha.changed("p-1", "childLock", False)
    assert ha.state("switch", "p-1_childLock").state == "off"


WATER_HEATER = {
    "domain": "waterHeater",
    "stateProperty": "mode",
    "commandProperty": "mode",
    "climate": {"current": "currentTemperature", "target": "targetTemperature", "mode": "mode"},
}


async def test_a_water_heater_offers_its_modes_and_range(hass: HomeAssistant) -> None:
    boiler = stored(
        "w-1",
        "waterHeater",
        {**WATER_HEATER, "states": {"off": "off", "eco": "eco", "heat_pump": "heat_pump"}},
        properties={"mode": "eco", "currentTemperature": 48.5, "targetTemperature": 55},
        propertySpecs={
            "targetTemperature": {
                "type": "number",
                "min": 40,
                "max": 65,
                "step": 1,
                "unit": "°C",
                "writable": True,
            },
            "mode": {
                "type": "enum",
                "writable": True,
                "values": {"off": "off", "eco": "eco", "heat_pump": "heat_pump"},
            },
        },
    )
    tank = stored(
        "w-2",
        "waterHeater",
        {**WATER_HEATER, "states": {"off": "off", "electric": "electric"}},
        properties={"mode": "off", "targetTemperature": 50},
    )
    ha = await setup(hass, boiler, tank)

    state = ha.state("water_heater", "w-1")
    assert state.state == "eco"
    assert state.attributes["operation_list"] == ["off", "eco", "heat_pump"]
    assert state.attributes["operation_mode"] == "eco"
    assert state.attributes["current_temperature"] == 48.5
    assert state.attributes["temperature"] == 55
    assert state.attributes["min_temp"] == 40
    assert state.attributes["max_temp"] == 65
    assert state.attributes["target_temp_step"] == 1
    # target temperature and operation mode, turning on has no single mode to go to
    assert state.attributes["supported_features"] == 1 | 2
    assert "away_mode" not in state.attributes

    tank_state = ha.state("water_heater", "w-2")
    assert tank_state.state == "off"
    # target temperature, operation mode and on/off
    assert tank_state.attributes["supported_features"] == 1 | 2 | 8
    assert tank_state.attributes["min_temp"] == 43.3
    assert tank_state.attributes["max_temp"] == 60
    assert tank_state.attributes["current_temperature"] is None
    assert "target_temp_step" not in tank_state.attributes

    await ha.changed("w-1", "mode", "heat_pump")
    assert ha.state("water_heater", "w-1").state == "heat_pump"

    entity = ha.entity("water_heater", "w-1")
    await entity.async_set_temperature(temperature=60, operation_mode="off")
    await entity.async_handle_set_operation_mode("eco")
    await ha.entity("water_heater", "w-2").async_turn_on()
    await ha.entity("water_heater", "w-2").async_turn_off()
    assert ha.client.commands == [
        ("w-1", "mode", "off"),
        ("w-1", "targetTemperature", 60),
        ("w-1", "mode", "eco"),
        ("w-2", "mode", "electric"),
        ("w-2", "mode", "off"),
    ]

    with pytest.raises(ServiceValidationError):
        await entity.async_handle_set_operation_mode("gas")


async def test_a_toggle_is_a_switch_while_the_sensor_offers_it(hass: HomeAssistant) -> None:
    ha = await setup(
        hass,
        stored(
            "w-1",
            "waterHeater",
            {**WATER_HEATER, "states": {"off": "off", "eco": "eco"}},
            properties={"mode": "eco", "targetTemperature": 50, "away": False},
        ),
    )
    assert not ha.has("switch", "w-1_away")

    semantics = {**WATER_HEATER, "states": {"off": "off", "eco": "eco"}}
    await ha.push(
        {
            "type": "meta",
            "sensorId": "w-1",
            "capabilities": ["away"],
            "semantics": {**semantics, "toggles": ["away"]},
        }
    )
    away = ha.state("switch", "w-1_away")
    assert away.state == "off"
    assert away.attributes["friendly_name"] == "Front Away"

    await ha.entity("switch", "w-1_away").async_turn_on()
    await ha.changed("w-1", "away", True)
    assert ha.state("switch", "w-1_away").state == "on"

    await ha.entity("switch", "w-1_away").async_turn_off()
    assert ha.client.commands == [("w-1", "away", True), ("w-1", "away", False)]

    await ha.push({"type": "meta", "sensorId": "w-1", "capabilities": [], "semantics": semantics})
    assert ha.state("switch", "w-1_away").state == "unavailable"


VACUUM = {"domain": "vacuum", "stateProperty": "activity", "commandProperty": "command"}


async def test_a_vacuum_offers_the_commands_and_fan_speeds_it_has(hass: HomeAssistant) -> None:
    commands = {name: name for name in ("start", "pause", "stop", "dock", "locate", "spot")}
    robot = stored(
        "r-1",
        "vacuum",
        {**VACUUM, "commands": commands, "fanSpeed": {"property": "fanSpeed"}},
        properties={"activity": "docked", "command": "", "fanSpeed": "quiet"},
        capabilities=["fanSpeed"],
        propertySpecs={
            "fanSpeed": {
                "type": "string",
                "writable": True,
                "choices": [{"value": "quiet", "label": "Quiet"}, {"value": "max", "label": "Max"}],
            }
        },
    )
    basic = stored(
        "r-2",
        "vacuum",
        {**VACUUM, "commands": {"start": "start", "dock": "dock"}},
        properties={"command": ""},
    )
    ha = await setup(hass, robot, basic)

    state = ha.state("vacuum", "r-1")
    assert state.state == "docked"
    assert state.attributes["fan_speed"] == "Quiet"
    assert state.attributes["fan_speed_list"] == ["Quiet", "Max"]
    # state, start, pause, stop, return home, locate, clean spot and fan speed
    assert state.attributes["supported_features"] == 4096 | 8192 | 4 | 8 | 16 | 512 | 1024 | 32
    assert not ha.has("select", "r-1_fanSpeed")

    basic_state = ha.state("vacuum", "r-2")
    assert basic_state.state == "unknown"
    # state, start and return home
    assert basic_state.attributes["supported_features"] == 4096 | 8192 | 16
    assert "fan_speed" not in basic_state.attributes
    assert "fan_speed_list" not in basic_state.attributes

    for activity in ("cleaning", "paused", "returning", "idle", "error"):
        await ha.changed("r-1", "activity", activity)
        assert ha.state("vacuum", "r-1").state == activity
    await ha.changed("r-1", "command", "dock")
    assert ha.state("vacuum", "r-1").state == "error"
    await ha.changed("r-1", "activity", None)
    assert ha.state("vacuum", "r-1").state == "unknown"
    await ha.changed("r-1", "fanSpeed", "max")
    assert ha.state("vacuum", "r-1").attributes["fan_speed"] == "Max"

    entity = ha.entity("vacuum", "r-1")
    await entity.async_start()
    await entity.async_pause()
    await entity.async_stop()
    await entity.async_return_to_base()
    await entity.async_locate()
    await entity.async_clean_spot()
    await entity.async_set_fan_speed("Quiet")
    await ha.entity("vacuum", "r-2").async_return_to_base()
    assert ha.client.commands == [
        ("r-1", "command", "start"),
        ("r-1", "command", "pause"),
        ("r-1", "command", "stop"),
        ("r-1", "command", "dock"),
        ("r-1", "command", "locate"),
        ("r-1", "command", "spot"),
        ("r-1", "fanSpeed", "quiet"),
        ("r-2", "command", "dock"),
    ]

    with pytest.raises(ServiceValidationError):
        await entity.async_set_fan_speed("Turbo")


LAWN_MOWER = {"domain": "lawnMower", "stateProperty": "activity", "commandProperty": "command"}


async def test_a_lawn_mower_mows_pauses_and_docks_when_it_can(hass: HomeAssistant) -> None:
    garden = stored(
        "m-1",
        "lawnMower",
        {**LAWN_MOWER, "commands": {"start": "start", "pause": "pause", "dock": "dock"}},
        properties={"activity": "mowing", "command": ""},
    )
    meadow = stored(
        "m-2", "lawnMower", {**LAWN_MOWER, "commands": {"start": "start", "dock": "dock"}}, properties={}
    )
    ha = await setup(hass, garden, meadow)

    state = ha.state("lawn_mower", "m-1")
    assert state.state == "mowing"
    # start mowing, pause and dock
    assert state.attributes["supported_features"] == 1 | 2 | 4

    meadow_state = ha.state("lawn_mower", "m-2")
    assert meadow_state.state == "unknown"
    # start mowing and dock
    assert meadow_state.attributes["supported_features"] == 1 | 4

    for activity in ("paused", "returning", "docked", "error"):
        await ha.changed("m-1", "activity", activity)
        assert ha.state("lawn_mower", "m-1").state == activity
    await ha.changed("m-1", "command", "start")
    assert ha.state("lawn_mower", "m-1").state == "error"

    entity = ha.entity("lawn_mower", "m-1")
    await entity.async_start_mowing()
    await entity.async_pause()
    await entity.async_dock()
    await ha.entity("lawn_mower", "m-2").async_start_mowing()
    assert ha.client.commands == [
        ("m-1", "command", "start"),
        ("m-1", "command", "pause"),
        ("m-1", "command", "dock"),
        ("m-2", "command", "start"),
    ]


MEDIA_PLAYER = {"domain": "mediaPlayer", "stateProperty": "state", "commandProperty": "command"}


async def test_a_media_player_offers_the_controls_and_commands_it_has(hass: HomeAssistant) -> None:
    tv = stored(
        "p-1",
        "mediaPlayer",
        {
            **MEDIA_PLAYER,
            "deviceClass": "tv",
            "commands": {name: name for name in ("play", "pause", "stop", "next", "previous")},
            "mediaPlayer": {
                "power": "on",
                "volume": "volume",
                "muted": "muted",
                "source": "source",
                "title": "title",
                "artist": "artist",
            },
        },
        properties={
            "on": True,
            "state": "playing",
            "command": "",
            "volume": 40,
            "muted": False,
            "source": "hdmi1",
            "title": "So What",
            "artist": "Miles Davis",
        },
        capabilities=["power", "volume", "mute", "source", "nowPlaying"],
        propertySpecs={
            "source": {
                "type": "string",
                "writable": True,
                "choices": [{"value": "hdmi1", "label": "HDMI 1"}, {"value": "netflix", "label": "Netflix"}],
            }
        },
    )
    speaker = stored(
        "p-2",
        "mediaPlayer",
        {**MEDIA_PLAYER, "commands": {"play": "play", "pause": "pause"}, "mediaPlayer": {"volume": "volume"}},
        properties={"state": "idle", "command": "", "volume": 25},
        capabilities=["volume"],
    )
    ha = await setup(hass, tv, speaker)

    state = ha.state("media_player", "p-1")
    assert state.state == "playing"
    assert state.attributes["device_class"] == "tv"
    assert state.attributes["volume_level"] == 0.4
    assert state.attributes["is_volume_muted"] is False
    assert state.attributes["source"] == "HDMI 1"
    assert state.attributes["source_list"] == ["HDMI 1", "Netflix"]
    assert state.attributes["media_title"] == "So What"
    assert state.attributes["media_artist"] == "Miles Davis"
    # play, pause, stop, next, previous, turn on, turn off, volume set, mute and select source
    assert state.attributes["supported_features"] == 16384 | 1 | 4096 | 32 | 16 | 128 | 256 | 4 | 8 | 2048
    assert not ha.has("select", "p-1_source")
    assert not ha.has("number", "p-1_volume")

    speaker_state = ha.state("media_player", "p-2")
    assert speaker_state.state == "idle"
    assert speaker_state.attributes["volume_level"] == 0.25
    # play, pause and volume set
    assert speaker_state.attributes["supported_features"] == 16384 | 1 | 4
    for attribute in ("device_class", "is_volume_muted", "source", "source_list", "media_title"):
        assert attribute not in speaker_state.attributes

    for player_state in ("on", "idle", "paused", "buffering", "off"):
        await ha.changed("p-1", "state", player_state)
        assert ha.state("media_player", "p-1").state == player_state
    await ha.changed("p-1", "command", "play")
    assert ha.state("media_player", "p-1").state == "off"
    await ha.changed("p-1", "state", None)
    assert ha.state("media_player", "p-1").state == "unknown"
    await ha.changed("p-1", "state", "playing")
    await ha.changed("p-1", "volume", 0)
    await ha.changed("p-1", "source", "netflix")
    playing = ha.state("media_player", "p-1")
    assert playing.attributes["volume_level"] == 0
    assert playing.attributes["source"] == "Netflix"

    entity = ha.entity("media_player", "p-1")
    await entity.async_turn_on()
    await entity.async_turn_off()
    await entity.async_set_volume_level(0.55)
    await entity.async_mute_volume(True)
    await entity.async_select_source("HDMI 1")
    await entity.async_media_play()
    await entity.async_media_pause()
    await entity.async_media_stop()
    await entity.async_media_next_track()
    await entity.async_media_previous_track()
    await ha.entity("media_player", "p-2").async_volume_up()
    await ha.entity("media_player", "p-2").async_media_pause()
    assert ha.client.commands == [
        ("p-1", "on", True),
        ("p-1", "on", False),
        ("p-1", "volume", 55),
        ("p-1", "muted", True),
        ("p-1", "source", "hdmi1"),
        ("p-1", "command", "play"),
        ("p-1", "command", "pause"),
        ("p-1", "command", "stop"),
        ("p-1", "command", "next"),
        ("p-1", "command", "previous"),
        ("p-2", "volume", 35),
        ("p-2", "command", "pause"),
    ]

    with pytest.raises(ServiceValidationError):
        await entity.async_select_source("Cable")
