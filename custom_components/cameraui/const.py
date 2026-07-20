from __future__ import annotations

DOMAIN = "cameraui"

DEFAULT_PORT = 3443

CONF_TOKEN = "token"
CONF_PROXY_SECRET = "proxy_secret"

SIGNAL_DETECTION = f"{DOMAIN}_detection"
SIGNAL_CONNECTION = f"{DOMAIN}_connection"
SIGNAL_SENSOR_NEW = f"{DOMAIN}_sensor_new"

# fired on the HA event bus for automations to trigger on
EVENT_CAMERAUI = f"{DOMAIN}_event"

# object-detection labels surfaced as binary sensors; mirrors the SDK OBJECT_DETECTION_LABELS
OBJECT_DETECTION_LABELS = ("person", "vehicle", "animal", "package")

OBJECT_LABEL_ICONS = {
    "person": "mdi:account",
    "vehicle": "mdi:car",
    "animal": "mdi:paw",
    "package": "mdi:package-variant-closed",
}


def signal_sensor_update(stable_id: str) -> str:
    return f"{DOMAIN}_sensor_update_{stable_id}"


def signal_sensor_remove(stable_id: str) -> str:
    return f"{DOMAIN}_sensor_remove_{stable_id}"
