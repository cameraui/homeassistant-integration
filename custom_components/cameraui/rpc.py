from __future__ import annotations

import asyncio
import contextlib
import logging
import secrets
import time
from collections import OrderedDict
from typing import Any

from camera_ui_rpc import create_rpc_client
from camera_ui_rpc.types import RPCClient
from homeassistant.util.ssl import client_context_no_verify
from yarl import URL

_LOGGER = logging.getLogger(__name__)

NVR_PLUGIN = "@camera.ui/camera-ui-nvr"
CORE_MANAGER_RPC = "coreManager.rpc"
IDLE_TIMEOUT = 5 * 60
CONNECT_TIMEOUT = 15
PLUGIN_CHECK_INTERVAL = 60
THUMBNAIL_CACHE_SIZE = 300
EVENT_PAGE = 200
EVENT_LIMIT = 600


class CameraUiRpcError(Exception):
    """Raised when an RPC call to camera.ui fails."""


class CameraUiRpc:
    """One lazy NATS-over-WebSocket connection per config entry, closed again when idle."""

    def __init__(self, host: str, port: int, token: str) -> None:
        self._host = host
        self._port = port
        self._token = token
        self._client: RPCClient | None = None
        self._connecting: asyncio.Task[RPCClient] | None = None
        self._idle_handle: asyncio.TimerHandle | None = None
        self._nvr_id: str | None = None
        self._nvr_checked = 0.0
        self._thumbnails: OrderedDict[str, bytes] = OrderedDict()

    async def nvr_plugin_id(self) -> str | None:
        if time.monotonic() - self._nvr_checked < PLUGIN_CHECK_INTERVAL:
            return self._nvr_id
        client = await self._ensure()
        try:
            info = await client.create_proxy(CORE_MANAGER_RPC).getPlugin(NVR_PLUGIN)
        except Exception as err:  # noqa: BLE001
            raise CameraUiRpcError(f"Plugin lookup failed: {err}") from err
        self._nvr_id = info["id"] if info and info.get("running") is not False else None
        self._nvr_checked = time.monotonic()
        return self._nvr_id

    async def get_events(
        self, camera_ids: list[str] | None, start_ms: int, end_ms: int, limit: int = EVENT_LIMIT
    ) -> list[dict[str, Any]]:
        nvr = await self._nvr()
        events: list[dict[str, Any]] = []
        seen: set[str] = set()
        before: int | None = None
        while len(events) < limit:
            options: dict[str, Any] = {
                "startMs": start_ms,
                "endMs": end_ms,
                "limit": min(EVENT_PAGE, limit - len(events)),
                "hasRecording": True,
                "hasDetections": True,
                "state": "ended",
            }
            if before:
                options["before"] = before
            try:
                if camera_ids:
                    result = await nvr.getCameraEvents(camera_ids, options)
                else:
                    result = await nvr.getEvents(options)
            except Exception as err:  # noqa: BLE001
                raise CameraUiRpcError(f"Event query failed: {err}") from err
            page = result.get("events") or []
            fresh = [event for event in page if event.get("id") not in seen]
            seen.update(event.get("id") for event in fresh)
            events.extend(fresh)
            # events reaching in from before the window come with every page and
            # sort last, so page on the oldest start inside the window
            cursor = min(
                (event["startTime"] for event in page if event.get("startTime", 0) >= start_ms), default=None
            )
            if not result.get("hasMore") or cursor is None or not fresh:
                break
            before = cursor
        return events

    async def get_event_thumbnail(self, camera_id: str, start_ms: int, event_id: str) -> bytes | None:
        cached = self._thumbnails.get(event_id)
        if cached is not None:
            self._thumbnails.move_to_end(event_id)
            return cached
        nvr = await self._nvr()
        try:
            # only the picture shown here; NVRs without the keys argument ignore it and send all
            thumbnails = await nvr.getEventThumbnails(camera_id, start_ms, event_id, ["event"])
        except Exception as err:  # noqa: BLE001
            raise CameraUiRpcError(f"Thumbnail failed: {err}") from err
        image = thumbnails.get("event") if thumbnails else None
        if not image:
            return None
        self._thumbnails[event_id] = image
        while len(self._thumbnails) > THUMBNAIL_CACHE_SIZE:
            self._thumbnails.popitem(last=False)
        return bytes(image)

    async def export_event(self, camera_id: str, start_ms: int, end_ms: int, source_role: str) -> str:
        nvr = await self._nvr()
        try:
            result = await nvr.nvrExport(
                camera_id, start_ms * 1000, end_ms * 1000, {"sourceRole": source_role}
            )
        except Exception as err:  # noqa: BLE001
            raise CameraUiRpcError(f"Export failed: {err}") from err
        url = result.get("url") if result else None
        if not url:
            raise CameraUiRpcError("Export returned no download url")
        return str(url)

    async def close(self) -> None:
        connecting, self._connecting = self._connecting, None
        if connecting:
            connecting.cancel()
            await asyncio.wait([connecting])
        await self._drop_client()

    async def _drop_client(self) -> None:
        if self._idle_handle:
            self._idle_handle.cancel()
            self._idle_handle = None
        client, self._client = self._client, None
        if client:
            with contextlib.suppress(Exception):
                await client.disconnect()

    async def _nvr(self) -> Any:
        plugin_id = await self.nvr_plugin_id()
        if not plugin_id:
            raise CameraUiRpcError("NVR plugin not available")
        client = await self._ensure()
        return client.create_proxy(f"plugin.{plugin_id}.child.rpc")

    # callers share one connect, so a caller that gives up does not abort it for the others
    async def _ensure(self) -> RPCClient:
        if self._client and self._client.is_connected:
            self._touch()
            return self._client
        if not self._connecting:
            self._connecting = asyncio.get_running_loop().create_task(self._connect())
        connecting = self._connecting
        try:
            client = await asyncio.shield(connecting)
        except asyncio.CancelledError:
            current = asyncio.current_task()
            if connecting.cancelled() and current and not current.cancelling():
                raise CameraUiRpcError("Connection closed") from None
            raise
        self._touch()
        return client

    async def _connect(self) -> RPCClient:
        try:
            await self._drop_client()
            conn_id = secrets.token_urlsafe(12)
            url = URL.build(
                scheme="wss",
                host=self._host,
                port=self._port,
                path="/api/proxy",
                query={"token": self._token, "connId": conn_id},
            )
            client = create_rpc_client(
                {
                    "servers": [str(url)],
                    "name": "homeassistant",
                    "conn_id": conn_id,
                    "tls": client_context_no_verify(),
                    "timeout": 15000,
                    "connect_timeout": 10000,
                    "reconnect": False,
                }
            )
            try:
                async with asyncio.timeout(CONNECT_TIMEOUT):
                    await client.connect()
            except BaseException as err:
                with contextlib.suppress(Exception):
                    await client.disconnect()
                if isinstance(err, Exception):
                    raise CameraUiRpcError(
                        f"Cannot connect to the camera.ui RPC bus: {str(err) or type(err).__name__}"
                    ) from err
                raise
            self._client = client
            return client
        finally:
            if self._connecting is asyncio.current_task():
                self._connecting = None

    def _touch(self) -> None:
        if self._idle_handle:
            self._idle_handle.cancel()
        loop = asyncio.get_running_loop()
        self._idle_handle = loop.call_later(IDLE_TIMEOUT, lambda: loop.create_task(self._drop_client()))
