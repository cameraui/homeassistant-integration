from __future__ import annotations

import asyncio
import random
import tracemalloc
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import aiohttp
import pytest
from aiohttp import hdrs, web
from homeassistant.components.http import KEY_HASS
from homeassistant.components.media_source import MediaSourceItem, PlayMedia
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cameraui import clips, media_source, views
from custom_components.cameraui.const import DOMAIN
from custom_components.cameraui.rpc import CameraUiRpc, CameraUiRpcError

from .helpers import make_entry, serve, wait_until

DAY = "2026-10-04"
CAMERA = "cam-1"
MIB = 1024 * 1024


@dataclass
class FakeNvr:
    events: list[dict[str, Any]] = field(default_factory=list)
    queries: list[dict[str, Any]] = field(default_factory=list)
    thumbnail_calls: list[tuple[Any, ...]] = field(default_factory=list)
    pictures: dict[str, Any] = field(default_factory=dict)

    async def getCameraEvents(self, camera_ids: list[str], options: dict[str, Any]) -> dict[str, Any]:
        self.queries.append(dict(options))
        upper = min(options["endMs"], options.get("before") or options["endMs"])
        hits = sorted(
            (
                event
                for event in self.events
                if event["cameraId"] in camera_ids and options["startMs"] <= event["startTime"] <= upper
            ),
            key=lambda event: event["startTime"],
            reverse=True,
        )
        limit = options["limit"]
        return {"events": hits[:limit], "hasMore": len(hits) > limit}

    async def nvrExport(
        self, camera_id: str, start_us: int, end_us: int, options: dict[str, Any]
    ) -> dict[str, Any]:
        return {"url": f"/export/{camera_id}.mp4"}

    async def getEventThumbnails(self, *args: Any) -> dict[str, Any]:
        self.thumbnail_calls.append(args)
        return self.pictures


class FakeRpc(CameraUiRpc):
    def __init__(self, nvr: FakeNvr) -> None:
        super().__init__("127.0.0.1", 1, "token")
        self.nvr = nvr

    async def _nvr(self) -> Any:
        return self.nvr


@dataclass
class Export:
    body: bytes = field(default_factory=lambda: random.Random(3).randbytes(2 * MIB))
    chunk: int = 64 * 1024
    delay: float = 0
    fail_after: int | None = None
    sent: int = 0

    async def handle(self, request: web.Request) -> web.StreamResponse:
        response = web.StreamResponse(headers={hdrs.CONTENT_LENGTH: str(len(self.body))})
        await response.prepare(request)
        for offset in range(0, len(self.body), self.chunk):
            if self.fail_after is not None and offset >= self.fail_after:
                assert request.transport is not None
                request.transport.abort()
                return response
            await response.write(self.body[offset : offset + self.chunk])
            self.sent = offset + self.chunk
            if self.delay:
                await asyncio.sleep(self.delay)
        await response.write_eof()
        return response


@dataclass
class Media:
    hass: HomeAssistant
    entry: MockConfigEntry
    nvr: FakeNvr
    export: Export
    cache: clips.ClipCache
    port: int
    session: aiohttp.ClientSession

    def add_events(self, count: int) -> list[dict[str, Any]]:
        day_start, _ = clips.day_bounds(date.fromisoformat(DAY))
        added = [
            {
                "id": f"event-{len(self.nvr.events) + i:04d}",
                "cameraId": CAMERA,
                "startTime": day_start + 60_000 * (len(self.nvr.events) + i + 1),
                "endTime": day_start + 60_000 * (len(self.nvr.events) + i + 1) + 30_000,
                "types": ["person"],
            }
            for i in range(count)
        ]
        self.nvr.events.extend(added)
        return added

    def identifier(self, event: dict[str, Any], with_start: bool = True) -> str:
        identifier = f"{self.entry.entry_id}/{CAMERA}/{DAY}/{event['id']}"
        return f"{identifier}/{event['startTime']}" if with_start else identifier

    async def resolve(self, identifier: str) -> PlayMedia:
        source = media_source.CameraUiMediaSource(self.hass)
        return await source.async_resolve_media(MediaSourceItem(self.hass, DOMAIN, identifier, None))

    async def get(self, url: str, byte_range: str | None = None) -> tuple[int, bytes]:
        headers = {hdrs.RANGE: byte_range} if byte_range else {}
        async with self.session.get(f"http://127.0.0.1:{self.port}{url}", headers=headers) as res:
            return res.status, await res.read()

    async def open(self, event: dict[str, Any]) -> Path | Any:
        return await self.cache.open(CAMERA, event["id"], event["startTime"], event["endTime"])


