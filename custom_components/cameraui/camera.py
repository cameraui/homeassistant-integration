from __future__ import annotations

from typing import Any

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .api import CameraUiApiError
from .coordinator import CameraUiCoordinator
from .entity import CameraUiEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = entry.runtime_data.coordinator
    async_add_entities(CameraUiCamera(coordinator, camera_id) for camera_id in coordinator.data)


def _pick_source(sources: list[dict[str, Any]]) -> dict[str, Any] | None:
    for role in ("high-resolution", "mid-resolution", "low-resolution"):
        for source in sources:
            if source.get("role") == role:
                return source
    return sources[0] if sources else None


class CameraUiCamera(CameraUiEntity, Camera):
    _attr_name = None
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, coordinator: CameraUiCoordinator, camera_id: str) -> None:
        CameraUiEntity.__init__(self, coordinator, camera_id)
        Camera.__init__(self)
        self._attr_unique_id = camera_id

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        # the cameraui-card reads these to open the proxied go2rtc stream + show the PTZ overlay
        attrs: dict[str, Any] = {
            "camera_name": self.camera_data.get("name"),
            "entry_id": self.coordinator.config_entry.entry_id,
            "sources": [
                {"id": source.get("_id"), "name": source.get("name"), "role": source.get("role")}
                for source in self.camera_data.get("sources", [])
            ],
        }
        ptz = self.coordinator.config_entry.runtime_data.sensor_manager.sensor_for_camera_type(
            self._camera_id, "ptz"
        )
        if ptz:
            attrs["ptz"] = ptz.get("capabilities", [])
        return attrs

    async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
        name = self.camera_data.get("name")
        if not name:
            return None
        try:
            return await self.coordinator.client.get_snapshot(name)
        except CameraUiApiError:
            return None

    async def stream_source(self) -> str | None:
        name = self.camera_data.get("name")
        if not name:
            return None
        try:
            sources = await self.coordinator.client.get_rtsp_sources(name)
        except CameraUiApiError:
            return None
        source = _pick_source(sources)
        return source.get("url") if source else None
