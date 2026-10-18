import dataclasses
import json
from pathlib import Path

import pytest

from gateway.labels import Labels, build_labels, label_table, labels_from_table, question_labels
from gateway.layouts import PROMPTS_DIR, load_layouts
from gateway.prompts import build_rows, chat_frame, encode
from gateway.questions import render_question
from gateway.schema import Question, RequestError
from tests.helpers import LAYOUTS, STATE

GOLDEN = Path(__file__).parents[1] / "fixtures" / "header_rows_golden.json"
EXPERIMENTS = load_layouts(PROMPTS_DIR / "experiments")
CITIES = [f"City {k}" for k in range(12)]


def choice(texts: list[str]) -> dict:
    return {"type": "choice", "instructions": "Which option fits", "criteria": {t: None for t in texts}}


QUESTIONS = {
    "urgent": {"type": "noul", "instructions": "The message conveys urgency"},
    "team": choice(["billing", "technical", "sales", "other"]),
    "city": choice(CITIES),
}


def rows(tok, layout, labels, questions, orders=("identity", "reversed")):
    rendered = {k: render_question(Question(**v), layout) for k, v in questions.items()}
    perms = {
        k: [list(range(len(r.options)))[:: 1 if o == "identity" else -1] for o in orders] for k, r in rendered.items()
    }
    return build_rows(tok, chat_frame(tok, layout), layout, labels, STATE, rendered, perms).rows


def experiment(tok, name):
    layout = EXPERIMENTS[f"labels-{name}"]
    return layout, labels_from_table(build_labels(tok, layout))


def header_rows(tok) -> list[dict]:
    built = rows(tok, LAYOUTS["header"], label_table(tok), QUESTIONS)
    return [{"question_id": r.question_id, "perm": r.perm, "ids": r.ids, "label_ids": r.label_ids} for r in built]


def test_served_header_rows_unchanged(gemma_tok):
    assert header_rows(gemma_tok) == json.loads(GOLDEN.read_text())
    assert {r.label_tag for r in rows(gemma_tok, LAYOUTS["header"], label_table(gemma_tok), QUESTIONS)} == {"set"}


def test_long_list_ids_match_short(gemma_tok):
    layout, lab = experiment(gemma_tok, "lower")
    end = len(chat_frame(gemma_tok, layout).tail + encode(gemma_tok, layout.answer))
    short = rows(gemma_tok, layout, lab, {"q": choice(CITIES[:4])}, ["identity"])[0]
    long = rows(gemma_tok, layout, lab, {"q": choice(CITIES)}, ["identity"])[0]
    assert long.label_ids[:4] == short.label_ids == lab.ids[:4]
    assert long.ids[: len(short.ids) - end] == short.ids[:-end]
    opening = encode(gemma_tok, layout.option_open)
    for token in long.label_ids:
        at = long.ids.index(token)
        assert long.ids.count(token) == 1 and long.ids[at - len(opening) : at] == opening


def test_noul_reads_set_ids(gemma_tok):
    layout, lab = experiment(gemma_tok, "digits")
    slot = encode(gemma_tok, layout.answer)
    want = [encode(gemma_tok, layout.answer + d)[len(slot)] for d in ("1", "2")]
    built = rows(gemma_tok, layout, lab, {"q": QUESTIONS["urgent"]})
    assert [r.perm for r in built] == [[0, 1], [1, 0]]
    assert all(r.label_ids == want and r.label_tag == "set" for r in built)
    assert "\n(1) no\n(2) yes" in gemma_tok.decode(built[0].ids)
    assert "\n(1) yes\n(2) no" in gemma_tok.decode(built[1].ids)


def test_fallback_past_size(gemma_tok):
    layout, lab = experiment(gemma_tok, "digits")
    row = rows(gemma_tok, layout, lab, {"q": choice(CITIES[:10])}, ["identity"])[0]
    assert row.label_tag == "fallback" and row.label_ids == lab.fallback.ids[:10]
    assert "\n(A) City 0" in gemma_tok.decode(row.ids) and "\n(J) City 9" in gemma_tok.decode(row.ids)


def test_fallback_too_small_is_refused(gemma_tok):
    layout, lab = experiment(gemma_tok, "digits")
    tiny = dataclasses.replace(lab, fallback=Labels(lab.fallback.names[:9], lab.fallback.ids[:9]))
    with pytest.raises(RequestError, match="10 options"):
        question_labels(gemma_tok, layout, tiny, CITIES[:10])


