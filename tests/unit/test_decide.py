import base64
import dataclasses
import io
import math
import threading

import PIL.Image
import pytest

import gateway.decide
from gateway.calibration import UNCALIBRATED, Calibration, Curve, softmax
from gateway.decide import (
    answers_for,
    blend,
    build_batch,
    calibration_for,
    combine,
    decide,
    gated_questions,
    probabilities,
    read_rows,
    reading_once,
)
from gateway.images import decode_image
from gateway.labels import label_table
from gateway.orders import option_orders
from gateway.padding import Padding, newline_token
from gateway.prompts import chat_frame
from gateway.schema import ImageError, RequestError, SystemOneRequest
from tests.helpers import QUICKSTART, STATE, FavourFirstLabel, SureOf, vision_for


def request(**kw):
    return SystemOneRequest.model_validate({"state": STATE, "questions": QUICKSTART} | kw)


def png_b64(w=64, h=32) -> str:
    buf = io.BytesIO()
    PIL.Image.new("RGB", (w, h)).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@pytest.fixture
def seeing(engine, qwen_tok):
    """The test engine with qwen's image placeholder and 100 soft tokens per image."""
    return dataclasses.replace(engine, vision=vision_for(qwen_tok))


async def test_quickstart_answers_have_jev_shapes(engine):
    out = await decide(engine, request())
    p3 = softmax([0.0, -1.0, -2.0], 1.0)
    dept = out["answers"]["department"]
    assert dept["choice"] == "billing"
    assert list(dept["probabilities"].values()) == pytest.approx(p3, abs=1e-4)
    assert set(out["answers"]["frustration"]) == {"type", "score", "confidence", "legend", "probabilities"}
    assert out["answers"]["is_urgent"] == {"type": "noul", "noul": round(softmax([0.0, -1.0], 1.0)[1], 4)}
    assert out["model"] == "qwen3.6-27b"
    assert out["usage"]["output_tokens"] == 0 and out["usage"]["input_tokens"] > 0


async def test_reversed_orders_average_back(engine):
    out = await decide(engine, request(option_orders="identity+reversed"))
    probs = list(out["answers"]["department"]["probabilities"].values())
    assert probs == pytest.approx([1 / 3, 1 / 3, 1 / 3], abs=1e-4)  # mean logprobs are [-1, -1, -1]
    assert len(engine.readout.calls[0][0]) == 6  # 3 questions x 2 orders


async def test_bad_overrides_are_refusals(engine):
    with pytest.raises(RequestError, match="unknown layout"):
        await decide(engine, request(layout="nope"))
    with pytest.raises(RequestError, match="unknown option_orders"):
        await decide(engine, request(option_orders="shuffle"))
    with pytest.raises(RequestError, match="must not be empty"):
        await decide(engine, SystemOneRequest.model_validate({"state": STATE, "questions": {}}))


async def test_too_long_prompt_is_refused_before_vllm(engine):
    small = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, systemone_max_len=50))
    with pytest.raises(RequestError, match="maximum context length"):
        await decide(small, request())
    assert engine.readout.calls == []


async def test_decision_cap_applies_below_the_model_limit(engine):
    s = dataclasses.replace(engine.settings, max_model_len=262144, systemone_max_len=50)
    with pytest.raises(RequestError, match=r"\(\d+ >= 50 tokens\)"):
        await decide(dataclasses.replace(engine, settings=s), request())


async def test_padded_rows_reach_the_readout_and_usage_leaves_the_pad_out(engine, qwen_tok):
    padded = dataclasses.replace(engine, padding=Padding("end", 784, True, newline_token(qwen_tok)))
    usage = (await decide(padded, request()))["usage"]
    assert engine.readout.calls[0][2] == 784  # the shared length the warm-up rule sees
    assert usage == (await decide(engine, request()))["usage"]


async def test_padding_never_refuses_a_request_that_fits_without_it(engine, qwen_tok):
    small = dataclasses.replace(engine.settings, systemone_max_len=200)  # rows fit unpadded, not padded to 784
    padded = dataclasses.replace(engine, settings=small, padding=Padding("end", 784, True, newline_token(qwen_tok)))
    await decide(padded, request())
    prompts, _, shared_len = engine.readout.calls[0]
    assert shared_len < 784 and max(len(p) for p in prompts) < 200


