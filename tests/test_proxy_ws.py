from __future__ import annotations

import asyncio
import logging
import ssl
from collections.abc import AsyncIterator, Awaitable, Callable

import aiohttp
import pytest
from aiohttp import web
from homeassistant.components.http import KEY_HASS
from homeassistant.core import HomeAssistant

from custom_components.cameraui import views

from .helpers import TOKEN, make_entry, serve

Upstream = Callable[[web.Request], Awaitable[web.StreamResponse]]
StartRelay = Callable[..., Awaitable[str]]


@pytest.fixture
async def relay(
    hass: HomeAssistant, socket_enabled: None, server_tls: ssl.SSLContext
) -> AsyncIterator[StartRelay]:
    runners: list[web.AppRunner] = []

    async def start(upstream: Upstream, path: str = "api/go2rtc/ws") -> str:
        up = web.Application()
        up.router.add_get("/{path:.*}", upstream)
        up_runner, up_port = await serve(up, server_tls)
        entry = make_entry(up_port)

        async def handler(request: web.Request) -> web.StreamResponse:
            return await views._proxy_ws(request, entry, path, TOKEN)

        proxy = web.Application()
        proxy[KEY_HASS] = hass
        proxy.router.add_get("/ws", handler)
        proxy_runner, proxy_port = await serve(proxy)
        runners.extend([proxy_runner, up_runner])
        return f"http://127.0.0.1:{proxy_port}/ws"

    yield start
    for runner in runners:
        await runner.cleanup()


async def browse(url: str) -> tuple[int | None, str | None, list[str]]:
    async with aiohttp.ClientSession() as session, session.ws_connect(url) as ws:
        texts: list[str] = []
        while True:
            msg = await asyncio.wait_for(ws.receive(), 5)
            if msg.type is aiohttp.WSMsgType.TEXT:
                texts.append(msg.data)
                continue
            reason = msg.extra if msg.type is aiohttp.WSMsgType.CLOSE else None
            return ws.close_code, reason, texts


async def refuse_upgrade(request: web.Request) -> web.StreamResponse:
    return web.Response(status=500, text="Internal Server Error")


async def test_failed_upstream_handshake_keeps_token_out_of_log(
    relay: StartRelay, caplog: pytest.LogCaptureFixture
) -> None:
    url = await relay(refuse_upgrade)
    with caplog.at_level(logging.DEBUG, logger="custom_components.cameraui"):
        await browse(url)
    # the fake upstream's own access log carries the query, only the integration's lines count
    ours = [r.getMessage() for r in caplog.records if r.name.startswith("custom_components.cameraui")]
    assert any("Proxy WebSocket" in line and "500" in line for line in ours)
    assert not any(TOKEN in line for line in ours)


async def test_failed_upstream_handshake_reaches_browser_as_upstream_lost(relay: StartRelay) -> None:
    code, _, _ = await browse(await relay(refuse_upgrade))
    assert code == 4500


@pytest.mark.parametrize(
    ("upstream_code", "browser_code"),
    [(4403, 4403), (4400, 4400), (4401, 4403), (4500, 4500), (1001, 1001), (1000, 1000)],
)
async def test_upstream_close_code_reaches_browser(
    relay: StartRelay, upstream_code: int, browser_code: int
) -> None:
    async def upstream(request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await ws.send_str("INFO {}")
        await ws.close(code=upstream_code, message=b"bye")
        return ws

    code, reason, texts = await browse(await relay(upstream))
    assert texts == ["INFO {}"]
    assert code == browser_code
    if upstream_code == browser_code:
        assert reason == "bye"
    else:
        assert reason is not None and "unauthorized" not in reason


async def test_upstream_drop_without_close_frame_reaches_browser_as_upstream_lost(relay: StartRelay) -> None:
    async def upstream(request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await ws.send_str("INFO {}")
        await asyncio.sleep(0.1)
        assert request.transport is not None
        request.transport.abort()
        return ws

    code, _, texts = await browse(await relay(upstream))
    assert texts == ["INFO {}"]
    assert code == 4500


async def test_browser_messages_reach_the_upstream(relay: StartRelay) -> None:
    seen: asyncio.Future[tuple[aiohttp.WSMsgType, object]] = asyncio.get_running_loop().create_future()

    async def upstream(request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        msg = await ws.receive()
        seen.set_result((msg.type, msg.data))
        return ws

    url = await relay(upstream)
    async with aiohttp.ClientSession() as session, session.ws_connect(url) as ws:
        await ws.send_str("SUB x 1")
        await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY)
    assert await asyncio.wait_for(seen, 5) == (aiohttp.WSMsgType.TEXT, "SUB x 1")


async def test_browser_leaving_sends_upstream_a_normal_close(relay: StartRelay) -> None:
    seen: asyncio.Future[tuple[aiohttp.WSMsgType, object]] = asyncio.get_running_loop().create_future()

    async def upstream(request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        msg = await ws.receive()
        seen.set_result((msg.type, msg.data))
        return ws

    url = await relay(upstream)
    async with aiohttp.ClientSession() as session, session.ws_connect(url) as ws:
        await ws.close(code=aiohttp.WSCloseCode.GOING_AWAY)
    assert await asyncio.wait_for(seen, 5) == (aiohttp.WSMsgType.CLOSE, 1000)


async def test_failed_send_to_the_upstream_reaches_browser_as_upstream_lost(
    relay: StartRelay, monkeypatch: pytest.MonkeyPatch
) -> None:
    forward = views._websocket_forward

    async def upstream_gone(
        ws_from: web.WebSocketResponse | aiohttp.ClientWebSocketResponse,
        ws_to: web.WebSocketResponse | aiohttp.ClientWebSocketResponse,
    ) -> aiohttp.WSMessage | None:
        if isinstance(ws_to, aiohttp.ClientWebSocketResponse):
            # what the forward returns when a send to the upstream raised
            return None
        return await forward(ws_from, ws_to)

    monkeypatch.setattr(views, "_websocket_forward", upstream_gone)

    async def upstream(request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        async for _ in ws:
            pass
        return ws

    code, reason, _ = await browse(await relay(upstream))
    assert code == 4500
    assert reason == "upstream lost"


@pytest.mark.parametrize(
    ("path", "deflate"),
    [
        ("api/go2rtc", False),
        ("api/go2rtc/ws", False),
        ("api/proxy", True),
        ("api/socket.io/", True),
        ("api/go2rtcx", True),
    ],
)
async def test_video_relay_skips_deflate_and_the_rest_keeps_it(
    relay: StartRelay, path: str, deflate: bool
) -> None:
    async def upstream(request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await ws.send_bytes(b"\x00" * 4096)
        await ws.close()
        return ws

    url = await relay(upstream, path)
    # browsers always offer permessage-deflate
    async with aiohttp.ClientSession() as session, session.ws_connect(url, compress=15) as ws:
        msg = await asyncio.wait_for(ws.receive(), 5)
        assert msg.data == b"\x00" * 4096
        assert bool(ws.compress) is deflate
