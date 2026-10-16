from __future__ import annotations

import asyncio
import ssl
from collections.abc import AsyncIterator
from pathlib import Path

import aiohttp
import pytest
from aiohttp import hdrs, web
from homeassistant.components.http import KEY_HASS
from homeassistant.core import HomeAssistant

from custom_components.cameraui import views

from .helpers import TOKEN, make_entry, mute_server, serve


@pytest.fixture
async def shared_session(hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[None]:
    # HA's shared session carries aiohttp's default total timeout of 300 s, scaled down here
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=1, sock_connect=30),
        connector=aiohttp.TCPConnector(ssl=False),
    )
    monkeypatch.setattr(views, "async_get_clientsession", lambda hass, verify_ssl=True: session)
    yield
    await session.close()


async def test_slow_proxied_download_outlives_the_session_total_timeout(
    hass: HomeAssistant, socket_enabled: None, server_tls: ssl.SSLContext, shared_session: None
) -> None:
    async def slow(request: web.Request) -> web.StreamResponse:
        response = web.StreamResponse()
        await response.prepare(request)
        for _ in range(8):
            await response.write(b"x" * 65536)
            await asyncio.sleep(0.25)
        return response

    up = web.Application()
    up.router.add_get("/dl", slow)
    up_runner, up_port = await serve(up, server_tls)
    entry = make_entry(up_port)

    async def handler(request: web.Request) -> web.StreamResponse:
        return await views._proxy_http(request, entry, "dl", TOKEN, base=None)

    proxy = web.Application()
    proxy[KEY_HASS] = hass
    proxy.router.add_get("/dl", handler)
    proxy_runner, proxy_port = await serve(proxy)
    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(f"http://127.0.0.1:{proxy_port}/dl") as res,
        ):
            body = await res.read()
        assert res.status == 200
        assert len(body) == 8 * 65536
    finally:
        await proxy_runner.cleanup()
        await up_runner.cleanup()


async def test_upstream_that_never_answers_the_handshake_gets_gateway_timeout(
    hass: HomeAssistant, socket_enabled: None, shared_session: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(views, "PROXY_TIMEOUT", aiohttp.ClientTimeout(total=None, sock_connect=0.3))
    async with mute_server() as (port, _):
        entry = make_entry(port)

        async def handler(request: web.Request) -> web.StreamResponse:
            return await views._proxy_http(request, entry, "api/", TOKEN, base=None)

        proxy = web.Application()
        proxy[KEY_HASS] = hass
        proxy.router.add_get("/x", handler)
        proxy_runner, proxy_port = await serve(proxy)
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(f"http://127.0.0.1:{proxy_port}/x") as res,
            ):
                assert res.status == 504
        finally:
            await proxy_runner.cleanup()


@pytest.fixture
async def stalled_upstream(
    hass: HomeAssistant,
    socket_enabled: None,
    server_tls: ssl.SSLContext,
    shared_session: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> AsyncIterator[tuple[str, str]]:
    hass.config.config_dir = str(tmp_path)
    monkeypatch.setattr(
        views, "ASSET_TIMEOUT", aiohttp.ClientTimeout(total=None, sock_connect=3, sock_read=0.3)
    )
    release = asyncio.Event()

    async def stall(request: web.Request) -> web.StreamResponse:
        await release.wait()
        return web.Response()

    up = web.Application()
    up.router.add_route("*", "/{path:.*}", stall)
    up_runner, up_port = await serve(up, server_tls)
    entry = make_entry(up_port)
    entry.add_to_hass(hass)

    async def cards(request: web.Request) -> web.StreamResponse:
        return await views.CameraUiCardsAssetView().get(
            request, request.match_info["entry_id"], request.match_info["file"]
        )

    async def fonts(request: web.Request) -> web.StreamResponse:
        return await views.CameraUiCardsFontView().get(
            request, request.match_info["entry_id"], request.match_info["file"]
        )

    proxy = web.Application()
    proxy[KEY_HASS] = hass
    proxy.router.add_get("/api/cameraui/cards/{entry_id}/fonts/{file}", fonts)
    proxy.router.add_get("/api/cameraui/cards/{entry_id}/{file}", cards)
    proxy_runner, proxy_port = await serve(proxy)
    yield f"http://127.0.0.1:{proxy_port}", entry.entry_id
    release.set()
    await proxy_runner.cleanup()
    await up_runner.cleanup()


async def test_cards_bundle_falls_back_to_the_mirror_when_upstream_stalls(
    hass: HomeAssistant, stalled_upstream: tuple[str, str]
) -> None:
    base, entry_id = stalled_upstream
    mirror = views._CardsMirror(hass, entry_id)
    await mirror.remember_tag("abc123")
    await mirror.store("cameraui-cards.abc123.js", b"cached bundle")

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{base}/api/cameraui/cards/{entry_id}/cameraui-cards.js", allow_redirects=False
        ) as res:
            assert res.status == 302
            assert res.headers["Location"].endswith("/cameraui-cards.abc123.js")
        async with session.get(f"{base}/api/cameraui/cards/{entry_id}/cameraui-cards.abc123.js") as res:
            assert res.status == 200
            assert await res.read() == b"cached bundle"


