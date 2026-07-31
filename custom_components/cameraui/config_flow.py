from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import CameraUiApiError, CameraUiAuthError, CameraUiClient
from .const import CONF_TOKEN, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_TOKEN): str,
    }
)

STEP_TOKEN_SCHEMA = vol.Schema({vol.Required(CONF_TOKEN): str})


class CameraUiConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._host: str | None = None
        self._port: int = DEFAULT_PORT

    async def _validate(self, host: str, port: int, token: str) -> tuple[dict[str, str], dict[str, Any]]:
        errors: dict[str, str] = {}
        info: dict[str, Any] = {}
        client = CameraUiClient(host, port, token, async_get_clientsession(self.hass, verify_ssl=False))
        try:
            info = await client.validate()
        except CameraUiAuthError as err:
            _LOGGER.warning("Validation against %s:%s failed with auth error: %s", host, port, err)
            errors["base"] = "invalid_auth"
        except CameraUiApiError as err:
            _LOGGER.warning("Validation against %s:%s failed: %s", host, port, err)
            errors["base"] = "cannot_connect"
        return errors, info

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            errors, info = await self._validate(
                user_input[CONF_HOST], user_input[CONF_PORT], user_input[CONF_TOKEN]
            )
            if not errors:
                unique_id = info.get("instanceId") or f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors)

    async def _async_reachable(self, host: str, port: int) -> bool:
        session = async_get_clientsession(self.hass, verify_ssl=False)
        try:
            async with asyncio.timeout(5):
                await session.get(f"https://{host}:{port}/api/", ssl=False)
        except (TimeoutError, aiohttp.ClientError):
            return False
        return True

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo) -> ConfigFlowResult:
        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT
        instance_id = discovery_info.properties.get("id")
        if instance_id:
            await self.async_set_unique_id(instance_id)
            entry = next(
                (e for e in self._async_current_entries(include_ignore=False) if e.unique_id == instance_id),
                None,
            )
            # servers in docker may announce bridge addresses, never trade a stored host for one we can't reach
            if (
                entry
                and (entry.data[CONF_HOST], entry.data[CONF_PORT]) != (host, port)
                and not await self._async_reachable(host, port)
            ):
                return self.async_abort(reason="already_configured")
            self._abort_if_unique_id_configured(updates={CONF_HOST: host, CONF_PORT: port})

        self._host = host
        self._port = port
        self.context["title_placeholders"] = {"host": self._host}
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        assert self._host is not None

        if user_input is not None:
            errors, info = await self._validate(self._host, self._port, user_input[CONF_TOKEN])
            if not errors:
                if not self.unique_id and info.get("instanceId"):
                    await self.async_set_unique_id(info["instanceId"])
                    self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=self._host,
                    data={CONF_HOST: self._host, CONF_PORT: self._port, CONF_TOKEN: user_input[CONF_TOKEN]},
                )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=STEP_TOKEN_SCHEMA,
            errors=errors,
            description_placeholders={"host": self._host},
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            errors, info = await self._validate(
                entry.data[CONF_HOST], entry.data[CONF_PORT], user_input[CONF_TOKEN]
            )
            if not errors:
                if info.get("instanceId"):
                    await self.async_set_unique_id(info["instanceId"])
                    self._abort_if_unique_id_mismatch(reason="wrong_account")
                return self.async_update_reload_and_abort(entry, data_updates=user_input)

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_TOKEN_SCHEMA,
            errors=errors,
            description_placeholders={"host": entry.data[CONF_HOST]},
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            errors, info = await self._validate(
                user_input[CONF_HOST], user_input[CONF_PORT], user_input[CONF_TOKEN]
            )
            if not errors:
                if info.get("instanceId"):
                    await self.async_set_unique_id(info["instanceId"])
                    self._abort_if_unique_id_mismatch(reason="wrong_account")
                return self.async_update_reload_and_abort(entry, data_updates=user_input)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(STEP_USER_SCHEMA, entry.data),
            errors=errors,
        )