async def test_pad_rows_makes_extra_orders_pad_like_the_identity_request(engine, qwen_tok):
    padded = dataclasses.replace(engine, padding=Padding("end", 784, False, newline_token(qwen_tok)))
    req = request(state=STATE * 4, layout="header")  # 3 rows do not pay for the pad, 8 rows do
    _, _, live = await build_batch(padded, req, lambda n: [list(range(n))])
    _, _, many = await build_batch(padded, req, lambda n: option_orders(n, "cyclic:4"))
    _, _, pinned = await build_batch(padded, req, lambda n: option_orders(n, "cyclic:4"), pad_rows=3)
    assert many.shared_len == 784 and live.shared_len < 784
    identity = [r.ids for r in pinned.rows if r.perm == sorted(r.perm)]
    assert identity == [r.ids for r in live.rows]


async def test_read_rows_keeps_raw_logprobs_per_order(engine):
    r = await read_rows(engine, request(option_orders="identity+reversed"))
    assert r.layout == "decider_chat"
    assert [perm for _, perm in r.reads["department"]] == [[0, 1, 2], [2, 1, 0]]
    assert r.reads["department"][0][0] == [0.0, -1.0, -2.0]  # raw: no temperature applied


async def test_orders_function_overrides_the_setting(engine):
    r = await read_rows(engine, request(), orders=lambda n: [list(range(n))[::-1]])
    assert r.reads["department"][0][1] == [2, 1, 0]
    assert r.reads["is_urgent"][0][1] == [1, 0]


async def test_decide_is_read_rows_then_answers_for(engine):
    r = await read_rows(engine, request())
    out = await decide(engine, request())
    assert out["answers"] == answers_for(r.questions, r.reads, engine.calibration["decider_chat"])
    assert out["usage"] == {"input_tokens": r.input_tokens, "output_tokens": 0}


def test_blend_maps_a_reversed_order_back():
    q = softmax([0.0, -1.0], 2.0)
    assert blend([([0.0, -1.0], [0, 1])], 2.0) == pytest.approx(q)
    assert blend([([0.0, -1.0], [1, 0])], 2.0) == pytest.approx([q[1], q[0]])


def test_yes_offset_shifts_noul_toward_yes_in_every_order():
    reads = [([0.0, 0.0], [0, 1]), ([0.0, 0.0], [1, 0])]  # no/yes even in both orders
    p = probabilities(reads, "noul", Calibration({"choice": 1, "score": 1, "noul": 2.0}, b=1.0))
    assert p[1] == pytest.approx(1 / (1 + math.exp(-1.0)))  # sigma(0/T + b)


def test_offset_is_ignored_for_choice_and_zero_keeps_old_math():
    reads = [([0.0, -1.0, -2.0], [0, 1, 2])]
    cal = Calibration({"choice": 1.0, "score": 1.0, "noul": 1.0}, b=3.0)
    assert probabilities(reads, "choice", cal) == pytest.approx(softmax([0.0, -1.0, -2.0], 1.0))
    assert probabilities(reads, "noul", Calibration(cal.T, b=0.0)) == pytest.approx(blend(reads, 1.0))


@pytest.mark.parametrize("body", [{"images": ["https://x/a.png"]}, {"state": [{"image": "not decoded"}, STATE]}])
async def test_images_on_a_text_profile_are_refused(engine, body):
    with pytest.raises(ImageError, match="this profile serves text only"):
        await decide(engine, request(**body))
    assert engine.readout.calls == engine.readout.image_calls == []


async def test_image_requests_read_through_the_image_path(seeing):
    src = png_b64()
    await decide(seeing, request(images=[src], layout="header"))
    _, _, shared_len, shared_tokens, parts, prefix_parts = seeing.readout.image_calls[0]
    assert parts == [decode_image(src, "images[0]").part()]
    assert prefix_parts == parts
    assert shared_tokens == shared_len + 99  # 100 soft tokens + 2 marks - 3 placeholder ids
    assert seeing.readout.calls == []
    await decide(seeing, request())
    assert len(seeing.readout.calls) == 1 and len(seeing.readout.image_calls) == 1