async def test_cards_font_falls_back_to_the_mirror_when_upstream_stalls(
    hass: HomeAssistant, stalled_upstream: tuple[str, str]
) -> None:
    base, entry_id = stalled_upstream
    await views._CardsMirror(hass, entry_id).store("fonts/inter.woff2", b"font")

    async with (
        aiohttp.ClientSession() as session,
        session.get(f"{base}/api/cameraui/cards/{entry_id}/fonts/inter.woff2") as res,
    ):
        assert res.status == 200
        assert res.headers[hdrs.CONTENT_TYPE] == views.FONT_CONTENT_TYPE
        assert await res.read() == b"font"


def with_short_pool_wait(timeout: aiohttp.ClientTimeout) -> aiohttp.ClientTimeout:
    # a missing pool bound stays missing
    return aiohttp.ClientTimeout(
        total=timeout.total,
        connect=timeout.connect and 0.5,
        sock_connect=timeout.sock_connect,
        sock_read=timeout.sock_read,
    )


@pytest.fixture
async def crowded_upstream(
    hass: HomeAssistant,
    socket_enabled: None,
    server_tls: ssl.SSLContext,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> AsyncIterator[tuple[str, str]]:
    hass.config.config_dir = str(tmp_path)
    # one connection per host stands in for a pool that proxied WebSockets filled up
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False, limit_per_host=1))
    monkeypatch.setattr(views, "async_get_clientsession", lambda hass, verify_ssl=True: session)
    monkeypatch.setattr(views, "PROXY_TIMEOUT", with_short_pool_wait(views.PROXY_TIMEOUT))
    monkeypatch.setattr(views, "ASSET_TIMEOUT", with_short_pool_wait(views.ASSET_TIMEOUT))

    holding = asyncio.Event()
    release = asyncio.Event()

    async def hold(request: web.Request) -> web.StreamResponse:
        holding.set()
        await release.wait()
        return web.Response()

    async def answer(request: web.Request) -> web.StreamResponse:
        return web.Response(text="fresh")

    up = web.Application()
    up.router.add_get("/hold", hold)
    up.router.add_route("*", "/{path:.*}", answer)
    up_runner, up_port = await serve(up, server_tls)
    entry = make_entry(up_port)
    entry.add_to_hass(hass)
    held = asyncio.create_task(session.get(f"https://127.0.0.1:{up_port}/hold"))
    await asyncio.wait_for(holding.wait(), 5)

    async def proxied(request: web.Request) -> web.StreamResponse:
        return await views._proxy_http(request, entry, "api/x", TOKEN, base=None)

    async def fonts(request: web.Request) -> web.StreamResponse:
        return await views.CameraUiCardsFontView().get(
            request, request.match_info["entry_id"], request.match_info["file"]
        )

    proxy = web.Application()
    proxy[KEY_HASS] = hass
    proxy.router.add_get("/x", proxied)
    proxy.router.add_get("/api/cameraui/cards/{entry_id}/fonts/{file}", fonts)
    proxy_runner, proxy_port = await serve(proxy)
    yield f"http://127.0.0.1:{proxy_port}", entry.entry_id
    release.set()
    (await held).release()
    await proxy_runner.cleanup()
    await up_runner.cleanup()
    await session.close()


async def test_proxied_request_waiting_for_a_free_connection_gets_gateway_timeout(
    crowded_upstream: tuple[str, str],
) -> None:
    base, _ = crowded_upstream
    async with aiohttp.ClientSession() as session:
        res = await asyncio.wait_for(session.get(f"{base}/x"), 10)
        res.release()
    assert res.status == 504


async def test_cards_font_falls_back_to_the_mirror_when_no_connection_is_free(
    hass: HomeAssistant, crowded_upstream: tuple[str, str]
) -> None:
    base, entry_id = crowded_upstream
    await views._CardsMirror(hass, entry_id).store("fonts/inter.woff2", b"font")

    async with aiohttp.ClientSession() as session:
        res = await asyncio.wait_for(
            session.get(f"{base}/api/cameraui/cards/{entry_id}/fonts/inter.woff2"), 10
        )
        body = await res.read()
    assert res.status == 200
    assert res.headers[hdrs.CONTENT_TYPE] == views.FONT_CONTENT_TYPE
    assert body == b"font"
