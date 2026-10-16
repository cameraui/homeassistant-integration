from __future__ import annotations

import asyncio
import contextlib
import gzip
import hmac
import logging
import re
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiohttp
from aiohttp import hdrs, web
from homeassistant.components.http import KEY_HASS, KEY_HASS_USER, HomeAssistantView
from homeassistant.components.http.auth import SIGN_QUERY_PARAM
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from yarl import URL

from .api import bundle_tag
from .clips import ClipDownload, async_find_event
from .const import (
    CARD_ACCESS_ADMINS,
    CARD_ACCESS_ALL,
    CONF_CARD_ACCESS,
    CONF_PROXY_SECRET,
    CONF_TOKEN,
    CONF_VIEWER_TOKEN,
    DOMAIN,
)
from .rpc import CameraUiRpcError

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

CARDS_ASSET_NAME = re.compile(r"^[\w.-]+\.js$")
CARDS_BUNDLE = "cameraui-cards.js"
CARDS_TAGGED_BUNDLE = re.compile(r"^cameraui-cards\.(\w+)\.js$")
CARDS_IMPORT = re.compile(rb"""["'`]\./([\w.-]+\.js)["'`]""")
CARDS_FONT_NAME = re.compile(r"^[\w.-]+\.woff2$")
FONT_CONTENT_TYPE = "font/woff2"
CONDITIONAL_HEADERS = (hdrs.IF_NONE_MATCH, hdrs.IF_MODIFIED_SINCE)
GZIP_ACCEPTED = re.compile(r"\bgzip\b", re.IGNORECASE)
PASSTHROUGH_HEADERS = (hdrs.CONTENT_TYPE, hdrs.ETAG, hdrs.LAST_MODIFIED)
MAX_WS_MESSAGE_SIZE = 16 * 1024 * 1024
PROXY_TIMEOUT = aiohttp.ClientTimeout(total=None, connect=30, sock_connect=10)
ASSET_TIMEOUT = aiohttp.ClientTimeout(total=None, connect=5, sock_connect=3, sock_read=10)
WS_UPSTREAM_LOST = 4500
WS_FORBIDDEN = 4403
WS_UNAUTHORIZED = 4401

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
# proxied bodies stay encoded, so their Content-Encoding goes along
RESPONSE_HOP_BY_HOP = HOP_BY_HOP - {hdrs.CONTENT_ENCODING}
PROXY_PREFIX = "/api/cameraui/proxy"
VIDEO_RELAY_PATH = "api/go2rtc"


class CameraUiProxyView(HomeAssistantView):
    name = "api:cameraui:proxy"
    url = "/api/cameraui/proxy/{secret}/{path:.*}"
    requires_auth = False

    async def _handle(self, request: web.Request, secret: str, path: str) -> web.StreamResponse:
        hass = request.app[KEY_HASS]

        entry = _get_entry_by_proxy_secret(hass, secret)
        if not entry:
            raise web.HTTPNotFound

        if _is_websocket(request):
            return await _proxy_ws(request, entry, path, entry.data[CONF_TOKEN])
        return await _proxy_http(
            request, entry, path, entry.data[CONF_TOKEN], base=f"{PROXY_PREFIX}/{secret}/"
        )

    get = _handle
    post = _handle
    put = _handle
    delete = _handle
    patch = _handle


class CameraUiAuthProxyView(HomeAssistantView):
    # same forwarder as the secret proxy, but the caller authenticates as an HA user: Bearer header
    # for HTTP, a signed path for WebSockets. Serves the dashboard cards, not the embedded SPA.
    name = "api:cameraui:auth"
    url = "/api/cameraui/auth/{entry_id}/{path:.*}"
    requires_auth = True

    async def _handle(self, request: web.Request, entry_id: str, path: str) -> web.StreamResponse:
        hass = request.app[KEY_HASS]

        entry = _get_loaded_entry(hass, entry_id)
        if not entry:
            raise web.HTTPNotFound
        if not _card_access_allowed(request, entry):
            raise web.HTTPForbidden

        token = _card_token(request, entry)
        if _is_websocket(request):
            return await _proxy_ws(request, entry, path, token)
        return await _proxy_http(request, entry, path, token, base=None)

    get = _handle
    post = _handle
    put = _handle
    delete = _handle
    patch = _handle


