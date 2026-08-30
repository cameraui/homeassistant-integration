from __future__ import annotations

import asyncio
from datetime import date, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.media_player import MediaClass, MediaType
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceError,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .clips import MEDIA_PATH, async_find_event, day_bounds, event_labels, event_time
from .const import DOMAIN
from .rpc import CameraUiRpcError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import CameraUiConfigEntry

ALL_CAMERAS = "all"
DAYS = 14


async def async_get_media_source(hass: HomeAssistant) -> MediaSource:
    return CameraUiMediaSource(hass)


class CameraUiMediaSource(MediaSource):
    name = "camera.ui"

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(DOMAIN)
        self.hass = hass

    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        parts = [part for part in (item.identifier or "").split("/") if part]
        entries = _loaded_entries(self.hass)
        if not parts:
            if len(entries) == 1:
                return await self._browse_entry(entries[0])
            return _directory(
                "",
                self.name,
                [_directory(entry.entry_id, entry.title) for entry in entries],
            )
        entry = next((entry for entry in entries if entry.entry_id == parts[0]), None)
        if not entry:
            raise MediaSourceError("Unknown camera.ui server")
        if len(parts) == 1:
            return await self._browse_entry(entry)
        if len(parts) == 2:
            return await self._browse_days(entry, parts[1])
        if len(parts) == 3:
            return await self._browse_day(entry, parts[1], parts[2])
        raise MediaSourceError("Nothing to browse here")

    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        parts = [part for part in (item.identifier or "").split("/") if part]
        if len(parts) != 4:
            raise Unresolvable("Not a camera.ui event")
        entry = next((entry for entry in _loaded_entries(self.hass) if entry.entry_id == parts[0]), None)
        if not entry:
            raise Unresolvable("Unknown camera.ui server")
        camera_id, day, event_id = parts[1], parts[2], parts[3]
        try:
            event = await async_find_event(entry, camera_id, day, event_id)
            if not event:
                raise Unresolvable("The recording is no longer available")
            # start the export now, the player's request joins it a moment later
            await entry.runtime_data.clips.open(camera_id, event_id, event["startTime"], event["endTime"])
        except CameraUiRpcError as err:
            raise Unresolvable(str(err)) from err
        return PlayMedia(f"{MEDIA_PATH}/{entry.entry_id}/clip/{camera_id}/{day}/{event_id}", "video/mp4")

    async def _browse_entry(self, entry: CameraUiConfigEntry) -> BrowseMediaSource:
        try:
            nvr = await entry.runtime_data.rpc.nvr_plugin_id()
        except CameraUiRpcError as err:
            raise MediaSourceError(str(err)) from err
        if not nvr:
            return _directory(
                entry.entry_id,
                entry.title,
                [_leaf(f"{entry.entry_id}/{ALL_CAMERAS}", "camera.ui NVR plugin required")],
            )
        registry = er.async_get(self.hass)
        cameras = sorted(entry.runtime_data.coordinator.data.values(), key=lambda c: str(c.get("name", "")))
        children = []
        for camera in cameras:
            entity_id = registry.async_get_entity_id("camera", DOMAIN, camera["_id"])
            children.append(
                _directory(
                    f"{entry.entry_id}/{camera['_id']}",
                    str(camera.get("name", camera["_id"])),
                    thumbnail=f"/api/camera_proxy/{entity_id}" if entity_id else None,
                )
            )
        children.append(_directory(f"{entry.entry_id}/{ALL_CAMERAS}", "All cameras"))
        return _directory(entry.entry_id, entry.title, children)

    async def _browse_days(self, entry: CameraUiConfigEntry, camera_id: str) -> BrowseMediaSource:
        camera_ids = None if camera_id == ALL_CAMERAS else [camera_id]
        today = dt_util.now().date()
        days = [today - timedelta(days=offset) for offset in range(DAYS if camera_ids else 7)]

        async def probe(day: date) -> bool:
            start, end = day_bounds(day)
            return bool(await entry.runtime_data.rpc.get_events(camera_ids, start, end, limit=1))

        try:
            found = await asyncio.gather(*(probe(day) for day in days))
        except CameraUiRpcError as err:
            raise MediaSourceError(str(err)) from err
        children = [
            _directory(f"{entry.entry_id}/{camera_id}/{day.isoformat()}", _day_title(day, today))
            for day, has_events in zip(days, found, strict=True)
            if has_events
        ]
        return _directory(
            f"{entry.entry_id}/{camera_id}",
            self._camera_title(entry, camera_id),
            children,
            children_class=MediaClass.DIRECTORY,
        )

    async def _browse_day(self, entry: CameraUiConfigEntry, camera_id: str, day: str) -> BrowseMediaSource:
        camera_ids = None if camera_id == ALL_CAMERAS else [camera_id]
        try:
            start, end = day_bounds(date.fromisoformat(day))
        except ValueError as err:
            raise MediaSourceError("Invalid day") from err
        try:
            events = await entry.runtime_data.rpc.get_events(camera_ids, start, end)
        except CameraUiRpcError as err:
            raise MediaSourceError(str(err)) from err
        cameras = entry.runtime_data.coordinator.data
        children = []
        for event in sorted(events, key=lambda e: int(e["startTime"]), reverse=True):
            if not event.get("endTime"):
                continue
            title = f"{event_time(event['startTime'])} {event_labels(event)}"
            if not camera_ids:
                name = cameras.get(event["cameraId"], {}).get("name", event["cameraId"])
                title = f"{event_time(event['startTime'])} {name}: {event_labels(event)}"
            children.append(
                BrowseMediaSource(
                    domain=DOMAIN,
                    identifier=f"{entry.entry_id}/{event['cameraId']}/{day}/{event['id']}",
                    media_class=MediaClass.VIDEO,
                    media_content_type=MediaType.VIDEO,
                    title=title,
                    can_play=True,
                    can_expand=False,
                    thumbnail=f"{MEDIA_PATH}/{entry.entry_id}/thumb/{event['cameraId']}/{event['startTime']}/{event['id']}",
                )
            )
        return _directory(
            f"{entry.entry_id}/{camera_id}/{day}",
            _day_title(date.fromisoformat(day), dt_util.now().date()),
            children,
            children_class=MediaClass.VIDEO,
        )

    def _camera_title(self, entry: CameraUiConfigEntry, camera_id: str) -> str:
        if camera_id == ALL_CAMERAS:
            return "All cameras"
        camera = entry.runtime_data.coordinator.data.get(camera_id, {})
        return str(camera.get("name", camera_id))


