from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import shutil
import time
from collections.abc import AsyncGenerator
from datetime import date, timedelta
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util

from .rpc import CameraUiRpcError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import CameraUiConfigEntry
    from .rpc import CameraUiRpc

_LOGGER = logging.getLogger(__name__)

MEDIA_PATH = "/api/cameraui/media"
CLIP_TTL = 15 * 60
CLIP_CACHE_LIMIT = 200 * 1024 * 1024
CHUNK = 256 * 1024
READ_CHUNK = 1024 * 1024


class ClipDownload:
    """One running export: viewers read what already landed in the file, so late ones can join."""

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.written = 0
        self.created = False
        self.done: asyncio.Future[Path] = asyncio.get_running_loop().create_future()
        self._changed = asyncio.Event()

    def file_created(self) -> None:
        self.created = True
        self._wake()

    def wrote(self, size: int) -> None:
        self.written += size
        self._wake()

    def finish(self, result: Path | BaseException) -> None:
        if isinstance(result, BaseException):
            self.done.set_exception(result)
        else:
            self.done.set_result(result)
        self._wake()

    async def file(self) -> Path:
        """The complete clip file. A waiter that gives up leaves the export running for the others."""
        return await asyncio.shield(self.done)

    async def stream(self) -> AsyncGenerator[bytes]:
        loop = asyncio.get_running_loop()
        fd = await self._open()
        try:
            offset = 0
            while True:
                if offset < self.written:
                    size = min(READ_CHUNK, self.written - offset)
                    chunk = await loop.run_in_executor(None, os.pread, fd, size, offset)
                    if not chunk:
                        raise CameraUiRpcError("Clip file ended early")
                    offset += len(chunk)
                    yield chunk
                    continue
                if self.done.done():
                    self.done.result()
                    return
                await self._changed.wait()
        finally:
            os.close(fd)

    async def _open(self) -> int:
        loop = asyncio.get_running_loop()
        while not self.created and not self.done.done():
            await self._changed.wait()
        if not self.done.done():
            # the fd keeps reading the same file after the rename
            with contextlib.suppress(FileNotFoundError):
                return await loop.run_in_executor(None, os.open, self.tmp, os.O_RDONLY)
        path = await self.file()
        return await loop.run_in_executor(None, os.open, path, os.O_RDONLY)

    def _wake(self) -> None:
        self._changed.set()
        self._changed = asyncio.Event()


class ClipCache:
    """Event clips exported by the NVR, kept on the HA host so the player can seek."""

    def __init__(
        self, hass: HomeAssistant, entry_id: str, rpc: CameraUiRpc, base_url: str, quality: str
    ) -> None:
        self._hass = hass
        self._rpc = rpc
        self._base_url = base_url
        self._quality = quality
        self._dir = Path(hass.config.path(".cache", "cameraui", "clips", entry_id))
        self._downloads: dict[str, ClipDownload] = {}

    async def wipe(self) -> None:
        await self._hass.async_add_executor_job(self._wipe)

    async def cached(self, event_id: str) -> Path | ClipDownload | None:
        """The cached file or the export in progress, without asking the NVR."""
        path = self._dir / f"{event_id}.mp4"
        if await self._hass.async_add_executor_job(self._fresh, path):
            return path
        return self._downloads.get(event_id)

    async def open(self, camera_id: str, event_id: str, start_ms: int, end_ms: int) -> Path | ClipDownload:
        """The cached file, or the export in progress to stream from while it lands on disk."""
        ready = await self.cached(event_id)
        if ready is not None:
            return ready
        path = self._dir / f"{event_id}.mp4"
        download = ClipDownload(path.with_name(f"{path.name}.tmp"))
        self._downloads[event_id] = download
        self._hass.async_create_background_task(
            self._run(download, path, event_id, camera_id, start_ms, end_ms), f"cameraui clip {event_id}"
        )
        return download

    async def _run(
        self, download: ClipDownload, path: Path, event_id: str, camera_id: str, start_ms: int, end_ms: int
    ) -> None:
        try:
            await self._download(download, path, camera_id, start_ms, end_ms)
            download.finish(path)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Clip export failed: %s", err)
            download.finish(err if isinstance(err, CameraUiRpcError) else CameraUiRpcError(str(err)))
        finally:
            self._downloads.pop(event_id, None)
        await self._hass.async_add_executor_job(self._sweep)

    async def _download(
        self, download: ClipDownload, path: Path, camera_id: str, start_ms: int, end_ms: int
    ) -> None:
        url = await self._rpc.export_event(camera_id, start_ms, end_ms, self._quality)
        session = async_get_clientsession(self._hass, verify_ssl=False)
        tmp = download.tmp
        loop = asyncio.get_running_loop()
        timeout = aiohttp.ClientTimeout(total=600)
        try:
            async with session.get(f"{self._base_url}{url}", ssl=False, timeout=timeout) as res:
                if res.status != 200:
                    raise CameraUiRpcError(f"Export download returned {res.status}")
                fd = await loop.run_in_executor(None, self._create, tmp)
                download.file_created()
                try:
                    async for chunk in res.content.iter_chunked(CHUNK):
                        await loop.run_in_executor(None, _write_all, fd, chunk)
                        download.wrote(len(chunk))
                finally:
                    await loop.run_in_executor(None, os.close, fd)
            await loop.run_in_executor(None, tmp.replace, path)
        except aiohttp.ClientError as err:
            raise CameraUiRpcError(f"Export download failed: {err}") from err
        finally:
            await loop.run_in_executor(None, partial(tmp.unlink, missing_ok=True))

    def _create(self, tmp: Path) -> int:
        self._dir.mkdir(parents=True, exist_ok=True)
        return os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)

    def _fresh(self, path: Path) -> bool:
        if not path.is_file():
            return False
        if time.time() - path.stat().st_mtime > CLIP_TTL:
            path.unlink(missing_ok=True)
            return False
        path.touch()
        return True

    def _sweep(self) -> None:
        if not self._dir.is_dir():
            return
        files = sorted(self._dir.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True)
        total = 0
        now = time.time()
        for file in files:
            stat = file.stat()
            total += stat.st_size
            if now - stat.st_mtime > CLIP_TTL or total > CLIP_CACHE_LIMIT:
                file.unlink(missing_ok=True)

    def _wipe(self) -> None:
        shutil.rmtree(self._dir, ignore_errors=True)


async def async_find_event(
    entry: CameraUiConfigEntry, camera_id: str, day: str, event_id: str, start_ms: int | None = None
) -> dict[str, Any] | None:
    if start_ms is not None:
        # only the events starting at that moment instead of the whole day
        start = end = start_ms
    else:
        try:
            start, end = day_bounds(date.fromisoformat(day))
        except ValueError:
            return None
    events = await entry.runtime_data.rpc.get_events([camera_id], start, end)
    return next((event for event in events if event.get("id") == event_id and event.get("endTime")), None)


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        view = view[os.write(fd, view) :]


def day_bounds(day: date) -> tuple[int, int]:
    start = dt_util.start_of_local_day(day)
    end = dt_util.start_of_local_day(day + timedelta(days=1))
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def event_time(start_ms: int) -> str:
    return dt_util.as_local(dt_util.utc_from_timestamp(start_ms / 1000)).strftime("%H:%M")


def event_labels(event: dict[str, Any]) -> str:
    types = [str(label) for label in event.get("types") or []]
    labels = [label for label in types if label not in ("motion", "audio")] or types
    return ", ".join(labels) if labels else "event"
