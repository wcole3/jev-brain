"""The /v1/systemone flow as one async function, so the phase-3 router can call it in-process."""

import asyncio
import functools
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from typing import Any

from gateway.answers import answer
from gateway.calibration import UNCALIBRATED, Calibration, softmax
from gateway.config import Settings
from gateway.governor import Governor
from gateway.images import context_items, image_items
from gateway.labels import Labels
from gateway.layouts import Layout
from gateway.orders import average_back, gate, option_orders, rereads
from gateway.padding import OFF, Padding
from gateway.prompts import Batch, ChatFrame, build_rows, image_context, reads_twice
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
    other_calibrations: dict[str, dict[str, Calibration]] = field(default_factory=dict)  # orders -> layout -> fit


def calibration_for(engine: Engine, layout: str, orders: str) -> Calibration:
    """The fit for an order setting; an unknown setting (request override) uses the text fit."""
    if orders in engine.other_calibrations:
        return engine.other_calibrations[orders].get(layout, UNCALIBRATED)
    return engine.calibration[layout]  # a reread_p experiment has no fit of its own: it borrows this one


OrderFn = Callable[[int], list[list[int]]]


@dataclass(frozen=True)
class Reads:
    layout: str
    questions: dict[str, Rendered]
    reads: dict[str, list[tuple[list[float], list[int]]]]  # per question: (raw letter logprobs, perm) per order
    input_tokens: int
    shared_len: int  # leading ids every row shares, pad included
    padded: bool  # the shared prefix carries a pad
    batch: Batch  # the first pass's rows as built, for tools that need per-row token counts
    orders: str  # the order setting of the request (a caller's orders function reads other orders)


def has_images(request: SystemOneRequest) -> bool:
    return bool(request.images) or bool(image_items(request.state))


def setting_for(engine: Engine, request: SystemOneRequest) -> str:
    """The request's override, else the image setting for a request with images, else the text setting."""
    s = engine.settings
    return request.option_orders or (s.image_orders if has_images(request) else s.option_orders)


def decode_then_build(
    engine: Engine,
    layout: Layout,
    request: SystemOneRequest,
    rows: Callable[..., Batch],
    padding: Padding,
    pad_rows: int | None,
) -> Batch:
    """Decode the images and build the rows: seconds of CPU for big images, so it runs off the event loop."""
    items = context_items(request.state, request.images, layout.index_arrays)
    return rows(padding, pad_rows, images=image_context(engine.tokenizer, layout, items, engine.vision))


def reads_twice_at_all(layout: Layout) -> bool:
    return layout.read_twice != "off" or layout.read_question_twice != "off"


async def build_batch(
    engine: Engine,
    request: SystemOneRequest,
    orders: OrderFn | None = None,
    pad_rows: int | None = None,
    perms: dict[str, list[list[int]]] | None = None,
    read_once_when_long: bool = True,
):
    """Render and tokenize every row. Refuses bad requests, but not long ones: read_rows does that.
    perms, when given, replaces orders; a question with [] gets no rows but stays in the shared prefix."""
    s = engine.settings
    if not request.questions:
        raise RequestError("questions must not be empty")
    name = request.layout or s.prompt_layout
    if name not in engine.layouts:
        raise RequestError(f"unknown layout {name!r}; available: {sorted(engine.layouts)}")
    layout = engine.layouts[name]
    questions = {qid: render_question(q, layout) for qid, q in request.questions.items()}
    if perms is None:
        orders = orders or functools.partial(option_orders, setting=setting_for(engine, request))
        try:
            perms = {qid: orders(len(q.options)) for qid, q in questions.items()}
        except ValueError as e:
            raise RequestError(str(e)) from e
    images = has_images(request)
    if images and engine.vision is None:
        raise ImageError("this profile serves text only")
    state = "" if images else render_state(request.state, layout.index_arrays)  # image rows take the state from their image context
    rows = functools.partial(
        build_rows, engine.tokenizer, engine.frames[name], layout, engine.labels[name], state, questions, perms
    )
    first = functools.partial(decode_then_build, engine, layout, request, rows) if images else rows
    batch = await asyncio.to_thread(first, engine.padding, pad_rows)
    if read_once_when_long and batch.longest >= s.systemone_max_len and not images and reads_twice_at_all(layout):
        # a request too long to read twice is read once, as if read-twice were off
        layout = replace(layout, read_twice="off", read_question_twice="off")
        rows = functools.partial(
            build_rows, engine.tokenizer, engine.frames[name], layout, engine.labels[name], state, questions, perms
        )
        batch = await asyncio.to_thread(rows, engine.padding, pad_rows)
    if batch.longest >= s.systemone_max_len and engine.padding.enabled:
        # the pad must never refuse a request that fits without it; decoded images are reused
        batch = await asyncio.to_thread(rows, OFF, pad_rows, images=batch.images)
    return name, questions, batch


async def read_batch(readout, batch: Batch, warm: bool = True) -> list[list[float]]:
    """Text rows read as before; image rows go through the image path with their images attached.
    warm=False reports no shared prefix, so the readout does not warm a prefix that is already cached."""
    ids, labels = [r.ids for r in batch.rows], [r.label_ids for r in batch.rows]
    if batch.images is None:
        return await readout.letter_logprobs(ids, labels, batch.shared_len if warm else 0)
    parts = [image.part() for image in batch.images.images]
    prefix_parts = parts if batch.images_shared else []
    shared_tokens = batch.shared_tokens if warm else 0
    return await readout.image_logprobs(ids, labels, batch.shared_len, shared_tokens, parts, prefix_parts)


