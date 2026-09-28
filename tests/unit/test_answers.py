import pytest

from gateway.answers import answer, choice_confidence, score_confidence
from gateway.questions import Rendered


def test_confidence_matches_typesafe_examples():
    assert choice_confidence([0.88, 0.12, 0.0]) == pytest.approx(0.82)
    assert choice_confidence([0.85, 0.0, 0.15]) == pytest.approx(0.775)
    assert score_confidence([0.65, 0.30, 0.05]) == pytest.approx(0.40)
    assert score_confidence([0.0, 0.0, 0.1, 0.3, 0.6]) == pytest.approx(0.5833, abs=1e-4)


def test_answer_shapes():
    choice = Rendered("choice", "t", ["a: x", "b"], ["a", "b"])
    assert answer(choice, [0.25, 0.75]) == {
        "type": "choice",
        "choice": "b",
        "confidence": 0.5,
        "probabilities": {"a": 0.25, "b": 0.75},
    }
    score = Rendered("score", "t", ["0: lo", "1: hi"], [0, 1], ["lo", "hi"])
    assert answer(score, [0.25, 0.75]) == {
        "type": "score",
        "score": 0.75,
        "confidence": 0.5,
        "legend": {"0": "lo", "1": "hi"},
        "probabilities": {"0": 0.25, "1": 0.75},
    }
    noul = Rendered("noul", "t", ["no", "yes"], [False, True])
    assert answer(noul, [0.123456, 0.876544]) == {"type": "noul", "noul": 0.8765}
