from __future__ import annotations

import asyncio
import logging
import shutil
import time
from collections.abc import AsyncIterator
from datetime import date, timedelta
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

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


class _Download:
    """One running export: chunks are kept until the file is complete so late viewers can join."""

    def __init__(self) -> None:
        self.chunks: list[bytes] = []
        self.done: asyncio.Future[Path] = asyncio.get_running_loop().create_future()
        self._changed = asyncio.Event()

    def push(self, chunk: bytes) -> None:
        self.chunks.append(chunk)
        self._wake()

    def finish(self, result: Path | BaseException) -> None:
        if isinstance(result, BaseException):
            self.done.set_exception(result)
        else:
            self.done.set_result(result)
        self._wake()

    async def stream(self) -> AsyncIterator[bytes]:
        index = 0
        while True:
            while index < len(self.chunks):
                yield self.chunks[index]
                index += 1
            if self.done.done():
                self.done.result()
                return
            await self._changed.wait()

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
        self._downloads: dict[str, _Download] = {}

    async def wipe(self) -> None:
        await self._hass.async_add_executor_job(self._wipe)

    async def get(self, camera_id: str, event_id: str, start_ms: int, end_ms: int) -> Path:
        """The complete clip file, waiting for a running export."""
        ready = await self.open(camera_id, event_id, start_ms, end_ms)
        return ready if isinstance(ready, Path) else await ready.done

    async def open(self, camera_id: str, event_id: str, start_ms: int, end_ms: int) -> Path | _Download:
        """The cached file, or the export in progress to stream from while it lands on disk."""
        path = self._dir / f"{event_id}.mp4"
        if await self._hass.async_add_executor_job(self._fresh, path):
            return path
        download = self._downloads.get(event_id)
        if download is None:
            download = _Download()
            self._downloads[event_id] = download
            self._hass.async_create_background_task(
                self._run(download, path, event_id, camera_id, start_ms, end_ms), f"cameraui clip {event_id}"
            )
        return download

    async def _run(
        self, download: _Download, path: Path, event_id: str, camera_id: str, start_ms: int, end_ms: int
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
        self, download: _Download, path: Path, camera_id: str, start_ms: int, end_ms: int
    ) -> None:
        url = await self._rpc.export_event(camera_id, start_ms, end_ms, self._quality)
        session = async_get_clientsession(self._hass, verify_ssl=False)
        tmp = path.with_name(f"{path.name}.tmp")
        loop = asyncio.get_running_loop()
        timeout = aiohttp.ClientTimeout(total=600)
        try:
            async with session.get(f"{self._base_url}{url}", ssl=False, timeout=timeout) as res:
                if res.status != 200:
                    raise CameraUiRpcError(f"Export download returned {res.status}")
                handle = await loop.run_in_executor(None, self._open, tmp)
                try:
                    async for chunk in res.content.iter_chunked(CHUNK):
                        download.push(chunk)
                        await loop.run_in_executor(None, handle.write, chunk)
                finally:
                    await loop.run_in_executor(None, handle.close)
            await loop.run_in_executor(None, tmp.replace, path)
        except aiohttp.ClientError as err:
            raise CameraUiRpcError(f"Export download failed: {err}") from err
        finally:
            await loop.run_in_executor(None, partial(tmp.unlink, missing_ok=True))

    def _open(self, tmp: Path) -> BinaryIO:
        self._dir.mkdir(parents=True, exist_ok=True)
        return tmp.open("wb")

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
    entry: CameraUiConfigEntry, camera_id: str, day: str, event_id: str
) -> dict[str, Any] | None:
    try:
        start, end = day_bounds(date.fromisoformat(day))
    except ValueError:
        return None
    events = await entry.runtime_data.rpc.get_events([camera_id], start, end)
    return next((event for event in events if event.get("id") == event_id and event.get("endTime")), None)


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