class CameraUiCardsAssetView(HomeAssistantView):
    # Lovelace loads resources with a plain <script>, so the cards bundle (public JS built by the
    # camera.ui server) is served without HA auth. Only bundle files, never the token. The registered
    # URL redirects to a name carrying the server's ETag, so every build gets a fresh module URL and
    # the tagged file can be cached forever. Every file served is mirrored to disk: with the server
    # down the dashboard still renders the cards, which then show camera.ui's own offline state.
    name = "api:cameraui:cards"
    url = "/api/cameraui/cards/{entry_id}/{file}"
    requires_auth = False

    async def get(self, request: web.Request, entry_id: str, file: str) -> web.StreamResponse:
        hass = request.app[KEY_HASS]
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry or entry.domain != DOMAIN or not CARDS_ASSET_NAME.match(file):
            raise web.HTTPNotFound
        mirror = _CardsMirror(hass, entry_id)

        if file == CARDS_BUNDLE:
            tag = await self._upstream_tag(hass, entry)
            if tag:
                await mirror.remember_tag(tag)
            else:
                tag = await mirror.last_tag()
            if not tag:
                raise web.HTTPBadGateway
            raise web.HTTPFound(
                f"/api/cameraui/cards/{entry_id}/cameraui-cards.{tag}.js",
                headers={hdrs.CACHE_CONTROL: "no-store"},
            )

        tagged = CARDS_TAGGED_BUNDLE.match(file)
        upstream_file = CARDS_BUNDLE if tagged else file
        headers = {name: request.headers[name] for name in CONDITIONAL_HEADERS if name in request.headers}
        # the mirror keeps plain files and Python only unpacks gzip, so gzip is the one encoding passed on
        gzip_ok = GZIP_ACCEPTED.search(request.headers.get(hdrs.ACCEPT_ENCODING, ""))
        headers[hdrs.ACCEPT_ENCODING] = "gzip" if gzip_ok else "identity"
        session = async_get_clientsession(hass, verify_ssl=False)
        try:
            async with session.get(
                _cards_url(entry, upstream_file),
                headers=headers,
                allow_redirects=False,
                auto_decompress=False,
                timeout=ASSET_TIMEOUT,
            ) as upstream:
                if upstream.status == 304:
                    return _cards_response(304, upstream.headers)
                if upstream.status != 200:
                    raise web.HTTPNotFound
                encoding = upstream.headers.get(hdrs.CONTENT_ENCODING, "identity")
                if encoding not in ("gzip", "identity"):
                    raise web.HTTPBadGateway
                body = await upstream.read()
                plain = (
                    await hass.async_add_executor_job(gzip.decompress, body) if encoding == "gzip" else body
                )
                await mirror.store(file, plain)
                if tagged:
                    await mirror.bundle_stored(tagged[1])
                return _cards_response(200, upstream.headers, body)
        except (aiohttp.ClientError, TimeoutError) as err:
            cached = await mirror.load(file)
            if cached is None:
                _LOGGER.debug("Cards asset %s failed and is not mirrored: %s", file, err)
                raise web.HTTPBadGateway from err
            return _cards_response(200, None, cached)

    async def _upstream_tag(self, hass: HomeAssistant, entry: ConfigEntry) -> str | None:
        session = async_get_clientsession(hass, verify_ssl=False)
        try:
            async with session.head(
                _cards_url(entry, CARDS_BUNDLE), allow_redirects=False, timeout=ASSET_TIMEOUT
            ) as head:
                if head.status != 200:
                    return None
                return bundle_tag(head.headers)
        except aiohttp.ClientError, TimeoutError:
            return None


