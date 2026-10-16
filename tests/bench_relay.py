from __future__ import annotations

import argparse
import asyncio
import json
import multiprocessing as mp
import random
import resource
import ssl
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import aiohttp
from aiohttp import web
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

MIB = 1024 * 1024
TOKEN = "cui_BENCH_TOKEN"
GOP = 30
KEYFRAME_SIZE = 160 * 1024
DELTA_SIZE = 8 * 1024
EXPORT_CHUNK = 256 * 1024
PATHS = {"go2rtc": "api/go2rtc", "nats": "api/proxy"}


class CountingExecutor(ThreadPoolExecutor):
    def __init__(self) -> None:
        super().__init__()
        self.jobs = 0

    def submit(self, fn: Any, /, *args: Any, **kwargs: Any) -> Any:
        self.jobs += 1
        return super().submit(fn, *args, **kwargs)


class BenchHass:
    def __init__(self, root: str) -> None:
        self.config = SimpleNamespace(path=lambda *parts: str(Path(root, *parts)))

    async def async_add_executor_job(self, target: Callable[..., Any], *args: Any) -> Any:
        return await asyncio.get_running_loop().run_in_executor(None, target, *args)

    def async_create_background_task(self, coro: Any, name: str) -> asyncio.Task[Any]:
        return asyncio.get_running_loop().create_task(coro, name=name)


class BenchRpc:
    def __init__(self, size: int, rate: float) -> None:
        self._size = size
        self._rate = rate

    async def export_event(self, camera_id: str, start_ms: int, end_ms: int, quality: str) -> str:
        return f"/export/{camera_id}.mp4?size={self._size}&rate={self._rate}"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m tests.bench_relay",
        description="Measures the Home Assistant relay: WebSocket forwarding and clip export.",
    )
    parser.add_argument("scenario", choices=("throughput", "paced", "clip", "all"))
    parser.add_argument("--path", choices=(*PATHS, "both"), default="both")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--mib", type=int, default=128, help="payload per throughput run")
    parser.add_argument("--seconds", type=float, default=10, help="length of a paced run")
    parser.add_argument("--streams", type=int, default=4, help="parallel sockets in a paced run")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--clip", type=Path, help="mp4 whose video packets replace the synthetic frames")
    parser.add_argument("--export-mib", type=int, default=64, help="size of the exported clip")
    parser.add_argument("--export-rate", type=float, default=0, help="MiB/s the NVR serves, 0 is unlimited")
    parser.add_argument(
        "--late-viewer", type=float, default=0.5, help="share of the clip after which a second viewer joins"
    )
    args = parser.parse_args()

    paths = list(PATHS) if args.path == "both" else [args.path]
    scenarios = ("throughput", "paced", "clip") if args.scenario == "all" else (args.scenario,)
    ctx = mp.get_context("spawn")
    with tempfile.TemporaryDirectory(prefix="cameraui-bench-") as root:
        cert_dir = Path(root, "tls")
        cert_dir.mkdir()
        _write_certificate(cert_dir)
        upstream_port, stop_upstream = _start(ctx, _upstream_process, cert_dir, args.clip)
        try:
            print(f"python {sys.version.split()[0]}, aiohttp {aiohttp.__version__}, {_zlib_backend()}")
            for scenario in scenarios:
                if scenario == "clip":
                    _report_clip(ctx, args, root, upstream_port)
                    continue
                for name in paths:
                    _report_relay(ctx, args, scenario, name, upstream_port)
        finally:
            stop_upstream()


