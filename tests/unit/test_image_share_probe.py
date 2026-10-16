import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest

from scripts.image_share_probe import ARMS, Probe, counters, summarize, summary_markdown


def record(arm: str, questions: int, ratio: float, ms: float) -> dict:
    return {"arm": arm, "questions": questions, "ratio": ratio, "ms": ms}


RECORDS = [
    record("all", 4, 1.30, 400.0), record("prefix", 4, 1.00, 500.0),
    record("all", 4, 1.10, 300.0), record("prefix", 4, 1.02, 520.0),
    record("all", 4, 1.20, 900.0), record("prefix", 4, 0.98, 480.0),
    record("all", 16, 2.50, 1200.0), record("prefix", 16, 1.05, 1100.0),
]


def test_summarize_takes_medians_per_arm_and_question_count_in_run_order():
    assert summarize(RECORDS) == [
        {"arm": "all", "questions": 4, "reps": 3, "ratio": pytest.approx(1.20), "ms": 400.0},
        {"arm": "prefix", "questions": 4, "reps": 3, "ratio": pytest.approx(1.00), "ms": 500.0},
        {"arm": "all", "questions": 16, "reps": 1, "ratio": 2.50, "ms": 1200.0},
        {"arm": "prefix", "questions": 16, "reps": 1, "ratio": 1.05, "ms": 1100.0},
    ]


def test_summary_markdown_has_one_row_per_arm_and_question_count():
    md = summary_markdown("gemma-4-31b", summarize(RECORDS))
    assert "| all | 4 | 3 | 1.20 | 400 |" in md
    assert "| prefix | 16 | 1 | 1.05 | 1100 |" in md
    assert "computed includes the prefix pad; usage does not" in md


def test_counters_sum_label_sets_and_skip_lookalikes():
    page = """# HELP vllm:prompt_tokens_total Number of prefill tokens processed.
vllm:prompt_tokens_total{engine="0",model_name="m"} 100.0
vllm:prompt_tokens_total{engine="1",model_name="m"} 20.0
vllm:prompt_tokens_cached_total{engine="0",model_name="m"} 64.0
vllm:prompt_tokens_created{engine="0",model_name="m"} 1.7e9
vllm:prompt_tokens_by_source_total{engine="0",source="local_compute"} 999.0
"""
    assert counters(page) == {"prompt": 120.0, "cached": 64.0}


def fake_batch():
    image = SimpleNamespace(part=lambda: {"type": "image_url", "url": "data:x", "uuid": "u"})
    return SimpleNamespace(images=SimpleNamespace(images=[image]), images_shared=True, shared_len=2,
                           unpadded_len=3, shared_tokens=2, added=5, input_tokens=10,
                           rows=[SimpleNamespace(ids=[1, 2, 3]), SimpleNamespace(ids=[1, 2, 4]),
                                 SimpleNamespace(ids=[1, 2, 5])])


def test_row_arm_sends_row_one_first():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/metrics":
            return httpx.Response(200, text="vllm:prompt_tokens_total 10\n")
        seen.append(json.loads(request.content)["token_ids"])
        return httpx.Response(200, json={})

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://v") as http:
            return await Probe(http, "m").call_set(fake_batch(), "row")

    asyncio.run(go())
    assert seen[0] == [1, 2, 3]
    assert sorted(seen[1:]) == [[1, 2, 4], [1, 2, 5]]
    assert ARMS == ("all", "prefix", "row")


def test_summarize_handles_the_row_arm():
    md = summary_markdown("p", summarize([record("row", 4, 1.0, 450.0)]))
    assert "| row | 4 | 1 | 1.00 | 450 |" in md
