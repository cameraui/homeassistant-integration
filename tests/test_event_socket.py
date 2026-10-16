from __future__ import annotations

import asyncio
import ssl
import time
from typing import Any
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
import socketio
from aiohttp import web
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

import custom_components.cameraui as integration
from custom_components.cameraui import api
from custom_components.cameraui.api import CameraUiClient

from .helpers import TOKEN, make_entry, mute_server, serve, wait_until


async def start_events_server(
    tls: ssl.SSLContext, connects: list[str], port: int = 0
) -> tuple[web.AppRunner, int, socketio.AsyncServer]:
    sio = socketio.AsyncServer(async_mode="aiohttp")
    app = web.Application()
    sio.attach(app, socketio_path="/api/socket.io")

    async def me(request: web.Request) -> web.Response:
        return web.json_response({"role": "viewer"})

    app.router.add_get("/api/auth/me", me)

    @sio.event(namespace="/events")
    async def connect(sid: str, environ: Any, auth: Any) -> None:
        connects.append(sid)

    # a short drain drops the client at once on stop, like a crashed server
    runner, bound = await serve(app, tls, port, shutdown_timeout=0.2)
    return runner, bound, sio


async def stop_events_server(runner: web.AppRunner, sio: socketio.AsyncServer) -> None:
    await sio.shutdown()
    await runner.cleanup()
    # the server's engine.io ping loops outlive shutdown()
    for task in asyncio.all_tasks():
        if task.get_coro().__qualname__.startswith("AsyncSocket."):  # type: ignore[union-attr]
            task.cancel()
    await asyncio.sleep(0)


async def connect_client(
    session: aiohttp.ClientSession, port: int
) -> tuple[CameraUiClient, socketio.AsyncClient]:
    client = CameraUiClient("127.0.0.1", port, TOKEN, session)
    await client.connect_events()
    sio = client._sio
    assert sio is not None
    # retry every 0.2 s instead of every 5 s
    sio.reconnection_delay = 0.1
    sio.reconnection_delay_max = 0.2
    sio.randomization_factor = 0
    return client, sio


def reconnect_loops() -> list[asyncio.Task[Any]]:
    return [
        task
        for task in asyncio.all_tasks()
        if not task.done() and "_handle_reconnect" in task.get_coro().__qualname__  # type: ignore[union-attr]
    ]


async def test_unload_during_reconnect_stops_the_event_socket(
    socket_enabled: None, server_tls: ssl.SSLContext
) -> None:
    connects: list[str] = []
    runner, port, server = await start_events_server(server_tls, connects)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        client, _ = await connect_client(session, port)
        assert len(connects) == 1

        await stop_events_server(runner, server)
        await wait_until(lambda: not client.events_connected)

        await client.disconnect_events()

        runner, _, server = await start_events_server(server_tls, connects, port)
        try:
            await asyncio.sleep(1.5)
            assert len(connects) == 1
        finally:
            await stop_events_server(runner, server)


async def test_unload_during_a_stalled_reconnect_dial_returns_quickly(
    socket_enabled: None, server_tls: ssl.SSLContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(api, "EVENTS_SHUTDOWN_TIMEOUT", 0.5)
    connects: list[str] = []
    runner, port, server = await start_events_server(server_tls, connects)
    # the default session gives a dial 30 s, like HA's shared session
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        client, sio = await connect_client(session, port)
        await stop_events_server(runner, server)

        # the host stops answering, the next reconnect hangs in the TLS handshake
        async with mute_server(port) as (_, dialing):
            await asyncio.wait_for(dialing.wait(), 5)
            started = time.monotonic()
            await client.disconnect_events()
            assert time.monotonic() - started < 3
            assert not sio.connected
            assert sio not in socketio.base_client.reconnecting_clients
            assert reconnect_loops() == []


async def test_unload_while_connected_closes_the_event_socket(
    socket_enabled: None, server_tls: ssl.SSLContext
) -> None:
    connects: list[str] = []
    runner, port, server = await start_events_server(server_tls, connects)
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            client, sio = await connect_client(session, port)
            await client.disconnect_events()
            assert not client.events_connected
            assert not sio.connected
            assert reconnect_loops() == []
    finally:
        await stop_events_server(runner, server)


@pytest.mark.parametrize(
    ("ack", "active"),
    [({"subscribed": "all", "active": ["cam1"]}, ["cam1"]), ({"subscribed": "all"}, None)],
)
async def test_connected_is_reported_after_the_subscribe_ack(
    socket_enabled: None, server_tls: ssl.SSLContext, ack: dict[str, Any], active: list[str] | None
) -> None:
    connects: list[str] = []
    runner, port, server = await start_events_server(server_tls, connects)

    @server.on("subscribe", namespace="/events")
    async def subscribe(sid: str, payload: Any) -> dict[str, Any]:
        return ack

    calls: list[tuple[str, Any]] = []
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            client = CameraUiClient("127.0.0.1", port, TOKEN, session)
            client.on_subscribed(lambda running: calls.append(("subscribed", running)))
            client.on_connection(lambda connected: calls.append(("connection", connected)))
            await client.connect_events()
            await wait_until(lambda: len(calls) == 2)
            assert calls == [("subscribed", active), ("connection", True)]
            await client.disconnect_events()
    finally:
        await stop_events_server(runner, server)


async def test_failed_setup_after_the_socket_connected_closes_it(hass: HomeAssistant) -> None:
    hass.data[integration.DATA_GLOBAL_SETUP] = True
    entry = make_entry()
    entry.add_to_hass(hass)
    entry.mock_state(hass, ConfigEntryState.SETUP_IN_PROGRESS)
    disconnect = AsyncMock()

    with (
        patch.object(CameraUiClient, "get_cameras", AsyncMock(return_value=[])),
        patch.object(CameraUiClient, "get_info", AsyncMock(return_value={"version": "9.9.9"})),
        patch.object(CameraUiClient, "cards_bundle_tag", AsyncMock(return_value=None)),
        patch.object(CameraUiClient, "connect_events", AsyncMock()),
        patch.object(CameraUiClient, "disconnect_events", disconnect),
        patch.object(
            integration.CameraUiSensorManager, "async_setup", AsyncMock(side_effect=RuntimeError("boom"))
        ),
        pytest.raises(RuntimeError),
    ):
        await integration.async_setup_entry(hass, entry)

    disconnect.assert_awaited_once()
