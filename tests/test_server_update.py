from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.cameraui.api import CameraUiApiError, CameraUiClient
from custom_components.cameraui.update import CameraUiServerUpdateEntity

LEFT_BEHIND = "winpc would no longer connect to camera.ui 2.4.0. Update them first or confirm the update."


class Response:
    def __init__(self, status: int, body: Any) -> None:
        self.status = status
        self._body = body

    async def json(self, content_type: str | None = None) -> Any:
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


class Session:
    def __init__(self, response: Response) -> None:
        self.response = response

    async def request(self, method: str, url: str, **kwargs: Any) -> Response:
        return self.response


async def test_a_refused_request_carries_the_reason_of_the_server() -> None:
    session: Any = Session(Response(409, {"statusCode": 409, "message": LEFT_BEHIND}))
    client = CameraUiClient("cameraui.local", 443, "token", session)

    with pytest.raises(CameraUiApiError) as caught:
        await client.update_server("2.4.0")

    assert caught.value.status == 409
    assert str(caught.value) == f"Request to /server/update returned 409: {LEFT_BEHIND}"


async def test_a_refused_request_without_a_json_body_keeps_the_status() -> None:
    session: Any = Session(Response(502, ValueError("not json")))
    client = CameraUiClient("cameraui.local", 443, "token", session)

    with pytest.raises(CameraUiApiError, match=r"^Request to /server/update returned 502$"):
        await client.update_server("2.4.0")


async def test_a_server_update_the_server_refuses_shows_why_and_does_not_restart() -> None:
    restarts: list[bool] = []

    class Client:
        async def update_server(self, version: str) -> None:
            raise CameraUiApiError(f"Request to /server/update returned 409: {LEFT_BEHIND}", status=409)

        async def restart_server(self) -> None:
            restarts.append(True)

    coordinator = SimpleNamespace(client=Client(), data={"server": {"installed": "2.3.0", "latest": "2.4.0"}})
    entity = CameraUiServerUpdateEntity(coordinator, SimpleNamespace(entry_id="e1"), {}, allow_install=True)  # type: ignore[arg-type]
    entity.async_write_ha_state = lambda: None  # type: ignore[method-assign]

    with pytest.raises(HomeAssistantError, match=LEFT_BEHIND):
        await entity.async_install("2.4.0", backup=False)

    assert restarts == []
    assert entity.in_progress is False
