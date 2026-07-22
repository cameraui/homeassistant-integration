from __future__ import annotations

import asyncio
import hmac
import logging
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import hdrs, web
from homeassistant.components.http import KEY_HASS, KEY_HASS_USER, HomeAssistantView
from homeassistant.components.http.auth import SIGN_QUERY_PARAM
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from yarl import URL

from .const import CONF_PROXY_SECRET, CONF_TOKEN, DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

WS_TARGETS = {"go2rtc": "/api/go2rtc", "rpc": "/api/proxy"}
MAX_WS_MESSAGE_SIZE = 16 * 1024 * 1024

HOP_BY_HOP = {
    hdrs.CONTENT_LENGTH,
    hdrs.CONTENT_ENCODING,
    hdrs.TRANSFER_ENCODING,
    hdrs.CONNECTION,
    hdrs.KEEP_ALIVE,
    hdrs.HOST,
    hdrs.SEC_WEBSOCKET_EXTENSIONS,
    hdrs.SEC_WEBSOCKET_PROTOCOL,
    hdrs.SEC_WEBSOCKET_VERSION,
    hdrs.SEC_WEBSOCKET_KEY,
}
PROXY_PREFIX = "/api/cameraui/proxy"


class CameraUiWsProxyView(HomeAssistantView):
    name = "api:cameraui:ws"
    url = "/api/cameraui/ws/{entry_id}/{target}"
    requires_auth = True

    async def get(
        self, request: web.Request, entry_id: str, target: str
    ) -> web.WebSocketResponse:
        hass = request.app[KEY_HASS]

        upstream_path = WS_TARGETS.get(target)
        if not upstream_path:
            raise web.HTTPNotFound

        # the rpc bus runs with the stored token's full privileges, keep it to HA admins
        if target == "rpc" and not request[KEY_HASS_USER].is_admin:
            raise web.HTTPForbidden

        entry = _get_loaded_entry(hass, entry_id)
        if not entry:
            raise web.HTTPNotFound

        # camera.ui authenticates WS upgrades via the token query param
        query = {
            key: value
            for key, value in request.query.items()
            if key != SIGN_QUERY_PARAM
        }
        query["token"] = entry.data[CONF_TOKEN]
        upstream_url = URL.build(
            scheme="wss",
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            path=upstream_path,
            query=query,
        )

        protocols: list[str] = []
        if hdrs.SEC_WEBSOCKET_PROTOCOL in request.headers:
            protocols = [
                proto.strip()
                for proto in request.headers[hdrs.SEC_WEBSOCKET_PROTOCOL].split(",")
            ]

        ws_server = web.WebSocketResponse(
            protocols=protocols,
            autoclose=False,
            autoping=False,
            max_msg_size=MAX_WS_MESSAGE_SIZE,
        )
        await ws_server.prepare(request)

        session = async_get_clientsession(hass, verify_ssl=False)
        try:
            async with session.ws_connect(
                upstream_url,
                protocols=protocols,
                autoclose=False,
                autoping=False,
                max_msg_size=MAX_WS_MESSAGE_SIZE,
            ) as ws_client:
                await asyncio.wait(
                    [
                        asyncio.create_task(_websocket_forward(ws_server, ws_client)),
                        asyncio.create_task(_websocket_forward(ws_client, ws_server)),
                    ],
                    return_when=asyncio.FIRST_COMPLETED,
                )
        except aiohttp.ClientError as err:
            _LOGGER.warning(
                "Upstream WebSocket connection to %s failed: %s", target, err
            )
            await ws_server.close(code=aiohttp.WSCloseCode.INTERNAL_ERROR)

        return ws_server


class CameraUiSnapshotView(HomeAssistantView):
    name = "api:cameraui:snapshot"
    url = "/api/cameraui/snapshot/{entry_id}/{camera_name}"
    requires_auth = True

    async def get(
        self, request: web.Request, entry_id: str, camera_name: str
    ) -> web.Response:
        hass = request.app[KEY_HASS]

        entry = _get_loaded_entry(hass, entry_id)
        if not entry:
            raise web.HTTPNotFound

        upstream_url = URL.build(
            scheme="https",
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            path=f"/api/cameras/{camera_name}/snapshot",
            query={"forceNew": "true"},
        )
        session = async_get_clientsession(hass, verify_ssl=False)
        try:
            async with session.get(
                upstream_url,
                headers={"Authorization": f"Bearer {entry.data[CONF_TOKEN]}"},
            ) as upstream:
                if upstream.status != 200:
                    raise web.HTTPBadGateway
                body = await upstream.read()
        except aiohttp.ClientError as err:
            _LOGGER.debug("Snapshot fetch for %s failed: %s", camera_name, err)
            raise web.HTTPBadGateway from err

        return web.Response(
            body=body, content_type="image/jpeg", headers={"Cache-Control": "no-store"}
        )


