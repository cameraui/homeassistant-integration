from __future__ import annotations

from typing import Any

from homeassistant.const import Platform

# The server describes what each sensor means (camera/sensors/semantics.ts) and
# ships that description with every sensor. Translating a domain to an HA platform
# is all that is left here, so a new sensor type needs no change on this side.
DOMAIN_PLATFORM: dict[str, Platform] = {
    "binary": Platform.BINARY_SENSOR,
    "measurement": Platform.SENSOR,
    "switch": Platform.SWITCH,
    "light": Platform.LIGHT,
    "siren": Platform.SIREN,
    "lock": Platform.LOCK,
    "cover": Platform.COVER,
    "climate": Platform.CLIMATE,
    "fan": Platform.FAN,
    "valve": Platform.VALVE,
    "scene": Platform.SCENE,
    "humidifier": Platform.HUMIDIFIER,
    "airPurifier": Platform.FAN,
    "waterHeater": Platform.WATER_HEATER,
    "vacuum": Platform.VACUUM,
    "lawnMower": Platform.LAWN_MOWER,
    "mediaPlayer": Platform.MEDIA_PLAYER,
    "alarm": Platform.ALARM_CONTROL_PANEL,
    "event": Platform.EVENT,
    "text": Platform.TEXT,
}

# settings of a sensor (volume, tone, preset) sit there next to its main entity
SETTING_PLATFORMS = [Platform.NUMBER, Platform.SELECT]

SENSOR_PLATFORMS: list[Platform] = list(dict.fromkeys([*DOMAIN_PLATFORM.values(), *SETTING_PLATFORMS]))


def sensor_semantics(sensor: dict[str, Any]) -> dict[str, Any]:
    return sensor.get("semantics") or {}


def sensor_platform(sensor: dict[str, Any]) -> Platform | None:
    return DOMAIN_PLATFORM.get(sensor_semantics(sensor).get("domain", ""))
