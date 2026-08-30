from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

LEGACY_CARD_URL = "/cameraui/cameraui-card.js"
CARDS_URL_PREFIX = "/api/cameraui/cards"
CARDS_BUNDLE = "cameraui-cards.js"


# the cards bundle is built and served by the camera.ui server (same version as the backend); the
# integration only points Lovelace at it
async def async_register_cards_bundle(hass: HomeAssistant, entry_id: str, version: str) -> None:
    base = f"{CARDS_URL_PREFIX}/{entry_id}/"
    await _async_register_resource(hass, base, f"{base}{CARDS_BUNDLE}?v={version}")
    await _async_remove_resource(hass, LEGACY_CARD_URL)


async def async_unregister_cards_bundle(hass: HomeAssistant, entry_id: str) -> None:
    await _async_remove_resource(hass, f"{CARDS_URL_PREFIX}/{entry_id}/")


async def _get_resources(hass: HomeAssistant) -> ResourceStorageCollection | Any | None:
    lovelace = hass.data.get("lovelace")
    resources = getattr(lovelace, "resources", None)
    if not resources:
        return None
    if not resources.loaded:
        await resources.async_load()
        resources.loaded = True
    return resources


async def _async_register_resource(hass: HomeAssistant, base_url: str, versioned_url: str) -> None:
    resources = await _get_resources(hass)
    if not resources:
        return

    storage_mode = isinstance(resources, ResourceStorageCollection)

    for item in resources.async_items():
        url = item.get("url", "")
        if not url.startswith(base_url):
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


async def _async_remove_resource(hass: HomeAssistant, base_url: str) -> None:
    resources = await _get_resources(hass)
    if not isinstance(resources, ResourceStorageCollection):
        return
    for item in list(resources.async_items()):
        if item.get("url", "").startswith(base_url):
            await resources.async_delete_item(item["id"])
