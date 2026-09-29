"""A client that leaves cancels its work: first the helper alone, then the whole app over a vLLM that never answers."""

import asyncio
import json

import httpx
import pytest

from gateway.app import create_app
from gateway.disconnect import unless_disconnected
from tests.helpers import QUICKSTART, STATE, fake_vllm

SYSTEMONE = {"state": STATE, "questions": QUICKSTART}
CHAT = {"model": "qwen3.6-27b", "messages": [{"role": "user", "content": "hi"}]}


class FakeRequest:
    """Stands in for a Starlette request whose client leaves once `leave` is set."""

    def __init__(self):
        self.leave = asyncio.Event()
        self.stopped_listening = False

    async def receive(self) -> dict:
        try:
            await self.leave.wait()
        except asyncio.CancelledError:
            self.stopped_listening = True
            raise
        return {"type": "http.disconnect"}


async def sleep_forever(seen: list[str]) -> None:
    try:
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        seen.append("cancelled")
        raise


async def test_work_that_finishes_first_returns_and_stops_the_watcher():
    request = FakeRequest()

    async def work():
        await asyncio.sleep(0)
        return 42

    assert await unless_disconnected(request, work()) == 42
    await asyncio.sleep(0)  # let the cancelled watcher unwind
    assert request.stopped_listening


async def test_leaving_client_cancels_the_work():
    request, seen = FakeRequest(), []
    request.leave.set()
    assert await unless_disconnected(request, sleep_forever(seen)) is None
    assert seen == ["cancelled"]


async def test_work_that_finishes_in_the_race_still_returns():
    request = FakeRequest()
    request.leave.set()

    async def finishes_anyway():
        try:
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            return "response"

    assert await unless_disconnected(request, finishes_anyway()) == "response"


async def test_work_errors_propagate():
    async def broken():
        raise RuntimeError("vLLM said no")

    with pytest.raises(RuntimeError):
        await unless_disconnected(FakeRequest(), broken())


async def test_cancelled_endpoint_leaves_nothing_running():
    request, seen = FakeRequest(), []
    endpoint = asyncio.create_task(unless_disconnected(request, sleep_forever(seen)))
    await asyncio.sleep(0.01)
    endpoint.cancel()
    with pytest.raises(asyncio.CancelledError):
        await endpoint
    await asyncio.sleep(0)
    assert seen == ["cancelled"]
    assert request.stopped_listening


class HangingVllm:
    """A vLLM that never answers; it records the paths of the calls that got cancelled."""

    def __init__(self):
        self.called = asyncio.Event()
        self.cancelled: list[str] = []

    async def __call__(self, request: httpx.Request) -> httpx.Response:
        self.called.set()
        try:
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            self.cancelled.append(request.url.path)
            raise


def http_scope(path: str) -> dict:
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},  # what uvicorn advertises
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "root_path": "",
        "query_string": b"",
        "headers": [(b"host", b"gateway"), (b"content-type", b"application/json")],
        "client": ("127.0.0.1", 50000),
        "server": ("127.0.0.1", 9000),
    }


async def post(settings, handler, path: str, body: dict, client_leaves: asyncio.Event) -> list[dict]:
    """POST into the ASGI app from a client that disconnects once client_leaves is set; returns what the app sent."""
    app = create_app(settings, httpx.MockTransport(handler))
    pending = [{"type": "http.request", "body": json.dumps(body).encode(), "more_body": False}]
    sent = []

    async def receive() -> dict:
        if pending:
            return pending.pop()
        await client_leaves.wait()
        return {"type": "http.disconnect"}

    async def send(message: dict) -> None:
        sent.append(message)

    async with app.router.lifespan_context(app):
        await asyncio.wait_for(app(http_scope(path), receive, send), timeout=10)
    return sent


@pytest.mark.parametrize(
    ("path", "body", "vllm_path"),
    [
        ("/v1/systemone", SYSTEMONE, "/v1/completions"),
        ("/v1/chat/completions", CHAT, "/v1/chat/completions"),
        ("/v1/completions", {"model": "qwen3.6-27b", "prompt": "hi"}, "/v1/completions"),
    ],
)
async def test_leaving_client_cancels_the_vllm_call(qwen_settings, path, body, vllm_path):
    vllm = HangingVllm()
    sent = await post(qwen_settings, vllm, path, body, client_leaves=vllm.called)
    assert sent[0]["status"] == 499
    assert vllm.cancelled == [vllm_path]


async def test_staying_client_gets_its_decision(qwen_settings):
    sent = await post(qwen_settings, fake_vllm, "/v1/systemone", SYSTEMONE, client_leaves=asyncio.Event())
    assert sent[0]["status"] == 200
    assert set(json.loads(sent[1]["body"])["answers"]) == set(QUICKSTART)
