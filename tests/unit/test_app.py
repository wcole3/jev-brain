import asyncio
import dataclasses
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.requests import ClientDisconnect

import gateway.app
from gateway import chat
from gateway.app import create_app, load_engine
from gateway.calibration import UNCALIBRATED
from gateway.governor import Governor
from tests.helpers import QUICKSTART, SSE, STATE, fake_vllm

NOUL = {"state": "s", "questions": {"q": {"type": "noul", "instructions": "ok?"}}}
CHAT = {"model": "qwen3.6-27b", "messages": [{"role": "user", "content": "hi"}]}
GATEWAY_KEY = {"Authorization": "Bearer gateway-key"}


@pytest.fixture
def sent() -> list[httpx.Request]:
    """Every request the gateway sent to the fake vLLM during the test."""
    return []


@pytest.fixture
def vllm(sent):
    def record(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return fake_vllm(request)

    return httpx.MockTransport(record)


@pytest.fixture
def client(qwen_settings, vllm):
    with TestClient(create_app(qwen_settings, vllm)) as c:
        yield c


@pytest.fixture
def locked(qwen_settings, vllm):
    """A gateway that wants the gateway key and holds vLLM's key."""
    s = dataclasses.replace(qwen_settings, api_key="gateway-key", vllm_api_key="vllm-key")
    with TestClient(create_app(s, vllm)) as c:
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
    assert client.post("/v1/chat/completions", json=CHAT).json() == {"echo": CHAT}
    r = client.post("/v1/chat/completions", json=CHAT | {"stream": True})
    assert r.content == SSE
    assert r.headers["content-type"].startswith("text/event-stream")


@pytest.mark.parametrize("content", [b"{not json", b"[1, 2]", b"\xff"])
def test_chat_body_must_be_a_json_object(client, content):
    r = client.post("/v1/chat/completions", content=content, headers={"content-type": "application/json"})
    assert r.status_code == 400
    assert r.json() == {"error": {"message": "request body must be a JSON object"}}


def test_chat_maps_jev_aliases_to_served_model(client):
    body = {"model": "jev-latest", "messages": [{"role": "user", "content": "hi"}]}
    assert client.post("/v1/chat/completions", json=body).json() == {"echo": body | {"model": "qwen3.6-27b"}}


def test_models_include_jev_aliases(client):
    ids = [m["id"] for m in client.get("/v1/models").json()["data"]]
    assert ids == ["qwen3.6-27b", "jev-latest", "jev-preview"]


def test_other_v1_paths_pass_through(client):
    r = client.get("/v1/unknown")
    assert r.status_code == 404
    assert r.json() == {"path": "/v1/unknown"}


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["vllm_version"] == "0.30.0"
    assert body["hf_model"] and body["hf_revision"]
    assert body["prompt_layout"] and body["option_orders"]
    s = client.app.state.engine.settings
    padding = (body["prefix_pad"], body["prefix_block"], body["prefix_pad_always"], body["warm_min_prefix_tokens"])
    assert padding == (s.prefix_pad, s.prefix_block, s.prefix_pad_always, s.warm_min_prefix_tokens)
    assert body["warm_up"] == s.warm_up
    assert body["systemone_max_len"] == s.systemone_max_len
    assert (body["governor_duty"], body["governor_wave"], body["chats_decoding"]) == (s.governor_duty, s.governor_wave, 0)
    assert body["calibration"] == {k: c.as_dict() for k, c in client.app.state.engine.calibration.items()}


CHUNKS = [b'data: {"choices": []}\n\n'] * 3


def streaming_vllm(seen: list, fail_after: int | None = None) -> httpx.MockTransport:
    """A fake vLLM whose chat stream records the gateway's chat count before each chunk after the first."""
    state = {}  # the engine, set once the app has started

    async def chunks():
        for i, chunk in enumerate(CHUNKS):
            if i == fail_after:
                raise httpx.ReadError("upstream died")
            if i:
                seen.append(state["engine"].governor.decoding)
            yield chunk

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content) if request.content else {}
        if request.url.path != "/v1/chat/completions":
            return fake_vllm(request)
        state["engine"] = state["app"].state.engine
        if body.get("stream"):
            return httpx.Response(200, content=chunks(), headers={"content-type": "text/event-stream"})
        seen.append(state["engine"].governor.decoding)
        return httpx.Response(200, json={"echo": body})

    transport = httpx.MockTransport(handler)
    transport.state = state
    return transport


