from __future__ import annotations

import asyncio
import socket
from types import SimpleNamespace
from typing import Any

import pytest

from custom_components.cameraui import rpc as rpc_module
from custom_components.cameraui.rpc import CameraUiRpc, CameraUiRpcError

from .helpers import TOKEN, mute_server

Bus = tuple[list["FakeBusClient"], asyncio.Event]


class FakeBusClient:
    def __init__(self, gate: asyncio.Event) -> None:
        self.gate = gate
        self.connected = False
        self.disconnected = False

    @property
    def is_connected(self) -> bool:
        return self.connected and not self.disconnected

    async def connect(self) -> None:
        await self.gate.wait()
        self.connected = True

    async def disconnect(self) -> None:
        self.disconnected = True

    def create_proxy(self, name: str) -> Any:
        async def get_plugin(plugin: str) -> dict[str, Any]:
            return {"id": "nvr", "running": True}

        return SimpleNamespace(getPlugin=get_plugin)


@pytest.fixture
def bus(monkeypatch: pytest.MonkeyPatch) -> Bus:
    created: list[FakeBusClient] = []
    gate = asyncio.Event()

    def factory(options: Any) -> FakeBusClient:
        client = FakeBusClient(gate)
        created.append(client)
        return client

    monkeypatch.setattr(rpc_module, "create_rpc_client", factory)
    return created, gate


async def test_unreachable_server_fails_within_seconds(socket_enabled: None) -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    rpc = CameraUiRpc("127.0.0.1", port, TOKEN)
    try:
        with pytest.raises(CameraUiRpcError):
            await asyncio.wait_for(rpc.nvr_plugin_id(), 10)
    finally:
        await rpc.close()


async def test_server_that_never_answers_fails_after_the_connect_timeout(
    socket_enabled: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(rpc_module, "CONNECT_TIMEOUT", 1)
    async with mute_server() as (port, _):
        rpc = CameraUiRpc("127.0.0.1", port, TOKEN)
        try:
            with pytest.raises(CameraUiRpcError):
                await asyncio.wait_for(rpc.nvr_plugin_id(), 10)
        finally:
            await rpc.close()


async def test_hanging_connect_gives_up_and_drops_the_client(
    bus: Bus, monkeypatch: pytest.MonkeyPatch
) -> None:
    created, _ = bus
    monkeypatch.setattr(rpc_module, "CONNECT_TIMEOUT", 0.2)
    rpc = CameraUiRpc("127.0.0.1", 1, TOKEN)
    try:
        with pytest.raises(CameraUiRpcError):
            await asyncio.wait_for(rpc.nvr_plugin_id(), 5)
        assert created[0].disconnected
    finally:
        await rpc.close()


async def test_next_call_after_a_failed_connect_tries_again(
    bus: Bus, monkeypatch: pytest.MonkeyPatch
) -> None:
    created, gate = bus
    monkeypatch.setattr(rpc_module, "CONNECT_TIMEOUT", 0.2)
    rpc = CameraUiRpc("127.0.0.1", 1, TOKEN)
    try:
        with pytest.raises(CameraUiRpcError):
            await asyncio.wait_for(rpc.nvr_plugin_id(), 5)
        gate.set()
        assert await asyncio.wait_for(rpc.nvr_plugin_id(), 5) == "nvr"
        assert len(created) == 2
    finally:
        await rpc.close()


async def test_cancelled_caller_does_not_abort_the_shared_connect(bus: Bus) -> None:
    created, gate = bus
    rpc = CameraUiRpc("127.0.0.1", 1, TOKEN)
    try:
        first = asyncio.create_task(rpc.nvr_plugin_id())
        second = asyncio.create_task(rpc.nvr_plugin_id())
        await asyncio.sleep(0.01)
        first.cancel()
        gate.set()
        assert await asyncio.wait_for(second, 5) == "nvr"
        with pytest.raises(asyncio.CancelledError):
            await first
        assert len(created) == 1
    finally:
        await rpc.close()


async def test_close_while_connecting_discards_the_new_connection(bus: Bus) -> None:
    created, gate = bus
    rpc = CameraUiRpc("127.0.0.1", 1, TOKEN)
    caller = asyncio.create_task(rpc.nvr_plugin_id())
    await asyncio.sleep(0.01)
    await rpc.close()
    gate.set()
    with pytest.raises(CameraUiRpcError):
        await asyncio.wait_for(caller, 5)
    await asyncio.sleep(0.01)
    assert not created[0].is_connected
    await rpc.close()