async def read_into(reads: dict[str, list], engine: Engine, batch: Batch, warm: bool = True) -> None:
    """Refuse a batch over the decision cap, else read it and append each row's (logprobs, perm) to its question."""
    limit = engine.settings.systemone_max_len
    if batch.longest >= limit:
        raise RequestError(f"prompt is longer than the maximum context length ({batch.longest} >= {limit} tokens)")
    logprobs = await read_batch(engine.readout, batch, warm)
    for row, lp in zip(batch.rows, logprobs, strict=True):
        reads[row.question_id].append((lp, row.perm))


def gated_questions(reads: dict[str, list], questions: dict[str, Rendered], cal: Calibration, tau: float) -> set[str]:
    """The questions whose first read, softmaxed at the identity fit's T (no b), tops out under tau."""
    return {qid for qid, q in questions.items()
            if max(softmax(reads[qid][0][0], cal.temperature(q.type, len(q.options)))) < tau}


async def second_pass(engine: Engine, request: SystemOneRequest, r: Reads, kept: set[str]) -> int:
    """Read the reversed order of the kept questions into r.reads; returns the input tokens it used."""
    perms = {qid: [list(range(len(q.options)))[::-1]] if qid in kept else [] for qid, q in r.questions.items()}
    # pad as the first pass did: it read one identity row per question
    _, _, batch = await build_batch(engine, request, pad_rows=len(request.questions), perms=perms)
    await read_into(r.reads, engine, batch, warm=False)
    return batch.input_tokens


def reading_once(engine: Engine, request: SystemOneRequest) -> Engine:
    """The engine with the request's layout reading its shared block once; an unknown layout is build_batch's to refuse."""
    name = request.layout or engine.settings.prompt_layout
    if name not in engine.layouts:
        return engine
    return replace(engine, layouts=engine.layouts | {name: replace(engine.layouts[name], read_twice="off")})


async def reread_pass(engine: Engine, request: SystemOneRequest, r: Reads, kept: set[str]) -> int | None:
    """Read the kept questions in identity and reversed order with the block read twice; these reads replace their
    first. None when the request does not stack the block (images, more questions, too long): read top_p's way."""
    if not reads_twice(engine.layouts[r.layout].read_twice, len(r.questions), has_images(request)):
        return None
    perms = {qid: option_orders(len(q.options), "identity+reversed") if qid in kept else [] for qid, q in r.questions.items()}
    _, _, batch = await build_batch(engine, request, pad_rows=len(request.questions), perms=perms, read_once_when_long=False)
    if batch.longest >= engine.settings.systemone_max_len:
        return None
    for qid in kept:
        r.reads[qid].clear()
    # the first pass cached the block once; warm only if the rest of the shared prefix is long enough to pay
    warm = batch.shared_len - r.shared_len >= engine.settings.warm_min_prefix_tokens
    await read_into(r.reads, engine, batch, warm)
    return batch.input_tokens


async def read_rows(
    engine: Engine, request: SystemOneRequest, orders: OrderFn | None = None, pad_rows: int | None = None
) -> Reads:
    """Read every row; a gated setting then reads the unsure questions again (second_pass or reread_pass), unless
    orders is given. reread_p reads the block once first, so its reread starts with a cached prefix."""
    setting = setting_for(engine, request)
    first = reading_once(engine, request) if not orders and rereads(setting) else engine
    name, questions, batch = await build_batch(first, request, orders, pad_rows)
    reads: dict[str, list] = {qid: [] for qid in questions}
    await read_into(reads, engine, batch)
    padded = batch.shared_len != batch.unpadded_len
    r = Reads(name, questions, reads, batch.input_tokens, batch.shared_len, padded, batch, setting)
    tau = None if orders else gate(setting)  # build_batch has refused a malformed setting
    if tau is None:
        return r
    kept = gated_questions(r.reads, r.questions, calibration_for(engine, r.layout, "identity"), tau)
    if not kept:
        return r
    extra = await reread_pass(engine, request, r, kept) if rereads(setting) else None
    if extra is None:
        extra = await second_pass(engine, request, r, kept)
    return replace(r, input_tokens=r.input_tokens + extra)


def blend(reads: list[tuple[list[float], list[int]]], temperature: float, yes_offset: float = 0.0) -> list[float]:
    """Softmax each order at T (noul: "yes" shifted by yes_offset after /T), then average back to caller order."""
    probs = []
    for lp, perm in reads:
        shifted = [x + yes_offset * temperature if perm[j] == 1 else x for j, x in enumerate(lp)] if yes_offset else lp
        probs.append(softmax(shifted, temperature))
    return average_back(probs, [perm for _, perm in reads])


def combine(reads: list[tuple[list[float], list[int]]], temperature: float, yes_offset: float = 0.0) -> list[float]:
    """Mean-logprob: average raw logprobs in caller order, shift caller "yes" by yes_offset, one softmax at T."""
    perms = [perm for _, perm in reads]
    lp = average_back([lp for lp, _ in reads], perms)
    if yes_offset:
        lp[1] += yes_offset * temperature
    return softmax(lp, temperature)


def probabilities(reads: list[tuple[list[float], list[int]]], q_type: str, cal: Calibration) -> list[float]:
    """The question's T at its option count (one logprob per option), then combine."""
    return combine(reads, cal.temperature(q_type, len(reads[0][0])), cal.b if q_type == "noul" else 0.0)


def answers_for(questions: dict[str, Rendered], reads: dict, cal: Calibration) -> dict:
    return {qid: answer(q, probabilities(reads[qid], q.type, cal)) for qid, q in questions.items()}


async def decide(engine: Engine, request: SystemOneRequest) -> dict:
    r = await read_rows(engine, request)
    return {
        "model": engine.settings.served_model,
        "answers": answers_for(r.questions, r.reads, calibration_for(engine, r.layout, r.orders)),
        "usage": {"input_tokens": r.input_tokens, "output_tokens": 0},
    }
