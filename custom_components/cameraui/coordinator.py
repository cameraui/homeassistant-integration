from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import CameraUiApiError, CameraUiClient
from .const import DOMAIN, EVENT_CAMERAUI, SIGNAL_CONNECTION, SIGNAL_DETECTION

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=60)


class CameraUiCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: CameraUiClient) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL, config_entry=entry)
        self.client = client
        self._detections: dict[str, dict[str, Any]] = {}
        client.on_detection(self._handle_detection)
        client.on_connection(self._handle_connection)

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            cameras = await self.client.get_cameras()
        except CameraUiApiError as err:
            raise UpdateFailed(str(err)) from err

        data = {camera["_id"]: camera for camera in cameras}
        self._remove_stale_devices(data)
        return data

    @callback
    def _remove_stale_devices(self, cameras: dict[str, dict[str, Any]]) -> None:
        registry = dr.async_get(self.hass)
        entry_id = self.config_entry.entry_id
        for device in dr.async_entries_for_config_entry(registry, entry_id):
            camera_id = next((ident for domain, ident in device.identifiers if domain == DOMAIN), None)
            if camera_id and camera_id not in cameras:
                _LOGGER.debug("Removing device for deleted camera %s", camera_id)
                registry.async_update_device(device.id, remove_config_entry_id=entry_id)

    def _handle_detection(self, message: dict[str, Any]) -> None:
        event = message.get("event", {})
        camera_id = event.get("cameraId")
        if not camera_id:
            return

        msg_type = message.get("type")
        if msg_type == "start":
            self._detections[camera_id] = {"labels": set(), "attributes": {}}

        state = self._detections.setdefault(camera_id, {"labels": set(), "attributes": {}})
        labels_grew = False
        attrs_grew = False
        for label in message.get("labels", []):
            if label not in state["labels"]:
                state["labels"].add(label)
                labels_grew = True
        for attribute in message.get("attributes", []):
            key = (attribute.get("type"), attribute.get("label"))
            if key[1] and key not in state["attributes"]:
                state["attributes"][key] = attribute
                attrs_grew = True

        labels = sorted(state["labels"])
        attributes = list(state["attributes"].values())

        if msg_type == "end":
            self._detections.pop(camera_id, None)

        # object-label sensors read the accumulated set (sticky during the event); on end it clears, so they fall back to off
        message["labels"] = [] if msg_type == "end" else labels
        message["attributes"] = [] if msg_type == "end" else attributes
        async_dispatcher_send(self.hass, f"{SIGNAL_DETECTION}_{camera_id}", message)

        if msg_type == "start":
            self._fire_event(camera_id, "start", event, labels, attributes)
        elif msg_type == "end":
            self._fire_event(camera_id, "end", event, labels, attributes)
        elif attrs_grew:
            # a face/plate/classifier result was recognized, fire so those automations trigger promptly
            self._fire_event(camera_id, "recognized", event, labels, attributes)
        elif labels_grew:
            # a new object class appeared mid-event (objects also have their own binary sensors)
            self._fire_event(camera_id, "object", event, labels, attributes)

    def _fire_event(
        self,
        camera_id: str,
        state: str,
        event: dict[str, Any],
        labels: list[str],
        attributes: list[dict[str, Any]],
    ) -> None:
        camera = self.data.get(camera_id, {})
        faces = [a["label"] for a in attributes if a.get("type") == "face"]
        plates = [a["label"] for a in attributes if a.get("type") == "license_plate"]
        classifications = [a["label"] for a in attributes if a.get("type") not in ("face", "license_plate")]
        self.hass.bus.async_fire(
            EVENT_CAMERAUI,
            {
                "camera_id": camera_id,
                "camera_name": camera.get("name"),
                "state": state,
                "detection_types": event.get("types", []),
                "event_id": event.get("id"),
                "labels": labels,
                "faces": faces,
                "plates": plates,
                "classifications": classifications,
                "attributes": attributes,
            },
        )

    def _handle_connection(self, connected: bool) -> None:
        async_dispatcher_send(self.hass, SIGNAL_CONNECTION, connected)
