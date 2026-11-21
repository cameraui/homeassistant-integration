from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry, MockEntityPlatform

from custom_components.cameraui import async_remove_config_entry_device
from custom_components.cameraui.binary_sensor import CameraUiBinarySensor
from custom_components.cameraui.const import DOMAIN
from custom_components.cameraui.coordinator import CameraUiCoordinator
from custom_components.cameraui.devices import async_get_device, async_remove_empty_sensor_devices
from custom_components.cameraui.sensor import CameraUiMeasurement
from custom_components.cameraui.sensor_manager import CameraUiSensorManager

from .helpers import FakeEventsClient, make_entry

HUB = {
    "id": "d-1",
    "name": "Hallway sensor",
    "sourceName": "Hallway sensor",
    "manufacturer": "Ubiquiti",
    "model": "UP-Sense",
    "firmware": "4.1.2",
    "serialNumber": "F4E2C6",
}


def sensor(sensor_id: str, display_name: str, **changes: Any) -> dict[str, Any]:
    return {
        "id": sensor_id,
        "type": "contact",
        "name": display_name,
        "displayName": display_name,
        "shortName": display_name,
        "primary": False,
        "pluginName": "UniFi Protect",
        "exposed": True,
        "connected": True,
        "assignedCameraIds": [],
        "properties": {"detected": False},
        "semantics": {"domain": "binary", "deviceClass": "door", "stateProperty": "detected"},
        **changes,
    }