def _probe_flags(probe: dict[str, Any]) -> dict[str, bool]:
    # go2rtc media lines look like "audio, recvonly, OPUS/48000"; recvonly audio is the backchannel
    medias = [
        media.lower()
        for producer in probe.get("producers") or []
        for media in producer.get("medias") or []
    ]
    return {
        "has_backchannel": any(m.startswith("audio") and "recvonly" in m for m in medias),
        "has_audio": any(m.startswith("audio") and "sendonly" in m for m in medias),
        "has_video": any(m.startswith("video") and "sendonly" in m for m in medias),
    }


class CameraUiProbeView(HomeAssistantView):
    name = "api:cameraui:probe"
    url = "/api/cameraui/probe/{entry_id}/{camera_name}/{source_name}"
    requires_auth = True

    async def get(
        self, request: web.Request, entry_id: str, camera_name: str, source_name: str
    ) -> web.Response:
        hass = request.app[KEY_HASS]

        entry = _get_loaded_entry(hass, entry_id)
        if not entry:
            raise web.HTTPNotFound

        upstream_url = URL.build(
            scheme="https",
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            path=f"/api/cameras/{camera_name}/probe/{source_name}",
            query={"microphone": "true"},
        )
        session = async_get_clientsession(hass, verify_ssl=False)
        try:
            async with session.get(
                upstream_url,
                headers={"Authorization": f"Bearer {entry.data[CONF_TOKEN]}"},
            ) as upstream:
                if upstream.status != 200:
                    raise web.HTTPBadGateway
                data = await upstream.json()
        except aiohttp.ClientError as err:
            _LOGGER.debug("Probe for %s failed: %s", camera_name, err)
            raise web.HTTPBadGateway from err

        return web.json_response(_probe_flags(data.get("probe", {})))


