import dataclasses
import math

import pytest

from gateway.calibration import Calibration, softmax
from gateway.decide import answers_for, blend, build_batch, decide, probabilities, read_rows
from gateway.orders import option_orders
from gateway.padding import Padding, newline_token
from gateway.schema import RequestError, SystemOneRequest
from tests.helpers import QUICKSTART, STATE


def request(**kw):
    return SystemOneRequest.model_validate({"state": STATE, "questions": QUICKSTART} | kw)


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
    p3 = softmax([0.0, -1.0, -2.0], 1.0)
    probs = list(out["answers"]["department"]["probabilities"].values())
    assert probs == pytest.approx([(p3[0] + p3[2]) / 2, p3[1], (p3[0] + p3[2]) / 2], abs=1e-4)
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
