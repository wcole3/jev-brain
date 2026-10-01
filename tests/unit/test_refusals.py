"""Capacity refusals must carry a decision-index harness marker, or the harness records them as errors."""

import dataclasses

import pytest

from gateway.decide import decide
from gateway.schema import RequestError, SystemOneRequest
from tests.helpers import STATE

# decision_index/engines/http.py at 87d4650: 400/413/422 bodies containing one of these become `unsupported`
HARNESS_MARKERS = (
    "options per choice",
    "a choice needs at least two options",
    "a score takes 2 to 10 levels",
    "the canvas holds",
    "maximum context length",
    "maximum model length",
    "longer than the maximum model length",
    "context window",
    "too many tokens",
)

TOO_MANY = {"q": {"type": "choice", "instructions": "pick", "criteria": {f"o{i}": None for i in range(256)}}}
TOO_FEW = {"q": {"type": "choice", "instructions": "pick", "criteria": {"only": None}}}
TOO_MANY_LEVELS = {"q": {"type": "score", "instructions": "rate", "criteria": [str(i) for i in range(11)]}}
FITS = {"q": {"type": "noul", "instructions": "is it?"}}


@pytest.mark.parametrize("questions", [TOO_MANY, TOO_FEW, TOO_MANY_LEVELS])
async def test_capacity_refusals_carry_a_marker(engine, questions):
    with pytest.raises(RequestError) as refused:
        await decide(engine, SystemOneRequest.model_validate({"state": STATE, "questions": questions}))
    assert any(m in str(refused.value) for m in HARNESS_MARKERS)


async def test_length_refusal_carries_a_marker(engine):
    small = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, systemone_max_len=10))
    with pytest.raises(RequestError) as refused:
        await decide(small, SystemOneRequest.model_validate({"state": STATE, "questions": FITS}))
    assert any(m in str(refused.value) for m in HARNESS_MARKERS)
