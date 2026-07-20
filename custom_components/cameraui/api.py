from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import aiohttp
import socketio

_LOGGER = logging.getLogger(__name__)


class CameraUiApiError(Exception):
    """Raised when the camera.ui API returns an error."""


class CameraUiAuthError(CameraUiApiError):
    """Raised when authentication fails."""


class CameraUiClient:
    def __init__(self, host: str, port: int, token: str, session: aiohttp.ClientSession) -> None:
        self._host = host
        self._port = port
        self._token = token
        self._session = session
        self._sio: socketio.AsyncClient | None = None
        self._detection_callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._connection_callbacks: list[Callable[[bool], None]] = []
        self._sensor_callbacks: list[Callable[[dict[str, Any]], None]] = []

    @property
    def base_url(self) -> str:
        return f"https://{self._host}:{self._port}"

    @property
    def events_connected(self) -> bool:
        return bool(self._sio and self._sio.connected)

    async def _request(self, method: str, path: str, **kwargs: Any) -> aiohttp.ClientResponse:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token}"
        try:
            response = await self._session.request(
                method, f"{self.base_url}/api{path}", headers=headers, ssl=False, **kwargs
            )
        except aiohttp.ClientError as err:
            raise CameraUiApiError(f"Request to {path} failed: {err}") from err
        if response.status in (401, 403):
            raise CameraUiAuthError(f"Authentication failed ({response.status})")
        if response.status >= 400:
            raise CameraUiApiError(f"Request to {path} returned {response.status}")
        return response

    async def get_info(self) -> dict[str, Any]:
        try:
            response = await self._session.get(f"{self.base_url}/api/", ssl=False)
        except aiohttp.ClientError as err:
            raise CameraUiApiError(f"Cannot reach server: {err}") from err
        if response.status >= 400:
            raise CameraUiApiError(f"Server info returned {response.status}")
        return await response.json()

    async def validate(self) -> dict[str, Any]:
        info = await self.get_info()
        await self.get_cameras()
        return info

    async def get_cameras(self) -> list[dict[str, Any]]:
        response = await self._request("GET", "/cameras", params={"pageSize": "-1"})
        data = await response.json()
        return data.get("result", [])

    async def get_snapshot(self, camera_name: str, force_new: bool = False) -> bytes:
        params = {"forceNew": "true"} if force_new else None
        response = await self._request("GET", f"/cameras/{camera_name}/snapshot", params=params)
        return await response.read()

    async def get_rtsp_sources(self, camera_name: str) -> list[dict[str, Any]]:
        response = await self._request("GET", f"/cameras/{camera_name}/rtsp")
        data = await response.json()
        return data.get("sources", [])

    async def get_sensors(self, camera_name: str) -> list[dict[str, Any]]:
        response = await self._request("GET", f"/cameras/{camera_name}/sensors")
        data = await response.json()
        return data.get("sensors", [])

    async def command_sensor(self, camera_name: str, stable_id: str, property_name: str, value: Any) -> None:
        await self._request(
            "POST",
            f"/cameras/{camera_name}/sensors/{stable_id}/command",
            json={"property": property_name, "value": value},
        )

    def on_detection(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._detection_callbacks.append(callback)

    def on_connection(self, callback: Callable[[bool], None]) -> None:
        self._connection_callbacks.append(callback)

    def on_sensor(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._sensor_callbacks.append(callback)

    async def connect_events(self) -> None:
        if self._sio:
            return

        sio = socketio.AsyncClient(http_session=self._session, reconnection=True, reconnection_delay=5)
        self._sio = sio

        @sio.event(namespace="/events")
        async def connect() -> None:
            await sio.emit("subscribe", {"cameraIds": "all"}, namespace="/events")
            for callback in self._connection_callbacks:
                callback(True)

        @sio.event(namespace="/events")
        async def disconnect() -> None:
            for callback in self._connection_callbacks:
                callback(False)

        @sio.on("detection", namespace="/events")
        async def detection(message: dict[str, Any]) -> None:
            for callback in self._detection_callbacks:
                callback(message)

        @sio.on("sensor", namespace="/events")
        async def sensor(message: dict[str, Any]) -> None:
            for callback in self._sensor_callbacks:
                callback(message)

        try:
            await sio.connect(
                self.base_url,
                socketio_path="/api/socket.io",
                namespaces=["/events"],
                auth={"token": f"Bearer {self._token}"},
                transports=["websocket"],
            )
        except socketio.exceptions.ConnectionError as err:
            self._sio = None
            raise CameraUiApiError(f"Event socket connection failed: {err}") from err

    async def disconnect_events(self) -> None:
        if self._sio:
            sio = self._sio
            self._sio = None
            await sio.disconnect()