def _loaded_entries(hass: HomeAssistant) -> list[CameraUiConfigEntry]:
    return [
        entry for entry in hass.config_entries.async_entries(DOMAIN) if entry.state is ConfigEntryState.LOADED
    ]


def _day_title(day: date, today: date) -> str:
    if day == today:
        return "Today"
    if day == today - timedelta(days=1):
        return "Yesterday"
    return day.strftime("%A, %-d %B")


def _directory(
    identifier: str,
    title: str,
    children: list[BrowseMediaSource] | None = None,
    *,
    thumbnail: str | None = None,
    children_class: MediaClass = MediaClass.DIRECTORY,
) -> BrowseMediaSource:
    return BrowseMediaSource(
        domain=DOMAIN,
        identifier=identifier,
        media_class=MediaClass.DIRECTORY,
        media_content_type=MediaType.VIDEO,
        title=title,
        can_play=False,
        can_expand=True,
        thumbnail=thumbnail,
        children=children,
        children_media_class=children_class,
    )


def _leaf(identifier: str, title: str) -> BrowseMediaSource:
    return BrowseMediaSource(
        domain=DOMAIN,
        identifier=identifier,
        media_class=MediaClass.DIRECTORY,
        media_content_type=MediaType.VIDEO,
        title=title,
        can_play=False,
        can_expand=False,
    )