def _report_relay(ctx: Any, args: argparse.Namespace, scenario: str, name: str, upstream_port: int) -> None:
    relay_port, stop_relay, results = _start_relay(ctx, upstream_port)
    try:
        runs = [asyncio.run(_relay_run(args, scenario, name, relay_port, results)) for _ in range(args.runs)]
    finally:
        stop_relay()
    print(f"\n{scenario} {name} ({PATHS[name]}), {args.runs} runs")
    if scenario == "throughput":
        _summary(runs, "relay_cpu_ms_per_mib", "relay CPU ms/MiB", "{:.2f}")
        _summary(runs, "mib_per_s", "MiB/s through the relay", "{:.0f}")
    else:
        _summary(runs, "relay_cpu_pct", "relay CPU % of one core", "{:.2f}")
        _summary(runs, "latency_p50_ms", "latency p50 ms", "{:.2f}")
        _summary(runs, "latency_p99_ms", "latency p99 ms", "{:.2f}")
    _summary(runs, "wire_ratio", "browser wire bytes / payload", "{:.3f}")
    _summary(runs, "deflate", "permessage-deflate negotiated", "{:.0f}")
    _summary(runs, "relay_maxrss_mib", "relay peak RSS MiB", "{:.1f}")


def _report_clip(ctx: Any, args: argparse.Namespace, root: str, upstream_port: int) -> None:
    timed = [_in_process(ctx, _clip_process, args, root, upstream_port, False) for _ in range(args.runs)]
    traced = [_in_process(ctx, _clip_process, args, root, upstream_port, True) for _ in range(args.runs)]
    print(f"\nclip export {args.export_mib} MiB, second viewer at {args.late_viewer:.0%}, {args.runs} runs")
    _summary(traced, "traced_peak_mib", "tracemalloc peak MiB", "{:.1f}")
    _summary(timed, "rss_growth_mib", "RSS growth MiB", "{:.1f}")
    _summary(timed, "seconds", "export plus both viewers s", "{:.2f}")
    _summary(timed, "cpu_ms_per_mib", "process CPU ms per exported MiB", "{:.2f}")
    _summary(timed, "executor_jobs", "executor jobs", "{:.0f}")
    _summary(timed, "complete", "both viewers got every byte", "{:.0f}")


def _summary(runs: list[dict[str, Any]], key: str, label: str, fmt: str) -> None:
    values = [float(run[key]) for run in runs]
    median = statistics.median(values)
    spread = f"min {fmt.format(min(values))}, max {fmt.format(max(values))}"
    print(f"  {label}: median {fmt.format(median)} ({spread})")


async def _relay_run(
    args: argparse.Namespace, scenario: str, name: str, relay_port: int, results: Any
) -> dict[str, Any]:
    wire = [0]
    proxy = await asyncio.start_server(_counting_pipe(relay_port, wire), "127.0.0.1", 0)
    proxy_port = proxy.sockets[0].getsockname()[1]
    query = {"scenario": scenario, "kind": name, "mib": args.mib, "seconds": args.seconds, "fps": args.fps}
    url = f"http://127.0.0.1:{proxy_port}/ws/{PATHS[name]}"
    sockets = 1 if scenario == "throughput" else args.streams
    try:
        async with aiohttp.ClientSession() as session:
            outcomes = await asyncio.gather(*(_browser(session, url, query) for _ in range(sockets)))
    finally:
        proxy.close()
        await proxy.wait_closed()
    relay = [await asyncio.to_thread(results.get, True, 60) for _ in range(sockets)]
    payload = sum(outcome["bytes"] for outcome in outcomes)
    # rusage is process-wide, so parallel sockets share one window instead of adding up
    cpu = max(entry["cpu_end"] for entry in relay) - min(entry["cpu_start"] for entry in relay)
    wall = max(entry["ended"] for entry in relay) - min(entry["started"] for entry in relay)
    latencies = sorted(ms for outcome in outcomes for ms in outcome["latencies"])
    return {
        "relay_cpu_ms_per_mib": cpu * 1000 / (payload / MIB),
        "mib_per_s": payload / MIB / wall,
        "relay_cpu_pct": cpu / wall * 100,
        "latency_p50_ms": _percentile(latencies, 0.5),
        "latency_p99_ms": _percentile(latencies, 0.99),
        "wire_ratio": wire[0] / payload,
        "deflate": all(outcome["deflate"] for outcome in outcomes),
        "relay_maxrss_mib": max(entry["maxrss"] for entry in relay) / MIB,
    }


