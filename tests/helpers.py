"""Values shared by tests. Import from here, not from conftest or other test modules."""

import functools
import json

import httpx
from transformers import AutoTokenizer

from gateway.config import Settings
from gateway.labels import label_table
from gateway.layouts import load_layouts
from gateway.padding import OFF
from gateway.prompts import build_rows, chat_frame
from gateway.questions import render_question
from gateway.schema import Question

PROFILES = ["qwen3.8-27b", "qwen3.6-27b", "gemma-4-31b"]


@functools.cache
def tokenizer_for(profile: str):
    """The pinned tokenizer of a profile (downloads a few MB into the HF cache once)."""
    s = Settings.from_profile(profile)
    return AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)


QUICKSTART = {
    "department": {
        "type": "choice",
        "instructions": "Which team should handle this",
        "criteria": {
            "billing": "Payment or subscription issues",
            "technical": "Bugs or integration problems",
            "sales": "Pricing or account questions",
        },
    },
    "frustration": {
        "type": "score",
        "instructions": "How frustrated the customer appears",
        "criteria": ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
    },
    "is_urgent": {"type": "noul", "instructions": "The message conveys urgency or time-sensitivity"},
}
STATE = "Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP."
LAYOUTS = load_layouts()


def batch_for(tok, layout_name, questions=QUICKSTART, orders=None, padding=OFF):
    """build_rows for STATE, one row per question (or per order in `orders`)."""
    layout = LAYOUTS[layout_name]
    rendered = {k: render_question(Question(**v), layout) for k, v in questions.items()}
    perms = {k: orders or [list(range(len(r.options)))] for k, r in rendered.items()}
    return build_rows(tok, chat_frame(tok, layout), layout, label_table(tok), STATE, rendered, perms, padding)


class FavourFirstLabel:
    """Fake readout: label A always most likely (logprobs 0, -1, -2, ...)."""

    def __init__(self):
        self.calls = []

    async def letter_logprobs(self, prompts, label_ids, shared_len):
        self.calls.append((prompts, label_ids, shared_len))
        return [[-float(j) for j in range(len(ids))] for ids in label_ids]


SSE = b'data: {"choices": []}\n\ndata: [DONE]\n\n'


def fake_vllm(request: httpx.Request) -> httpx.Response:
    """A stand-in vLLM: label logprobs for completions, chat echoed back, and the GET routes the gateway uses."""
    path = request.url.path
    if path == "/v1/completions":
        body = json.loads(request.content)
        top = {f"token_id:{t}": -0.001 * t for t in body["logprob_token_ids"]}
        return httpx.Response(
            200,
            json={"choices": [{"index": i, "logprobs": {"top_logprobs": [top]}} for i in range(len(body["prompt"]))]},
        )
    if path == "/v1/chat/completions":
        body = json.loads(request.content)
        if body.get("stream"):
            return httpx.Response(200, content=SSE, headers={"content-type": "text/event-stream"})
        return httpx.Response(200, json={"echo": body})
    if path == "/v1/models":
        return httpx.Response(200, json={"object": "list", "data": [{"id": "qwen3.6-27b", "object": "model"}]})
    if path == "/health":
        return httpx.Response(200)
    if path == "/version":
        return httpx.Response(200, json={"version": "0.30.0"})
    return httpx.Response(404, json={"path": path})
