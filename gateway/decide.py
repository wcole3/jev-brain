"""The /v1/systemone flow as one async function, so the phase-3 router can call it in-process."""

import asyncio
import functools
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
from gateway.questions import render_question, render_state
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


async def decide(engine: Engine, request: SystemOneRequest) -> dict:
    s = engine.settings
    if not request.questions:
        raise RequestError("questions must not be empty")
    name = request.layout or s.prompt_layout
    if name not in engine.layouts:
        raise RequestError(f"unknown layout {name!r}; available: {sorted(engine.layouts)}")
    layout = engine.layouts[name]
    questions = {qid: render_question(q, layout) for qid, q in request.questions.items()}
    try:
        setting = request.option_orders or s.option_orders
        perms = {qid: option_orders(len(q.options), setting) for qid, q in questions.items()}
    except ValueError as e:
        raise RequestError(str(e)) from e

    state = render_state(request.state)
    build = functools.partial(
        build_rows, engine.tokenizer, engine.frames[name], layout, engine.labels[name], state, questions, perms
    )
    batch = await asyncio.to_thread(build, engine.padding)
    if batch.longest >= s.systemone_max_len and engine.padding.enabled:
        batch = await asyncio.to_thread(build, OFF)  # the pad must never refuse a request that fits without it
    longest = batch.longest
    if longest >= s.systemone_max_len:
        raise RequestError(
            f"prompt is longer than the maximum context length ({longest} >= {s.systemone_max_len} tokens)"
        )

    logprobs = await engine.readout.letter_logprobs(
        [r.ids for r in batch.rows], [r.label_ids for r in batch.rows], batch.shared_len
    )
    temperatures = engine.temperatures[name]
    reads: dict[str, list] = {qid: [] for qid in questions}
    for row, lp in zip(batch.rows, logprobs, strict=True):
        reads[row.question_id].append((softmax(lp, temperatures[questions[row.question_id].type]), row.perm))

    answers = {}
    for qid, q in questions.items():
        probs, perms_used = zip(*reads[qid])
        answers[qid] = answer(q, average_back(list(probs), list(perms_used)))
    return {
        "model": s.served_model,
        "answers": answers,
        "usage": {"input_tokens": batch.input_tokens, "output_tokens": 0},
    }
