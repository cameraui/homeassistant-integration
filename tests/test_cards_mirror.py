from __future__ import annotations

import gzip
import re
import ssl
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from pathlib import Path

import aiohttp
import pytest
from aiohttp import hdrs, web
from homeassistant.components.http import KEY_HASS
from homeassistant.core import HomeAssistant

from custom_components.cameraui import views

from .helpers import make_entry, serve

IMPORT = re.compile(rb"""["'`]\./([\w.-]+\.js)["'`]""")

BUILD_A = {
    "etag": 'W/"2a-18f0000000a"',
    "cameraui-cards.js": b'import { t } from "./types-T1.js"; import("./cards-A1.js");',
    "types-T1.js": b"export const t = 1;",
    "cards-A1.js": b'import "./vendor-V1.js"; import("./dialog-D1.js");',
    "vendor-V1.js": b"vendor",
    "dialog-D1.js": b"dialog",
}

BUILD_B = {
    "etag": 'W/"2a-18f0000000b"',
    "cameraui-cards.js": b'import { t } from "./types-T1.js"; import("./cards-B2.js");',
    "types-T1.js": b"export const t = 1;",
    "cards-B2.js": b'import "./vendor-V1.js"; import("./dialog-D1.js");',
    "vendor-V1.js": b"vendor",
    "dialog-D1.js": b"dialog",
}

BUILD_C = {
    "etag": 'W/"2a-18f0000000c"',
    "cameraui-cards.js": b'import { t } from "./types-T1.js"; import("./cards-C3.js");',
    "types-T1.js": b"export const t = 1;",
    "cards-C3.js": b'import "./vendor-V3.js";',
    "vendor-V3.js": b"vendor three",
}


@dataclass
class Upstream:
    build: dict[str, bytes | str]
    bundle_get_fails: bool = False
    # an encoding the server answers with no matter what was asked
    forced_encoding: str | None = None
    runner: web.AppRunner | None = None
    requests: list[str] = field(default_factory=list)
    accept_encodings: list[str] = field(default_factory=list)


@dataclass
class Browser:
    base: str
    entry_id: str
    cache: dict[str, bytes] = field(default_factory=dict)

    async def load(self, session: aiohttp.ClientSession) -> dict[str, int]:
        # follows the module graph like a browser with an immutable cache
        statuses: dict[str, int] = {}
        async with session.get(self.url("cameraui-cards.js"), allow_redirects=False) as res:
            statuses["cameraui-cards.js"] = res.status
            if res.status != 302:
                return statuses
            queue = [res.headers["Location"].rsplit("/", 1)[1]]
        while queue:
            name = queue.pop()
            if name in statuses:
                continue
            body = self.cache.get(name)
            if body is None:
                async with session.get(self.url(name)) as res:
                    statuses[name] = res.status
                    if res.status != 200:
                        continue
                    body = await res.read()
                    self.cache[name] = body
            else:
                statuses[name] = 200
            queue.extend(match.decode() for match in IMPORT.findall(body))
        return statuses

    def url(self, file: str) -> str:
        return f"{self.base}/api/cameraui/cards/{self.entry_id}/{file}"


