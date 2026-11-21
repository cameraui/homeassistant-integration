from __future__ import annotations

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

# from Home Assistant 2026.8 on an identifier is unique per config entry only, 2026.3 is still supported
_PER_ENTRY = hasattr(dr.DeviceRegistry, "async_get_device_by_identifier")


@callback
def async_get_device(
    hass: HomeAssistant, identifier: tuple[str, str], entry_id: str
) -> dr.DeviceEntry | None:
    registry = dr.async_get(hass)
    if _PER_ENTRY:
        return registry.async_get_device_by_identifier(identifier, entry_id)
    return registry.async_get_device(identifiers={identifier})


@callback
def async_remove_device_if_empty(hass: HomeAssistant, device_id: str) -> None:
    if not er.async_entries_for_device(er.async_get(hass), device_id, include_disabled_entities=True):
        dr.async_get(hass).async_remove_device(device_id)


@callback
def async_remove_empty_sensor_devices(hass: HomeAssistant, entry_id: str) -> None:
    for device in dr.async_entries_for_config_entry(dr.async_get(hass), entry_id):
        if any(
            domain == DOMAIN and ident.startswith(("sensor_", "device_"))
            for domain, ident in device.identifiers
        ):
            async_remove_device_if_empty(hass, device.id)


@callback
def async_set_via_device(
    hass: HomeAssistant, info: DeviceInfo, parent: tuple[str, str], entry_id: str
) -> None:
    if not _PER_ENTRY:
        info["via_device"] = parent
    elif device := async_get_device(hass, parent, entry_id):
        info["via_device_id"] = device.id
