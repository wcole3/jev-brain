import base64
import dataclasses
import io
import math
import threading

import PIL.Image
import pytest

import gateway.decide
from gateway.calibration import UNCALIBRATED, Calibration, softmax
from gateway.decide import answers_for, blend, build_batch, calibration_for, combine, decide, probabilities, read_rows
from gateway.images import decode_image
from gateway.orders import option_orders
from gateway.padding import Padding, newline_token
from gateway.schema import ImageError, RequestError, SystemOneRequest
from tests.helpers import QUICKSTART, STATE, vision_for


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