class CameraUiCardsFontView(HomeAssistantView):
    name = "api:cameraui:cards:fonts"
    url = "/api/cameraui/cards/{entry_id}/fonts/{file}"
    requires_auth = False

    async def get(self, request: web.Request, entry_id: str, file: str) -> web.Response:
        hass = request.app[KEY_HASS]
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry or entry.domain != DOMAIN or not CARDS_FONT_NAME.match(file):
            raise web.HTTPNotFound
        mirror = _CardsMirror(hass, entry_id)
        key = f"fonts/{file}"
        upstream_url = URL.build(
            scheme="https", host=entry.data[CONF_HOST], port=entry.data[CONF_PORT], path=f"/fonts/{file}"
        )
        session = async_get_clientsession(hass, verify_ssl=False)
        try:
            async with session.get(upstream_url, allow_redirects=False, timeout=ASSET_TIMEOUT) as upstream:
                if upstream.status != 200:
                    raise web.HTTPNotFound
                body = await upstream.read()
                await mirror.store(key, body)
                return _asset_response(200, upstream.headers, body, FONT_CONTENT_TYPE)
        except (aiohttp.ClientError, TimeoutError) as err:
            cached = await mirror.load(key)
            if cached is None:
                raise web.HTTPBadGateway from err
            return _asset_response(200, None, cached, FONT_CONTENT_TYPE)


class CameraUiNotifyAssetView(HomeAssistantView):
    name = "api:cameraui:notify"
    url = "/api/cameraui/notify/{path:.*}"
    requires_auth = True

    async def get(self, request: web.Request, path: str) -> web.Response:
        hass = request.app[KEY_HASS]
        session = async_get_clientsession(hass, verify_ssl=False)
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.state is not ConfigEntryState.LOADED:
                continue
            upstream_url = URL.build(
                scheme="https", host=entry.data[CONF_HOST], port=entry.data[CONF_PORT], path=f"/{path}"
            )
            try:
                async with session.get(upstream_url) as upstream:
                    if upstream.status != 200:
                        continue
                    body = await upstream.read()
                    return web.Response(
                        body=body,
                        content_type=upstream.content_type,
                        headers={hdrs.CACHE_CONTROL: "private, max-age=600"},
                    )
            except aiohttp.ClientError:
                continue
        raise web.HTTPNotFound


class CameraUiMediaView(HomeAssistantView):
    name = "api:cameraui:media"
    url = "/api/cameraui/media/{entry_id}/{kind}/{path:.*}"
    requires_auth = True

    async def get(self, request: web.Request, entry_id: str, kind: str, path: str) -> web.StreamResponse:
        hass = request.app[KEY_HASS]
        entry = _get_loaded_entry(hass, entry_id)
        parts = path.split("/")
        if not entry or len(parts) not in (3, 4):
            raise web.HTTPNotFound
        runtime = entry.runtime_data
        try:
            if kind == "thumb" and len(parts) == 3:
                image = await runtime.rpc.get_event_thumbnail(parts[0], int(parts[1]), parts[2])
                if not image:
                    raise web.HTTPNotFound
                return web.Response(
                    body=image,
                    content_type="image/jpeg",
                    headers={hdrs.CACHE_CONTROL: "private, max-age=3600"},
                )
            if kind == "clip":
                return await _clip_response(request, await _open_clip(entry, *parts), parts[2])
        except ValueError as err:
            raise web.HTTPNotFound from err
        except CameraUiRpcError as err:
            _LOGGER.warning("Media request failed: %s", err)
            raise web.HTTPBadGateway from err
        raise web.HTTPNotFound


async def _open_clip(
    entry: ConfigEntry, camera_id: str, day: str, event_id: str, start: str | None = None
) -> Path | ClipDownload:
    clips = entry.runtime_data.clips
    ready = await clips.cached(event_id)
    if ready is not None:
        return ready
    event = await async_find_event(entry, camera_id, day, event_id, int(start) if start else None)
    if not event:
        raise web.HTTPNotFound
    return await clips.open(camera_id, event_id, event["startTime"], event["endTime"])


