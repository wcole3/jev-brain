"""The /v1/systemone flow as one async function, so the phase-3 router can call it in-process."""

import asyncio
import functools
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from gateway.answers import answer
from gateway.calibration import Calibration, softmax
from gateway.config import Settings
from gateway.governor import Governor
from gateway.images import context_items, image_items
from gateway.labels import Labels
from gateway.layouts import Layout
from gateway.orders import average_back, option_orders
from gateway.padding import OFF, Padding
from gateway.prompts import Batch, ChatFrame, build_rows, image_context
from gateway.questions import Rendered, render_question, render_state
from gateway.schema import ImageError, RequestError, SystemOneRequest
from gateway.vision import Vision


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
    governor: Governor = field(default_factory=Governor)
    vision: Vision | None = None  # None: the profile serves text only


OrderFn = Callable[[int], list[list[int]]]


@dataclass(frozen=True)
class Reads:
    layout: str
    questions: dict[str, Rendered]
    reads: dict[str, list[tuple[list[float], list[int]]]]  # per question: (raw letter logprobs, perm) per order
    input_tokens: int


def has_images(request: SystemOneRequest) -> bool:
    return bool(request.images) or bool(image_items(request.state))


def decode_then_build(
    engine: Engine,
    layout: Layout,
    request: SystemOneRequest,
    rows: Callable[..., Batch],
    padding: Padding,
    pad_rows: int | None,
) -> Batch:
    """Decode the images and build the rows: seconds of CPU for big images, so it runs off the event loop."""
    items = context_items(request.state, request.images)
    return rows(padding, pad_rows, images=image_context(engine.tokenizer, layout, items, engine.vision))


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
    images = has_images(request)
    if images and engine.vision is None:
        raise ImageError("this profile serves text only")
    state = "" if images else render_state(request.state)  # image rows take the state from their image context
    rows = functools.partial(
        build_rows, engine.tokenizer, engine.frames[name], layout, engine.labels[name], state, questions, perms
    )
    first = functools.partial(decode_then_build, engine, layout, request, rows) if images else rows
    batch = await asyncio.to_thread(first, engine.padding, pad_rows)
    if batch.longest >= s.systemone_max_len and engine.padding.enabled:
        # the pad must never refuse a request that fits without it; decoded images are reused
        batch = await asyncio.to_thread(rows, OFF, pad_rows, images=batch.images)
    return name, questions, batch


async def read_batch(readout, batch: Batch) -> list[list[float]]:
    """Text rows read as before; image rows go through the image path with their images attached."""
    ids, labels = [r.ids for r in batch.rows], [r.label_ids for r in batch.rows]
    if batch.images is None:
        return await readout.letter_logprobs(ids, labels, batch.shared_len)
    parts = [image.part() for image in batch.images.images]
    prefix_parts = parts if batch.images_shared else []
    return await readout.image_logprobs(ids, labels, batch.shared_len, batch.shared_tokens, parts, prefix_parts)


async def read_rows(
    engine: Engine, request: SystemOneRequest, orders: OrderFn | None = None, pad_rows: int | None = None
) -> Reads:
    name, questions, batch = await build_batch(engine, request, orders, pad_rows)
    limit = engine.settings.systemone_max_len
    if batch.longest >= limit:
        raise RequestError(f"prompt is longer than the maximum context length ({batch.longest} >= {limit} tokens)")
    logprobs = await read_batch(engine.readout, batch)
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
