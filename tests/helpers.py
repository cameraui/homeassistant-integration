from __future__ import annotations

import asyncio
import ssl
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any

from aiohttp import web
from homeassistant.const import CONF_HOST, CONF_PORT
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cameraui.const import CONF_TOKEN, DOMAIN

TOKEN = "cui_SECRET_INTEGRATION_TOKEN"


async def serve(
    app: web.Application,
    ssl_context: ssl.SSLContext | None = None,
    port: int = 0,
    shutdown_timeout: float = 60.0,
    handler_cancellation: bool = False,
) -> tuple[web.AppRunner, int]:
    runner = web.AppRunner(app, shutdown_timeout=shutdown_timeout, handler_cancellation=handler_cancellation)
    await runner.setup()
    await web.TCPSite(runner, "127.0.0.1", port, ssl_context=ssl_context).start()
    return runner, runner.addresses[0][1]


@asynccontextmanager
async def mute_server(port: int = 0) -> AsyncIterator[tuple[int, asyncio.Event]]:
    # accepts connections and never answers, the event is set on the first one
    writers: list[asyncio.StreamWriter] = []
    dialed = asyncio.Event()

    async def accept(_reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        writers.append(writer)
        dialed.set()

    server = await asyncio.start_server(accept, "127.0.0.1", port)
    try:
        yield server.sockets[0].getsockname()[1], dialed
    finally:
        for writer in writers:
            writer.close()
        server.close()
        await server.wait_closed()


async def wait_until(predicate: Callable[[], bool], timeout: float = 5) -> None:
    async with asyncio.timeout(timeout):
        while not predicate():
            await asyncio.sleep(0.05)


def make_entry(port: int = 3443) -> MockConfigEntry:
    return MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "127.0.0.1", CONF_PORT: port, CONF_TOKEN: TOKEN})


class FakeEventsClient:
    def __init__(self) -> None:
        self.base_url = "https://127.0.0.1:3443"
        self.sensors: dict[str, dict[str, Any]] = {}
        self._detection: list[Callable[[dict[str, Any]], None]] = []
        self._connection: list[Callable[[bool], None]] = []
        self._subscribed: list[Callable[[list[str] | None], None]] = []
        self._sensor: list[Callable[[dict[str, Any]], None]] = []

    def on_detection(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._detection.append(callback)

    def on_connection(self, callback: Callable[[bool], None]) -> None:
        self._connection.append(callback)

    def on_subscribed(self, callback: Callable[[list[str] | None], None]) -> None:
        self._subscribed.append(callback)

    def on_sensor(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._sensor.append(callback)

    def detection(self, message: dict[str, Any]) -> None:
        for callback in self._detection:
            callback(message)

    def connection(self, connected: bool) -> None:
        for callback in self._connection:
            callback(connected)

    # the subscribe ack, active is None for servers that do not report running detections
    def subscribed(self, active: list[str] | None) -> None:
        for callback in self._subscribed:
            callback(active)
        self.connection(True)

    def sensor(self, message: dict[str, Any]) -> None:
        for callback in self._sensor:
            callback(message)

    async def get_sensors(self) -> list[dict[str, Any]]:
        return list(self.sensors.values())

    async def get_sensor(self, sensor_id: str) -> dict[str, Any] | None:
        return self.sensors.get(sensor_id)