def test_streaming_chat_counts_while_streaming(qwen_settings):
    seen = []
    vllm = streaming_vllm(seen)
    app = create_app(qwen_settings, vllm)
    vllm.state["app"] = app
    with TestClient(app) as c:
        r = c.post("/v1/chat/completions", json=CHAT | {"stream": True})
        assert r.content == b"".join(CHUNKS)
        assert seen == [1, 1]  # counted from the first chunk on
        assert c.app.state.engine.governor.decoding == 0


def test_plain_chat_is_not_counted(qwen_settings):
    seen = []
    vllm = streaming_vllm(seen)
    app = create_app(qwen_settings, vllm)
    vllm.state["app"] = app
    with TestClient(app) as c:
        assert c.post("/v1/chat/completions", json=CHAT).status_code == 200
        assert seen == [0]
        assert c.app.state.engine.governor.decoding == 0


class RecordedStream(httpx.AsyncByteStream):
    """An upstream body that notes whether it was closed."""

    def __init__(self, chunks):
        self.chunks, self.closed = chunks, False

    async def __aiter__(self):
        async for chunk in self.chunks():
            yield chunk

    async def aclose(self):
        self.closed = True


async def stream_through_gateway(chunks, governor, spec: str = "2.4", leave_after: int | None = None):
    """Run chat.chat_completions as an ASGI response; the client leaves when it is sent chunk number leave_after.

    ASGI 2.4: send raises OSError. 2.3 (uvicorn): send hangs and receive reports http.disconnect.
    Returns the highest chat count seen while sending, and whether upstream was closed at the end.
    """
    upstream = RecordedStream(chunks)
    transport = httpx.MockTransport(lambda r: httpx.Response(200, stream=upstream))
    async with httpx.AsyncClient(base_url="http://vllm", transport=transport) as client:
        response = await chat.chat_completions(client, CHAT | {"stream": True}, "m", governor)
        sent, peak = 0, 0

        async def send(message):
            nonlocal sent, peak
            sent += message["type"] == "http.response.body"
            peak = max(peak, governor.decoding)
            if sent == leave_after:
                if spec == "2.4":
                    raise OSError("client left")
                await asyncio.sleep(10)

        async def receive():
            await asyncio.sleep(0.05)
            return {"type": "http.disconnect"}

        try:
            await response({"type": "http", "asgi": {"spec_version": spec}}, receive, send)
        except (OSError, ClientDisconnect, httpx.ReadError):
            pass
    return peak, upstream.closed


@pytest.mark.parametrize("spec", ["2.3", "2.4"])
async def test_stream_count_drops_when_client_leaves_mid_stream(spec):
    governor = Governor()

    async def chunks():
        for chunk in CHUNKS:
            yield chunk

    peak, upstream_closed = await stream_through_gateway(chunks, governor, spec, leave_after=2)
    assert peak == 1
    assert governor.decoding == 0
    assert upstream_closed


async def test_stream_count_drops_on_upstream_error():
    governor = Governor()
    seen = []

    async def chunks():
        yield CHUNKS[0]
        seen.append(governor.decoding)
        raise httpx.ReadError("upstream died")

    peak, _ = await stream_through_gateway(chunks, governor)
    assert seen == [1]
    assert peak == 1
    assert governor.decoding == 0


