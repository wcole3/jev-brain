import pytest

from tests.live.api import post

pytestmark = pytest.mark.live


def choice(n: int) -> dict:
    return {"type": "choice", "instructions": "Which code applies?", "criteria": {f"code_{i}": None for i in range(n)}}


def test_null_descriptions_and_bare_noul(gateway_url):
    body = {
        "state": "Order 7 arrived broken.",
        "questions": {
            "kind": {"type": "choice", "instructions": "Issue?", "criteria": {"damage": None, "late": None}},
            "refund": {"type": "noul", "instructions": "A refund is appropriate"},
        },
    }
    r = post(gateway_url, body)
    assert r.status_code == 200
    assert set(r.json()["answers"]["refund"]) == {"type", "noul"}


def test_noul_described_without_instructions(gateway_url):
    body = {
        "state": "I am furious!!!",
        "questions": {"q": {"type": "noul", "criteria": {"true": "The writer is angry"}}},
    }
    assert post(gateway_url, body).json()["answers"]["q"]["noul"] > 0.5


@pytest.mark.parametrize("n", [130, 255])
def test_wide_choices(gateway_url, n):
    r = post(gateway_url, {"state": "code_7 applies.", "questions": {"q": choice(n)}})
    assert r.status_code == 200
    probs = r.json()["answers"]["q"]["probabilities"]
    assert len(probs) == n
    assert sum(probs.values()) == pytest.approx(1, abs=1e-2)


def test_too_many_options_refused_with_marker(gateway_url):
    r = post(gateway_url, {"state": "s", "questions": {"q": choice(256)}})
    assert r.status_code == 422
    assert "options per choice" in r.text


def test_oversized_state_refused_with_marker(gateway_url):
    r = post(gateway_url, {"state": "word " * 40000, "questions": {"q": choice(2)}})
    assert r.status_code == 422
    assert "maximum context length" in r.text
