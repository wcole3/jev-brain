import dataclasses
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from gateway.app import create_app
from tests.helpers import QUICKSTART, STATE

SSE = b'data: {"choices": []}\n\ndata: [DONE]\n\n'


def fake_vllm(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/v1/completions":
        body = json.loads(request.content)
        top = {f"token_id:{t}": -0.001 * t for t in body["logprob_token_ids"]}
        return httpx.Response(200, json={"choices": [{"index": i, "logprobs": {"top_logprobs": [top]}}
                                                     for i in range(len(body["prompt"]))]})
    if path == "/v1/chat/completions":
        body = json.loads(request.content)
        if body.get("stream"):
            return httpx.Response(200, content=SSE, headers={"content-type": "text/event-stream"})
        return httpx.Response(200, json={"echo": body})
    if path == "/v1/models":
        return httpx.Response(200, json={"object": "list", "data": [{"id": "qwen3.6-27b", "object": "model"}]})
    if path == "/health":
        return httpx.Response(200)
    return httpx.Response(404, json={"path": path})


@pytest.fixture
def client(qwen_settings):
    with TestClient(create_app(qwen_settings, httpx.MockTransport(fake_vllm))) as c:
        yield c


def test_systemone_quickstart(client):
    r = client.post("/v1/systemone", json={"model": "jev-latest", "state": STATE, "questions": QUICKSTART})
    assert r.status_code == 200
    out = r.json()
    dept = out["answers"]["department"]
    assert set(dept["probabilities"]) == {"billing", "technical", "sales"}
    assert sum(dept["probabilities"].values()) == pytest.approx(1, abs=1e-3)
    assert set(out["answers"]["frustration"]["legend"]) == {"0", "1", "2"}
    assert set(out["answers"]["is_urgent"]) == {"type", "noul"}
    assert out["usage"]["output_tokens"] == 0


def test_capacity_refusal_carries_harness_marker(client):
    q = {"type": "choice", "instructions": "?", "criteria": {str(i): None for i in range(256)}}
    r = client.post("/v1/systemone", json={"state": "s", "questions": {"q": q}})
    assert r.status_code == 422
    assert "options per choice" in r.text


def test_chat_passthrough_plain_and_streaming(client):
    body = {"model": "qwen3.6-27b", "messages": [{"role": "user", "content": "hi"}]}
    assert client.post("/v1/chat/completions", json=body).json() == {"echo": body}
    r = client.post("/v1/chat/completions", json=body | {"stream": True})
    assert r.content == SSE
    assert r.headers["content-type"].startswith("text/event-stream")


def test_models_include_jev_aliases(client):
    ids = [m["id"] for m in client.get("/v1/models").json()["data"]]
    assert ids == ["qwen3.6-27b", "jev-latest", "jev-preview"]


def test_other_v1_paths_pass_through(client):
    r = client.get("/v1/unknown")
    assert r.status_code == 404
    assert r.json() == {"path": "/v1/unknown"}


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_api_key_is_enforced_when_set(qwen_settings):
    locked = dataclasses.replace(qwen_settings, api_key="secret")
    with TestClient(create_app(locked, httpx.MockTransport(fake_vllm))) as c:
        body = {"state": "s", "questions": {"q": {"type": "noul", "instructions": "ok?"}}}
        assert c.post("/v1/systemone", json=body).status_code == 401
        assert c.post("/v1/systemone", json=body, headers={"Authorization": "Bearer secret"}).status_code == 200


def test_vllm_down_is_503(qwen_settings):
    def down(request):
        raise httpx.ConnectError("down")
    with TestClient(create_app(qwen_settings, httpx.MockTransport(down))) as c:
        body = {"state": "s", "questions": {"q": {"type": "noul", "instructions": "ok?"}}}
        assert c.post("/v1/systemone", json=body).status_code == 503