async def _clip_response(
    request: web.Request, ready: Path | ClipDownload, event_id: str
) -> web.StreamResponse:
    headers = {hdrs.CONTENT_TYPE: "video/mp4"}
    byte_range = request.headers.get(hdrs.RANGE, "").replace(" ", "")
    if isinstance(ready, ClipDownload) and byte_range and byte_range != "bytes=0-":
        ready = await ready.file()
    if isinstance(ready, Path):
        return web.FileResponse(ready, headers=headers)
    started = time.monotonic()
    response = web.StreamResponse(status=200, headers=headers)
    await response.prepare(request)
    sent = 0
    async with contextlib.aclosing(ready.stream()) as chunks:
        async for chunk in chunks:
            sent += len(chunk)
            await response.write(chunk)
    await response.write_eof()
    _LOGGER.debug("clip %s streamed %d bytes in %.1fs", event_id[:8], sent, time.monotonic() - started)
    return response


def _asset_response(
    status: int, upstream_headers: Any, body: bytes | None = None, content_type: str = "text/javascript"
) -> web.Response:
    headers = {
        hdrs.CACHE_CONTROL: "public, max-age=31536000, immutable",
        hdrs.CONTENT_TYPE: content_type,
    }
    if upstream_headers is not None:
        for name in PASSTHROUGH_HEADERS:
            if name in upstream_headers:
                headers[name] = upstream_headers[name]
    return web.Response(status=status, headers=headers, body=body)


def _cards_response(status: int, upstream_headers: Any, body: bytes | None = None) -> web.Response:
    response = _asset_response(status, upstream_headers, body)
    response.headers[hdrs.VARY] = hdrs.ACCEPT_ENCODING
    if upstream_headers is not None and upstream_headers.get(hdrs.CONTENT_ENCODING) == "gzip":
        response.headers[hdrs.CONTENT_ENCODING] = "gzip"
    return response


class _CardsMirror:
    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._hass = hass
        self._dir = Path(hass.config.path(".storage", "cameraui_cards", entry_id))

    async def remember_tag(self, tag: str) -> None:
        await self._hass.async_add_executor_job(self._write_tag, tag)

    async def last_tag(self) -> str | None:
        return await self._hass.async_add_executor_job(self._read_tag)

    async def bundle_stored(self, tag: str) -> None:
        await self._hass.async_add_executor_job(self._switch_tag, tag)

    async def store(self, file: str, body: bytes) -> None:
        await self._hass.async_add_executor_job(self._write_file, file, body)

    async def load(self, file: str) -> bytes | None:
        return await self._hass.async_add_executor_job(self._read_file, file)

    def _write_tag(self, tag: str) -> None:
        latest = self._read_tag()
        if latest == tag:
            (self._dir / "pending").unlink(missing_ok=True)
        elif latest is None:
            self._write_file("latest", tag.encode())
        else:
            # a new build takes over once its bundle is mirrored, until then the old one stays complete
            self._write_file("pending", tag.encode())

    def _switch_tag(self, tag: str) -> None:
        pending = self._dir / "pending"
        if self._read_marker(pending) != tag:
            return
        previous = self._read_tag()
        if previous == tag:
            # another request switched already, a second pass would drop the previous build's chunks
            pending.unlink(missing_ok=True)
            return
        # chunks a build shares with the one before keep their names and sit in browser caches, a
        # browser never fetches them again. Keep everything both bundles import, drop older builds
        keep = self._imported([f"cameraui-cards.{name}.js" for name in (tag, previous) if name])
        self._write_file("latest", tag.encode())
        pending.unlink(missing_ok=True)
        for old in self._dir.glob("*.js"):
            if old.name not in keep:
                old.unlink(missing_ok=True)

    def _imported(self, roots: list[str]) -> set[str]:
        seen: set[str] = set()
        queue = list(roots)
        while queue:
            name = queue.pop()
            if name in seen:
                continue
            seen.add(name)
            path = self._dir / name
            if path.is_file():
                queue.extend(match.decode() for match in CARDS_IMPORT.findall(path.read_bytes()))
        return seen

    def _read_tag(self) -> str | None:
        return self._read_marker(self._dir / "latest")

    @staticmethod
    def _read_marker(marker: Path) -> str | None:
        # markers change from parallel executor jobs, a missing one reads as unset
        try:
            tag = marker.read_text().strip()
        except OSError:
            return None
        return tag if tag.isalnum() else None

    def _write_file(self, file: str, body: bytes) -> None:
        target = self._dir / file
        target.parent.mkdir(parents=True, exist_ok=True)
        # parallel requests can store the same file, a shared tmp would vanish under one of them
        tmp = target.with_name(f"{target.name}.{threading.get_ident()}.tmp")
        tmp.write_bytes(body)
        tmp.replace(target)

    def _read_file(self, file: str) -> bytes | None:
        path = self._dir / file
        return path.read_bytes() if path.is_file() else None


