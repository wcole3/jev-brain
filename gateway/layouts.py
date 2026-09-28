"""Prompt layouts. All prompt wording lives in prompts/<name>.toml; this module only loads and checks it."""

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

from gateway.config import ROOT

PROMPTS_DIR = ROOT / "prompts"
PARTS = ("questions", "context", "question", "options")
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

    @property
    def option_open(self) -> str:
        return self.option.split("{label}")[0]

    @property
    def option_close(self) -> str:
        return self.option.split("{label}")[1]


def _check(name: str, data: dict) -> None:
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError(f"{name}: missing keys {missing}")
    order = data["order"]
    if (
        len(order) != len(set(order))
        or not set(order) <= set(PARTS)
        or not {"context", "question", "options"} <= set(order)
    ):
        raise ValueError(f"{name}: order must list context, question, options (and optionally questions) once each")
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
    if "{text}" not in data["option"].split("{label}")[-1]:
        raise ValueError(f"{name}: option needs {{text}} after {{label}}")
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
    )


def load_layouts(directory: Path = PROMPTS_DIR) -> dict[str, Layout]:
    return {p.stem: load_layout(p) for p in sorted(directory.glob("*.toml"))}
