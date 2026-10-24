from dataclasses import replace

import pytest

from gateway.layouts import PROMPTS_DIR, load_layout
from gateway.prompts import chat_frame
from tests.helpers import LAYOUTS, batch_for

H2 = "reread-system"


@pytest.fixture
def h2(monkeypatch):
    monkeypatch.setitem(LAYOUTS, H2, load_layout(PROMPTS_DIR / "experiments" / f"{H2}.toml"))


def test_served_layouts_have_no_system_turn():
    assert all(layout.system == "" for layout in LAYOUTS.values())


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_system_turn_sits_before_the_user_turn(tok_name, request, h2):
    tok = request.getfixturevalue(tok_name)
    head = tok.decode(chat_frame(tok, LAYOUTS[H2]).head)
    assert head.index(LAYOUTS[H2].system) < head.index("user")
    assert chat_frame(tok, LAYOUTS[H2]).tail == chat_frame(tok, LAYOUTS["blurb_header_reread"]).tail


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_rows_differ_only_by_the_head(tok_name, request, h2):
    tok = request.getfixturevalue(tok_name)
    served, arm = batch_for(tok, "blurb_header_reread"), batch_for(tok, H2)
    cut = len(chat_frame(tok, LAYOUTS[H2]).head), len(chat_frame(tok, LAYOUTS["blurb_header_reread"]).head)
    assert [r.ids[cut[0]:] for r in arm.rows] == [r.ids[cut[1]:] for r in served.rows]


def test_h2_is_the_served_layout_plus_a_system_turn(h2):
    assert replace(LAYOUTS[H2], name="blurb_header_reread", sha256=LAYOUTS["blurb_header_reread"].sha256, system="") == (
        LAYOUTS["blurb_header_reread"]
    )