async def test_images_decode_once_off_the_event_loop(seeing, qwen_tok, monkeypatch):
    threads, decode = [], gateway.decide.context_items

    def recording(*args):
        threads.append(threading.current_thread())
        return decode(*args)

    monkeypatch.setattr(gateway.decide, "context_items", recording)
    small = dataclasses.replace(seeing.settings, systemone_max_len=500)  # fits unpadded, not padded to 784
    padded = dataclasses.replace(seeing, settings=small, padding=Padding("end", 784, True, newline_token(qwen_tok)))
    await decide(padded, request(images=[png_b64()]))
    assert seeing.readout.image_calls[0][3] < 784  # shared_tokens: padded, they would end on 784
    assert len(threads) == 1 and threads[0] is not threading.main_thread()


async def test_expanded_image_prompts_over_the_cap_are_refused(seeing):
    req = request(images=[png_b64()])
    _, _, batch = await build_batch(seeing, req)
    unexpanded = max(len(r.ids) for r in batch.rows)
    s = dataclasses.replace(seeing.settings, systemone_max_len=unexpanded + 1)  # fits until the image expands
    with pytest.raises(RequestError, match="maximum context length"):
        await decide(dataclasses.replace(seeing, settings=s), req)
    assert seeing.readout.image_calls == []


async def test_usage_counts_image_tokens(seeing):
    req = request(images=[png_b64()])
    _, _, batch = await build_batch(seeing, req)
    text = batch.unpadded_len + sum(len(r.ids) - batch.shared_len for r in batch.rows)
    usage = (await decide(seeing, req))["usage"]
    assert usage["input_tokens"] == batch.input_tokens == text + batch.added
    assert batch.added == 99


async def test_images_after_the_question_are_not_prefix_parts(seeing):
    await decide(seeing, request(images=[png_b64()], layout="question_first"))
    _, _, shared_len, shared_tokens, parts, prefix_parts = seeing.readout.image_calls[0]
    assert len(parts) == 1 and prefix_parts == []
    assert shared_tokens == shared_len


def test_combine_equals_blend_with_one_order():
    reads = [([-0.2, -1.9, -3.0], [0, 1, 2])]
    assert combine(reads, 1.7) == pytest.approx(blend(reads, 1.7))
    noul = [([-0.4, -1.2], [0, 1])]
    assert combine(noul, 0.9, 0.3) == pytest.approx(blend(noul, 0.9, 0.3))


def test_combine_averages_logprobs_then_softmaxes():
    reads = [([0.0, -2.0], [0, 1]), ([-1.0, 0.0], [1, 0])]  # caller logprobs: [0, -2] and [0, -1]
    assert combine(reads, 1.0) == pytest.approx(softmax([0.0, -1.5], 1.0))


def test_combine_puts_the_yes_offset_on_caller_yes_in_a_reversed_noul():
    reads = [([-0.5, -1.0], [0, 1]), ([-1.0, -0.5], [1, 0])]
    assert combine(reads, 2.0, 0.25) == pytest.approx(softmax([-0.5, -1.0 + 0.5], 2.0))


def test_calibration_for_picks_the_fit_of_the_setting(engine):
    text = "top_p:0.9+reversed"
    ident = Calibration({"choice": 2.0, "score": 2.0, "noul": 2.0}, orders="identity")
    s = dataclasses.replace(engine.settings, option_orders=text)
    e = dataclasses.replace(engine, settings=s, other_calibrations={"identity": {"decider_chat": ident}})
    assert calibration_for(e, "decider_chat", text) is e.calibration["decider_chat"]
    assert calibration_for(e, "decider_chat", "identity") is ident
    assert calibration_for(e, "header", "identity") == UNCALIBRATED
    assert calibration_for(e, "decider_chat", "cyclic:3") is e.calibration["decider_chat"]
    assert calibration_for(e, "decider_chat", "reread_p:0.9") is e.calibration["decider_chat"]  # borrows the text fit


TOP_P = "top_p:0.9+reversed"


def gated(engine, readout=None, **settings):
    """The engine on top_p text orders (other settings as given), reading through `readout` when given."""
    s = dataclasses.replace(engine.settings, **({"option_orders": TOP_P} | settings))
    return dataclasses.replace(engine, settings=s, readout=readout or engine.readout)


