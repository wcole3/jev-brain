"""Values shared by tests. Import from here, not from conftest or other test modules."""

import functools
import hashlib
import json

import httpx
from transformers import AutoTokenizer

from gateway.config import Settings
from gateway.images import Image
from gateway.labels import label_table
from gateway.layouts import load_layouts
from gateway.padding import OFF
from gateway.prompts import build_rows, chat_frame, image_context
from gateway.questions import render_question
from gateway.schema import Question
from gateway.vision import Vision

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
# A one-choice HLE question named A..E and a score question; ORDERS show its options three ways.
HLE = {
    "hle": {
        "type": "choice",
        "instructions": "Which of the following will help troubleshoot an enzyme kinetics assay?",
        "criteria": {
            "A": "Increase temperature",
            "B": "Decrease temperature",
            "C": "Increase Enzyme Concentration",
            "D": "Decrease Enzyme Concentration",
            "E": "None of the above",
        },
    },
    "rank": {
        "type": "score",
        "instructions": "How sure is the assay",
        "criteria": ["no", "a bit", "half", "most", "all"],
    },
}
ORDERS = [[0, 1, 2, 3, 4], [4, 3, 2, 1, 0], [2, 0, 4, 1, 3]]
STATE = "Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP."
LAYOUTS = load_layouts()


def batch_for(tok, layout_name, questions=QUICKSTART, orders=None, padding=OFF, images=None):
    """build_rows for STATE, one row per question (or per order in `orders`)."""
    layout = LAYOUTS[layout_name]
    rendered = {k: render_question(Question(**v), layout) for k, v in questions.items()}
    perms = {k: orders or [list(range(len(r.options)))] for k, r in rendered.items()}
    return build_rows(
        tok, chat_frame(tok, layout), layout, label_table(tok), STATE, rendered, perms, padding, images=images
    )


def img() -> Image:
    """A stand-in image: prompts only read its size, and vision_for counts 100 soft tokens for any size."""
    data = b"stand-in image"
    return Image(data, "image/png", 64, 64, hashlib.sha256(data).hexdigest())


GEMMA_IMAGE = ["<|image|>"]
QWEN_IMAGE = ["<|vision_start|>", "<|image_pad|>", "<|vision_end|>"]


def vision_for(tok) -> Vision:
    """The tokenizer's own image placeholder (gemma or qwen) and 100 soft tokens per image."""
    marks = GEMMA_IMAGE if GEMMA_IMAGE[0] in tok.get_added_vocab() else QWEN_IMAGE
    return Vision(tuple(tok.convert_tokens_to_ids(marks)), lambda w, h: 100)


def image_batch(tok, layout_name, questions=1, padding=OFF, instructions=None, vision=None):
    """batch_for with one image before STATE and `questions` yes/no questions."""
    asked = {f"q{k}": {"type": "noul", "instructions": instructions or f"Shape {k} is red"} for k in range(questions)}
    images = image_context(tok, LAYOUTS[layout_name], [img(), STATE], vision or vision_for(tok))
    return batch_for(tok, layout_name, asked, padding=padding, images=images)


class FavourFirstLabel:
    """Fake readout: label A always most likely (logprobs 0, -1, -2, ...). Text reads land in calls, image reads
    in image_calls."""

    def __init__(self):
        self.calls = []
        self.image_calls = []

    def logprobs(self, ids: list[int]) -> list[float]:
        return [-float(j) for j in range(len(ids))]

    async def letter_logprobs(self, prompts, label_ids, shared_len):
        self.calls.append((prompts, label_ids, shared_len))
        return [self.logprobs(ids) for ids in label_ids]

    async def image_logprobs(self, prompts, label_ids, shared_len, shared_tokens, parts, prefix_parts):
        self.image_calls.append((prompts, label_ids, shared_len, shared_tokens, parts, prefix_parts))
        return [self.logprobs(ids) for ids in label_ids]


class SureOf(FavourFirstLabel):
    """FavourFirstLabel, but questions with one of these option counts read 0, -10, -20, ...: sure at any tau."""

    def __init__(self, *counts: int):
        super().__init__()
        self.counts = counts

    def logprobs(self, ids: list[int]) -> list[float]:
        gap = 10.0 if len(ids) in self.counts else 1.0
        return [-gap * j for j in range(len(ids))]


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
        return httpx.Response(200, json={"version": "0.32.0"})
    return httpx.Response(404, json={"path": path})
