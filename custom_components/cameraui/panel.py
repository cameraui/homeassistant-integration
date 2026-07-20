from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components.frontend import (
    add_extra_js_url,
    async_register_built_in_panel,
    async_remove_panel,
)
from homeassistant.components.http import StaticPathConfig

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

PANEL_JS_URL = "/cameraui/panel.js"
ICON_JS_URL = "/cameraui/icon.js"


def _hashed(url: str, path: Path) -> str:
    if not path.is_file():
        return url
    digest = hashlib.md5(path.read_bytes()).hexdigest()[:12]
    return f"{url}?v={digest}"


_BASE = Path(__file__).parent
PANEL_JS_VERSIONED = _hashed(PANEL_JS_URL, _BASE / "panel.js")
ICON_JS_VERSIONED = _hashed(ICON_JS_URL, _BASE / "icon.js")


async def async_register_panel_static(hass: HomeAssistant) -> None:
    base = Path(__file__).parent
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(PANEL_JS_URL, str(base / "panel.js"), True),
            StaticPathConfig(ICON_JS_URL, str(base / "icon.js"), True),
        ]
    )
    add_extra_js_url(hass, ICON_JS_VERSIONED)


def _panel_url_path(entry_id: str) -> str:
    return f"cameraui-{entry_id}"


def async_register_panel(hass: HomeAssistant, entry: ConfigEntry, secret: str) -> None:
    async_register_built_in_panel(
        hass,
        "custom",
        sidebar_title="camera.ui",
        sidebar_icon="cameraui:logo",
        frontend_url_path=_panel_url_path(entry.entry_id),
        config={
            "_panel_custom": {
                "name": "cameraui-panel",
                "embed_iframe": False,
                "trust_external": False,
                "module_url": PANEL_JS_VERSIONED,
            },
            "proxyUrl": f"/api/cameraui/proxy/{secret}/",
        },
        require_admin=True,
    )


def async_unregister_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    async_remove_panel(hass, _panel_url_path(entry.entry_id))