async def test_top_p_reads_reversed_only_for_questions_under_tau(engine):
    e = gated(engine, SureOf(3))  # the 3-option question is sure, the yes/no one reads 0.73 < 0.9
    req = request(questions={"sure": QUICKSTART["department"], "unsure": QUICKSTART["is_urgent"]})
    r = await read_rows(e, req)
    assert [len(r.reads[q]) for q in ("sure", "unsure")] == [1, 2]
    assert r.reads["unsure"][1][1] == [1, 0]
    assert [len(prompts) for prompts, _, _ in e.readout.calls] == [2, 1]
    _, _, first = await build_batch(e, req)
    _, _, second = await build_batch(e, req, pad_rows=2, perms={"sure": [], "unsure": [[1, 0]]})
    assert r.input_tokens == first.input_tokens + second.input_tokens
    assert r.orders == TOP_P and r.batch.rows == first.rows


async def test_top_p_with_every_question_confident_sends_one_call(engine):
    e = gated(engine, SureOf(2, 3))
    r = await read_rows(e, request())
    assert len(e.readout.calls) == 1
    assert all(len(reads) == 1 for reads in r.reads.values())


async def test_gated_override_without_identity_file_gates_at_T_1(engine):
    r = await read_rows(engine, request(option_orders=TOP_P))  # UNCALIBRATED: every question is under tau at T = 1
    assert all(len(reads) == 2 for reads in r.reads.values())
    sharp = Calibration({"choice": 0.2, "score": 0.2, "noul": 0.2})  # no identity file: the text fit's T gates
    e = dataclasses.replace(engine, readout=SureOf(), calibration=engine.calibration | {"decider_chat": sharp})
    await decide(e, request(option_orders=TOP_P))
    assert len(e.readout.calls) == 1


async def test_image_request_uses_image_orders_and_their_calibration(seeing):
    ident = Calibration({"choice": 2.0, "score": 2.0, "noul": 2.0}, orders="identity")
    text = Calibration({"choice": 3.0, "score": 3.0, "noul": 3.0}, orders=TOP_P)
    e = dataclasses.replace(
        gated(seeing, option_orders_images="identity"),
        calibration=seeing.calibration | {"decider_chat": text},
        other_calibrations={"identity": {"decider_chat": ident}},
    )
    req = request(images=[png_b64()])
    r = await read_rows(e, req)
    assert r.orders == "identity" and len(seeing.readout.image_calls) == 1
    assert all(len(reads) == 1 for reads in r.reads.values())
    assert (await decide(e, req))["answers"] == answers_for(r.questions, r.reads, ident)


async def test_gated_image_rows_take_the_same_two_passes(seeing):
    await read_rows(gated(seeing), request(images=[png_b64()]))
    first, second = seeing.readout.image_calls
    assert first[3] > 0 and second[3] == 0  # shared_tokens: the second pass does not warm the prefix again
    assert len(second[0]) == len(first[0]) == 3


async def test_orders_fn_from_collect_disables_the_gate(engine):
    e = gated(engine)
    r = await read_rows(e, request(), orders=lambda n: option_orders(n, "identity+reversed"), pad_rows=3)
    assert len(e.readout.calls) == 1
    assert all(len(reads) == 2 for reads in r.reads.values())


async def test_bad_gated_override_is_a_request_error(engine):
    with pytest.raises(RequestError, match="bad option_orders"):
        await decide(engine, request(option_orders="top_p:1.5+reversed"))
    assert engine.readout.calls == []


async def test_second_pass_skips_warm_up(engine):
    e = gated(engine)
    r = await read_rows(e, request())
    (_, _, first), (_, _, second) = e.readout.calls
    assert first == r.shared_len > 0 and second == 0


async def test_second_pass_keeps_every_question_in_the_shared_prefix(engine):
    req = request(layout="header")  # header lists every question in the shared prefix
    _, _, first = await build_batch(engine, req)
    perms = {"department": [], "frustration": [], "is_urgent": [[1, 0]]}
    _, _, second = await build_batch(engine, req, pad_rows=3, perms=perms)
    assert [(r.question_id, r.perm) for r in second.rows] == [("is_urgent", [1, 0])]
    assert second.rows[0].ids[: first.shared_len] == first.rows[0].ids[: first.shared_len]


async def test_identity_profile_answers_with_its_text_fit(engine):
    fit = Calibration({"choice": 1.7, "score": 0.8, "noul": 1.3}, b=0.4, orders="identity")
    e = dataclasses.replace(engine, calibration=engine.calibration | {"decider_chat": fit})
    r = await read_rows(e, request())
    assert (await decide(e, request()))["answers"] == answers_for(r.questions, r.reads, fit)


