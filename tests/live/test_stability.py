import threading
import time
import warnings

import httpx
import pytest

from tests.live.api import auth, post

pytestmark = pytest.mark.live

# Soft limit (warn only): bf16 logit steps under load move p by ~0.03, scaling 1/T;
# decider_chat noul T 1.386 gives ~0.045 worst case, lower-T layouts can exceed it.
MAX_DRIFT = 0.05
# a 0.05 move in each of two probabilities can close a 0.10 gap.
DECISIVE_GAP = 2 * MAX_DRIFT

BODY = {
    "state": "Customer: my invoice shows a charge I don't recognise and support hasn't replied in a week.",
    "questions": {
        "topic": {
            "type": "choice",
            "instructions": "Topic?",
            "criteria": {"billing": None, "shipping": None, "account": None, "other": None},
        },
        "anger": {"type": "score", "instructions": "Anger", "criteria": ["none", "some", "a lot"]},
        "escalate": {"type": "noul", "instructions": "Should a manager see this"},
    },
}


def distribution(answer: dict) -> list[float]:
    if answer["type"] == "noul":
        return [1 - answer["noul"], answer["noul"]]
    return list(answer["probabilities"].values())


def test_answers_stable_under_chat_load(gateway_url, served_model):
    idle = post(gateway_url, BODY).json()["answers"]
    stop = threading.Event()

    def chat_load():
        while not stop.is_set():
            httpx.post(
                f"{gateway_url}/v1/chat/completions",
                headers=auth(),
                timeout=600,
                json={
                    "model": served_model,
                    "max_tokens": 512,
                    "messages": [{"role": "user", "content": "Write a long story about a lighthouse keeper."}],
                },
            )

    threads = [threading.Thread(target=chat_load) for _ in range(4)]
    for t in threads:
        t.start()
    time.sleep(3)
    try:
        loaded = [post(gateway_url, BODY).json()["answers"] for _ in range(5)]
    finally:
        stop.set()
        for t in threads:
            t.join()
    drifts = []
    for run in loaded:
        for qid, answer in idle.items():
            p0, p1 = distribution(answer), distribution(run[qid])
            drifts.append((qid, answer["type"], max(abs(a - b) for a, b in zip(p0, p1))))
            first, second = sorted(p0, reverse=True)[:2]
            if first - second > DECISIVE_GAP:
                assert p0.index(max(p0)) == p1.index(max(p1))
    over = [f"{qid} ({kind}) {drift:.3f}" for qid, kind, drift in drifts if drift > MAX_DRIFT]
    if over:
        warnings.warn(f"drift over {MAX_DRIFT}: " + ", ".join(over))
