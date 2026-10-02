"""The /v1/systemone flow as one async function, so the phase-3 router can call it in-process."""

import asyncio
import functools
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from gateway.answers import answer
from gateway.calibration import Calibration, softmax
from gateway.config import Settings
from gateway.labels import Labels
from gateway.layouts import Layout
from gateway.orders import average_back, option_orders
from gateway.padding import OFF, Padding
from gateway.prompts import ChatFrame, build_rows
from gateway.questions import Rendered, render_question, render_state
from gateway.schema import RequestError, SystemOneRequest


@dataclass(frozen=True)
class Engine:
    """Everything a decision needs, loaded once at startup."""

    settings: Settings
    tokenizer: Any
    layouts: dict[str, Layout]
    frames: dict[str, ChatFrame]
    labels: dict[str, Labels]
    calibration: dict[str, Calibration]
    readout: Any
    padding: Padding = OFF


OrderFn = Callable[[int], list[list[int]]]


@dataclass(frozen=True)
class Reads:
    layout: str
    questions: dict[str, Rendered]
    reads: dict[str, list[tuple[list[float], list[int]]]]  # per question: (raw letter logprobs, perm) per order
    input_tokens: int


async def build_batch(
    engine: Engine, request: SystemOneRequest, orders: OrderFn | None = None, pad_rows: int | None = None
):
    """Render and tokenize every row. Refuses bad requests, but not long ones: read_rows does that."""
    s = engine.settings
    if not request.questions:
        raise RequestError("questions must not be empty")
    name = request.layout or s.prompt_layout
    if name not in engine.layouts:
        raise RequestError(f"unknown layout {name!r}; available: {sorted(engine.layouts)}")
    layout = engine.layouts[name]
    questions = {qid: render_question(q, layout) for qid, q in request.questions.items()}
    if orders is None:
        orders = functools.partial(option_orders, setting=request.option_orders or s.option_orders)
    try:
        perms = {qid: orders(len(q.options)) for qid, q in questions.items()}
    except ValueError as e:
        raise RequestError(str(e)) from e
    state = render_state(request.state)
    rows = functools.partial(
        build_rows, engine.tokenizer, engine.frames[name], layout, engine.labels[name], state, questions, perms
    )
    batch = await asyncio.to_thread(rows, engine.padding, pad_rows)
    if batch.longest >= s.systemone_max_len and engine.padding.enabled:
        # the pad must never refuse a request that fits without it
        batch = await asyncio.to_thread(rows, OFF, pad_rows)
    return name, questions, batch


async def read_rows(
    engine: Engine, request: SystemOneRequest, orders: OrderFn | None = None, pad_rows: int | None = None
) -> Reads:
    name, questions, batch = await build_batch(engine, request, orders, pad_rows)
    limit = engine.settings.systemone_max_len
    if batch.longest >= limit:
        raise RequestError(f"prompt is longer than the maximum context length ({batch.longest} >= {limit} tokens)")
    logprobs = await engine.readout.letter_logprobs(
        [r.ids for r in batch.rows], [r.label_ids for r in batch.rows], batch.shared_len
    )
    reads: dict[str, list] = {qid: [] for qid in questions}
    for row, lp in zip(batch.rows, logprobs, strict=True):
        reads[row.question_id].append((lp, row.perm))
    return Reads(name, questions, reads, batch.input_tokens)


def blend(reads: list[tuple[list[float], list[int]]], temperature: float, yes_offset: float = 0.0) -> list[float]:
    """Softmax each order at T (noul: "yes" shifted by yes_offset after /T), then average back to caller order."""
    probs = []
    for lp, perm in reads:
        shifted = [x + yes_offset * temperature if perm[j] == 1 else x for j, x in enumerate(lp)] if yes_offset else lp
        probs.append(softmax(shifted, temperature))
    return average_back(probs, [perm for _, perm in reads])


def probabilities(reads: list[tuple[list[float], list[int]]], q_type: str, cal: Calibration) -> list[float]:
    return blend(reads, cal.T[q_type], cal.b if q_type == "noul" else 0.0)


def answers_for(questions: dict[str, Rendered], reads: dict, cal: Calibration) -> dict:
    return {qid: answer(q, probabilities(reads[qid], q.type, cal)) for qid, q in questions.items()}


async def decide(engine: Engine, request: SystemOneRequest) -> dict:
    r = await read_rows(engine, request)
    return {
        "model": engine.settings.served_model,
        "answers": answers_for(r.questions, r.reads, engine.calibration[r.layout]),
        "usage": {"input_tokens": r.input_tokens, "output_tokens": 0},
    }
