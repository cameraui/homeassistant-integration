from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, EVENT_CAMERAUI

# trigger type -> the `state` field the cameraui_event carries
TRIGGER_STATES = {
    "detection_started": "start",
    "detection_ended": "end",
    "detection_recognized": "recognized",
}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend({vol.Required(CONF_TYPE): vol.In(TRIGGER_STATES)})


async def async_get_triggers(hass: HomeAssistant, device_id: str) -> list[dict[str, Any]]:
    return [
        {CONF_PLATFORM: "device", CONF_DOMAIN: DOMAIN, CONF_DEVICE_ID: device_id, CONF_TYPE: trigger_type}
        for trigger_type in TRIGGER_STATES
    ]


async def async_attach_trigger(
    hass: HomeAssistant, config: ConfigType, action: TriggerActionType, trigger_info: TriggerInfo
) -> CALLBACK_TYPE:
    device = dr.async_get(hass).async_get(config[CONF_DEVICE_ID])
    camera_id = (
        next((ident for domain, ident in device.identifiers if domain == DOMAIN), None) if device else None
    )

    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: EVENT_CAMERAUI,
            event_trigger.CONF_EVENT_DATA: {
                "camera_id": camera_id,
                "state": TRIGGER_STATES[config[CONF_TYPE]],
            },
        }
    )
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
