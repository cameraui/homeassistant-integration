from __future__ import annotations

import hmac
import secrets
import time

PANEL_COOKIE = "cameraui_panel"
PANEL_SESSION_TTL = 15 * 60  # seconds, SESSION_TTL_MS in panel.js
PANEL_PROXY_PREFIX = "/api/cameraui/proxy"


class PanelSessions:
    def __init__(self) -> None:
        self._sessions: dict[str, float] = {}

    def create(self) -> str:
        now = time.monotonic()
        self._sessions = {token: expires for token, expires in self._sessions.items() if expires > now}
        token = secrets.token_urlsafe(32)
        self._sessions[token] = now + PANEL_SESSION_TTL
        return token

    def valid(self, token: str | None) -> bool:
        if not token:
            return False
        now = time.monotonic()
        matched = False
        for stored, expires in self._sessions.items():
            matched |= hmac.compare_digest(stored.encode(), token.encode()) and expires > now
        return matched

    def clear(self) -> None:
        self._sessions.clear()


def panel_proxy_base(entry_id: str) -> str:
    return f"{PANEL_PROXY_PREFIX}/{entry_id}/"
