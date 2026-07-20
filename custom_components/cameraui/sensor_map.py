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
    "alarm": Platform.ALARM_CONTROL_PANEL,
}

SENSOR_PLATFORMS: list[Platform] = list(dict.fromkeys(DOMAIN_PLATFORM.values()))


def sensor_semantics(sensor: dict[str, Any]) -> dict[str, Any]:
    return sensor.get("semantics") or {}


def sensor_platform(sensor: dict[str, Any]) -> Platform | None:
    """The HA platform a sensor belongs on, or None if it is not exposable."""
    return DOMAIN_PLATFORM.get(sensor_semantics(sensor).get("domain", ""))