@pytest.fixture
async def media(hass: HomeAssistant, socket_enabled: None, tmp_path: Path) -> AsyncIterator[Media]:
    hass.config.config_dir = str(tmp_path)
    export = Export()
    upstream = web.Application()
    upstream.router.add_get("/export/{name}", export.handle)
    up_runner, up_port = await serve(upstream)

    nvr = FakeNvr()
    rpc = FakeRpc(nvr)
    entry = make_entry()
    entry.add_to_hass(hass)
    cache = clips.ClipCache(hass, entry.entry_id, rpc, f"http://127.0.0.1:{up_port}", "low")
    entry.runtime_data = SimpleNamespace(
        rpc=rpc, clips=cache, coordinator=SimpleNamespace(data={CAMERA: {"_id": CAMERA, "name": "Front"}})
    )
    entry.mock_state(hass, ConfigEntryState.LOADED)

    view = views.CameraUiMediaView()

    async def handler(request: web.Request) -> web.StreamResponse:
        return await view.get(request, **request.match_info)

    app = web.Application()
    app[KEY_HASS] = hass
    app.router.add_get(views.CameraUiMediaView.url, handler)
    # like Home Assistant's http server, a browser that goes away cancels its request
    runner, port = await serve(app, handler_cancellation=True)
    session = aiohttp.ClientSession()
    try:
        yield Media(hass, entry, nvr, export, cache, port, session)
    finally:
        await session.close()
        await runner.cleanup()
        await up_runner.cleanup()
        await hass.async_block_till_done(wait_background_tasks=True)


async def collect(ready: Path | Any) -> bytes:
    if isinstance(ready, Path):
        return ready.read_bytes()
    return b"".join([chunk async for chunk in ready.stream()])


async def test_browsed_events_carry_their_start(media: Media) -> None:
    events = media.add_events(3)
    source = media_source.CameraUiMediaSource(media.hass)
    day = await source.async_browse_media(
        MediaSourceItem(media.hass, DOMAIN, f"{media.entry.entry_id}/{CAMERA}/{DAY}", None)
    )
    assert day.children is not None
    assert [child.identifier for child in day.children] == [media.identifier(e) for e in reversed(events)]


async def test_resolve_asks_only_for_events_starting_with_the_clip(media: Media) -> None:
    media.add_events(50)
    event = media.nvr.events[20]

    play = await media.resolve(media.identifier(event))

    assert [(query["startMs"], query["endMs"]) for query in media.nvr.queries] == [
        (event["startTime"], event["startTime"])
    ]
    assert play.url.endswith(f"/clip/{CAMERA}/{DAY}/{event['id']}/{event['startTime']}")


async def test_playing_and_seeking_a_clip_asks_the_nvr_once(media: Media) -> None:
    [event] = media.add_events(1)

    play = await media.resolve(media.identifier(event))
    status, body = await media.get(play.url)
    assert (status, body) == (200, media.export.body)
    for start in (MIB, 4096, 0):
        status, body = await media.get(play.url, f"bytes={start}-")
        assert (status, body) == (206, media.export.body[start:])
    await media.resolve(media.identifier(event))

    assert len(media.nvr.queries) == 1


async def test_clip_of_a_busy_day_plays_past_the_newest_600_events(media: Media) -> None:
    oldest = media.add_events(700)[0]

    play = await media.resolve(media.identifier(oldest))

    assert await media.get(play.url) == (200, media.export.body)


async def test_identifier_without_start_still_plays(media: Media) -> None:
    media.add_events(5)
    event = media.nvr.events[2]

    play = await media.resolve(media.identifier(event, with_start=False))

    assert await media.get(play.url) == (200, media.export.body)


