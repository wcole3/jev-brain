"""Option labels (A..Z, then AA..), each exactly one token. Built once per tokenizer and layout."""

import functools
import hashlib
import json
import random
import string
from dataclasses import dataclass
from pathlib import Path

from gateway.layouts import Layout

MAX_LABELS = 255
NARROW = 10  # up to 10 options are rendered as plain text "(A) ..", as decider does
_rest = [c for c in string.punctuation if c != "'"]
random.Random("labels-symbols").shuffle(_rest)
SYMBOLS = ["'", *_rest]


@dataclass(frozen=True)
class Labels:
    names: list[str]
    ids: list[int]
    set: str = "letters"
    fallback: "Labels | None" = None
    read: list[str] | None = None  # text read after the answer slot per label; None for letters and unused


def label_table(tok) -> Labels:
    """decider's rule: the first 255 of A..Z, AA..ZZ that encode to a single token on their own."""
    letters = string.ascii_uppercase
    names, ids = [], []
    for name in list(letters) + [a + b for a in letters for b in letters]:
        encoded = tok.encode(name, add_special_tokens=False)
        if len(encoded) == 1:
            names.append(name)
            ids.append(encoded[0])
        if len(names) == MAX_LABELS:
            break
    if len(names) < MAX_LABELS or len(set(ids)) < MAX_LABELS:
        raise ValueError("tokenizer has fewer than 255 distinct single-token labels")
    return Labels(names, ids)


@functools.cache  # keyed by tokenizer identity; hashing the full vocab is slow
def tokenizer_sha256(tok) -> str:
    text = json.dumps(tok.get_vocab(), sort_keys=True) + str(tok.chat_template)
    return hashlib.sha256(text.encode()).hexdigest()


def _in_context(tok, layout: Layout, names: list[str]) -> tuple[list[str], list[int]]:
    """Names that are one token right after the answer slot, with that token's id."""
    slot = tok.encode(layout.answer, add_special_tokens=False)
    kept, ids = [], []
    for name in names:
        read = layout.answer_label.format(label=name)
        encoded = tok.encode(layout.answer + read, add_special_tokens=False)
        if len(encoded) == len(slot) + 1 and encoded[:-1] == slot:
            kept.append(name)
            ids.append(encoded[-1])
    return kept, ids


def _own_names(tok, layout: Layout) -> tuple[list[str], list[int]]:
    if layout.labels == "unused":
        names = [f"<unused{i}>" for i in range(MAX_LABELS)]
        ids = tok.convert_tokens_to_ids(names)
        if tok.unk_token_id in ids:
            raise ValueError(f"layout {layout.name}: tokenizer has no <unusedN> tokens")
        return names, ids
    candidates = {
        "lower": list(string.ascii_lowercase),
        "spaced": list(string.ascii_uppercase),
        "digits": list(string.digits[1:]),
        "symbols": SYMBOLS,
        "content": [],
    }[layout.labels]
    names, ids = _in_context(tok, layout, candidates)
    if names != candidates:
        bad = [n for n in candidates if n not in names]
        raise ValueError(f"layout {layout.name}: labels {bad} are not one token after {layout.answer!r}")
    return names, ids


def build_labels(tok, layout: Layout) -> dict:
    """The label table plus the hashes it depends on. A..J are also checked right after the answer slot."""
    if layout.labels != "letters":
        return _build_set(tok, layout)
    labels = label_table(tok)
    slot = tok.encode(layout.answer, add_special_tokens=False)
    for name, token in zip(labels.names[:NARROW], labels.ids[:NARROW]):
        if tok.encode(layout.answer + name, add_special_tokens=False) != slot + [token]:
            raise ValueError(f"layout {layout.name}: label {name!r} is not one token after {layout.answer!r}")
    return {
        "layout": layout.name,
        "layout_sha256": layout.sha256,
        "tokenizer_sha256": tokenizer_sha256(tok),
        "names": labels.names,
        "ids": labels.ids,
    }


def _build_set(tok, layout: Layout) -> dict:
    """An experiment layout's own names plus today's letters that survive this layout's slot as fallback."""
    names, ids = _own_names(tok, layout)
    fallback_names, fallback_ids = _in_context(tok, layout, label_table(tok).names)
    read = None if layout.labels == "unused" else [layout.answer_label.format(label=n) for n in names]
    return {
        "layout": layout.name,
        "layout_sha256": layout.sha256,
        "tokenizer_sha256": tokenizer_sha256(tok),
        "names": names,
        "ids": ids,
        "set": layout.labels,
        "read": read,
        "fallback_names": fallback_names,
        "fallback_ids": fallback_ids,
        "fallback_read": [layout.answer_label.format(label=n) for n in fallback_names],
    }


def labels_from_table(table: dict) -> Labels:
    if "set" not in table:
        return Labels(table["names"], table["ids"])
    fallback = Labels(table["fallback_names"], table["fallback_ids"], read=table["fallback_read"])
    return Labels(table["names"], table["ids"], table["set"], fallback, table["read"])


def save_labels(path: Path, table: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(table, indent=1) + "\n")


def load_labels(path: Path, tok, layout: Layout) -> Labels:
    """Refuse stale tables: the tokenizer or the layout text changed since build_labels ran."""
    if not path.exists():
        raise RuntimeError(f"{path} missing: run scripts/build_labels.py")
    table = json.loads(path.read_text())
    if table["tokenizer_sha256"] != tokenizer_sha256(tok):
        raise RuntimeError(f"{path}: tokenizer changed, rerun scripts/build_labels.py")
    if table["layout_sha256"] != layout.sha256:
        raise RuntimeError(f"{path}: layout {layout.name} changed, rerun scripts/build_labels.py")
    return labels_from_table(table)
