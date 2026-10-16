from __future__ import annotations

import gzip
import ssl
from collections.abc import AsyncIterator, Awaitable, Callable

import aiohttp
import pytest
from aiohttp import hdrs, web
from homeassistant.components.http import KEY_HASS
from homeassistant.core import HomeAssistant
from multidict import CIMultiDictProxy

from custom_components.cameraui import views

from .helpers import TOKEN, make_entry, serve

SCRIPT = b"export const card = 1;\n"
# one uncompressed brotli meta-block: valid br that aiohttp only decodes with the Brotli package
BROTLI_SCRIPT = b"\x0b\x0b\x80" + SCRIPT + b"\x03"

Upstream = Callable[[web.Request], Awaitable[web.StreamResponse]]
StartProxy = Callable[[Upstream], Awaitable[str]]


@pytest.fixture
async def proxied(
    hass: HomeAssistant,
    socket_enabled: None,
    server_tls: ssl.SSLContext,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[StartProxy]:
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    monkeypatch.setattr(views, "async_get_clientsession", lambda hass, verify_ssl=True: session)
    runners: list[web.AppRunner] = []

    async def start(upstream: Upstream) -> str:
        up = web.Application()
        up.router.add_get("/{path:.*}", upstream)
        up_runner, up_port = await serve(up, server_tls)
        entry = make_entry(up_port)

        async def handler(request: web.Request) -> web.StreamResponse:
            return await views._proxy_http(request, entry, "assets/card.js", TOKEN, base=None)

        proxy = web.Application()
        proxy[KEY_HASS] = hass
        proxy.router.add_get("/x", handler)
        proxy_runner, proxy_port = await serve(proxy)
        runners.extend([proxy_runner, up_runner])
        return f"http://127.0.0.1:{proxy_port}/x"

    yield start
    for runner in runners:
        await runner.cleanup()
    await session.close()


@pytest.mark.parametrize(
    ("encoding", "body"),
    [("gzip", gzip.compress(SCRIPT)), ("br", BROTLI_SCRIPT)],
    ids=["gzip", "br"],
)
async def test_compressed_body_reaches_the_browser_as_the_server_sent_it(
    proxied: StartProxy, encoding: str, body: bytes
) -> None:
    async def compressed(request: web.Request) -> web.StreamResponse:
        return web.Response(
            body=body,
            headers={
                hdrs.CONTENT_TYPE: "text/javascript",
                hdrs.CONTENT_ENCODING: encoding,
                hdrs.VARY: "Accept-Encoding",
            },
        )

    url = await proxied(compressed)
    async with (
        aiohttp.ClientSession(auto_decompress=False) as session,
        session.get(url, headers={hdrs.ACCEPT_ENCODING: "gzip, deflate, br"}) as res,
    ):
        assert res.status == 200
        assert res.headers.get(hdrs.CONTENT_ENCODING) == encoding
        assert res.headers.get(hdrs.VARY) == "Accept-Encoding"
        assert await res.read() == body


async def test_server_negotiates_with_the_browser_accept_encoding_only(proxied: StartProxy) -> None:
    seen: list[CIMultiDictProxy[str]] = []

    async def echo(request: web.Request) -> web.StreamResponse:
        seen.append(request.headers)
        return web.Response(text="ok")

    url = await proxied(echo)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={hdrs.ACCEPT_ENCODING: "br"}) as res:
            assert res.status == 200
        async with session.get(url, skip_auto_headers=(hdrs.ACCEPT_ENCODING,)) as res:
            assert res.status == 200

    assert seen[0].get(hdrs.ACCEPT_ENCODING) == "br"
    assert seen[0].get("X-Cui-Encoding") == "passthrough"
    assert hdrs.ACCEPT_ENCODING not in seen[1]