def test_content_first_tokens_and_collisions(gemma_tok):
    layout, lab = experiment(gemma_tok, "content")
    first = [encode(gemma_tok, " " + t)[0] for t in ("approve", "reject")]
    assert question_labels(gemma_tok, layout, lab, ["approve", "reject"]) == (["- ", "- "], first, "set")
    names, ids, tag = question_labels(gemma_tok, layout, lab, ["New York", "New Jersey"])
    assert (names, ids, tag) == (["A) ", "B) "], lab.fallback.ids[:2], "fallback")
    assert question_labels(gemma_tok, layout, lab, ["", "x"])[2] == "fallback"
    row = rows(gemma_tok, layout, lab, {"q": choice(["approve", "reject"])}, ["reversed"])[0]
    assert row.label_ids == first[::-1] and "\n- reject\n- approve" in gemma_tok.decode(row.ids)


def test_unused_spliced(gemma_tok):
    layout, lab = experiment(gemma_tok, "unused")
    for row in rows(gemma_tok, layout, lab, QUESTIONS, ["identity"]):
        n = len(row.label_ids)
        assert row.label_tag == "set" and row.label_ids == lab.ids[:n]
        assert gemma_tok.convert_ids_to_tokens(row.label_ids) == [f"<unused{k}>" for k in range(n)]
        at = row.ids.index(lab.ids[0])
        assert row.ids.count(lab.ids[0]) == 1 and row.ids[at - 1 : at] == encode(gemma_tok, layout.option_open)


def test_content_whitespace_read_falls_back(gemma_tok):
    layout, lab = experiment(gemma_tok, "content")
    names, ids, tag = question_labels(gemma_tok, layout, lab, ["5 apples", "pears"])
    assert (names, ids, tag) == (["A) ", "B) "], lab.fallback.ids[:2], "fallback")


def test_unused_fallback_reads_spaced_letter(gemma_tok):
    layout, lab = experiment(gemma_tok, "unused")
    slot = encode(gemma_tok, layout.answer)
    assert lab.fallback.read[:2] == [" A", " B"]
    assert lab.fallback.ids[:2] == [encode(gemma_tok, layout.answer + r)[len(slot)] for r in (" A", " B")]
    two = dataclasses.replace(lab, names=lab.names[:2], ids=lab.ids[:2])
    assert question_labels(gemma_tok, layout, two, ["x", "y", "z"]) == (["A", "B", "C"], lab.fallback.ids[:3], "fallback")


def test_shuffled_q_per_question_letters(gemma_tok):
    layout, lab = experiment(gemma_tok, "shuffled-q")
    texts = ["billing", "technical", "sales", "other"]
    names, ids, tag = question_labels(gemma_tok, layout, lab, texts)
    back, back_ids, _ = question_labels(gemma_tok, layout, lab, texts[::-1])
    assert tag == "set" and len(set(names)) == 4 and names != lab.names[:4]
    assert back == names[::-1] and back_ids == ids[::-1]
    assert [lab.ids[lab.names.index(n)] for n in names] == ids
    other = question_labels(gemma_tok, layout, lab, ["a", "b", "c", "d"])[0]
    assert other != names
    built = rows(gemma_tok, layout, lab, {"q": choice(texts)})
    assert [r.label_ids for r in built] == [ids, ids[::-1]]
    for name, text in zip(names, texts):
        assert f"\n({name}) {text}" in gemma_tok.decode(built[0].ids)
        assert f"\n({name}) {text}" in gemma_tok.decode(built[1].ids)


def test_shuffled_q_fallback_past_26(gemma_tok):
    layout, lab = experiment(gemma_tok, "shuffled-q")
    _, ids, tag = question_labels(gemma_tok, layout, lab, [f"t{k}" for k in range(27)])
    assert tag == "fallback" and ids == lab.fallback.ids[:27]
    assert question_labels(gemma_tok, layout, lab, [f"t{k}" for k in range(26)])[2] == "set"


def test_shuffled_fixed_letters_in_prompt(gemma_tok):
    layout, lab = experiment(gemma_tok, "shuffled")
    row = rows(gemma_tok, layout, lab, {"q": choice(CITIES[:4])}, ["identity"])[0]
    assert row.label_ids == lab.ids[:4] and row.label_tag == "set"
    assert f"\n({lab.names[0]}) City 0" in gemma_tok.decode(row.ids)


def test_digits_boundary_at_nine(gemma_tok):
    layout, lab = experiment(gemma_tok, "digits")
    assert question_labels(gemma_tok, layout, lab, CITIES[:9]) == (lab.names, lab.ids, "set")