def test_padded_gateway_reports_padding_and_bills_without_it(qwen_settings, vllm, sent):
    request = {"state": STATE, "questions": QUICKSTART}
    padded = dataclasses.replace(qwen_settings, prefix_pad="end", prefix_block=32, prefix_pad_always=True)
    with TestClient(create_app(padded, vllm)) as c:
        health = c.get("/health").json()
        usage = c.post("/v1/systemone", json=request).json()["usage"]
    with TestClient(create_app(dataclasses.replace(qwen_settings, prefix_pad="off"), vllm)) as c:
        assert c.post("/v1/systemone", json=request).json()["usage"] == usage
    assert (health["prefix_pad"], health["prefix_block"], health["prefix_pad_always"]) == ("end", 32, True)
    first, last = [json.loads(r.content)["prompt"] for r in sent if r.url.path == "/v1/completions"]
    assert {len(a) - len(b) for a, b in zip(first, last)} == {32 - 23}  # 23 shared tokens padded to 32


@pytest.mark.parametrize(
    "authorization", [None, "Bearer wrong", "gateway-key", "bearer gateway-key", "Bearer gateway-kéy".encode()]
)
def test_wrong_or_missing_key_is_401(locked, authorization):
    headers = {} if authorization is None else {"Authorization": authorization}
    r = locked.post("/v1/systemone", json=NOUL, headers=headers)
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"
    assert r.json() == {"error": {"message": "invalid or missing API key"}}


def test_right_key_is_accepted(locked):
    assert locked.post("/v1/systemone", json=NOUL, headers=GATEWAY_KEY).status_code == 200


def test_vllm_calls_carry_the_vllm_key_not_the_gateway_key(locked, sent):
    locked.post("/v1/systemone", json=NOUL, headers=GATEWAY_KEY)
    locked.post("/v1/chat/completions", json=CHAT, headers=GATEWAY_KEY)
    locked.get("/v1/unknown", headers=GATEWAY_KEY)
    assert [r.url.path for r in sent] == ["/v1/completions", "/v1/chat/completions", "/v1/unknown"]
    assert all(r.headers["authorization"] == "Bearer vllm-key" for r in sent)


def test_gateway_key_never_reaches_vllm(qwen_settings, vllm, sent):
    s = dataclasses.replace(qwen_settings, api_key="gateway-key")
    with TestClient(create_app(s, vllm)) as c:
        c.post("/v1/chat/completions", json=CHAT, headers=GATEWAY_KEY)
        c.get("/v1/unknown", headers=GATEWAY_KEY)
    assert len(sent) == 2
    assert not any("authorization" in r.headers for r in sent)


def test_passthrough_forwards_content_type_accept_and_repeated_query_keys(client, sent):
    headers = {"content-type": "multipart/form-data; boundary=x", "accept": "text/event-stream", "x-other": "1"}
    client.post("/v1/audio/transcriptions?a=1&a=2&b=3", content=b"--x--", headers=headers)
    upstream = sent[-1]
    assert upstream.headers["content-type"] == "multipart/form-data; boundary=x"
    assert upstream.headers["accept"] == "text/event-stream"
    assert "x-other" not in upstream.headers
    assert upstream.url.params.multi_items() == [("a", "1"), ("a", "2"), ("b", "3")]
    assert upstream.content == b"--x--"


