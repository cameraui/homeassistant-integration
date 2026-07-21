from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import CameraUiConfigEntry
from .const import CONF_PROXY_SECRET, CONF_TOKEN

TO_REDACT = {CONF_TOKEN, CONF_PROXY_SECRET, "token", "password", "secret", "source", "sources", "url"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: CameraUiConfigEntry
) -> dict[str, Any]:
    coordinator = entry.runtime_data.coordinator
    return {
        "entry": async_redact_data(entry.data, TO_REDACT),
        "events_connected": coordinator.client.events_connected,
        "last_update_success": coordinator.last_update_success,
        "cameras": async_redact_data(coordinator.data, TO_REDACT),
    }
