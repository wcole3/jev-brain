import uuid

import httpx
import pytest

from tests.live.api import post

pytestmark = pytest.mark.live


def prefix_cache_hits(vllm_url: str) -> float:
    lines = httpx.get(f"{vllm_url}/metrics", timeout=10).text.splitlines()
    return sum(
        float(line.rsplit(" ", 1)[1]) for line in lines if line.startswith("vllm:") and "prefix_cache_hits" in line
    )


def test_questions_share_the_state_prefix(gateway_url, vllm_url):
    before = prefix_cache_hits(vllm_url)
    state = f"[{uuid.uuid4()}] " + "The quarterly report lists revenue, costs and staffing changes. " * 200
    questions = {f"q{i}": {"type": "noul", "instructions": f"Statement {i} is supported"} for i in range(8)}
    assert post(gateway_url, {"state": state, "questions": questions}).status_code == 200
    assert prefix_cache_hits(vllm_url) > before
