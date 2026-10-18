import json
import string

import pytest

from gateway.config import Settings
from gateway.labels import (
    MAX_LABELS,
    SHUFFLED,
    SYMBOLS,
    build_labels,
    label_table,
    labels_from_table,
    load_labels,
    save_labels,
)
from gateway.layouts import LABEL_SETS, PROMPTS_DIR, load_layouts
from scripts.build_labels import table_for
from tests.helpers import tokenizer_for

EXPERIMENT_LAYOUTS = load_layouts(PROMPTS_DIR / "experiments")


def test_label_table_follows_deciders_rule(qwen_tok):
    labels = label_table(qwen_tok)
    assert labels.names[:26] == list(string.ascii_uppercase)
    assert len(labels.names) == len(set(labels.ids)) == MAX_LABELS
    for name, token in zip(labels.names, labels.ids):
        assert qwen_tok.encode(name, add_special_tokens=False) == [token]


def test_round_trip_and_stale_detection(qwen_tok, tmp_path):
    layouts = load_layouts()
    table = build_labels(qwen_tok, layouts["decider_chat"])
    path = tmp_path / "labels.json"
    save_labels(path, table)
    assert load_labels(path, qwen_tok, layouts["decider_chat"]).ids == table["ids"]
    with pytest.raises(RuntimeError, match="layout header changed"):
        load_labels(path, qwen_tok, layouts["header"])


def test_missing_file_explains_how_to_fix(qwen_tok, tmp_path):
    with pytest.raises(RuntimeError, match="build_labels.py"):
        load_labels(tmp_path / "labels.json", qwen_tok, load_layouts()["decider_chat"])


def experiment(name):
    return EXPERIMENT_LAYOUTS[f"labels-{name}"]


@pytest.mark.parametrize("profile", ["gemma-4-31b", "qwen3.8-27b"])
def test_served_label_tables_byte_identical(profile, tmp_path):
    s, tok = Settings.from_profile(profile), tokenizer_for(profile)
    for name, layout in load_layouts().items():
        save_labels(tmp_path / "labels.json", table_for(tok, layout, s))
        assert (tmp_path / "labels.json").read_bytes() == (s.data_dir(name) / "labels.json").read_bytes()


def test_every_set_has_a_layout():
    assert {n.removeprefix("labels-") for n in EXPERIMENT_LAYOUTS if n.startswith("labels-")} == set(LABEL_SETS)


def test_set_sizes_and_fallback(gemma_tok):
    sizes = {"lower": 26, "spaced": 26, "digits": 9, "symbols": 32, "shuffled": 26, "shuffled-q": 26}
    for name, size in sizes.items():
        lab = labels_from_table(build_labels(gemma_tok, experiment(name)))
        assert len(lab.names) == size and len(lab.fallback.names) >= 249
    assert SYMBOLS[0] == "'" and len(set(SYMBOLS)) == 32


def test_shuffled_is_a_fixed_permutation(gemma_tok):
    first = labels_from_table(build_labels(gemma_tok, experiment("shuffled")))
    again = labels_from_table(build_labels(gemma_tok, experiment("shuffled")))
    assert sorted(first.names) == list(string.ascii_uppercase) and first.names != list(string.ascii_uppercase)
    assert first.names == again.names == SHUFFLED and first.fallback.names[0] == "A"


def test_content_has_only_a_fallback(gemma_tok):
    lab = labels_from_table(build_labels(gemma_tok, experiment("content")))
    assert lab.names == [] and len(lab.fallback.names) >= 249


def test_table_round_trips_through_json(gemma_tok):
    table = build_labels(gemma_tok, experiment("spaced"))
    lab = labels_from_table(json.loads(json.dumps(table)))
    assert lab.set == "spaced" and lab.read[0] == " A" and lab.fallback.read[0] == " A"


@pytest.mark.parametrize("tok_name", ["gemma_tok", "qwen_tok"])
def test_every_label_one_token_in_context(tok_name, request):
    tok = request.getfixturevalue(tok_name)
    for name in LABEL_SETS:
        layout = experiment(name)
        if name in ("unused", "letters"):
            continue
        lab = labels_from_table(build_labels(tok, layout))
        slot = tok.encode(layout.answer, add_special_tokens=False)
        for group in (lab, lab.fallback):
            for label, token, read in zip(group.names, group.ids, group.read):
                assert tok.encode(layout.answer + read, add_special_tokens=False) == slot + [token], label


def test_unused_only_with_unused_tokens(gemma_tok, qwen_tok):
    lab = labels_from_table(build_labels(gemma_tok, experiment("unused")))
    assert lab.names == [f"<unused{i}>" for i in range(255)] and len(set(lab.ids)) == 255 and lab.read is None
    assert all(gemma_tok.convert_ids_to_tokens(i).startswith("<unused") for i in lab.ids)
    with pytest.raises(ValueError, match="no <unusedN> tokens"):
        build_labels(qwen_tok, experiment("unused"))


def test_letters_experiment_is_the_plain_table(gemma_tok):
    assert "set" not in build_labels(gemma_tok, experiment("letters"))
