from __future__ import annotations

from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CameraUiConfigEntry
from .entity import CameraUiCommandEntity, async_setup_sensor_platform, choice_value

PARALLEL_UPDATES = 1

COMMAND_FEATURES = {
    "play": MediaPlayerEntityFeature.PLAY,
    "pause": MediaPlayerEntityFeature.PAUSE,
    "stop": MediaPlayerEntityFeature.STOP,
    "next": MediaPlayerEntityFeature.NEXT_TRACK,
    "previous": MediaPlayerEntityFeature.PREVIOUS_TRACK,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: CameraUiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_setup_sensor_platform(hass, entry, async_add_entities, Platform.MEDIA_PLAYER, CameraUiMediaPlayer)


class CameraUiMediaPlayer(CameraUiCommandEntity, MediaPlayerEntity):
    _block = "mediaPlayer"

    @property
    def _sources(self) -> list[dict[str, Any]]:
        choices: list[dict[str, Any]] = self._part_spec("source").get("choices", [])
        return choices

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        features = self._command_features(COMMAND_FEATURES, MediaPlayerEntityFeature(0))
        if self._parts.get("power"):
            features |= MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
        if self._parts.get("volume"):
            features |= MediaPlayerEntityFeature.VOLUME_SET
        if self._parts.get("muted"):
            features |= MediaPlayerEntityFeature.VOLUME_MUTE
        if self._parts.get("source"):
            features |= MediaPlayerEntityFeature.SELECT_SOURCE
        return features

    @property
    def device_class(self) -> MediaPlayerDeviceClass | None:
        device_class = self._semantics.get("deviceClass")
        return MediaPlayerDeviceClass(device_class) if device_class else None

    @property
    def state(self) -> MediaPlayerState | None:
        return MediaPlayerState(self._state) if self._state else None

    @property
    def volume_level(self) -> float | None:
        volume = self._read("volume")
        return None if volume is None else volume / 100

    @property
    def is_volume_muted(self) -> bool | None:
        return self._read("muted")

    @property
    def source_list(self) -> list[str]:
        return [choice["label"] for choice in self._sources]

    @property
    def source(self) -> str | None:
        value = self._read("source")
        return next((choice["label"] for choice in self._sources if choice["value"] == value), None)

    @property
    def media_title(self) -> str | None:
        return self._read("title")

    @property
    def media_artist(self) -> str | None:
        return self._read("artist")

    async def async_turn_on(self) -> None:
        await self.async_command(self._parts["power"], True)

    async def async_turn_off(self) -> None:
        await self.async_command(self._parts["power"], False)

    async def async_set_volume_level(self, volume: float) -> None:
        await self.async_command(self._parts["volume"], round(volume * 100))

    async def async_mute_volume(self, mute: bool) -> None:
        await self.async_command(self._parts["muted"], mute)

    async def async_select_source(self, source: str) -> None:
        await self.async_command(self._parts["source"], choice_value(self._sources, source, "source"))

    async def async_media_play(self) -> None:
        await self._send("play")

    async def async_media_pause(self) -> None:
        await self._send("pause")

    async def async_media_stop(self) -> None:
        await self._send("stop")

    async def async_media_next_track(self) -> None:
        await self._send("next")

    async def async_media_previous_track(self) -> None:
        await self._send("previous")
