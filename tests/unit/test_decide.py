import dataclasses

import pytest

from gateway.calibration import softmax
from gateway.config import Settings
from gateway.decide import Engine, decide
from gateway.labels import label_table
from gateway.layouts import load_layouts
from gateway.padding import Padding, newline_token
from gateway.prompts import chat_frame
from gateway.schema import RequestError, SystemOneRequest
from tests.helpers import QUICKSTART, STATE


class FavourFirstLabel:
    """Fake readout: label A always most likely (logprobs 0, -1, -2, ...)."""

    def __init__(self):
        self.calls = []

    async def letter_logprobs(self, prompts, label_ids, shared_len):
        self.calls.append((prompts, label_ids, shared_len))
        return [[-float(j) for j in range(len(ids))] for ids in label_ids]


@pytest.fixture
def engine(qwen_tok):
    layouts = load_layouts()
    return Engine(
        settings=Settings.from_profile("qwen3.6-27b"),
        tokenizer=qwen_tok,
        layouts=layouts,
        frames={n: chat_frame(qwen_tok, l) for n, l in layouts.items()},
        labels={n: label_table(qwen_tok) for n in layouts},
        temperatures={n: {"choice": 1.0, "score": 1.0, "noul": 1.0} for n in layouts},
        readout=FavourFirstLabel(),
    )


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
    small = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, max_model_len=50))
    with pytest.raises(RequestError, match="maximum context length"):
        await decide(small, request())
    assert engine.readout.calls == []


async def test_padded_rows_reach_the_readout_and_usage_leaves_the_pad_out(engine, qwen_tok):
    padded = dataclasses.replace(engine, padding=Padding("end", 784, True, newline_token(qwen_tok)))
    usage = (await decide(padded, request()))["usage"]
    assert engine.readout.calls[0][2] == 784  # the shared length the warm-up rule sees
    assert usage == (await decide(engine, request()))["usage"]


async def test_padding_never_refuses_a_request_that_fits_without_it(engine, qwen_tok):
    small = dataclasses.replace(engine.settings, max_model_len=200)  # rows fit unpadded, not padded to 784
    padded = dataclasses.replace(engine, settings=small, padding=Padding("end", 784, True, newline_token(qwen_tok)))
    await decide(padded, request())
    prompts, _, shared_len = engine.readout.calls[0]
    assert shared_len < 784 and max(len(p) for p in prompts) < 200
