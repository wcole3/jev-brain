from pathlib import Path

import pytest

from gateway.labels import label_table
from gateway.layouts import load_layouts
from gateway.prompts import build_rows, chat_frame
from gateway.questions import render_question
from gateway.schema import Question
from tests.helpers import PROFILES, QUICKSTART, STATE, tokenizer_for

GOLDEN = Path(__file__).parent / "golden"
LAYOUTS = load_layouts()


def batch_for(tok, layout_name, questions=QUICKSTART, orders=None):
    layout = LAYOUTS[layout_name]
    rendered = {k: render_question(Question(**v), layout) for k, v in questions.items()}
    perms = {k: orders or [list(range(len(r.options)))] for k, r in rendered.items()}
    return build_rows(tok, chat_frame(tok, layout), layout, label_table(tok), STATE, rendered, perms)


def assert_golden(name: str, text: str) -> None:
    path = GOLDEN / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        pytest.fail(f"wrote new golden {path}; review it, then rerun")
    assert text == path.read_text()


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("layout_name", sorted(LAYOUTS))
def test_prompts_match_golden(profile, layout_name):
    tok = tokenizer_for(profile)
    batch = batch_for(tok, layout_name)
    assert_golden(f"{profile}/{layout_name}.txt", "\n=====\n".join(tok.decode(r.ids) for r in batch.rows))


@pytest.mark.parametrize("layout_name", sorted(LAYOUTS))
def test_rows_share_the_reported_prefix(qwen_tok, layout_name):
    batch = batch_for(qwen_tok, layout_name)
    first = batch.rows[0].ids[:batch.shared_len]
    assert all(r.ids[:batch.shared_len] == first for r in batch.rows)
    assert batch.input_tokens == batch.shared_len + sum(len(r.ids) - batch.shared_len for r in batch.rows)


def test_prefix_sharing_by_layout(qwen_tok):
    head = len(chat_frame(qwen_tok, LAYOUTS["question_first"]).head)
    assert batch_for(qwen_tok, "question_first").shared_len == head
    assert batch_for(qwen_tok, "header").shared_len > batch_for(qwen_tok, "decider_chat").shared_len > head


def test_rows_end_at_the_answer_slot_with_one_label_per_option(qwen_tok):
    batch = batch_for(qwen_tok, "decider_chat")
    for row in batch.rows:
        assert qwen_tok.decode(row.ids[-4:]).endswith("Answer: (")
    assert [len(r.label_ids) for r in batch.rows] == [3, 3, 2]


def test_wide_choice_splices_label_tokens(qwen_tok):
    labels = label_table(qwen_tok)
    wide = {"q": {"type": "choice", "instructions": "Pick", "criteria": {f"opt{i}": None for i in range(12)}}}
    row = batch_for(qwen_tok, "decider_chat", wide).rows[0]
    for token in labels.ids[:12]:
        assert token in row.ids
    assert row.label_ids == labels.ids[:12]


def test_reversed_order_shows_options_reversed(qwen_tok):
    two = {"q": {"type": "choice", "instructions": "Pick", "criteria": {"first": None, "second": None}}}
    row = batch_for(qwen_tok, "decider_chat", two, orders=[[1, 0]]).rows[0]
    assert "(A) second\n(B) first" in qwen_tok.decode(row.ids)
    assert row.perm == [1, 0]
