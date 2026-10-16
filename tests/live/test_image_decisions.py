"""Image decisions on a vision profile: answers, cache reuse, refusals, and our image token counts against vLLM's."""

import asyncio
import base64
import io
import json
import os
import uuid

import httpx
import PIL.Image
import pytest

from gateway.app import load_engine
from gateway.config import Settings
from gateway.decide import build_batch
from gateway.images import MAX_BODY_BYTES, MAX_PIXELS
from gateway.prompts import Batch
from gateway.schema import SystemOneRequest
from gateway.vision import load_vision
from tests.live.api import auth, post
from tests.live.test_prefix_cache import prefix_cache_hits

pytestmark = pytest.mark.live

GENERATE_PATH = "/inference/v1/generate"
NOTES = "Notes: the photo was taken at the quarterly review, next to the sales board. " * 100


def unique_png(width: int, height: int) -> str:
    """A PNG data URL no earlier request sent: a random colour and one random pixel give it a new cache key."""
    seed = uuid.uuid4().bytes
    im = PIL.Image.new("RGB", (width, height), tuple(seed[:3]))
    im.putpixel((0, 0), tuple(seed[3:6]))
    out = io.BytesIO()
    im.save(out, format="PNG")
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


def noul(statement: str) -> dict:
    return {"type": "noul", "instructions": statement}


def choice(question: str, options: list[str]) -> dict:
    return {"type": "choice", "instructions": question, "criteria": dict.fromkeys(options)}


@pytest.fixture(scope="module")
def health(gateway_url) -> dict:
    return httpx.get(f"{gateway_url}/health", timeout=5).json()


@pytest.fixture(scope="module")
def settings(health) -> Settings:
    """The live profile's settings, built here so the test counts image tokens the way the gateway does."""
    if not health["systemone_images"]:
        pytest.skip(f"profile {health['profile']} serves text only")
    s = Settings.from_profile(health["profile"])
    differ = f"the gateway's MM_PROCESSOR_KWARGS differ from profiles/{health['profile']}.env"
    assert s.mm_processor_kwargs == health["mm_processor_kwargs"], differ
    return s


@pytest.fixture(scope="module")
def vision(settings):
    return load_vision(settings)


@pytest.fixture(scope="module")
def engine(settings):
    client = httpx.AsyncClient()
    yield load_engine(settings, client, calibrated=False)
    asyncio.run(client.aclose())


@pytest.mark.usefixtures("settings")
def test_one_image_several_questions(gateway_url):
    questions = {
        "bright": noul("The image is bright"),
        "photo": noul("The image is a photograph"),
        "colour": choice("Main colour?", ["red", "green", "blue", "other"]),
        "kind": choice("What is shown?", ["chart", "photo", "plain colour"]),
    }
    r = post(gateway_url, {"images": [unique_png(640, 480)], "state": "One picture.", "questions": questions})
    assert r.status_code == 200, r.text
    answers = r.json()["answers"]
    assert {qid: a["type"] for qid, a in answers.items()} == {qid: q["type"] for qid, q in questions.items()}
    for qid in ("bright", "photo"):
        assert 0 <= answers[qid]["noul"] <= 1
    for qid in ("colour", "kind"):
        assert sum(answers[qid]["probabilities"].values()) == pytest.approx(1, abs=1e-2)


@pytest.mark.usefixtures("settings")
def test_image_parts_in_state(gateway_url):
    body = {"state": [{"image": unique_png(320, 240)}, "text"], "questions": {"q": noul("The image is dark")}}
    r = post(gateway_url, body)
    assert r.status_code == 200, r.text


def batch_for(engine, body: dict) -> Batch:
    """The rows the gateway builds for this body."""
    return asyncio.run(build_batch(engine, SystemOneRequest.model_validate(body)))[2]


def image_end(engine, vision, body: dict) -> int:
    """Where the request's first image ends once vLLM expands it."""
    batch = batch_for(engine, body)
    return batch.rows[0].ids.index(vision.placeholder[0]) + vision.expanded(batch.images.images[0])


