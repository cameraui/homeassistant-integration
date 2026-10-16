from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from pytest_homeassistant_custom_component.common import async_capture_events

from custom_components.cameraui.const import EVENT_CAMERAUI, SIGNAL_DETECTION
from custom_components.cameraui.coordinator import CameraUiCoordinator

from .helpers import FakeEventsClient, make_entry


def start_message(camera_id: str, event_id: str) -> dict[str, Any]:
    return {
        "type": "start",
        "event": {"id": event_id, "cameraId": camera_id, "state": "active", "types": ["motion", "person"]},
        "labels": ["person"],
    }


def update_message(camera_id: str, event_id: str, labels: list[str]) -> dict[str, Any]:
    return {
        "type": "update",
        "event": {"id": event_id, "cameraId": camera_id, "state": "active", "types": ["motion"]},
        "labels": labels,
    }


def make_coordinator(hass: HomeAssistant) -> tuple[FakeEventsClient, list[Event]]:
    entry = make_entry()
    entry.add_to_hass(hass)
    client = FakeEventsClient()
    coordinator = CameraUiCoordinator(hass, entry, client)  # type: ignore[arg-type]
    coordinator.data = {"cam1": {"name": "Front"}, "cam2": {"name": "Back"}}
    return client, async_capture_events(hass, EVENT_CAMERAUI)


def record_detections(hass: HomeAssistant, camera_id: str) -> tuple[list[dict[str, Any]], Callable[[], None]]:
    seen: list[dict[str, Any]] = []

    @callback
    def record(message: dict[str, Any]) -> None:
        seen.append(message)

    return seen, async_dispatcher_connect(hass, f"{SIGNAL_DETECTION}_{camera_id}", record)


def fired(events: list[Event]) -> list[tuple[str, str, str]]:
    return [(e.data["camera_id"], e.data["state"], e.data["event_id"]) for e in events]


async def test_socket_loss_ends_detections_that_were_running(hass: HomeAssistant) -> None:
    client, events = make_coordinator(hass)
    seen, unsub = record_detections(hass, "cam1")

    client.detection(start_message("cam1", "e1"))
    client.detection({"type": "end", "event": {"id": "e0", "cameraId": "cam2", "state": "ended"}})
    client.connection(False)
    await hass.async_block_till_done()

    ended = seen[-1]
    assert ended["type"] == "end"
    assert ended["event"]["state"] != "active"
    assert ended["labels"] == []
    assert [(e.data["camera_id"], e.data["state"]) for e in events] == [
        ("cam1", "start"),
        ("cam2", "end"),
        ("cam1", "end"),
    ]
    assert events[-1].data["event_id"] == "e1"

    client.connection(False)
    await hass.async_block_till_done()
    assert len(events) == 3
    unsub()


async def test_reconnect_ends_only_the_detections_the_server_no_longer_reports(hass: HomeAssistant) -> None:
    client, events = make_coordinator(hass)
    front, unsub_front = record_detections(hass, "cam1")
    back, unsub_back = record_detections(hass, "cam2")
    client.subscribed([])
    client.detection(start_message("cam1", "e1"))
    client.detection(start_message("cam2", "e2"))

    client.connection(False)
    await hass.async_block_till_done()
    assert fired(events) == [("cam1", "start", "e1"), ("cam2", "start", "e2")]

    client.subscribed(["cam1"])
    client.detection(start_message("cam1", "e1"))
    await hass.async_block_till_done()

    assert fired(events) == [("cam1", "start", "e1"), ("cam2", "start", "e2"), ("cam2", "end", "e2")]
    assert back[-1]["event"]["state"] == "ended"
    assert back[-1]["labels"] == []
    assert all(message["event"]["state"] == "active" for message in front)
    assert front[-1]["labels"] == ["person"]
    unsub_front()
    unsub_back()


async def test_ack_without_running_detections_ends_all_of_them(hass: HomeAssistant) -> None:
    client, events = make_coordinator(hass)
    client.subscribed([])
    client.detection(start_message("cam1", "e1"))

    client.connection(False)
    await hass.async_block_till_done()
    assert fired(events) == [("cam1", "start", "e1")]

    client.subscribed(None)
    await hass.async_block_till_done()
    assert fired(events) == [("cam1", "start", "e1"), ("cam1", "end", "e1")]


async def test_message_of_another_event_ends_the_one_whose_end_was_missed(hass: HomeAssistant) -> None:
    client, events = make_coordinator(hass)
    seen, unsub = record_detections(hass, "cam1")

    client.detection(start_message("cam1", "e1"))
    client.detection(update_message("cam1", "e2", ["car"]))
    await hass.async_block_till_done()

    assert fired(events) == [("cam1", "start", "e1"), ("cam1", "end", "e1"), ("cam1", "object", "e2")]
    assert seen[-1]["event"]["id"] == "e2"
    assert seen[-1]["labels"] == ["car"]
    unsub()


async def test_replayed_start_of_a_running_event_is_not_a_second_start(hass: HomeAssistant) -> None:
    client, events = make_coordinator(hass)
    seen, unsub = record_detections(hass, "cam1")

    client.detection(start_message("cam1", "e1"))
    client.detection(update_message("cam1", "e1", ["car"]))
    client.detection({**start_message("cam1", "e1"), "labels": ["person", "car"]})
    await hass.async_block_till_done()

    assert fired(events) == [("cam1", "start", "e1"), ("cam1", "object", "e1")]
    assert seen[-1]["labels"] == ["car", "person"]
    unsub()
