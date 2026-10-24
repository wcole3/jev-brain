import json
from dataclasses import asdict, replace

import pytest

from gateway.labels import label_table
from gateway.layouts import PROMPTS_DIR, load_layout
from gateway.prompts import build_rows, chat_frame
from gateway.questions import render_question, render_state
from gateway.schema import Question
from tests.helpers import HLE, LAYOUTS, QUICKSTART, batch_for

CLEAN, NOINDEX = "reread-clean", "reread-noindex"
SENTIMENT = {"Negative": "Negative", "Neutral": "Neutral", "Positive": "Positive"}
SHAPES = {"(A)": "circle", "(B)": "heptagon", "(C)": "kite"}
ROWS = {"records": [{"v": i} for i in range(10)]}


def choice(criteria):
    return {"q": {"type": "choice", "instructions": "Which one?", "criteria": criteria}}


def options(criteria, name=CLEAN):
    return render_question(Question(**choice(criteria)["q"]), LAYOUTS[name]).options


@pytest.fixture(autouse=True)
def experiments(monkeypatch):
    for name in (CLEAN, NOINDEX):
        monkeypatch.setitem(LAYOUTS, name, load_layout(PROMPTS_DIR / "experiments" / f"{name}.toml"))


def test_experiments_differ_from_the_served_layout_only_by_their_keys():
    served = asdict(LAYOUTS["blurb_header_reread"])
    del served["name"], served["sha256"], served["again"]  # the arms ran with the joiner of their day
    keys = {CLEAN: {"index_arrays": True}, NOINDEX: {"same_name_once": False, "drop_label_names": False}}
    for name, flags in keys.items():
        arm = asdict(LAYOUTS[name])
        del arm["name"], arm["sha256"], arm["again"]
        assert {k: arm.pop(k) for k in flags} == flags
        assert arm == {k: v for k, v in served.items() if k not in flags}


def test_only_the_default_layout_turns_the_new_keys_on():
    for name in ("blurb_header", "decider_chat", "header", "question_first"):
        layout = LAYOUTS[name]
        assert (layout.same_name_once, layout.drop_label_names, layout.index_arrays) == (False, False, True)
    reread = LAYOUTS["blurb_header_reread"]
    assert (reread.same_name_once, reread.drop_label_names, reread.index_arrays) == (True, True, False)


def test_a_name_repeating_its_description_shows_once():
    assert options(SENTIMENT) == ["Negative", "Neutral", "Positive"]
    assert options({"Yes": "Yes", "No": "No"}) == ["Yes", "No"]
    assert options({"Yes": "Yes", "No": "Not so"}) == ["Yes", "No: Not so"]


def test_same_name_once_is_off_by_default():
    assert options(SENTIMENT, "blurb_header") == ["Negative: Negative", "Neutral: Neutral", "Positive: Positive"]


def test_same_name_once_leaves_other_types_alone():
    layout = LAYOUTS[CLEAN]
    noul = render_question(Question(type="noul", instructions="Is it red", criteria={"true": "yes"}), layout)
    assert noul.options == ["no", "yes: yes"]
    score = render_question(Question(type="score", instructions="How red", criteria=["a", "b"]), layout)
    assert score.options == ["0: a", "1: b"]


def test_bracketed_letter_names_drop_in_order():
    assert options(SHAPES) == ["circle", "heptagon", "kite"]
    assert options({"A": "x", "B": "y"}) == ["x", "y"]
    assert options(SHAPES, "blurb_header") == ["(A): circle", "(B): heptagon", "(C): kite"]


@pytest.mark.parametrize("names", [["(B)", "(A)", "(C)"], ["(A)", "(C)"], ["(B)", "(C)"], ["(A)", "B", "(C)"]])
def test_other_bracketed_names_stay(names):
    assert options(dict(zip(names, "xyz"))) == [f"{n}: {t}" for n, t in zip(names, "xyz")]


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_reversed_bracketed_options_show_one_letter_each(tok_name, request):
    tok = request.getfixturevalue(tok_name)
    text = tok.decode(batch_for(tok, CLEAN, choice(SHAPES), orders=[[2, 1, 0]]).rows[0].ids)
    assert "(A) kite\n(B) heptagon\n(C) circle" in text
    assert "(A) (C)" not in text and "(A) C" not in text


def test_names_still_report_back():
    for criteria in (SENTIMENT, SHAPES):
        rendered = render_question(Question(**choice(criteria)["q"]), LAYOUTS[CLEAN])
        assert rendered.names == list(criteria)


def test_colliding_options_show_in_full():
    assert options({"A": "same", "B": "same", "C": "other"}) == ["A: same", "B: same", "other"]
    assert options({"(A)": "same", "(B)": "same"}) == ["(A): same", "(B): same"]


def test_the_letter_drop_alone_has_no_guard(monkeypatch):
    letters_only = replace(LAYOUTS["blurb_header_reread"], same_name_once=False, drop_label_names=False)
    monkeypatch.setitem(LAYOUTS, "letters-only", letters_only)
    criteria = {"A": "same", "B": "same", "C": "other"}
    assert options(criteria, "letters-only") == ["same", "same", "other"]
    assert options(criteria, "blurb_header_reread") == ["A: same", "B: same", "other"]


def test_index_arrays_off_drops_only_the_annotation():
    on, off = render_state(ROWS), render_state(ROWS, index_arrays=False)
    assert json.loads(on)["records"][3] == {"_index": 3, "v": 3}
    assert off == json.dumps(ROWS) and "_index" not in off
    assert render_state("text", index_arrays=False) == "text"
    short = {"r": [1, 2]}
    assert render_state(short, False) == render_state(short)


def test_index_arrays_reach_the_prompt(gemma_tok):
    def shown(name):
        layout = LAYOUTS[name]
        rendered = {"q": render_question(Question(**choice(SENTIMENT)["q"]), layout)}
        state = render_state(ROWS, layout.index_arrays)
        batch = build_rows(
            gemma_tok, chat_frame(gemma_tok, layout), layout, label_table(gemma_tok), state, rendered, {"q": [[0, 1, 2]]}
        )
        return gemma_tok.decode(batch.rows[0].ids)

    assert '{"_index": 3, "v": 3}' in shown("blurb_header") and '{"_index": 3, "v": 3}' in shown(CLEAN)
    assert '{"v": 3}' in shown("blurb_header_reread") and "_index" not in shown("blurb_header_reread")


@pytest.mark.parametrize("questions", [HLE, QUICKSTART])
def test_served_layouts_render_as_before(gemma_tok, questions):
    """The flags off are the old code path: a replaced-flags copy of a served layout builds the same rows."""
    served = LAYOUTS["blurb_header_reread"]
    LAYOUTS["_copy"] = replace(served, same_name_once=False, drop_label_names=False, index_arrays=True)
    try:
        a, b = batch_for(gemma_tok, "_copy", questions), batch_for(gemma_tok, "blurb_header_reread", questions)
    finally:
        del LAYOUTS["_copy"]
    assert [r.ids for r in a.rows] == [r.ids for r in b.rows]


def test_flags_must_be_booleans(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text((PROMPTS_DIR / "blurb_header.toml").read_text() + 'same_name_once = "yes"\n')
    with pytest.raises(ValueError, match="same_name_once must be true or false"):
        load_layout(bad)
