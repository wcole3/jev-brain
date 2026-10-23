"""Prompt layouts. All prompt wording lives in prompts/<name>.toml; this module only loads and checks it."""

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

from gateway.config import ROOT

PROMPTS_DIR = ROOT / "prompts"
PARTS = ("questions", "context", "question", "options", "again")
READ_TWICE = ("off", "one-question", "always")
LABEL_SETS = ("letters", "lower", "spaced", "digits", "symbols", "unused", "content", "shuffled", "shuffled-q")
REQUIRED = ("order", "context", "question", "option", "answer", "described", "noul", "noul_question")


@dataclass(frozen=True)
class Layout:
    name: str
    sha256: str
    order: tuple[str, ...]
    context: str
    question: str
    option: str
    answer: str
    described: str
    noul: tuple[str, str]
    noul_question: str
    questions: str = ""
    question_item: str = ""
    image_label: str = ""
    labels: str = "letters"
    answer_label: str = "{label}"
    again: str = ""  # the joiner before a part is read again
    drop_letter_names: bool = False  # choices named A, B, C, ... in order show only their descriptions
    read_twice: str = "off"  # when the shared parts are read again after the again joiner (prompts.reads_twice)

    @property
    def option_open(self) -> str:
        return self.option.split("{label}")[0]

    @property
    def option_close(self) -> str:
        return self.option.split("{label}")[1]


def _check_image_label(name: str, label: str) -> None:
    if "{n}" not in label:
        raise ValueError(f"{name}: image_label needs {{n}}")
    try:
        label.format(n=1)
    except (KeyError, IndexError, ValueError) as e:
        raise ValueError(f"{name}: image_label must format with {{n}} only ({e!r})") from None


def _check_read_twice(name: str, data: dict) -> None:
    mode, order = data.get("read_twice", "off"), data["order"]
    if mode not in READ_TWICE:
        raise ValueError(f"{name}: read_twice must be one of {READ_TWICE}")
    if mode != "off" and (not data.get("again") or "again" in order or order[0] in ("question", "options")):
        raise ValueError(f"{name}: read_twice needs the again text, no again part, and a shared part first")


def _check(name: str, data: dict) -> None:
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError(f"{name}: missing keys {missing}")
    order = data["order"]
    if not set(order) <= set(PARTS) or not {"context", "question", "options"} <= set(order):
        raise ValueError(f"{name}: order must list context, question and options, from {PARTS}")
    if len(order) != len(set(order)) and "again" not in order:
        raise ValueError(f"{name}: parts repeat only in a layout with an again part")
    needs = [
        ("context", "{state}"),
        ("question", "{question}"),
        ("option", "{label}"),
        ("described", "{name}"),
        ("described", "{description}"),
    ]
    if "questions" in order:
        needs += [("questions", "{questions}"), ("question_item", "{question}")]
    for key, placeholder in needs:
        if placeholder not in data.get(key, ""):
            raise ValueError(f"{name}: {key} needs {placeholder}")
    if "again" in order and not data.get("again"):
        raise ValueError(f"{name}: an again part needs the again text")
    _check_read_twice(name, data)
    if type(data.get("drop_letter_names", False)) is not bool:
        raise ValueError(f"{name}: drop_letter_names must be true or false")
    if "{text}" not in data["option"].split("{label}")[-1]:
        raise ValueError(f"{name}: option needs {{text}} after {{label}}")
    if "image_label" in data:
        _check_image_label(name, data["image_label"])
    if data.get("labels", "letters") not in LABEL_SETS:
        raise ValueError(f"{name}: labels must be one of {LABEL_SETS}")
    if "{label}" not in data.get("answer_label", "{label}"):
        raise ValueError(f"{name}: answer_label needs {{label}}")
    if len(data["noul"]) != 2:
        raise ValueError(f"{name}: noul must be [false word, true word]")


def load_layout(path: Path) -> Layout:
    raw = path.read_bytes()
    data = tomllib.loads(raw.decode())
    _check(path.name, data)
    return Layout(
        name=path.stem,
        sha256=hashlib.sha256(raw).hexdigest(),
        order=tuple(data["order"]),
        context=data["context"],
        question=data["question"],
        option=data["option"],
        answer=data["answer"],
        described=data["described"],
        noul=tuple(data["noul"]),
        noul_question=data["noul_question"],
        questions=data.get("questions", ""),
        question_item=data.get("question_item", ""),
        image_label=data.get("image_label", ""),
        labels=data.get("labels", "letters"),
        answer_label=data.get("answer_label", "{label}"),
        again=data.get("again", ""),
        drop_letter_names=data.get("drop_letter_names", False),
        read_twice=data.get("read_twice", "off"),
    )


def load_layouts(directory: Path = PROMPTS_DIR) -> dict[str, Layout]:
    return {p.stem: load_layout(p) for p in sorted(directory.glob("*.toml"))}
