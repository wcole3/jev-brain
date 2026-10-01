import math

import pytest

from scripts.metrics import Scored, brier, ece_of, nll, noul_bias, paired_bootstrap, summary


def test_ece_matches_the_worked_example_in_calibration_md():
    conf = [0.57] * 100 + [0.90] * 300 + [0.98] * 600
    correct = [True] * 55 + [False] * 45 + [True] * 234 + [False] * 66 + [True] * 558 + [False] * 42
    assert ece_of(conf, correct) == pytest.approx(0.068, abs=1e-9)


def test_brier_and_nll_worked_examples():
    right = Scored("s", "f", "choice", 0, [0.7, 0.2, 0.1])
    wrong = Scored("s", "f", "choice", 1, [0.7, 0.2, 0.1])
    assert brier([right]) == pytest.approx(0.14)
    assert brier([wrong]) == pytest.approx(1.14)
    assert nll([Scored("s", "f", "noul", 1, [0.5, 0.5])]) == pytest.approx(math.log(2))


def test_noul_predicts_yes_at_one_half():
    tie = Scored("s", "f", "noul", 1, [0.5, 0.5])
    assert tie.pred == 1 and tie.correct and tie.confidence == 0.5


def test_noul_bias_counts():
    items = [
        Scored("s", "f", "noul", 1, [0.8, 0.2]),  # gold yes, said no
        Scored("s", "f", "noul", 0, [0.3, 0.7]),  # gold no, said yes
        Scored("s", "f", "noul", 1, [0.1, 0.9]),
        Scored("s", "f", "choice", 0, [0.9, 0.1]),  # ignored
    ]
    assert noul_bias(items) == {"rows": 3, "said_yes": 2, "gold_yes": 2, "false_no": 1, "false_yes": 1}


def test_summary_keys_and_accuracy():
    s = summary([Scored("s", "f", "choice", 0, [0.9, 0.1]), Scored("s", "f", "choice", 1, [0.9, 0.1])])
    assert s["n"] == 2 and s["accuracy"] == 0.5 and set(s) == {"n", "accuracy", "ece", "nll", "brier"}


def test_paired_bootstrap_sees_a_clear_gain_and_no_gain():
    a, b = [0.0] * 200, [1.0] * 100 + [0.0] * 100
    mean, lo, hi = paired_bootstrap(a, b)
    assert mean == pytest.approx(0.5) and lo > 0.3 and hi < 0.7
    _, lo, hi = paired_bootstrap(a, a)
    assert lo == hi == 0.0
