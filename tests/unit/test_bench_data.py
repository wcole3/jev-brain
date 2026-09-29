import random

from scripts.bench_data import jevbench_request, prediction, synthetic_request


def test_synthetic_request_sizes(qwen_tok):
    req = synthetic_request(qwen_tok, random.Random(0), state_tokens=2048, n_questions=4, n_options=26, nonce=False)
    assert abs(len(qwen_tok.encode(req["state"], add_special_tokens=False)) - 2048) <= 16
    assert [q["type"] for q in req["questions"].values()] == ["choice", "score", "noul", "choice"]
    assert len(req["questions"]["q0"]["criteria"]) == 26


def test_nonce_makes_states_unique(qwen_tok):
    rng = random.Random(0)
    a = synthetic_request(qwen_tok, rng, 256, 1, 2)
    b = synthetic_request(qwen_tok, rng, 256, 1, 2)
    assert a["state"] != b["state"]


def test_jevbench_row_mapping():
    row = {
        "type": "score",
        "state": "s",
        "label": "2",
        "question": {"instructions": "How bad?", "levels": ["a", "b", "c"]},
    }
    req, gold = jevbench_request(row)
    assert req["questions"]["q"] == {"type": "score", "instructions": "How bad?", "criteria": ["a", "b", "c"]}
    assert gold == "2"


def test_prediction_per_type():
    assert prediction({"type": "choice", "choice": "x"}) == "x"
    assert prediction({"type": "noul", "noul": 0.7}) == "yes"
    assert prediction({"type": "score", "probabilities": {"0": 0.1, "1": 0.6, "2": 0.3}}) == "1"
