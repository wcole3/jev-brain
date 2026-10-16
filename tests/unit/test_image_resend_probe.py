import asyncio
import json
from types import SimpleNamespace

import httpx

from scripts.image_resend_probe import measure, summarize, summary_markdown


def fake_batch():
    image = SimpleNamespace(part=lambda: {"type": "image_url", "url": "data:x;base64,AAAA", "uuid": "abc"})
    return SimpleNamespace(images=SimpleNamespace(images=[image]),
                           rows=[SimpleNamespace(ids=[1, 2, 3], label_ids=[10, 11]),
                                 SimpleNamespace(ids=[1, 2, 4], label_ids=[10, 11])])


def answer(lp10: float, lp11: float) -> dict:
    top = [{"token": "token_id:10", "logprob": lp10}, {"token": "token_id:11", "logprob": lp11},
           {"token": "token_id:12", "logprob": -20.0}]
    return {"choices": [{"logprobs": {"content": [{"top_logprobs": top}]}}]}


def vllm(mode: str, seen: list):
    """mode: reuse (same logprobs), reject (400 on uuid-only) or drop (200 but different logprobs)."""
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        seen.append(body)
        uuid_only = "url" not in body["content_parts"][0]
        if uuid_only and mode == "reject":
            return httpx.Response(400, text="image url missing")
        return httpx.Response(200, json=answer(-3.0, -0.1) if uuid_only and mode == "drop" else answer(-0.1, -3.0))
    return httpx.MockTransport(handler)


def run_measure(mode: str):
    seen: list = []

    async def go():
        async with httpx.AsyncClient(transport=vllm(mode, seen), base_url="http://v") as http:
            return await measure(http, "m", fake_batch())

    return asyncio.run(go()), seen


def test_resend_summary_reports_json_ms_and_uuid_outcome():
    ok, seen = run_measure("reuse")
    bad, _ = run_measure("reject")
    dropped, _ = run_measure("drop")
    assert seen[0]["sampling_params"]["logprob_token_ids"] == [10, 11, 0]
    assert ok["uuid_same_answer"] and ok["max_abs_dlogprob"] == 0
    assert dropped["uuid_accepted"] and not dropped["uuid_same_answer"] and not dropped["top_match"]
    assert not bad["uuid_same_answer"]
    assert seen[1]["content_parts"] == [{"type": "image_url", "uuid": "abc"}]
    assert seen[0]["token_ids"] == seen[1]["token_ids"] == [1, 2, 3]
    assert seen[0]["sampling_params"]["max_tokens"] == 1 and seen[0]["sampling_params"]["temperature"] == 0
    assert ok["uuid_accepted"] and ok["json_ms"] >= 0 and ok["payload_bytes"] > 0
    assert not bad["uuid_accepted"] and bad["uuid_status"] == 400 and "missing" in bad["uuid_error"]
    s = summarize([ok, bad, dropped])
    assert s["uuid_accepted"] == 2 and s["uuid_same_answer"] == 1 and s["requests"] == 3 and s["full_ms"] is not None
    md = summary_markdown("p", s)
    assert "| 3 | 2 | 1 |" in md and "json_ms" in md


def test_summary_without_accepted_uuid_has_no_comparison():
    bad, _ = run_measure("reject")
    s = summarize([bad])
    assert s["uuid_accepted"] == 0 and s["full_ms"] is None
    assert "n/a" in summary_markdown("p", s)
