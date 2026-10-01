"""Answers rebuilt from collect.py's records must match live /v1/systemone answers within bf16 noise."""

import dataclasses
import os

import httpx
import pytest

from gateway.answers import answer
from gateway.app import load_engine, vllm_client
from gateway.config import Settings
from gateway.decide import blend
from gateway.orders import option_orders
from gateway.questions import render_question
from gateway.schema import Question
from scripts.collect import collect_one
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


def offline_answers(engine, row: dict, rec: dict, layout: str, orders: str) -> dict:
    """The live arm's orders picked out of the collected reads, then the gateway's own math."""
    out = {}
    for qid, reads in rec["questions"].items():
        q = render_question(Question(**row["questions"][qid]), engine.layouts[layout])
        wanted = option_orders(len(q.options), orders)
        chosen = [(r["logprobs"], r["perm"]) for r in reads if r["perm"] in wanted]
        out[qid] = answer(q, blend(chosen, engine.temperatures[layout][q.type]))
    return out


async def test_offline_answers_match_live(gateway_url, vllm_url):
    async with httpx.AsyncClient(base_url=gateway_url, headers=auth(), timeout=600) as gw:
        health = (await gw.get("/health")).json()
        layout, orders = health["prompt_layout"], health["option_orders"]
        s = dataclasses.replace(
            Settings.from_profile(health["profile"]),
            vllm_url=vllm_url,
            vllm_api_key=os.environ.get("VLLM_API_KEY") or None,
        )
        async with vllm_client(s, None) as client:
            engine = load_engine(s, client)
            misses = []
            for row in rows_for("eval")[:N]:
                rec = await collect_one(engine, row, layout)
                if rec["status"] != "ok":
                    continue
                body = {"model": "jev-latest", "state": row["state"], "questions": row["questions"]}
                live = (await gw.post("/v1/systemone", json=body)).json()["answers"]
                offline = offline_answers(engine, row, rec, layout, orders)
                misses += [(row["id"], q) for q in live if not close(live[q], offline[q])]
    assert misses == []
