"""Offline answers (gateway math on fresh logprobs) must match live /v1/systemone answers within bf16 noise."""

import dataclasses
import os

import httpx
import pytest

from gateway.app import load_engine, vllm_client
from gateway.config import Settings
from gateway.decide import answers_for, read_rows
from gateway.schema import SystemOneRequest
from scripts.splits import rows_for
from tests.live.api import auth

pytestmark = pytest.mark.live
N = int(os.environ.get("SPOTCHECK_N", "20"))
MAX_DRIFT = 0.05  # same bf16 rule as test_stability
DECISIVE_GAP = 2 * MAX_DRIFT


def top(probabilities: dict) -> str:
    return max(probabilities, key=probabilities.get)


def close(live: dict, offline: dict) -> bool:
    if live["type"] == "noul":
        return abs(live["noul"] - offline["noul"]) <= MAX_DRIFT
    a, b = live["probabilities"], offline["probabilities"]
    if any(abs(a[k] - b[k]) > MAX_DRIFT for k in a):
        return False
    first, second = sorted(b.values(), reverse=True)[:2]
    return first - second <= DECISIVE_GAP or top(a) == top(b)


async def test_offline_answers_match_live(gateway_url, vllm_url):
    async with httpx.AsyncClient(base_url=gateway_url, headers=auth(), timeout=600) as gw:
        profile = (await gw.get("/health")).json()["profile"]
        s = dataclasses.replace(
            Settings.from_profile(profile), vllm_url=vllm_url, vllm_api_key=os.environ.get("VLLM_API_KEY") or None
        )
        async with vllm_client(s, None) as client:
            engine = load_engine(s, client)
            misses = []
            for row in rows_for("eval")[:N]:
                body = {"model": "jev-latest", "state": row["state"], "questions": row["questions"]}
                live = (await gw.post("/v1/systemone", json=body)).json()["answers"]
                r = await read_rows(engine, SystemOneRequest.model_validate(body))
                offline = answers_for(r.questions, r.reads, engine.temperatures[r.layout])
                misses += [(row["id"], q) for q in live if not close(live[q], offline[q])]
    assert misses == []
