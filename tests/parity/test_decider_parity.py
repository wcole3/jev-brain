import json
from pathlib import Path

import pytest

from gateway.labels import label_table
from gateway.layouts import load_layouts
from gateway.prompts import build_rows, chat_frame
from gateway.questions import render_question, render_state
from gateway.schema import Question
from tests.helpers import PROFILES, tokenizer_for

HERE = Path(__file__).parent
CASES = json.loads((HERE / "cases.json").read_text())


@pytest.mark.parametrize("profile", PROFILES)
def test_decider_chat_matches_decider_token_for_token(profile):
    fixture = HERE / "fixtures" / f"{profile}.json"
    if not fixture.exists():
        pytest.fail(f"{fixture} missing: generate it with scripts/decider_fixtures.py")
    expected = json.loads(fixture.read_text())
    tok = tokenizer_for(profile)
    layout = load_layouts()["decider_chat"]
    labels = label_table(tok)
    assert labels.ids == expected["label_ids"]
    for case, rows in zip(CASES, expected["rows"], strict=True):
        questions = {k: render_question(Question(**v), layout) for k, v in case["questions"].items()}
        perms = {k: [list(range(len(q.options)))] for k, q in questions.items()}
        batch = build_rows(tok, chat_frame(tok, layout), layout, labels, render_state(case["state"]), questions, perms)
        assert [r.ids for r in batch.rows] == rows
