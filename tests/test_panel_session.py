from __future__ import annotations

import ssl
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from http.cookies import SimpleCookie
from types import SimpleNamespace

import aiohttp
import pytest
from aiohttp import hdrs, web
from aiohttp.typedefs import Handler, Middleware
from homeassistant.components.http import KEY_AUTHENTICATED, KEY_HASS, KEY_HASS_USER
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cameraui import async_migrate_entry, panel_session, views
from custom_components.cameraui.const import CONF_PROXY_SECRET, CONF_TOKEN, DOMAIN
from custom_components.cameraui.panel_session import PANEL_COOKIE, PANEL_SESSION_TTL, PanelSessions

from .helpers import TOKEN, serve


def signed_in(user: SimpleNamespace | None) -> Middleware:
    @web.middleware
    async def middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
        request[KEY_AUTHENTICATED] = user is not None
        if user is not None:
            request[KEY_HASS_USER] = user
        return await handler(request)

    return middleware


@dataclass
class Rig:
    base: str
    entry: MockConfigEntry
    browser: aiohttp.ClientSession
    seen: list[dict[str, str]]

    def proxy(self, path: str) -> str:
        return f"{self.base}/api/cameraui/proxy/{self.entry.entry_id}/{path}"

    def session(self) -> str:
        return f"{self.base}/api/cameraui/session/{self.entry.entry_id}"


@asynccontextmanager
async def home_assistant(
    hass: HomeAssistant,
    server_tls: ssl.SSLContext,
    monkeypatch: pytest.MonkeyPatch,
    user: SimpleNamespace | None,
) -> AsyncIterator[Rig]:
    seen: list[dict[str, str]] = []

    async def echo(request: web.Request) -> web.Response:
        seen.append(dict(request.headers))
        return web.Response(text="ok")

    up = web.Application()
    up.router.add_get("/api/echo", echo)
    up_runner, up_port = await serve(up, server_tls)

    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_HOST: "127.0.0.1", CONF_PORT: up_port, CONF_TOKEN: TOKEN}
    )
    entry.add_to_hass(hass)
    entry.mock_state(hass, ConfigEntryState.LOADED)
    entry.runtime_data = SimpleNamespace(panel_sessions=PanelSessions())

    upstream_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    monkeypatch.setattr(views, "async_get_clientsession", lambda hass, verify_ssl=True: upstream_session)

    app = web.Application(middlewares=[signed_in(user)])
    app[KEY_HASS] = hass
    views.CameraUiPanelSessionView().register(hass, app, app.router)
    views.CameraUiProxyView().register(hass, app, app.router)
    runner, port = await serve(app)
    try:
        async with aiohttp.ClientSession() as browser:
            yield Rig(f"http://127.0.0.1:{port}", entry, browser, seen)
    finally:
        await runner.cleanup()
        await up_runner.cleanup()
        await upstream_session.close()


async def test_proxy_turns_away_requests_without_a_session(
    hass: HomeAssistant, socket_enabled: None, server_tls: ssl.SSLContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    async with home_assistant(hass, server_tls, monkeypatch, user=None) as rig:
        sessions = rig.entry.runtime_data.panel_sessions
        clock = [time.monotonic()]
        monkeypatch.setattr(panel_session, "time", SimpleNamespace(monotonic=lambda: clock[0]))
        lapsed = sessions.create()
        clock[0] += PANEL_SESSION_TTL + 1
        valid = sessions.create()

        for cookie in (None, "guessed", lapsed):
            headers = {hdrs.COOKIE: f"{PANEL_COOKIE}={cookie}"} if cookie else {}
            async with rig.browser.get(rig.proxy("api/echo"), headers=headers) as res:
                assert res.status == 403
        async with rig.browser.get(
            rig.proxy("api/echo"), headers={hdrs.COOKIE: f"{PANEL_COOKIE}={valid}"}
        ) as res:
            assert res.status == 200

    assert [headers[hdrs.AUTHORIZATION] for headers in rig.seen] == [f"Bearer {TOKEN}"]


async def test_session_cookie_is_scoped_to_the_proxy(
    hass: HomeAssistant, socket_enabled: None, server_tls: ssl.SSLContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    admin = SimpleNamespace(is_admin=True)
    async with (
        home_assistant(hass, server_tls, monkeypatch, user=admin) as rig,
        rig.browser.post(rig.session()) as res,
    ):
        assert res.status == 204
        assert res.headers[hdrs.CACHE_CONTROL] == "no-store"
        cookie = SimpleCookie(res.headers[hdrs.SET_COOKIE])[PANEL_COOKIE]

    assert cookie["httponly"]
    assert cookie["samesite"] == "Strict"
    assert cookie["path"] == f"/api/cameraui/proxy/{rig.entry.entry_id}/"
    assert cookie["max-age"] == str(PANEL_SESSION_TTL)
    assert rig.entry.runtime_data.panel_sessions.valid(cookie.value)


@pytest.mark.parametrize(("user", "status"), [(None, 401), (SimpleNamespace(is_admin=False), 403)])
async def test_only_admins_get_a_session(
    hass: HomeAssistant,
    socket_enabled: None,
    server_tls: ssl.SSLContext,
    monkeypatch: pytest.MonkeyPatch,
    user: SimpleNamespace | None,
    status: int,
) -> None:
    async with (
        home_assistant(hass, server_tls, monkeypatch, user=user) as rig,
        rig.browser.post(rig.session()) as res,
    ):
        assert res.status == status
        assert hdrs.SET_COOKIE not in res.headers


async def test_panel_cookie_stays_in_home_assistant(
    hass: HomeAssistant, socket_enabled: None, server_tls: ssl.SSLContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    async with home_assistant(hass, server_tls, monkeypatch, user=None) as rig:
        token = rig.entry.runtime_data.panel_sessions.create()
        headers = {hdrs.COOKIE: f"theme=dark; {PANEL_COOKIE}={token}"}
        async with rig.browser.get(rig.proxy("api/echo"), headers=headers) as res:
            assert res.status == 200

    assert rig.seen[0][hdrs.COOKIE] == "theme=dark"


def test_unload_ends_every_session() -> None:
    sessions = PanelSessions()
    token = sessions.create()
    sessions.clear()
    assert not sessions.valid(token)


async def test_migration_drops_the_path_secret(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        minor_version=1,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: 3443, CONF_TOKEN: TOKEN, CONF_PROXY_SECRET: "path-secret"},
    )
    entry.add_to_hass(hass)

    assert await async_migrate_entry(hass, entry)
    assert entry.data == {CONF_HOST: "127.0.0.1", CONF_PORT: 3443, CONF_TOKEN: TOKEN}
    assert entry.minor_version == 2
