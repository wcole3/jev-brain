import string

import pytest

from gateway.labels import MAX_LABELS, build_labels, label_table, load_labels, save_labels
from gateway.layouts import load_layouts


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
