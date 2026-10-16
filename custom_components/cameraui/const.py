from __future__ import annotations

DOMAIN = "cameraui"

DEFAULT_PORT = 3443

CONF_TOKEN = "token"
CONF_PROXY_SECRET = "proxy_secret"
CONF_CARD_ACCESS = "card_access"
CONF_VIEWER_TOKEN = "viewer_token"
CONF_CLIP_QUALITY = "clip_quality"
CONF_ALLOW_UPDATES = "allow_updates"
CLIP_QUALITY_LOW = "low"
CLIP_QUALITY_HIGH = "high"
MIN_SERVER_VERSION = "2.1.13"
CARD_ACCESS_ADMINS = "admins"
CARD_ACCESS_ALL = "all_users"

SIGNAL_DETECTION = f"{DOMAIN}_detection"

# fired on the HA event bus for automations to trigger on
EVENT_CAMERAUI = f"{DOMAIN}_event"

# object-detection labels surfaced as binary sensors; mirrors the SDK OBJECT_DETECTION_LABELS
OBJECT_DETECTION_LABELS = ("person", "vehicle", "animal")


def signal_connection(entry_id: str) -> str:
    return f"{DOMAIN}_connection_{entry_id}"


def signal_sensor_new(entry_id: str) -> str:
    return f"{DOMAIN}_sensor_new_{entry_id}"


def signal_sensor_assigned(entry_id: str) -> str:
    return f"{DOMAIN}_sensor_assigned_{entry_id}"


def signal_sensor_update(sensor_id: str) -> str:
    return f"{DOMAIN}_sensor_update_{sensor_id}"


def signal_sensor_remove(sensor_id: str) -> str:
    return f"{DOMAIN}_sensor_remove_{sensor_id}"