def test_second_question_hits_the_image_cache(gateway_url, vllm_url, settings, vision, engine):
    # decider_chat puts the context first, so two questions share it; the notes carry it past the image
    state = [{"image": unique_png(1024, 1024)}, NOTES]
    first = {"layout": "decider_chat", "state": state, "questions": {"a": noul("The image is bright")}}
    second = {"layout": "decider_chat", "state": state, "questions": {"b": noul("The image shows a person")}}
    want = image_end(engine, vision, first)
    if settings.prefix_block:
        want -= want % settings.prefix_block  # hybrid Qwen reuses whole blocks only
    assert post(gateway_url, first).status_code == 200
    before = prefix_cache_hits(vllm_url)
    assert post(gateway_url, second).status_code == 200
    assert prefix_cache_hits(vllm_url) - before >= want


def generate(vllm_url: str, model: str, ids: list[int], parts: list[dict]) -> list[int]:
    """vLLM's token-in endpoint, returning the prompt ids after it expands the images."""
    key = os.environ.get("VLLM_API_KEY")
    body = {
        "model": model,
        "token_ids": ids,
        "content_parts": parts,
        "sampling_params": {"max_tokens": 1, "temperature": 0},
        "return_token_ids": True,
    }
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    r = httpx.post(f"{vllm_url}{GENERATE_PATH}", json=body, headers=headers, timeout=600)
    assert r.status_code == 200, r.text
    return r.json()["prompt_token_ids"]


SIZES = {
    "square": [(1024, 1024)],
    "odd": [(1280, 1092)],
    "tiny": [(10, 10)],
    "thin": [(3, 900)],  # over 200:1: gemma counts it, qwen refuses it
    "downscaled": [(4000, 3000)],
    "two images": [(640, 480), (800, 600)],
}


@pytest.mark.parametrize("sizes", SIZES.values(), ids=SIZES.keys())
def test_expanded_lengths_match_vllm(gateway_url, vllm_url, served_model, settings, vision, engine, sizes):
    body = {"images": [unique_png(w, h) for w, h in sizes], "state": "Pictures.", "questions": {"q": noul("Bright")}}
    if sizes == SIZES["thin"] and settings.hf_model.startswith("Qwen/"):
        r = post(gateway_url, body)
        assert r.status_code == 400 and "200:1" in r.text, r.text
        return
    batch = batch_for(engine, body)
    images = batch.images.images
    assert all(i.width * i.height <= MAX_PIXELS for i in images)
    ids = batch.rows[0].ids
    expanded = generate(vllm_url, served_model, ids, [i.part() for i in images])
    assert len(expanded) == len(ids) + sum(vision.added(i) for i in images)


def test_oversized_body_is_400(gateway_url):
    state = "x" * (MAX_BODY_BYTES + 1)
    content = json.dumps({"state": state, "questions": {"q": noul("Long")}}).encode()
    headers = auth() | {"Content-Type": "application/json"}
    r = httpx.post(f"{gateway_url}/v1/systemone", content=content, headers=headers, timeout=600)
    assert r.status_code == 400
    assert "request body over 20 MB" in r.text


def test_over_long_image_prompt_is_422(gateway_url, settings, engine):
    # the text alone fits under the cap and only the image's expanded tokens push the prompt over it
    limit = settings.systemone_max_len
    body = {"images": [unique_png(640, 480)], "state": "Pictures.", "questions": {"q": noul("Long")}}
    short = batch_for(engine, body)
    body["state"] += " word" * (limit - len(short.rows[0].ids) - short.added // 2)  # " word" is one token
    if len(json.dumps(body)) > MAX_BODY_BYTES:
        pytest.skip(f"text filling {limit} tokens does not fit in the 20 MB body limit")
    batch = batch_for(engine, body)
    assert len(batch.rows[0].ids) < limit <= batch.longest, "the filler missed the window only the image can cross"
    r = post(gateway_url, body)
    assert r.status_code == 422
    assert "maximum context length" in r.text