async def _browser(session: aiohttp.ClientSession, url: str, query: dict[str, Any]) -> dict[str, Any]:
    received = 0
    latencies: list[float] = []
    # browsers always offer permessage-deflate
    async with session.ws_connect(url, params=query, compress=15, max_msg_size=0) as ws:
        async for msg in ws:
            if msg.type is not aiohttp.WSMsgType.BINARY:
                break
            received += len(msg.data)
            if query["scenario"] == "paced":
                sent = int.from_bytes(msg.data[:8], "little")
                latencies.append((time.monotonic_ns() - sent) / 1e6)
        return {"bytes": received, "latencies": latencies, "deflate": bool(ws.compress)}


def _counting_pipe(
    port: int, wire: list[int]
) -> Callable[[asyncio.StreamReader, asyncio.StreamWriter], Awaitable[None]]:
    async def pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, count: bool) -> None:
        try:
            while data := await reader.read(256 * 1024):
                if count:
                    wire[0] += len(data)
                writer.write(data)
                await writer.drain()
        except ConnectionError:
            pass
        finally:
            writer.close()

    async def handle(client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter) -> None:
        relay_reader, relay_writer = await asyncio.open_connection("127.0.0.1", port)
        await asyncio.gather(
            pipe(client_reader, relay_writer, False), pipe(relay_reader, client_writer, True)
        )

    return handle


def _percentile(values: list[float], share: float) -> float:
    if not values:
        return 0.0
    return values[min(len(values) - 1, int(len(values) * share))]


def _start_relay(ctx: Any, upstream_port: int) -> tuple[int, Callable[[], None], Any]:
    results = ctx.Queue()
    port, stop = _start(ctx, _relay_process, upstream_port, results)
    return port, stop, results


def _start(ctx: Any, target: Callable[..., None], *args: Any) -> tuple[int, Callable[[], None]]:
    ready = ctx.Queue()
    process = ctx.Process(target=target, args=(ready, *args), daemon=True)
    process.start()
    port = ready.get(timeout=60)

    def stop() -> None:
        process.terminate()
        process.join(10)

    return port, stop


def _in_process(ctx: Any, target: Callable[..., None], *args: Any) -> dict[str, Any]:
    out = ctx.Queue()
    process = ctx.Process(target=target, args=(out, *args))
    process.start()
    result: dict[str, Any] = out.get(timeout=600)
    process.join(10)
    return result


def _upstream_process(ready: Any, cert_dir: Path, clip: Path | None) -> None:
    asyncio.run(_upstream(ready, cert_dir, clip))


async def _upstream(ready: Any, cert_dir: Path, clip: Path | None) -> None:
    frames = {"go2rtc": _video_frames(clip), "nats": _nats_frames()}
    block = random.Random(2).randbytes(MIB)

    async def socket(request: web.Request) -> web.StreamResponse:
        ws = web.WebSocketResponse(max_msg_size=0)
        await ws.prepare(request)
        query = request.query
        await _replay(ws, frames[query["kind"]], query)
        await ws.close()
        return ws

    async def export(request: web.Request) -> web.StreamResponse:
        size = int(request.query["size"])
        rate = float(request.query["rate"])
        response = web.StreamResponse(headers={"Content-Type": "video/mp4", "Content-Length": str(size)})
        await response.prepare(request)
        started = time.monotonic()
        sent = 0
        while sent < size:
            chunk = block[sent % MIB :][: min(EXPORT_CHUNK, size - sent)]
            await response.write(chunk)
            sent += len(chunk)
            if rate:
                await asyncio.sleep(max(0.0, started + sent / (rate * MIB) - time.monotonic()))
        await response.write_eof()
        return response

    app = web.Application()
    app.router.add_get("/export/{name}", export)
    app.router.add_get("/{path:.*}", socket)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0, ssl_context=_server_tls(cert_dir))
    await site.start()
    ready.put(runner.addresses[0][1])
    await asyncio.Event().wait()


