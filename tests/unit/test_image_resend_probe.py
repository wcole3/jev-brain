import asyncio
import json
from types import SimpleNamespace

import httpx

from scripts.image_resend_probe import measure, summarize, summary_markdown


def fake_batch():
    image = SimpleNamespace(part=lambda: {"type": "image_url", "url": "data:x;base64,AAAA", "uuid": "abc"})
    return SimpleNamespace(images=SimpleNamespace(images=[image]),
                           rows=[SimpleNamespace(ids=[1, 2, 3]), SimpleNamespace(ids=[1, 2, 4])])


def vllm(accept_uuid: bool, seen: list):
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        seen.append(body)
        if "url" not in body["content_parts"][0] and not accept_uuid:
            return httpx.Response(400, text="image url missing")
        return httpx.Response(200, json={})
    return httpx.MockTransport(handler)


def run_measure(accept_uuid: bool):
    seen: list = []

    async def go():
        async with httpx.AsyncClient(transport=vllm(accept_uuid, seen), base_url="http://v") as http:
            return await measure(http, "m", fake_batch())

    return asyncio.run(go()), seen


def test_resend_summary_reports_json_ms_and_uuid_outcome():
    ok, seen = run_measure(True)
    bad, _ = run_measure(False)
    assert seen[1]["content_parts"] == [{"type": "image_url", "uuid": "abc"}]
    assert seen[0]["token_ids"] == seen[1]["token_ids"] == [1, 2, 3]
    assert seen[0]["sampling_params"] == {"max_tokens": 1, "temperature": 0}
    assert ok["uuid_accepted"] and ok["json_ms"] >= 0 and ok["payload_bytes"] > 0
    assert not bad["uuid_accepted"] and bad["uuid_status"] == 400 and "missing" in bad["uuid_error"]
    s = summarize([ok, bad])
    assert s["uuid_accepted"] == 1 and s["requests"] == 2 and s["full_ms"] == ok["full_ms"]
    md = summary_markdown("p", s)
    assert "| 2 | 1 |" in md and "json_ms" in md


def test_summary_without_accepted_uuid_has_no_comparison():
    bad, _ = run_measure(False)
    s = summarize([bad])
    assert s["uuid_accepted"] == 0 and s["full_ms"] is None
    assert "n/a" in summary_markdown("p", s)
