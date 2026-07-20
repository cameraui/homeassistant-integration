from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

CARD_URL = "/cameraui/cameraui-card.js"


async def async_register_card(hass: HomeAssistant) -> None:
    card_path = Path(__file__).parent / "www" / "cameraui-card.js"
    if not card_path.is_file():
        _LOGGER.warning("Card bundle missing at %s, the cameraui-card will not be available", card_path)
        return

    await hass.http.async_register_static_paths([StaticPathConfig(CARD_URL, str(card_path), True)])

    digest = await hass.async_add_executor_job(lambda: hashlib.md5(card_path.read_bytes()).hexdigest()[:12])
    await _async_register_resource(hass, f"{CARD_URL}?v={digest}")


async def _async_register_resource(hass: HomeAssistant, versioned_url: str) -> None:
    lovelace = hass.data.get("lovelace")
    resources = getattr(lovelace, "resources", None)
    if not resources:
        return

    if not resources.loaded:
        await resources.async_load()
        resources.loaded = True

    storage_mode = isinstance(resources, ResourceStorageCollection)

    for item in resources.async_items():
        url = item.get("url", "")
        if not url.startswith(CARD_URL):
            continue
        if url == versioned_url:
            return
        if storage_mode:
            await resources.async_update_item(item["id"], {"res_type": "module", "url": versioned_url})
        return

    if storage_mode:
        await resources.async_create_item({"res_type": "module", "url": versioned_url})
    else:
        # yaml mode has no writable resource store, inject for this run
        add_extra_js_url(hass, versioned_url)