async def test_a_request_too_long_to_read_twice_is_read_once(engine):
    req = request(questions={"department": QUICKSTART["department"]}, layout="blurb_header_reread")
    _, _, twice = await build_batch(engine, req)
    once_layout = dataclasses.replace(engine.layouts["blurb_header_reread"], read_twice="off", read_question_twice="off")
    once_engine = dataclasses.replace(engine, layouts=engine.layouts | {"blurb_header_reread": once_layout})
    _, _, once = await build_batch(once_engine, req)
    assert once.longest < twice.longest
    fits_once = dataclasses.replace(engine.settings, systemone_max_len=once.longest + 1)
    _, _, got = await build_batch(dataclasses.replace(engine, settings=fits_once), req)
    assert [r.ids for r in got.rows] == [r.ids for r in once.rows]


REREAD = "reread_p:0.9"
STACKED = "blurb_header_reread"  # reads the shared block twice for one question


def one_question(**kw):
    """department alone: FavourFirstLabel tops it out at 0.665 at T = 1."""
    return request(questions={"department": QUICKSTART["department"]}, layout=STACKED, **kw)


async def rows_of(engine, req, **kw):
    return (await build_batch(engine, req, **kw))[2]


@pytest.mark.parametrize(("tau", "calls"), [(0.6, 1), (0.7, 2)])
async def test_reread_p_gates_on_the_identity_read(engine, tau, calls):
    await read_rows(engine, one_question(option_orders=f"reread_p:{tau}"))
    assert len(engine.readout.calls) == calls


async def test_reread_p_sure_question_reads_once_with_the_block_once(engine):
    e = dataclasses.replace(engine, readout=SureOf(3))
    r = await read_rows(e, one_question(option_orders=REREAD))
    once = await rows_of(reading_once(engine, one_question()), one_question())
    assert once.longest < (await rows_of(engine, one_question())).longest
    assert [prompts for prompts, _, _ in e.readout.calls] == [[row.ids for row in once.rows]]
    assert len(r.reads["department"]) == 1 and r.input_tokens == once.input_tokens


async def test_reread_p_unsure_question_answers_from_two_stacked_reads(engine):
    req = one_question(option_orders=REREAD)
    r = await read_rows(engine, req)
    first = await rows_of(reading_once(engine, req), req)
    second = await rows_of(engine, req, pad_rows=1, perms={"department": [[0, 1, 2], [2, 1, 0]]})
    assert [prompts for prompts, _, _ in engine.readout.calls] == [[row.ids for row in b.rows] for b in (first, second)]
    assert [perm for _, perm in r.reads["department"]] == [[0, 1, 2], [2, 1, 0]]  # the block-once read is dropped
    assert r.input_tokens == first.input_tokens + second.input_tokens
    out = await decide(engine, req)
    assert list(out["answers"]["department"]["probabilities"].values()) == pytest.approx([1 / 3] * 3, abs=1e-4)
    assert out["usage"]["input_tokens"] == r.input_tokens


@pytest.mark.parametrize(("warm_min", "warms"), [(800, False), (0, True)])
async def test_reread_pass_warms_only_a_long_uncached_part(engine, warm_min, warms):
    e = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, warm_min_prefix_tokens=warm_min))
    r = await read_rows(e, one_question(option_orders=REREAD))
    second = await rows_of(e, one_question(), pad_rows=1, perms={"department": [[0, 1, 2], [2, 1, 0]]})
    assert e.readout.calls[0][2] == r.shared_len
    assert e.readout.calls[1][2] == (second.shared_len if warms else 0)


async def test_reread_pass_starts_with_the_first_pass_prefix(engine, qwen_tok, gemma_tok):
    """The block-once first pass leaves its shared prefix in vLLM's cache; the stacked second pass starts with it."""
    for tok in (qwen_tok, gemma_tok):
        frames, labels = engine.frames | {STACKED: chat_frame(tok, engine.layouts[STACKED])}, {STACKED: label_table(tok)}
        e = dataclasses.replace(engine, tokenizer=tok, frames=frames, labels=labels, readout=FavourFirstLabel())
        r = await read_rows(e, one_question(option_orders=REREAD))
        (first, _, _), (second, _, _) = e.readout.calls
        assert r.shared_len > 0 and len(second[0]) > len(first[0])
        assert all(ids[: r.shared_len] == first[0][: r.shared_len] for ids in second)


