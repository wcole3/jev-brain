"""A client that gives up must stop the work on vLLM too (DS-009), watched through vLLM's Prometheus metrics."""

import itertools
import re
import time
import uuid
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest

from gateway.config import ROOT
from tests.live.api import auth

pytestmark = pytest.mark.live

SAMPLE = re.compile(r"^([A-Za-z_:][\w:]*)(?:\{.*\})?\s+(\S+)")  # name{labels} value
IDLE_WITHIN = 5  # seconds from the client giving up to vLLM having no requests
STAYS_IDLE = 5  # seconds vLLM must then stay idle; a decision still running would send its next call


def scrape(vllm_url: str) -> dict[str, float]:
    """Every vLLM metric, summed over its label sets."""
    totals: dict[str, float] = defaultdict(float)
    for line in httpx.get(f"{vllm_url}/metrics", timeout=10).text.splitlines():
        if sample := SAMPLE.match(line):
            totals[sample[1]] += float(sample[2])
    return totals


def in_flight(vllm_url: str) -> float:
    """Requests vLLM is running or has queued."""
    metrics = scrape(vllm_url)
    assert "vllm:num_requests_running" in metrics, "vLLM /metrics has no request gauges"
    return metrics["vllm:num_requests_running"] + metrics["vllm:num_requests_waiting"]


def finished(vllm_url: str) -> float:
    """Requests vLLM completed for any reason. vLLM 0.30 does not count client aborts here, even as "abort"."""
    return scrape(vllm_url)["vllm:request_success_total"]


def eventually(check: Callable[[], bool], within: float) -> bool:
    deadline = time.monotonic() + within
    while not check():
        if time.monotonic() > deadline:
            return False
        time.sleep(0.1)
    return True


def throughout(check: Callable[[], bool], seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if not check():
            return False
        time.sleep(0.1)
    return True


@pytest.fixture
def idle_vllm(gateway_url: str, vllm_url: str) -> str:
    """vLLM's URL once it has nothing to do, so every request it then sees is this test's."""
    assert eventually(lambda: in_flight(vllm_url) == 0, 120), "vLLM stays busy; run this on an idle stack"
    return vllm_url


def times_out(url: str, body: dict, seconds: float) -> None:
    with pytest.raises(httpx.TimeoutException):
        httpx.post(url, json=body, headers=auth(), timeout=seconds)


def give_up_mid_request(send: Callable[[], None], vllm_url: str) -> None:
    """Run send(), a request that times out, and check vLLM was working on it meanwhile."""
    with ThreadPoolExecutor(1) as pool:
        client = pool.submit(send)
        assert eventually(lambda: in_flight(vllm_url) > 0, 10), "the request never reached vLLM"
        client.result()


def assert_vllm_stops(vllm_url: str) -> None:
    assert eventually(lambda: in_flight(vllm_url) == 0, IDLE_WITHIN), "vLLM kept working after the client left"
    assert throughout(lambda: in_flight(vllm_url) == 0, STAYS_IDLE), "vLLM got new work after the client left"


def heavy_decision() -> dict:
    """Uncached (nonce first) and big enough to keep vLLM busy for well over 10 s."""
    state = f"[{uuid.uuid4()}] " + (ROOT / "data" / "bench" / "corpus.txt").read_text()[:30_000]
    codes = {f"code_{i}": None for i in range(255)}
    questions = {
        f"q{n}": {"type": "choice", "instructions": f"Which code fits part {n} of the text?", "criteria": codes}
        for n in range(64)
    }
    return {"state": state, "questions": questions}


def essay(served_model: str) -> dict:
    return {
        "model": served_model,
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": "Write a long, detailed essay on the history of lighthouses."}],
    }


def test_systemone_stops_when_the_client_times_out(gateway_url, idle_vllm):
    body = heavy_decision()
    give_up_mid_request(lambda: times_out(f"{gateway_url}/v1/systemone", body, 5), idle_vllm)
    assert_vllm_stops(idle_vllm)


def test_chat_stops_when_the_client_times_out(gateway_url, idle_vllm, served_model):
    before = finished(idle_vllm)
    give_up_mid_request(lambda: times_out(f"{gateway_url}/v1/chat/completions", essay(served_model), 3), idle_vllm)
    assert_vllm_stops(idle_vllm)
    assert finished(idle_vllm) == before, "vLLM finished the reply instead of aborting it"


def test_streaming_chat_stops_when_the_client_closes(gateway_url, idle_vllm, served_model):
    before = finished(idle_vllm)
    body = essay(served_model) | {"stream": True}
    with httpx.stream("POST", f"{gateway_url}/v1/chat/completions", json=body, headers=auth(), timeout=60) as r:
        events = (line for line in r.iter_lines() if line.startswith("data: "))
        assert len(list(itertools.islice(events, 5))) == 5
        assert in_flight(idle_vllm) > 0
    assert_vllm_stops(idle_vllm)
    assert finished(idle_vllm) == before, "vLLM finished the reply instead of aborting it"
