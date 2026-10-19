from dataclasses import asdict

import pytest

from gateway.layouts import PROMPTS_DIR, load_layout
from gateway.padding import Padding, newline_token
from gateway.prompts import image_context
from tests.helpers import LAYOUTS, STATE, batch_for, img, vision_for

BLURB = "You will be asked questions about the following context. Answer each with the letter of the best option.\n\n"
PAIRS = {"blurb-header": ("header", "questions"), "blurb-decider": ("decider_chat", "context")}
FIRST = {"header": "Questions that will be asked", "decider_chat": "Context:"}


def blurb_layout(name):
    return load_layout(PROMPTS_DIR / "experiments" / f"{name}.toml")


@pytest.fixture
def with_blurb_layouts(monkeypatch):
    monkeypatch.setitem(LAYOUTS, "blurb-header", blurb_layout("blurb-header"))
    monkeypatch.setitem(LAYOUTS, "blurb-decider", blurb_layout("blurb-decider"))


@pytest.mark.parametrize("name", PAIRS)
def test_blurb_layout_differs_only_by_the_prefix(name):
    served, field = PAIRS[name]
    blurb, base = asdict(blurb_layout(name)), asdict(LAYOUTS[served])
    for d in (blurb, base):
        del d["name"], d["sha256"]
    assert blurb.pop(field) == BLURB + base.pop(field)
    assert blurb == base
    assert blurb["order"][0] == field


@pytest.mark.parametrize("name", PAIRS)
@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_blurb_rows_match_served_after_the_blurb(name, tok_name, request, with_blurb_layouts):
    tok = request.getfixturevalue(tok_name)
    served = PAIRS[name][0]
    first = FIRST[served]
    for b, s in zip(batch_for(tok, name).rows, batch_for(tok, served).rows, strict=True):
        assert tok.decode(b.ids) == tok.decode(s.ids).replace(first, BLURB + first, 1)


def test_blurb_rows_share_the_prefix(qwen_tok, with_blurb_layouts):
    pad = Padding("front", 800, always=True, token=newline_token(qwen_tok))
    batch = batch_for(qwen_tok, "blurb-header", padding=pad)
    shared = batch.rows[0].ids[: batch.shared_len]
    assert all(r.ids[: batch.shared_len] == shared for r in batch.rows)
    assert BLURB.strip() in qwen_tok.decode(shared)


def test_blurb_decider_image_context(gemma_tok):
    layout = blurb_layout("blurb-decider")
    ctx = image_context(gemma_tok, layout, [img(), STATE], vision_for(gemma_tok))
    assert gemma_tok.decode(ctx.ids).startswith(BLURB.strip() + "\n\nContext:")