@pytest.fixture
async def setup(
    hass: HomeAssistant,
    socket_enabled: None,
    server_tls: ssl.SSLContext,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> AsyncIterator[tuple[Upstream, str, str]]:
    hass.config.config_dir = str(tmp_path)
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    monkeypatch.setattr(views, "async_get_clientsession", lambda hass, verify_ssl=True: session)

    upstream = Upstream(build=BUILD_A)

    async def asset(request: web.Request) -> web.StreamResponse:
        file = request.match_info["file"]
        upstream.requests.append(f"{request.method} {file}")
        body = upstream.build.get(file)
        if not isinstance(body, bytes):
            return web.Response(status=404)
        if request.method == "GET" and file == views.CARDS_BUNDLE and upstream.bundle_get_fails:
            return web.Response(status=503)
        headers = {"ETag": str(upstream.build["etag"]) if file == views.CARDS_BUNDLE else f'W/"{file}"'}
        upstream.accept_encodings.append(request.headers.get(hdrs.ACCEPT_ENCODING, ""))
        if request.headers.get(hdrs.IF_NONE_MATCH) == headers["ETag"]:
            return web.Response(status=304, headers=headers)
        # like the server: only hashed chunks have a gzip sibling, the entry goes out plain
        if upstream.forced_encoding:
            headers[hdrs.CONTENT_ENCODING] = upstream.forced_encoding
        elif file != views.CARDS_BUNDLE and "gzip" in request.headers.get(hdrs.ACCEPT_ENCODING, ""):
            headers[hdrs.CONTENT_ENCODING] = "gzip"
            headers[hdrs.VARY] = hdrs.ACCEPT_ENCODING
            body = gzip.compress(body)
        return web.Response(body=body, headers=headers, content_type="text/javascript")

    up = web.Application()
    up.router.add_route("*", "/ha/{file}", asset)
    upstream.runner, up_port = await serve(up, server_tls)
    entry = make_entry(up_port)
    entry.add_to_hass(hass)

    async def cards(request: web.Request) -> web.StreamResponse:
        return await views.CameraUiCardsAssetView().get(
            request, request.match_info["entry_id"], request.match_info["file"]
        )

    proxy = web.Application()
    proxy[KEY_HASS] = hass
    proxy.router.add_get("/api/cameraui/cards/{entry_id}/{file}", cards)
    proxy_runner, proxy_port = await serve(proxy)
    yield upstream, f"http://127.0.0.1:{proxy_port}", entry.entry_id
    await proxy_runner.cleanup()
    if upstream.runner:
        await upstream.runner.cleanup()
    await session.close()


async def go_offline(upstream: Upstream) -> None:
    assert upstream.runner
    await upstream.runner.cleanup()
    upstream.runner = None


def mirror_dir(hass: HomeAssistant, entry_id: str) -> Path:
    return Path(hass.config.path(".storage", "cameraui_cards", entry_id))


def mirrored(hass: HomeAssistant, entry_id: str) -> set[str]:
    return {path.name for path in mirror_dir(hass, entry_id).glob("*.js")}


async def test_new_build_keeps_the_chunks_browsers_already_cached(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    upstream, base, entry_id = setup
    device = Browser(base, entry_id)
    async with aiohttp.ClientSession() as session:
        assert set((await device.load(session)).values()) == {302, 200}

        upstream.build = BUILD_B
        await device.load(session)
        await go_offline(upstream)

        statuses = await Browser(base, entry_id).load(session)

    assert set(statuses.values()) == {302, 200}, statuses
    assert {"types-T1.js", "cards-B2.js", "vendor-V1.js", "dialog-D1.js"} <= statuses.keys()


async def test_mirror_switches_builds_only_once_the_new_bundle_is_mirrored(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    upstream, base, entry_id = setup
    async with aiohttp.ClientSession() as session:
        await Browser(base, entry_id).load(session)

        upstream.build = BUILD_B
        upstream.bundle_get_fails = True
        await Browser(base, entry_id).load(session)
        await go_offline(upstream)

        statuses = await Browser(base, entry_id).load(session)

    assert set(statuses.values()) == {302, 200}, statuses
    assert "cards-A1.js" in statuses


async def test_mirror_drops_chunks_only_builds_before_the_previous_one_used(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    upstream, base, entry_id = setup
    async with aiohttp.ClientSession() as session:
        for build in (BUILD_A, BUILD_B, BUILD_C):
            upstream.build = build
            await Browser(base, entry_id).load(session)

    files = mirrored(hass, entry_id)
    assert "cards-A1.js" not in files
    assert {"cards-B2.js", "vendor-V1.js", "dialog-D1.js"} <= files
    assert {"cards-C3.js", "vendor-V3.js", "types-T1.js"} <= files
    assert len([name for name in files if name.startswith("cameraui-cards.")]) == 2


async def test_a_repeated_switch_to_the_same_build_keeps_the_previous_chunks(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    upstream, base, entry_id = setup
    device = Browser(base, entry_id)
    async with aiohttp.ClientSession() as session:
        await device.load(session)

        upstream.build = BUILD_B
        async with session.get(device.url("cameraui-cards.js"), allow_redirects=False) as res:
            tagged = res.headers["Location"].rsplit("/", 1)[1]
        tag = tagged.split(".")[1]
        for _ in range(2):
            # a dashboard whose HEAD still saw the old build marks the new one pending again
            (mirror_dir(hass, entry_id) / "pending").write_text(tag)
            async with session.get(device.url(tagged)) as res:
                assert res.status == 200

        await device.load(session)
        await go_offline(upstream)
        statuses = await Browser(base, entry_id).load(session)

    assert set(statuses.values()) == {302, 200}, statuses
    assert {"cards-B2.js", "vendor-V1.js", "dialog-D1.js"} <= statuses.keys()


async def test_cards_hand_gzip_on_and_mirror_the_plain_file(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    upstream, base, entry_id = setup
    url = Browser(base, entry_id).url("cards-A1.js")
    async with (
        aiohttp.ClientSession(auto_decompress=False) as session,
        session.get(url, headers={hdrs.ACCEPT_ENCODING: "gzip, deflate, br, zstd"}) as res,
    ):
        assert res.status == 200
        assert res.headers[hdrs.CONTENT_ENCODING] == "gzip"
        assert res.headers[hdrs.VARY] == hdrs.ACCEPT_ENCODING
        assert gzip.decompress(await res.read()) == BUILD_A["cards-A1.js"]

    assert upstream.accept_encodings == ["gzip"]
    assert (mirror_dir(hass, entry_id) / "cards-A1.js").read_bytes() == BUILD_A["cards-A1.js"]


async def test_cards_stay_plain_for_a_browser_without_gzip(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    upstream, base, entry_id = setup
    url = Browser(base, entry_id).url("cards-A1.js")
    async with (
        aiohttp.ClientSession(auto_decompress=False) as session,
        session.get(url, headers={hdrs.ACCEPT_ENCODING: "identity"}) as res,
    ):
        assert res.status == 200
        assert hdrs.CONTENT_ENCODING not in res.headers
        assert await res.read() == BUILD_A["cards-A1.js"]

    assert upstream.accept_encodings == ["identity"]


async def test_offline_cards_come_plain_from_the_mirror(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    upstream, base, entry_id = setup
    url = Browser(base, entry_id).url("cards-A1.js")
    async with aiohttp.ClientSession(auto_decompress=False) as session:
        async with session.get(url, headers={hdrs.ACCEPT_ENCODING: "gzip"}) as res:
            assert res.headers[hdrs.CONTENT_ENCODING] == "gzip"
        await go_offline(upstream)
        async with session.get(url, headers={hdrs.ACCEPT_ENCODING: "gzip"}) as res:
            assert res.status == 200
            assert hdrs.CONTENT_ENCODING not in res.headers
            assert res.headers[hdrs.VARY] == hdrs.ACCEPT_ENCODING
            assert await res.read() == BUILD_A["cards-A1.js"]


async def test_revalidated_cards_keep_their_vary(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    _upstream, base, entry_id = setup
    url = Browser(base, entry_id).url("cards-A1.js")
    headers = {hdrs.ACCEPT_ENCODING: "gzip", hdrs.IF_NONE_MATCH: 'W/"cards-A1.js"'}
    async with (
        aiohttp.ClientSession(auto_decompress=False) as session,
        session.get(url, headers=headers) as res,
    ):
        assert res.status == 304
        assert res.headers[hdrs.VARY] == hdrs.ACCEPT_ENCODING
        assert hdrs.CONTENT_ENCODING not in res.headers


async def test_an_encoding_the_mirror_cannot_unpack_is_refused(
    hass: HomeAssistant, setup: tuple[Upstream, str, str]
) -> None:
    upstream, base, entry_id = setup
    upstream.forced_encoding = "br"
    url = Browser(base, entry_id).url("cards-A1.js")
    async with (
        aiohttp.ClientSession(auto_decompress=False) as session,
        session.get(url, headers={hdrs.ACCEPT_ENCODING: "gzip, br"}) as res,
    ):
        assert res.status == 502

    assert not (mirror_dir(hass, entry_id) / "cards-A1.js").exists()