def test_unknown_route_is_404_in_the_error_shape(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.json() == {"error": {"message": "Not Found"}}


def test_wrong_method_is_405_in_the_error_shape_and_keeps_allow(client):
    r = client.post("/health")
    assert r.status_code == 405
    assert r.json() == {"error": {"message": "Method Not Allowed"}}
    assert r.headers["allow"] == "GET"


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_api_docs_are_off(client, path):
    assert client.get(path).status_code == 404


def test_invalid_body_is_422_with_one_message(client):
    questions = {"q": {"type": "maybe", "instructions": "?"}, "r": {"instructions": "?"}}
    r = client.post("/v1/systemone", json={"state": "s", "questions": questions})
    assert r.status_code == 422
    message = "questions.q.type: Input should be 'choice', 'score' or 'noul'; questions.r.type: Field required"
    assert r.json() == {"error": {"message": message}}


def test_missing_body_is_422_about_the_body(client):
    r = client.post("/v1/systemone")
    assert r.status_code == 422
    assert r.json() == {"error": {"message": "body: Field required"}}


def test_invalid_json_is_422_about_the_body(client):
    r = client.post("/v1/systemone", content=b"{not json", headers={"content-type": "application/json"})
    assert r.status_code == 422
    assert r.json()["error"]["message"].startswith("body: JSON decode error")


def test_vllm_down_is_503(qwen_settings):
    def down(request):
        raise httpx.ConnectError("down")

    with TestClient(create_app(qwen_settings, httpx.MockTransport(down))) as c:
        assert c.post("/v1/systemone", json=NOUL).status_code == 503


def test_vllm_timeout_is_504(qwen_settings):
    def slow(request):
        raise httpx.ReadTimeout("slow")

    with TestClient(create_app(qwen_settings, httpx.MockTransport(slow))) as c:
        r = c.post("/v1/systemone", json=NOUL)
        assert r.status_code == 504
        assert r.json() == {"error": {"message": "model server timed out"}}
        assert c.post("/v1/chat/completions", json=CHAT).status_code == 504


def test_unexpected_error_is_500_with_request_id(qwen_settings, caplog):
    def broken(request):
        return httpx.Response(500)

    with TestClient(create_app(qwen_settings, httpx.MockTransport(broken)), raise_server_exceptions=False) as c:
        r = c.post("/v1/systemone", json=NOUL)
    assert r.status_code == 500
    assert r.json()["error"]["request_id"] in caplog.text


def test_startup_refuses_a_v1_calibration_file(qwen_settings):
    path = qwen_settings.data_dir("decider_chat") / "calibration.json"
    path.write_text(json.dumps({"choice": 1.943, "score": 1.943, "noul": 1.943}))
    with pytest.raises(RuntimeError, match="not a v2"):
        load_engine(qwen_settings, None)


def test_startup_refuses_a_decision_cap_above_the_model_limit(qwen_settings):
    bad = dataclasses.replace(qwen_settings, systemone_max_len=qwen_settings.max_model_len + 1)
    with pytest.raises(ValueError, match="SYSTEMONE_MAX_LEN"):
        load_engine(bad, None)


OLD_STAMP = {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "old", "prefix_pad": "off",
             "prefix_block": 0}


def write_calibration(s, name="calibration.json", **fit):
    """A v2 file stamped OLD_STAMP: stale for the real tokenizer and revision."""
    types = {"choice": {"T": 1.5}, "score": {"T": 1.5}, "noul": {"T": 1.5, "b": 0.0}}
    path = s.data_dir("decider_chat") / name
    path.write_text(json.dumps({"format": 2, "stamp": OLD_STAMP, "types": types, "fit": fit}))


def test_gateway_loads_the_calibration_file_of_its_prefix_block(qwen_settings):
    s = dataclasses.replace(qwen_settings, prefix_block=784)
    write_calibration(s, "calibration-784.json")
    with pytest.raises(RuntimeError, match="changed .* move the stale file aside"):
        load_engine(s, None)


def test_stale_calibration_refuses_the_gateway_but_not_collect(qwen_settings):
    write_calibration(qwen_settings)
    with pytest.raises(RuntimeError, match="changed .* move the stale file aside"):
        load_engine(qwen_settings, None)
    engine = load_engine(qwen_settings, None, calibrated=False)
    assert all(c == UNCALIBRATED for c in engine.calibration.values())


def test_startup_warns_when_a_fit_was_made_under_other_orders(qwen_settings, caplog, monkeypatch):
    monkeypatch.setattr(gateway.app, "stamp_for", lambda tok, layout, s: OLD_STAMP)  # the file is current
    write_calibration(qwen_settings, orders="identity")
    engine = load_engine(dataclasses.replace(qwen_settings, option_orders="identity+reversed"), None)
    assert engine.calibration["decider_chat"].T["choice"] == 1.5
    assert "fitted under option orders 'identity', used here with 'identity+reversed'" in caplog.text
