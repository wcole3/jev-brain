from dataclasses import asdict

import pytest

from gateway.layouts import PROMPTS_DIR, load_layout
from gateway.questions import render_question
from gateway.schema import Question
from tests.helpers import LAYOUTS, QUICKSTART, batch_for

NAME = "blurb-header-nolettername"
TEXTS = ["Increase temperature", "Decrease temperature", "Increase Enzyme Concentration"]


def choice(names, texts=TEXTS):
    return {"q": {"type": "choice", "instructions": "Which will help the assay?", "criteria": dict(zip(names, texts))}}


@pytest.fixture
def with_flag(monkeypatch):
    monkeypatch.setitem(LAYOUTS, NAME, load_layout(PROMPTS_DIR / "experiments" / f"{NAME}.toml"))


def shown(tok, layout_name, questions, orders=None):
    return tok.decode(batch_for(tok, layout_name, questions, orders).rows[0].ids)


def test_flag_is_the_only_difference_from_blurb_header(with_flag):
    arm, served = asdict(LAYOUTS[NAME]), asdict(LAYOUTS["blurb_header"])
    for d in (arm, served):
        del d["name"], d["sha256"]
    assert (arm.pop("drop_letter_names"), served.pop("drop_letter_names")) == (True, False)
    assert arm == served


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_letter_names_are_dropped(tok_name, request, with_flag):
    tok = request.getfixturevalue(tok_name)
    text = shown(tok, NAME, choice("ABC"))
    assert "(A) Increase temperature\n(B) Decrease temperature\n(C) Increase Enzyme Concentration" in text
    assert "(A) A: Increase temperature" in shown(tok, "blurb_header", choice("ABC"))


def test_reordered_options_show_one_letter_each(gemma_tok, with_flag):
    text = shown(gemma_tok, NAME, choice("ABC"), orders=[[2, 1, 0]])
    assert "(A) Increase Enzyme Concentration\n(B) Decrease temperature\n(C) Increase temperature" in text
    assert "(A) C:" in shown(gemma_tok, "blurb_header", choice("ABC"), orders=[[2, 1, 0]])


def test_names_still_report_back(with_flag):
    rendered = render_question(Question(**choice("ABC")["q"]), LAYOUTS[NAME])
    assert rendered.names == ["A", "B", "C"] and rendered.options == TEXTS


def test_empty_description_falls_back_to_the_name(with_flag):
    rendered = render_question(Question(**choice("ABC", ["Increase temperature", "", None])["q"]), LAYOUTS[NAME])
    assert rendered.options == ["Increase temperature", "B", "C"]


@pytest.mark.parametrize("names", ["ABD", "BAC", "abc", ["A", "B", "Cat"]])
def test_other_names_stay(names, with_flag):
    rendered = render_question(Question(**choice(names)["q"]), LAYOUTS[NAME])
    assert rendered.options == [f"{n}: {t}" for n, t in zip(names, TEXTS)]


def test_rows_without_letter_names_match_blurb_header(gemma_tok, with_flag):
    for a, s in zip(batch_for(gemma_tok, NAME).rows, batch_for(gemma_tok, "blurb_header").rows, strict=True):
        assert a.ids == s.ids
    assert set(QUICKSTART) == {r.question_id for r in batch_for(gemma_tok, NAME).rows}