def _cards_url(entry: ConfigEntry, file: str) -> URL:
    return URL.build(
        scheme="https", host=entry.data[CONF_HOST], port=entry.data[CONF_PORT], path=f"/ha/{file}"
    )


def _card_token(request: web.Request, entry: ConfigEntry) -> str:
    user = request.get(KEY_HASS_USER)
    viewer = entry.options.get(CONF_VIEWER_TOKEN)
    if viewer and not (user and user.is_admin):
        return str(viewer)
    return str(entry.data[CONF_TOKEN])


def _card_access_allowed(request: web.Request, entry: ConfigEntry) -> bool:
    if entry.options.get(CONF_CARD_ACCESS, CARD_ACCESS_ADMINS) == CARD_ACCESS_ALL:
        return True
    user = request.get(KEY_HASS_USER)
    return bool(user and user.is_admin)


async def _proxy_http(
    request: web.Request, entry: ConfigEntry, path: str, token: str, base: str | None
) -> web.StreamResponse:
    hass = request.app[KEY_HASS]
    query = {key: value for key, value in request.query.items() if key != SIGN_QUERY_PARAM}
    upstream_url = URL.build(
        scheme="https",
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        path=f"/{path}",
        query=query,
    )

    headers = {name: value for name, value in request.headers.items() if name not in HOP_BY_HOP}
    headers[hdrs.AUTHORIZATION] = f"Bearer {token}"
    if base:
        headers["X-Cui-Base"] = base
    headers["X-Cui-Embed"] = "homeassistant"
    # without it the server limits itself to gzip for proxies that decode and drop Content-Encoding
    headers["X-Cui-Encoding"] = "passthrough"

    session = async_get_clientsession(hass, verify_ssl=False)
    try:
        async with session.request(
            request.method,
            upstream_url,
            headers=headers,
            data=request.content if request.body_exists else None,
            allow_redirects=False,
            # only the browser's own Accept-Encoding counts, it gets the body as the server encoded it
            skip_auto_headers=(hdrs.CONTENT_TYPE, hdrs.ACCEPT_ENCODING),
            auto_decompress=False,
            timeout=PROXY_TIMEOUT,
        ) as upstream:
            response = web.StreamResponse(status=upstream.status)
            for name, value in upstream.headers.items():
                if name in RESPONSE_HOP_BY_HOP:
                    continue
                if name.lower() == "content-security-policy":
                    value = _strip_csp_upgrade(value)
                response.headers[name] = value
            await response.prepare(request)
            async for chunk in upstream.content.iter_chunked(65536):
                await response.write(chunk)
            return response
    except TimeoutError as err:
        _LOGGER.debug("Proxy request to %s timed out", path)
        raise web.HTTPGatewayTimeout from err
    except aiohttp.ClientError as err:
        _LOGGER.debug("Proxy request to %s failed: %s", path, _describe_error(err))
        raise web.HTTPBadGateway from err