class Setup:
    def __init__(
        self,
        hass: HomeAssistant,
        entry: MockConfigEntry,
        client: FakeEventsClient,
        manager: CameraUiSensorManager,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.client = client
        self.manager = manager

    def device(self, identifier: str) -> dr.DeviceEntry | None:
        return async_get_device(self.hass, (DOMAIN, identifier), self.entry.entry_id)

    def entity_device(self, sensor_id: str) -> dr.DeviceEntry | None:
        entity_id = er.async_get(self.hass).async_get_entity_id("binary_sensor", DOMAIN, sensor_id)
        assert entity_id
        entry = er.async_get(self.hass).async_get(entity_id)
        assert entry and entry.device_id
        return dr.async_get(self.hass).async_get(entry.device_id)

    def friendly_name(self, sensor_id: str) -> str:
        entity_id = er.async_get(self.hass).async_get_entity_id("binary_sensor", DOMAIN, sensor_id)
        assert entity_id
        state = self.hass.states.get(entity_id)
        assert state
        return str(state.attributes["friendly_name"])

    async def push(self, message: dict[str, Any]) -> None:
        self.client.sensor(message)
        await self.hass.async_block_till_done()


async def setup(hass: HomeAssistant, *sensors: dict[str, Any]) -> Setup:
    entry = make_entry()
    entry.add_to_hass(hass)
    client = FakeEventsClient()
    client.sensors = {item["id"]: item for item in sensors}
    coordinator = CameraUiCoordinator(hass, entry, client)  # type: ignore[arg-type]
    coordinator.data = {"cam-1": {"name": "Driveway"}}
    manager = CameraUiSensorManager(hass, coordinator)
    await manager.async_setup()
    entry.runtime_data = SimpleNamespace(coordinator=coordinator, sensor_manager=manager)

    platform = MockEntityPlatform(hass, domain="binary_sensor", platform_name=DOMAIN)
    platform.config_entry = entry
    await platform.async_add_entities(
        [CameraUiBinarySensor(manager, item) for item in manager.sensors_for_platform(Platform.BINARY_SENSOR)]
    )
    await hass.async_block_till_done()
    return Setup(hass, entry, client, manager)


async def test_a_sensor_without_a_device_is_its_own_device(hass: HomeAssistant) -> None:
    s = await setup(hass, sensor("s-door", "Front door"))

    device = s.entity_device("s-door")
    assert device and device.identifiers == {(DOMAIN, "sensor_s-door")}
    assert device.name == "Front door"
    assert s.friendly_name("s-door") == "Front door"


async def test_sensors_of_a_device_share_one_ha_device(hass: HomeAssistant) -> None:
    s = await setup(
        hass,
        sensor("s-contact", "Hallway sensor", shortName="Contact", primary=True, device=HUB),
        sensor("s-leak", "Hallway sensor Leak", shortName="Leak", device=HUB),
    )

    device = s.device("device_d-1")
    assert device
    assert (device.name, device.manufacturer, device.model, device.sw_version, device.serial_number) == (
        "Hallway sensor",
        "Ubiquiti",
        "UP-Sense",
        "4.1.2",
        "F4E2C6",
    )
    assert s.entity_device("s-contact") == s.entity_device("s-leak") == device
    assert s.friendly_name("s-contact") == "Hallway sensor"
    assert s.friendly_name("s-leak") == "Hallway sensor Leak"
    assert s.device("sensor_s-contact") is None


async def test_a_sensor_joining_a_device_moves_and_leaves_no_empty_device(hass: HomeAssistant) -> None:
    s = await setup(hass, sensor("s-door", "Door"))
    assert s.device("sensor_s-door")

    await s.push(
        {
            "type": "meta",
            "sensorId": "s-door",
            "displayName": "Hallway sensor",
            "shortName": "Door",
            "primary": True,
            "device": HUB,
        }
    )

    device = s.entity_device("s-door")
    assert device and device.identifiers == {(DOMAIN, "device_d-1")}
    assert s.device("sensor_s-door") is None
    assert s.friendly_name("s-door") == "Hallway sensor"

    await s.push(
        {
            "type": "meta",
            "sensorId": "s-door",
            "displayName": "Door",
            "shortName": "Door",
            "primary": False,
            "device": None,
        }
    )

    device = s.entity_device("s-door")
    assert device and device.identifiers == {(DOMAIN, "sensor_s-door")}
    assert s.device("device_d-1") is None
    assert s.friendly_name("s-door") == "Door"


async def test_a_device_rename_reaches_the_ha_device(hass: HomeAssistant) -> None:
    s = await setup(
        hass,
        sensor("s-contact", "Hallway sensor", shortName="Contact", primary=True, device=HUB),
        sensor("s-leak", "Hallway sensor Leak", shortName="Leak", device=HUB),
    )

    renamed = {**HUB, "name": "Flur"}
    for sensor_id, display_name, primary in (("s-contact", "Flur", True), ("s-leak", "Flur Leak", False)):
        await s.push(
            {
                "type": "meta",
                "sensorId": sensor_id,
                "displayName": display_name,
                "primary": primary,
                "device": renamed,
            }
        )

    device = s.device("device_d-1")
    assert device and device.name == "Flur"
    assert s.friendly_name("s-leak") == "Flur Leak"

    await s.push({"type": "meta", "sensorId": "s-leak", "shortName": "Wasser"})
    assert s.friendly_name("s-leak") == "Flur Wasser"


async def test_a_device_goes_with_its_last_sensor_and_stays_while_one_is_left(hass: HomeAssistant) -> None:
    s = await setup(
        hass,
        sensor("s-contact", "Hallway sensor", shortName="Contact", primary=True, device=HUB),
        sensor("s-leak", "Hallway sensor Leak", shortName="Leak", device=HUB),
    )
    device = s.device("device_d-1")
    assert device
    assert not await async_remove_config_entry_device(hass, s.entry, device)  # type: ignore[arg-type]

    await s.push({"type": "removed", "sensorId": "s-leak"})
    assert s.device("device_d-1")
    assert er.async_get(hass).async_get_entity_id("binary_sensor", DOMAIN, "s-leak") is None

    await s.push({"type": "removed", "sensorId": "s-contact"})
    assert s.device("device_d-1") is None


async def test_start_removes_a_sensor_device_its_entity_left(hass: HomeAssistant) -> None:
    s = await setup(
        hass, sensor("s-contact", "Hallway sensor", shortName="Contact", primary=True, device=HUB)
    )
    stale = dr.async_get(hass).async_get_or_create(
        config_entry_id=s.entry.entry_id, identifiers={(DOMAIN, "sensor_s-contact")}, name="Contact"
    )
    camera = dr.async_get(hass).async_get_or_create(
        config_entry_id=s.entry.entry_id, identifiers={(DOMAIN, "cam-1")}, name="Driveway"
    )

    async_remove_empty_sensor_devices(hass, s.entry.entry_id)

    assert dr.async_get(hass).async_get(stale.id) is None
    assert dr.async_get(hass).async_get(camera.id)
    assert s.device("device_d-1")


async def test_the_battery_of_a_device_is_a_diagnostic_entity_of_that_device(hass: HomeAssistant) -> None:
    battery = sensor(
        "s-battery",
        "Hallway sensor Battery",
        type="battery",
        shortName="Battery",
        device=HUB,
        properties={"level": 64},
        semantics={
            "domain": "measurement",
            "deviceClass": "battery",
            "stateProperty": "level",
            "unit": "%",
            "diagnostic": True,
        },
    )
    s = await setup(
        hass, sensor("s-contact", "Hallway sensor", shortName="Contact", primary=True, device=HUB), battery
    )
    platform = MockEntityPlatform(hass, domain="sensor", platform_name=DOMAIN)
    platform.config_entry = s.entry
    await platform.async_add_entities(
        [CameraUiMeasurement(s.manager, item) for item in s.manager.sensors_for_platform(Platform.SENSOR)]
    )
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("sensor", DOMAIN, "s-battery")
    assert entity_id
    entry = registry.async_get(entity_id)
    assert entry and entry.entity_category == er.EntityCategory.DIAGNOSTIC
    assert entry.device_id == s.entity_device("s-contact").id  # type: ignore[union-attr]
    state = hass.states.get(entity_id)
    assert state and state.state == "64"
    assert (state.attributes["device_class"], state.attributes["unit_of_measurement"]) == ("battery", "%")
    assert state.attributes["friendly_name"] == "Hallway sensor Battery"
