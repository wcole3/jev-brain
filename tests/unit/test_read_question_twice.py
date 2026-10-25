import pytest

from gateway.layouts import PROMPTS_DIR, load_layout
from tests.helpers import HLE, LAYOUTS, ORDERS, QUICKSTART, batch_for

ONE = {"hle": HLE["hle"]}


@pytest.fixture
def arms(monkeypatch):
    for name in ("reread-h1", "reread-h1q", "reread-h1q-opts"):
        monkeypatch.setitem(LAYOUTS, name, load_layout(PROMPTS_DIR / "experiments" / f"{name}.toml"))


def ids(batch):
    return [(r.ids, r.label_ids, r.perm) for r in batch.rows]


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_one_question_reads_like_h1(tok_name, request, arms):
    tok = request.getfixturevalue(tok_name)
    assert ids(batch_for(tok, "reread-h1q", ONE, ORDERS)) == ids(batch_for(tok, "reread-h1", ONE, ORDERS))
    text = tok.decode(batch_for(tok, "reread-h1q", ONE, ORDERS).rows[1].ids)
    assert text.count("(A) None of the above") == 2 and "\n\n\n" not in text


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_more_questions_read_like_the_default(tok_name, request, arms):
    tok = request.getfixturevalue(tok_name)
    assert ids(batch_for(tok, "reread-h1q", QUICKSTART)) == ids(batch_for(tok, "blurb_header_reread", QUICKSTART))


def test_needs_the_per_question_parts_last(tmp_path):
    text = (PROMPTS_DIR / "question_first.toml").read_text()
    (tmp_path / "bad.toml").write_text(text + '\nagain = "\\n\\nAgain\\n\\n"\nread_question_twice = "always"\n')
    with pytest.raises(ValueError, match="per-question parts last"):
        load_layout(tmp_path / "bad.toml")


@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_question_again_replaces_the_joiner_and_question(tok_name, request, arms):
    tok = request.getfixturevalue(tok_name)
    row = batch_for(tok, "reread-h1q-opts", ONE, ORDERS).rows[1]
    own = tok.decode(row.ids).split("Question: ")[-1]  # after the listed and the asked question
    assert own.count("(A) None of the above") == 2 and own.count("Options again:") == 1 and "Hmm" not in own


def test_question_again_needs_the_question_reread(tmp_path):
    text = (PROMPTS_DIR / "blurb_header_reread.toml").read_text()
    (tmp_path / "bad.toml").write_text(text + '\nquestion_again = "\\n\\nAgain:"\n')
    with pytest.raises(ValueError, match="question_again needs read_question_twice"):
        load_layout(tmp_path / "bad.toml")


@pytest.mark.parametrize(("cap", "like"), [(4, "blurb_header_reread"), (5, "reread-h1q")])
def test_a_longer_option_list_than_the_cap_reads_once(cap, like, gemma_tok, arms, monkeypatch, tmp_path):
    text = (PROMPTS_DIR / "experiments" / "reread-h1q.toml").read_text()
    (tmp_path / "capped.toml").write_text(text + f"\nquestion_twice_max_options = {cap}\n")
    monkeypatch.setitem(LAYOUTS, "capped", load_layout(tmp_path / "capped.toml"))
    assert ids(batch_for(gemma_tok, "capped", ONE, ORDERS)) == ids(batch_for(gemma_tok, like, ONE, ORDERS))
