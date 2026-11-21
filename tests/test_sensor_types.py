from __future__ import annotations

from types import ModuleType, SimpleNamespace
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import Entity
from pytest_homeassistant_custom_component.common import MockEntityPlatform

from custom_components.cameraui import event, number, select, sensor, siren, text
from custom_components.cameraui.const import DOMAIN
from custom_components.cameraui.coordinator import CameraUiCoordinator
from custom_components.cameraui.sensor_manager import CameraUiSensorManager

from .helpers import FakeEventsClient, make_entry

PLATFORMS: dict[str, ModuleType] = {
    "sensor": sensor,
    "event": event,
    "text": text,
    "number": number,
    "select": select,
    "siren": siren,
}

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