async def reads_like_top_p(engine, req):
    """reread_p and top_p send the same reads and keep the same results; returns the calls."""
    got = []
    for setting in (REREAD, TOP_P):
        e = dataclasses.replace(engine, readout=FavourFirstLabel())
        r = await read_rows(e, req.model_copy(update={"option_orders": setting}))
        got.append((e.readout.calls, e.readout.image_calls, r.reads, r.input_tokens))
    assert got[0] == got[1]
    return got[0][0] or got[0][1]


async def test_reread_p_reads_more_questions_like_top_p(engine):
    calls = await reads_like_top_p(engine, request(layout=STACKED))
    assert [len(prompts) for prompts, _, _ in calls] == [3, 3]  # every question is unsure at T = 1


async def test_reread_p_reads_a_request_too_long_to_stack_like_top_p(engine):
    once = await rows_of(reading_once(engine, one_question()), one_question())
    e = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, systemone_max_len=once.longest + 1))
    calls = await reads_like_top_p(e, one_question())
    assert calls[0][0] == [row.ids for row in once.rows] and len(calls) == 2


async def test_reread_p_reads_an_image_request_like_top_p(seeing):
    calls = await reads_like_top_p(seeing, one_question(images=[png_b64()]))
    assert len(calls) == 2


CURVE = Curve(6.85, -0.8)


def test_probabilities_take_the_curve_at_each_question_option_count():
    cal = Calibration({"choice": CURVE, "score": 1.0, "noul": 1.0})
    two = [([0.0, -2.0], [0, 1]), ([-2.5, 0.0], [1, 0])]
    five = [([0.0, -1.0, -2.0, -3.0, -4.0], [0, 1, 2, 3, 4])]
    assert probabilities(two, "choice", cal) == pytest.approx(combine(two, CURVE(2)))
    assert probabilities(five, "choice", cal) == pytest.approx(combine(five, CURVE(5)))
    assert CURVE(2) != CURVE(5)


@pytest.mark.parametrize("seed", range(5))
def test_a_curve_never_changes_the_top_answer(seed):
    import random

    rng = random.Random(seed)
    curve, flat = Calibration({"choice": CURVE, "score": 1, "noul": 1}), Calibration({"choice": 3.98, "score": 1, "noul": 1})
    for n in (2, 3, 5, 9, 20, 40):
        reads = [([rng.gauss(0, 3) for _ in range(n)], list(range(n)))]
        a, b = probabilities(reads, "choice", curve), probabilities(reads, "choice", flat)
        assert a.index(max(a)) == b.index(max(b))


def test_gate_softmaxes_the_first_read_at_the_identity_fit_for_its_option_count():
    from types import SimpleNamespace

    questions = {"q": SimpleNamespace(type="choice", options=["a", "b", "c"])}
    reads = {"q": [([0.0, -2.0, -2.0], [0, 1, 2])]}  # top 0.79 at T = 1
    flat = Calibration({"choice": 1.0, "score": 1.0, "noul": 1.0}, orders="identity")
    assert gated_questions(reads, questions, flat, 0.9) == {"q"} and gated_questions(reads, questions, flat, 0.7) == set()
    curved = Calibration({"choice": Curve(1.0 + math.log(3), -1.0), "score": 1.0, "noul": 1.0}, orders="identity")
    assert gated_questions(reads, questions, curved, 0.7) == set()  # T(3) = 1


async def test_top_p_gate_ignores_a_curve_in_the_answer_fit(engine):
    sharp = Calibration({"choice": Curve(0.1, 0.0), "score": 0.1, "noul": 0.1}, orders=TOP_P)
    ident = Calibration({"choice": 1.0, "score": 1.0, "noul": 1.0}, orders="identity")
    e = dataclasses.replace(gated(engine, SureOf(3)), calibration=engine.calibration | {"decider_chat": sharp},
                            other_calibrations={"identity": {"decider_chat": ident}})
    r = await read_rows(e, request(questions={"sure": QUICKSTART["department"], "unsure": QUICKSTART["is_urgent"]}))
    assert [len(r.reads[q]) for q in ("sure", "unsure")] == [1, 2]
