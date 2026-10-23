from dataclasses import replace

import pytest

from gateway.labels import label_table
from gateway.layouts import PROMPTS_DIR, load_layout
from gateway.padding import Padding, newline_token
from gateway.prompts import build_rows, chat_frame
from gateway.questions import render_question
from gateway.schema import Question
from tests.helpers import HLE, LAYOUTS, ORDERS, QUICKSTART, STATE, batch_for, image_batch

NAME = "blurb_header_reread"
ONE = {"hle": HLE["hle"]}


@pytest.fixture
def arms(monkeypatch):
    """Arm B and blurb_header, both without letter names, and the served layout with each read_twice mode."""
    arm_b = load_layout(PROMPTS_DIR / "experiments" / "blurb-header-again-b.toml")
    served = LAYOUTS[NAME]
    for name, layout in {
        "arm-b": replace(arm_b, drop_letter_names=True),
        "once": replace(LAYOUTS["blurb_header"], drop_letter_names=True),
        "always": replace(served, read_twice="always"),
        "off": replace(served, read_twice="off"),
    }.items():
        monkeypatch.setitem(LAYOUTS, name, layout)


def ids(batch):
    return [(r.ids, r.label_ids, r.perm) for r in batch.rows]


def test_served_layout_is_blurb_header_plus_the_new_keys():
    served, base = LAYOUTS[NAME], LAYOUTS["blurb_header"]
    plain = replace(served, name=base.name, sha256=base.sha256, drop_letter_names=False, again="", read_twice="off",
                    same_name_once=False, drop_label_names=False, index_arrays=True)
    assert plain == base
    assert (served.drop_letter_names, served.read_twice) == (True, "one-question")


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_one_question_reads_like_arm_b(tok_name, request, arms):
    tok = request.getfixturevalue(tok_name)
    assert ids(batch_for(tok, NAME, ONE, ORDERS)) == ids(batch_for(tok, "arm-b", ONE, ORDERS))
    assert ids(batch_for(tok, "always", ONE, ORDERS)) == ids(batch_for(tok, "arm-b", ONE, ORDERS))


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
@pytest.mark.parametrize("questions", [HLE, QUICKSTART])
def test_more_questions_read_once(tok_name, questions, request, arms):
    tok = request.getfixturevalue(tok_name)
    assert ids(batch_for(tok, NAME, questions)) == ids(batch_for(tok, "once", questions))
    assert ids(batch_for(tok, "always", questions)) == ids(batch_for(tok, "arm-b", questions))


def test_off_reads_once(gemma_tok, arms):
    assert ids(batch_for(gemma_tok, "off", ONE, ORDERS)) == ids(batch_for(gemma_tok, "once", ONE, ORDERS))


def test_a_question_without_rows_still_counts(gemma_tok):
    """A second pass gives unsure questions rows and others none; the prefix must stay the first pass's."""
    layout = LAYOUTS[NAME]
    rendered = {k: render_question(Question(**v), layout) for k, v in HLE.items()}
    perms = {"hle": [[4, 3, 2, 1, 0]], "rank": []}
    frame, labels = chat_frame(gemma_tok, layout), label_table(gemma_tok)
    second = build_rows(gemma_tok, frame, layout, labels, STATE, rendered, perms)
    assert second.rows[0].ids == batch_for(gemma_tok, NAME, HLE, [[4, 3, 2, 1, 0]]).rows[0].ids


def test_images_read_once(gemma_tok, arms):
    reread, once = image_batch(gemma_tok, NAME), image_batch(gemma_tok, "once")
    assert ids(reread) == ids(once) and reread.images_shared


@pytest.mark.parametrize("mode", ["front", "end"])
def test_padding_keeps_one_shared_prefix(qwen_tok, mode, arms):
    pad = Padding(mode, 800, always=True, token=newline_token(qwen_tok))
    batch = batch_for(qwen_tok, NAME, ONE, ORDERS, padding=pad)
    assert batch.shared_len % 800 == 0 and batch.shared_len > batch.unpadded_len
    assert all(r.ids[: batch.shared_len] == batch.rows[0].ids[: batch.shared_len] for r in batch.rows)
    unpadded = batch_for(qwen_tok, "arm-b", ONE, ORDERS)
    assert [[i for i in r.ids if i != pad.token] for r in batch.rows] == [
        [i for i in r.ids if i != pad.token] for r in unpadded.rows
    ]


def test_middle_padding_has_no_site_in_a_context_read_twice(qwen_tok, arms):
    pad = Padding("middle", 800, always=True, token=newline_token(qwen_tok))
    batch = batch_for(qwen_tok, NAME, ONE, ORDERS, padding=pad)
    assert batch.shared_len == batch.unpadded_len
    assert ids(batch) == ids(batch_for(qwen_tok, "arm-b", ONE, ORDERS))
    assert batch_for(qwen_tok, NAME, padding=pad).shared_len % 800 == 0  # read once: padded as before


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (('read_twice = "one-question"', 'read_twice = "twice"'), "one of"),
        (('again = "\\n\\nHmm, I should read that again before answer\\n\\n"', ""), "again text"),
        (('"context", "question"', '"context", "again", "question"'), "no again part"),
        (('["questions", "context", "question", "options"]', '["question", "options", "context"]'), "shared part"),
    ],
)
def test_bad_read_twice_refused(tmp_path, change, message):
    text = (PROMPTS_DIR / f"{NAME}.toml").read_text()
    assert change[0] in text
    (tmp_path / "bad.toml").write_text(text.replace(*change))
    with pytest.raises(ValueError, match=message):
        load_layout(tmp_path / "bad.toml")