async def test_clip_url_without_start_still_plays(media: Media) -> None:
    [event] = media.add_events(1)

    url = f"{clips.MEDIA_PATH}/{media.entry.entry_id}/clip/{CAMERA}/{DAY}/{event['id']}"

    assert await media.get(url) == (200, media.export.body)


async def test_clip_url_of_an_unknown_event_is_not_found(media: Media) -> None:
    [event] = media.add_events(1)

    url = f"{clips.MEDIA_PATH}/{media.entry.entry_id}/clip/{CAMERA}/{DAY}/missing/{event['startTime']}"

    assert (await media.get(url))[0] == 404


async def test_late_viewer_joins_the_running_export(media: Media) -> None:
    [event] = media.add_events(1)
    media.export.delay = 0.01

    first = await media.open(event)
    reading = asyncio.create_task(collect(first))
    await wait_until(lambda: media.export.sent >= len(media.export.body) // 2)
    second = await media.open(event)

    assert second is first
    assert await collect(second) == media.export.body
    assert await reading == media.export.body


async def test_running_export_keeps_the_clip_out_of_memory(media: Media) -> None:
    [event] = media.add_events(1)
    media.export.body = random.Random(4).randbytes(32 * MIB)
    media.export.chunk = 256 * 1024

    tracemalloc.start()
    try:
        ready = await media.open(event)
        received = 0
        async for chunk in ready.stream():
            received += len(chunk)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()

    assert received == len(media.export.body)
    assert peak < 8 * MIB


async def test_viewer_that_starts_after_the_export_finished_gets_the_clip(media: Media) -> None:
    [event] = media.add_events(1)

    ready = await media.open(event)
    await asyncio.shield(ready.done)

    assert await collect(ready) == media.export.body


async def test_failed_export_fails_every_viewer_and_leaves_no_file(media: Media) -> None:
    [event] = media.add_events(1)
    media.export.fail_after = 256 * 1024

    ready = await media.open(event)
    with pytest.raises(CameraUiRpcError):
        await collect(ready)
    with pytest.raises(CameraUiRpcError):
        await collect(ready)

    folder = Path(media.hass.config.path(".cache", "cameraui", "clips", media.entry.entry_id))
    assert [path.name for path in folder.iterdir()] == []


async def test_abandoned_seek_leaves_the_export_running(media: Media) -> None:
    [event] = media.add_events(1)
    media.export.delay = 0.01

    first = await media.open(event)
    seek = asyncio.create_task(first.file())
    await wait_until(lambda: media.export.sent > 0)
    seek.cancel()

    assert await collect(first) == media.export.body
    assert (await first.file()).read_bytes() == media.export.body


async def test_seek_the_browser_gives_up_on_leaves_the_export_running(media: Media) -> None:
    [event] = media.add_events(1)
    media.export.delay = 0.01

    play = await media.resolve(media.identifier(event))
    first = await media.cache.cached(event["id"])
    with pytest.raises(TimeoutError):
        await media.session.get(
            f"http://127.0.0.1:{media.port}{play.url}",
            headers={hdrs.RANGE: "bytes=4096-"},
            timeout=aiohttp.ClientTimeout(total=0.1),
        )

    assert await collect(first) == media.export.body
    assert await media.get(play.url, "bytes=4096-") == (206, media.export.body[4096:])


async def test_thumbnail_asks_only_for_the_event_picture(media: Media) -> None:
    [event] = media.add_events(1)
    media.nvr.pictures = {"event": b"jpeg", "selected": True}

    image = await media.entry.runtime_data.rpc.get_event_thumbnail(CAMERA, event["startTime"], event["id"])

    assert image == b"jpeg"
    assert media.nvr.thumbnail_calls == [(CAMERA, event["startTime"], event["id"], ["event"])]


async def test_thumbnail_from_an_nvr_that_sends_every_picture(media: Media) -> None:
    [event] = media.add_events(1)
    media.nvr.pictures = {"event": b"jpeg", "strips": {"0": b"strip"}, "cards": {"0": b"card"}}

    image = await media.entry.runtime_data.rpc.get_event_thumbnail(CAMERA, event["startTime"], event["id"])

    assert image == b"jpeg"
