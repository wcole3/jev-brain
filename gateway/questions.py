"""Jev questions → option texts, mirroring decider's systemone.render_question and render_state."""

import json
import string
from collections import Counter
from dataclasses import dataclass
from typing import Any

from gateway.layouts import Layout
from gateway.schema import MAX_LEVELS, MAX_OPTIONS, Question, RequestError

ANNOTATE_MIN = 8  # decider numbers long arrays so paths like records[47] become lookups


def as_text(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def annotate_indices(x: Any) -> Any:
    if isinstance(x, list):
        if len(x) < ANNOTATE_MIN:
            return [annotate_indices(v) for v in x]
        return [
            {"_index": i, **annotate_indices(v)} if isinstance(v, dict) else {"_index": i, "value": annotate_indices(v)}
            for i, v in enumerate(x)
        ]
    if isinstance(x, dict):
        return {k: annotate_indices(v) for k, v in x.items()}
    return x


def render_state(state: Any, index_arrays: bool = True) -> str:
    if isinstance(state, str):
        return state
    return json.dumps(annotate_indices(state) if index_arrays else state, ensure_ascii=False)


@dataclass(frozen=True)
class Rendered:
    type: str  # choice | score | noul
    text: str  # the question as shown to the model
    options: list[str]  # option texts in the caller's order
    names: list[Any]  # what each option reports back (choice keys, level numbers, False/True)
    legend: list[str] | None = None  # score level descriptions


def described(layout: Layout, name: Any, description: Any) -> str:
    return (
        str(name) if description in (None, "") else layout.described.format(name=name, description=as_text(description))
    )


def drops_names(layout: Layout, names: list[str]) -> bool:
    """Names A, B, C, ... in order repeat the shown label, and under a reordering contradict it."""
    letters = list(string.ascii_uppercase[: len(names)])
    if layout.drop_letter_names and names == letters:
        return True
    return layout.drop_label_names and names in (letters, [f"({c})" for c in letters])


def short_option(layout: Layout, name: str, description: Any, drop: bool) -> str:
    """The option without a name that repeats the label or its own description."""
    if drop:
        return str(name) if description in (None, "") else as_text(description)
    if layout.same_name_once and description == name:
        return str(name)
    return described(layout, name, description)


def question_text(q: Question, layout: Layout) -> str:
    if q.type == "noul" and q.instructions in (None, ""):
        criteria = q.criteria if isinstance(q.criteria, dict) else {}
        if all(criteria.get(k) in (None, "") for k in ("true", "false")):
            raise RequestError("noul question without instructions: criteria must describe true or false")
        return layout.noul_question
    text = "" if q.instructions is None else as_text(q.instructions)
    if not text:
        raise RequestError("question without instructions")
    return text


def render_choice(q: Question, text: str, layout: Layout) -> Rendered:
    criteria = {str(c): None for c in q.criteria} if isinstance(q.criteria, list) else q.criteria
    if not isinstance(criteria, dict):
        raise RequestError("choice criteria must map option names to descriptions")
    if len(criteria) < 2:
        raise RequestError("a choice needs at least two options")
    if len(criteria) > MAX_OPTIONS:
        raise RequestError(f"at most {MAX_OPTIONS} options per choice (got {len(criteria)})")
    names = list(criteria)
    drop = drops_names(layout, names)
    options = [short_option(layout, n, criteria[n], drop) for n in names]
    if layout.same_name_once or layout.drop_label_names:  # options that came out alike show in full
        same = Counter(options)
        options = [o if same[o] == 1 else described(layout, n, criteria[n]) for o, n in zip(options, names, strict=True)]
    return Rendered("choice", text, options, names)


def render_score(q: Question, text: str, layout: Layout) -> Rendered:
    levels = q.criteria
    if isinstance(levels, dict):  # legend form {"0": ..., "1": ...}
        try:
            levels = [levels[k] for k in sorted(levels, key=float)]
        except ValueError as e:
            raise RequestError("score legend keys must be level numbers") from e
    if not isinstance(levels, list) or not 2 <= len(levels) <= MAX_LEVELS:
        raise RequestError(f"a score takes 2 to {MAX_LEVELS} levels")
    options = [layout.described.format(name=i, description=as_text(d)) for i, d in enumerate(levels)]
    return Rendered("score", text, options, list(range(len(levels))), [as_text(d) for d in levels])


def render_noul(q: Question, text: str, layout: Layout) -> Rendered:
    if q.criteria is not None and not isinstance(q.criteria, dict):
        raise RequestError("noul criteria must be a map of optional true/false descriptions")
    criteria = q.criteria or {}
    no, yes = layout.noul
    options = [described(layout, no, criteria.get("false")), described(layout, yes, criteria.get("true"))]
    return Rendered("noul", text, options, [False, True])


def render_question(q: Question, layout: Layout) -> Rendered:
    text = question_text(q, layout)
    render = {"choice": render_choice, "score": render_score, "noul": render_noul}[q.type]
    return render(q, text, layout)
