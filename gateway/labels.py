"""Option labels (A..Z, then AA..), each exactly one token. Built once per tokenizer and layout."""
import hashlib
import json
import string
from dataclasses import dataclass
from pathlib import Path

from gateway.layouts import Layout

MAX_LABELS = 255
NARROW = 10  # up to 10 options are rendered as plain text "(A) ..", as decider does


@dataclass(frozen=True)
class Labels:
    names: list[str]
    ids: list[int]


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


def tokenizer_sha256(tok) -> str:
    text = json.dumps(tok.get_vocab(), sort_keys=True) + str(tok.chat_template)
    return hashlib.sha256(text.encode()).hexdigest()


def build_labels(tok, layout: Layout) -> dict:
    """The label table plus the hashes it depends on. A..J are also checked right after the answer slot."""
    labels = label_table(tok)
    slot = tok.encode(layout.answer, add_special_tokens=False)
    for name, token in zip(labels.names[:NARROW], labels.ids[:NARROW]):
        if tok.encode(layout.answer + name, add_special_tokens=False) != slot + [token]:
            raise ValueError(f"layout {layout.name}: label {name!r} is not one token after {layout.answer!r}")
    return {"layout": layout.name, "layout_sha256": layout.sha256, "tokenizer_sha256": tokenizer_sha256(tok),
            "names": labels.names, "ids": labels.ids}


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
    return Labels(table["names"], table["ids"])