class CameraUiProxyView(HomeAssistantView):
    name = "api:cameraui:proxy"
    url = "/api/cameraui/proxy/{secret}/{path:.*}"
    requires_auth = False

    async def _handle(
        self, request: web.Request, secret: str, path: str
    ) -> web.StreamResponse:
        hass = request.app[KEY_HASS]

        entry = _get_entry_by_proxy_secret(hass, secret)
        if not entry:
            raise web.HTTPNotFound

        if _is_websocket(request):
            return await self._handle_ws(request, entry, path)
        return await self._handle_http(request, entry, secret, path)

    get = _handle
    post = _handle
    put = _handle
    delete = _handle
    patch = _handle

    async def _handle_http(
        self, request: web.Request, entry: ConfigEntry, secret: str, path: str
    ) -> web.StreamResponse:
        hass = request.app[KEY_HASS]
        query = {
            key: value
            for key, value in request.query.items()
            if key != SIGN_QUERY_PARAM
        }
        upstream_url = URL.build(
            scheme="https",
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            path=f"/{path}",
            query=query,
        )

        headers = {
            name: value
            for name, value in request.headers.items()
            if name not in HOP_BY_HOP
        }
        headers[hdrs.AUTHORIZATION] = f"Bearer {entry.data[CONF_TOKEN]}"
        headers["X-Cui-Base"] = f"{PROXY_PREFIX}/{secret}/"
        headers["X-Cui-Embed"] = "homeassistant"

        session = async_get_clientsession(hass, verify_ssl=False)
        try:
            async with session.request(
                request.method,
                upstream_url,
                headers=headers,
                data=request.content if request.body_exists else None,
                allow_redirects=False,
            ) as upstream:
                response = web.StreamResponse(status=upstream.status)
                for name, value in upstream.headers.items():
                    if name in HOP_BY_HOP:
                        continue
                    if name.lower() == "content-security-policy":
                        value = _strip_csp_upgrade(value)
                    response.headers[name] = value
                await response.prepare(request)
                async for chunk in upstream.content.iter_chunked(65536):
                    await response.write(chunk)
                return response
        except aiohttp.ClientError as err:
            _LOGGER.debug("Proxy request to %s failed: %s", path, err)
            raise web.HTTPBadGateway from err

    async def _handle_ws(
        self, request: web.Request, entry: ConfigEntry, path: str
    ) -> web.WebSocketResponse:
        hass = request.app[KEY_HASS]
        query = {
            key: value
            for key, value in request.query.items()
            if key != SIGN_QUERY_PARAM
        }
        query["token"] = entry.data[CONF_TOKEN]
        upstream_url = URL.build(
            scheme="wss",
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            path=f"/{path}",
            query=query,
        )

        protocols: list[str] = []
        if hdrs.SEC_WEBSOCKET_PROTOCOL in request.headers:
            protocols = [
                proto.strip()
                for proto in request.headers[hdrs.SEC_WEBSOCKET_PROTOCOL].split(",")
            ]

        ws_server = web.WebSocketResponse(
            protocols=protocols,
            autoclose=False,
            autoping=False,
            max_msg_size=MAX_WS_MESSAGE_SIZE,
        )
        await ws_server.prepare(request)

        session = async_get_clientsession(hass, verify_ssl=False)
        try:
            async with session.ws_connect(
                upstream_url,
                protocols=protocols,
                autoclose=False,
                autoping=False,
                max_msg_size=MAX_WS_MESSAGE_SIZE,
            ) as ws_client:
                await asyncio.wait(
                    [
                        asyncio.create_task(_websocket_forward(ws_server, ws_client)),
                        asyncio.create_task(_websocket_forward(ws_client, ws_server)),
                    ],
                    return_when=asyncio.FIRST_COMPLETED,
                )
        except aiohttp.ClientError as err:
            _LOGGER.warning("Proxy WebSocket to %s failed: %s", path, err)
            await ws_server.close(code=aiohttp.WSCloseCode.INTERNAL_ERROR)

        return ws_server


def _strip_csp_upgrade(value: str) -> str:
    # camera.ui's CSP upgrades http->https
    directives = [
        d for d in value.split(";") if d.strip().lower() != "upgrade-insecure-requests"
    ]
    return ";".join(directives)


def _is_websocket(request: web.Request) -> bool:
    headers = request.headers
    return (
        "upgrade" in headers.get(hdrs.CONNECTION, "").lower()
        and headers.get(hdrs.UPGRADE, "").lower() == "websocket"
    )


def _get_loaded_entry(hass: HomeAssistant, entry_id: str) -> ConfigEntry | None:
    entry = hass.config_entries.async_get_entry(entry_id)
    if (
        not entry
        or entry.domain != DOMAIN
        or entry.state is not ConfigEntryState.LOADED
    ):
        return None
    return entry


def _get_entry_by_proxy_secret(hass: HomeAssistant, secret: str) -> ConfigEntry | None:
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.state is not ConfigEntryState.LOADED:
            continue
        stored = entry.data.get(CONF_PROXY_SECRET)
        if stored and hmac.compare_digest(stored, secret):
            return entry
    return None


async def _websocket_forward(
    ws_from: web.WebSocketResponse | aiohttp.ClientWebSocketResponse,
    ws_to: web.WebSocketResponse | aiohttp.ClientWebSocketResponse,
) -> None:
    try:
        async for msg in ws_from:
            if msg.type is aiohttp.WSMsgType.TEXT:
                await ws_to.send_str(msg.data)
            elif msg.type is aiohttp.WSMsgType.BINARY:
                await ws_to.send_bytes(msg.data)
            elif msg.type is aiohttp.WSMsgType.PING:
                await ws_to.ping()
            elif msg.type is aiohttp.WSMsgType.PONG:
                await ws_to.pong()
            elif ws_to.closed:
                # close_code is None on an abrupt drop, and extra carries the peer's
                # close reason as text while aiohttp wants bytes
                await ws_to.close(
                    code=ws_to.close_code or aiohttp.WSCloseCode.OK,
                    message=(msg.extra or "").encode(),
                )
    except (RuntimeError, ConnectionResetError):
        pass
