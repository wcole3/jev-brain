"""Prompt layouts. All prompt wording lives in prompts/<name>.toml; this module only loads and checks it."""

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

from gateway.config import ROOT

PROMPTS_DIR = ROOT / "prompts"
PARTS = ("questions", "context", "question", "options", "again", "plain_options")
PER_QUESTION = ("question", "options", "plain_options")
FLAGS = ("drop_letter_names", "same_name_once", "drop_label_names", "index_arrays")
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
    same_name_once: bool = False  # a choice option whose description repeats its name shows it once
    drop_label_names: bool = False  # like drop_letter_names, and "(A)", "(B)", ... count as letter names too
    index_arrays: bool = True  # JSON states number arrays of 8 or more items with _index
    read_twice: str = "off"  # when the shared parts are read again after the again joiner (prompts.reads_twice)
    read_question_twice: str = "off"  # when each row reads its question and options again after the joiner
    question_again: str = ""  # replaces the joiner and question before the second read of the options; empty: both
    question_twice_max_options: int = 0  # read_question_twice skips a request with a longer option list; 0: no cap
    system: str = ""  # a system turn before the user turn; empty means none
    plain_option: str = ""  # one unlabelled option line ("{text}") for the plain_options part, in caller order

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


def _check_read_question_twice(name: str, data: dict) -> None:
    mode, order = data.get("read_question_twice", "off"), data["order"]
    if mode not in READ_TWICE:
        raise ValueError(f"{name}: read_question_twice must be one of {READ_TWICE}")
    first = next(i for i, part in enumerate(order) if part in PER_QUESTION)
    if mode != "off" and (not data.get("again") or not set(order[first:]) <= set(PER_QUESTION)):
        raise ValueError(f"{name}: read_question_twice needs the again text and the per-question parts last")
    if "question_again" in data and (mode == "off" or "{" in data["question_again"].replace("{question}", "")):
        raise ValueError(f"{name}: question_again needs read_question_twice, and {{question}} is its only placeholder")
    cap = data.get("question_twice_max_options", 0)
    if type(cap) is not int or cap < 0 or (cap and mode == "off"):
        raise ValueError(f"{name}: question_twice_max_options must be a whole number >= 0, with read_question_twice on")


def _check_read_twice(name: str, data: dict) -> None:
    mode, order = data.get("read_twice", "off"), data["order"]
    if mode not in READ_TWICE:
        raise ValueError(f"{name}: read_twice must be one of {READ_TWICE}")
    shared = order[: next(i for i, part in enumerate(order) if part in PER_QUESTION)]
    if mode != "off" and (not data.get("again") or "again" in shared or not shared):
        raise ValueError(f"{name}: read_twice needs the again text, no shared again part, and a shared part first")


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
    if "plain_options" in order and ("{text}" not in data.get("plain_option", "") or order.index("plain_options") < order.index("question")):
        raise ValueError(f"{name}: plain_options needs plain_option with {{text}} and comes after a question part")
    _check_read_twice(name, data)
    _check_read_question_twice(name, data)
    for flag in FLAGS:
        if type(data.get(flag, False)) is not bool:
            raise ValueError(f"{name}: {flag} must be true or false")
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
        same_name_once=data.get("same_name_once", False),
        drop_label_names=data.get("drop_label_names", False),
        index_arrays=data.get("index_arrays", True),
        read_twice=data.get("read_twice", "off"),
        read_question_twice=data.get("read_question_twice", "off"),
        question_again=data.get("question_again", ""),
        question_twice_max_options=data.get("question_twice_max_options", 0),
        system=data.get("system", ""),
        plain_option=data.get("plain_option", ""),
    )


def load_layouts(directory: Path = PROMPTS_DIR) -> dict[str, Layout]:
    return {p.stem: load_layout(p) for p in sorted(directory.glob("*.toml"))}