async def _replay(ws: web.WebSocketResponse, frames: list[bytes], query: Any) -> None:
    if query["scenario"] == "throughput":
        total = int(query["mib"]) * MIB
        sent = 0
        for frame in _cycle(frames):
            if sent >= total:
                return
            await ws.send_bytes(frame)
            sent += len(frame)
    loop = asyncio.get_running_loop()
    interval = 1 / int(query["fps"])
    deadline = loop.time() + float(query["seconds"])
    due = loop.time()
    for frame in _cycle(frames):
        if loop.time() >= deadline:
            return
        stamped = time.monotonic_ns().to_bytes(8, "little") + frame[8:]
        await ws.send_bytes(stamped)
        due += interval
        await asyncio.sleep(max(0.0, due - loop.time()))


def _cycle(frames: list[bytes]) -> Iterator[bytes]:
    while True:
        yield from frames


def _video_frames(clip: Path | None) -> list[bytes]:
    if clip is None:
        rng = random.Random(0)
        return [rng.randbytes(KEYFRAME_SIZE if i % GOP == 0 else DELTA_SIZE) for i in range(GOP * 4)]
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-read_intervals",
            "%+30",
            "-show_entries",
            "packet=size,pos",
            "-of",
            "csv=p=0",
            str(clip),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    frames = []
    with clip.open("rb") as file:
        for line in probe.stdout.splitlines():
            size, pos = (int(field) for field in line.split(",")[:2])
            file.seek(pos)
            frames.append(file.read(size))
    return frames


def _nats_frames() -> list[bytes]:
    rng = random.Random(1)
    labels = ["person", "vehicle", "animal", "motion", "face", "license_plate"]
    frames = []
    for i in range(400):
        camera = f"cam-{i % 8}"
        detections = [
            {
                "label": rng.choice(labels),
                "confidence": round(rng.random(), 3),
                "boundingBox": [round(rng.random(), 4) for _ in range(4)],
                "id": f"{rng.getrandbits(64):016x}",
            }
            for _ in range(rng.randint(0, 12))
        ]
        payload = json.dumps(
            {
                "type": "sensor:property:changed",
                "cameraId": camera,
                "sensorId": f"{camera}-sensor-{i % 5}",
                "property": "detections",
                "value": detections,
                "timestamp": 1_790_000_000_000 + i * 37,
            }
        ).encode()
        frames.append(f"MSG camera.ui.events.{camera} 7 {len(payload)}\r\n".encode() + payload + b"\r\n")
    return frames


def _relay_process(ready: Any, upstream_port: int, results: Any) -> None:
    asyncio.run(_relay(ready, upstream_port, results))


async def _relay(ready: Any, upstream_port: int, results: Any) -> None:
    import aiohttp_fast_zlib
    from homeassistant.components.http import KEY_HASS
    from homeassistant.const import CONF_HOST, CONF_PORT
    from homeassistant.core import HomeAssistant

    from custom_components.cameraui import views
    from custom_components.cameraui.const import CONF_TOKEN

    # Home Assistant's http component does the same at startup
    aiohttp_fast_zlib.enable()
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    views.async_get_clientsession = _shared(session)
    entry = SimpleNamespace(data={CONF_HOST: "127.0.0.1", CONF_PORT: upstream_port, CONF_TOKEN: TOKEN})

    async def handler(request: web.Request) -> web.StreamResponse:
        before = resource.getrusage(resource.RUSAGE_SELF)
        started = time.monotonic()
        try:
            return await views._proxy_ws(request, entry, request.match_info["path"], TOKEN)  # type: ignore[arg-type]
        finally:
            after = resource.getrusage(resource.RUSAGE_SELF)
            results.put(
                {
                    "cpu_start": before.ru_utime + before.ru_stime,
                    "cpu_end": after.ru_utime + after.ru_stime,
                    "started": started,
                    "ended": time.monotonic(),
                    "maxrss": _maxrss_bytes(after),
                }
            )

    app = web.Application()
    app[KEY_HASS] = cast("HomeAssistant", None)
    app.router.add_get("/ws/{path:.*}", handler)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    await web.TCPSite(runner, "127.0.0.1", 0).start()
    ready.put(runner.addresses[0][1])
    await asyncio.Event().wait()


