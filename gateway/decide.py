"""The /v1/systemone flow as one async function, so the phase-3 router can call it in-process."""

import asyncio
import functools
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from gateway.answers import answer
from gateway.calibration import softmax
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
    temperatures: dict[str, dict[str, float]]
    readout: Any
    padding: Padding = OFF


OrderFn = Callable[[int], list[list[int]]]


@dataclass(frozen=True)
class Reads:
    layout: str
    questions: dict[str, Rendered]
    reads: dict[str, list[tuple[list[float], list[int]]]]  # per question: (raw letter logprobs, perm) per order
    input_tokens: int


async def build_batch(engine: Engine, request: SystemOneRequest, orders: OrderFn | None = None):
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
    batch = await asyncio.to_thread(rows, engine.padding)
    if batch.longest >= s.systemone_max_len and engine.padding.enabled:
        batch = await asyncio.to_thread(rows, OFF)  # the pad must never refuse a request that fits without it
    return name, questions, batch


async def read_rows(engine: Engine, request: SystemOneRequest, orders: OrderFn | None = None) -> Reads:
    name, questions, batch = await build_batch(engine, request, orders)
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


def blend(reads: list[tuple[list[float], list[int]]], temperature: float) -> list[float]:
    """Softmax each order's logprobs at this temperature, then average back to the caller's option order."""
    return average_back([softmax(lp, temperature) for lp, _ in reads], [perm for _, perm in reads])


def answers_for(questions: dict[str, Rendered], reads: dict, temperatures: dict[str, float]) -> dict:
    return {qid: answer(q, blend(reads[qid], temperatures[q.type])) for qid, q in questions.items()}


async def decide(engine: Engine, request: SystemOneRequest) -> dict:
    r = await read_rows(engine, request)
    return {
        "model": engine.settings.served_model,
        "answers": answers_for(r.questions, r.reads, engine.temperatures[r.layout]),
        "usage": {"input_tokens": r.input_tokens, "output_tokens": 0},
    }
