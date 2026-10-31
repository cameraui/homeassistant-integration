from __future__ import annotations

import ssl
from types import SimpleNamespace

import aiohttp
import pytest
from aiohttp import hdrs, web
from aiohttp.typedefs import Handler
from homeassistant.components.http import KEY_AUTHENTICATED, KEY_HASS, KEY_HASS_USER, HomeAssistantView
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.cameraui import views
from custom_components.cameraui.const import CONF_PROXY_SECRET, CONF_TOKEN, DOMAIN

from .helpers import TOKEN, serve

SECRET = "proxy-secret"


@web.middleware
async def as_admin(request: web.Request, handler: Handler) -> web.StreamResponse:
    request[KEY_AUTHENTICATED] = True
    request[KEY_HASS_USER] = SimpleNamespace(is_admin=True)
    return await handler(request)


@pytest.mark.parametrize(
    ("view", "prefix"),
    [
        (views.CameraUiProxyView, f"/api/cameraui/proxy/{SECRET}"),
        (views.CameraUiAuthProxyView, "/api/cameraui/auth/{entry_id}"),
    ],
)
async def test_download_check_reaches_the_server(
    hass: HomeAssistant,
    socket_enabled: None,
    server_tls: ssl.SSLContext,
    monkeypatch: pytest.MonkeyPatch,
    view: type[HomeAssistantView],
    prefix: str,
) -> None:
    checked: list[str] = []

    async def check(request: web.Request) -> web.Response:
        checked.append(request.match_info["token"])
        return web.Response(headers={hdrs.CONTENT_TYPE: "video/mp4"})

    up = web.Application()
    up.router.add_route(hdrs.METH_HEAD, "/api/download/{token}", check)
    up_runner, up_port = await serve(up, server_tls)

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_PORT: up_port, CONF_TOKEN: TOKEN, CONF_PROXY_SECRET: SECRET},
    )
    entry.add_to_hass(hass)
    entry.mock_state(hass, ConfigEntryState.LOADED)

    upstream_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    monkeypatch.setattr(views, "async_get_clientsession", lambda hass, verify_ssl=True: upstream_session)

    app = web.Application(middlewares=[as_admin])
    app[KEY_HASS] = hass
    view().register(hass, app, app.router)
    runner, port = await serve(app)

    url = f"http://127.0.0.1:{port}{prefix.format(entry_id=entry.entry_id)}/api/download/clip-token"
    try:
        async with aiohttp.ClientSession() as browser, browser.head(url) as res:
            assert res.status == 200
            assert res.headers[hdrs.CONTENT_TYPE] == "video/mp4"
    finally:
        await runner.cleanup()
        await up_runner.cleanup()
        await upstream_session.close()

    assert checked == ["clip-token"]