def _clip_process(out: Any, args: argparse.Namespace, root: str, upstream_port: int, trace: bool) -> None:
    out.put(asyncio.run(_clip(args, root, upstream_port, trace)))


async def _clip(args: argparse.Namespace, root: str, upstream_port: int, trace: bool) -> dict[str, Any]:
    from custom_components.cameraui import clips

    executor = CountingExecutor()
    asyncio.get_running_loop().set_default_executor(executor)
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))
    clips.async_get_clientsession = _shared(session)
    size = args.export_mib * MIB
    with tempfile.TemporaryDirectory(dir=root) as config:
        cache = clips.ClipCache(
            BenchHass(config),  # type: ignore[arg-type]
            "bench",
            BenchRpc(size, args.export_rate),  # type: ignore[arg-type]
            f"https://127.0.0.1:{upstream_port}",
            "low",
        )
        rss_before = _maxrss_bytes(resource.getrusage(resource.RUSAGE_SELF))
        cpu_before = time.process_time()
        if trace:
            tracemalloc.start()
        started = time.monotonic()
        first_half = asyncio.Event()
        ready = await cache.open("cam", "event", 0, 1)
        first = asyncio.create_task(_viewer(ready, size, args.late_viewer, first_half))
        await first_half.wait()
        late = await cache.open("cam", "event", 0, 1)
        second = asyncio.create_task(_viewer(late, size, 2.0, None))
        received = await asyncio.gather(first, second)
        seconds = time.monotonic() - started
        peak = tracemalloc.get_traced_memory()[1] if trace else 0
        tracemalloc.stop()
        cpu = time.process_time() - cpu_before
        rss_after = _maxrss_bytes(resource.getrusage(resource.RUSAGE_SELF))
    await session.close()
    executor.shutdown()
    return {
        "traced_peak_mib": peak / MIB,
        "rss_growth_mib": (rss_after - rss_before) / MIB,
        "seconds": seconds,
        "cpu_ms_per_mib": cpu * 1000 / (size / MIB),
        "executor_jobs": executor.jobs,
        "complete": all(count == size for count in received),
    }


async def _viewer(ready: Any, size: int, signal_at: float, signal: asyncio.Event | None) -> int:
    received = 0
    async for chunk in _chunks(ready):
        received += len(chunk)
        if signal and received >= size * signal_at:
            signal.set()
    if signal:
        signal.set()
    return received


async def _chunks(ready: Any) -> AsyncIterator[bytes]:
    if isinstance(ready, Path):
        # the view hands a finished file to sendfile, so read it the same piecewise way
        with ready.open("rb") as file:
            while chunk := await asyncio.to_thread(file.read, MIB):
                yield chunk
        return
    async for chunk in ready.stream():
        yield chunk


def _shared(session: aiohttp.ClientSession) -> Callable[..., aiohttp.ClientSession]:
    def get(hass: Any, verify_ssl: bool = True) -> aiohttp.ClientSession:
        return session

    return get


def _maxrss_bytes(usage: resource.struct_rusage) -> int:
    return usage.ru_maxrss if sys.platform == "darwin" else usage.ru_maxrss * 1024


def _zlib_backend() -> str:
    for module in ("isal", "zlib_ng"):
        try:
            __import__(module)
        except ImportError:
            continue
        return f"deflate backend {module}"
    return "deflate backend zlib (no isal or zlib_ng installed)"


def _write_certificate(folder: Path) -> None:
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "127.0.0.1")])
    now = datetime.now(UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=5))
        .not_valid_after(now + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    (folder / "cert.pem").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (folder / "key.pem").write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )
    )


def _server_tls(folder: Path) -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(folder / "cert.pem", folder / "key.pem")
    return ctx


if __name__ == "__main__":
    main()