async def _proxy_ws(request: web.Request, entry: ConfigEntry, path: str, token: str) -> web.WebSocketResponse:
    hass = request.app[KEY_HASS]
    query = {key: value for key, value in request.query.items() if key != SIGN_QUERY_PARAM}
    query["token"] = token
    upstream_url = URL.build(
        scheme="wss",
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        path=f"/{path}",
        query=query,
    )

    protocols: list[str] = []
    if hdrs.SEC_WEBSOCKET_PROTOCOL in request.headers:
        protocols = [proto.strip() for proto in request.headers[hdrs.SEC_WEBSOCKET_PROTOCOL].split(",")]

    ws_server = web.WebSocketResponse(
        protocols=protocols,
        autoclose=False,
        autoping=False,
        max_msg_size=MAX_WS_MESSAGE_SIZE,
        compress=not _is_video_relay(path),
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
            to_upstream = asyncio.create_task(_websocket_forward(ws_server, ws_client))
            to_browser = asyncio.create_task(_websocket_forward(ws_client, ws_server))
            forwards = (to_upstream, to_browser)
            try:
                await asyncio.wait(forwards, return_when=asyncio.FIRST_COMPLETED)
            finally:
                for task in forwards:
                    task.cancel()
                await asyncio.wait(forwards)
            if not to_upstream.cancelled() and to_upstream.result() is not None:
                await ws_server.close()
            else:
                last = None if to_browser.cancelled() else to_browser.result()
                code, reason = _browser_close(last)
                await ws_server.close(code=code, message=reason)
    except (aiohttp.ClientError, TimeoutError) as err:
        _LOGGER.warning("Proxy WebSocket to %s failed: %s", path, _describe_error(err))
        await ws_server.close(code=WS_UPSTREAM_LOST, message=b"upstream lost")

    return ws_server


def _browser_close(last: aiohttp.WSMessage | None) -> tuple[int, bytes]:
    if last is None or last.type is not aiohttp.WSMsgType.CLOSE:
        return WS_UPSTREAM_LOST, b"upstream lost"
    code = int(last.data)
    reason = (last.extra or "").encode()
    if code == WS_UNAUTHORIZED:
        # the integration's own token was rejected, a fresh browser token cannot fix that
        return WS_FORBIDDEN, b"forbidden: integration token rejected"
    if not _is_sendable_close_code(code):
        return aiohttp.WSCloseCode.OK, reason
    return code, reason


def _is_sendable_close_code(code: int) -> bool:
    return (1000 <= code <= 1014 and code not in (1004, 1005, 1006)) or 3000 <= code <= 4999


def _describe_error(err: Exception) -> str:
    if isinstance(err, aiohttp.ClientResponseError):
        return f"{err.status} {err.message}"
    return type(err).__name__


def _strip_csp_upgrade(value: str) -> str:
    # camera.ui's CSP upgrades http->https
    directives = [d for d in value.split(";") if d.strip().lower() != "upgrade-insecure-requests"]
    return ";".join(directives)


def _is_video_relay(path: str) -> bool:
    path = path.strip("/")
    return path == VIDEO_RELAY_PATH or path.startswith(f"{VIDEO_RELAY_PATH}/")


def _is_websocket(request: web.Request) -> bool:
    headers = request.headers
    return (
        "upgrade" in headers.get(hdrs.CONNECTION, "").lower()
        and headers.get(hdrs.UPGRADE, "").lower() == "websocket"
    )


def _get_loaded_entry(hass: HomeAssistant, entry_id: str) -> ConfigEntry | None:
    entry = hass.config_entries.async_get_entry(entry_id)
    if not entry or entry.domain != DOMAIN or entry.state is not ConfigEntryState.LOADED:
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
) -> aiohttp.WSMessage | None:
    try:
        while True:
            msg = await ws_from.receive()
            if msg.type is aiohttp.WSMsgType.TEXT:
                await ws_to.send_str(msg.data)
            elif msg.type is aiohttp.WSMsgType.BINARY:
                await ws_to.send_bytes(msg.data)
            elif msg.type is aiohttp.WSMsgType.PING:
                await ws_to.ping()
            elif msg.type is aiohttp.WSMsgType.PONG:
                await ws_to.pong()
            else:
                return msg
    except RuntimeError, ConnectionResetError:
        return None
