import gzip
import json

import pytest

from scripts.index_agreement import agreement, load, main


def choice(a, b):
    return {"type": "choice", "probabilities": {"A": a, "B": b}}


def noul(p):
    return {"type": "noul", "noul": p}


def line(run_id, answers, status="ok", as_string=False):
    response = {"answers": answers}
    return json.dumps({"run_id": run_id, "status": status, "response": json.dumps(response) if as_string else response})


BEFORE = {
    "r1": {"q1": choice(0.52, 0.48), "q2": noul(0.9)},
    "r2": {"q1": noul(0.95), "q2": choice(0.7, 0.3)},
    "only-before": {"q1": noul(0.5)},
}
AFTER = {
    "r1": {"q1": choice(0.45, 0.55), "q2": noul(0.8)},
    "r2": {"q1": noul(0.2), "q2": choice(0.68, 0.32)},
    "only-after": {"q1": noul(0.5)},
}


def test_load_keeps_ok_rows_and_the_last_line_per_run(tmp_path):
    path = tmp_path / "results.jsonl"
    path.write_text(
        "\n".join(
            [
                line("a", {"q": noul(0.1)}),
                line("a", {"q": noul(0.2)}, as_string=True),
                line("b", {"q": noul(0.3)}, status="error"),
                line("c", {"q": noul(0.4)}),
                line("c", {"q": noul(0.5)}, status="error"),
            ]
        )
        + "\n"
    )
    assert load(str(path)) == {"a": {"q": noul(0.2)}}


def test_load_reads_gzip(tmp_path):
    path = tmp_path / "results.jsonl.gz"
    with gzip.open(path, "wt") as f:
        f.write(line("a", {"q": noul(0.1)}) + "\n")
    assert load(str(path)) == {"a": {"q": noul(0.1)}}


def test_agreement_counts_flips_and_gap_rule():
    result = agreement(BEFORE, AFTER)
    assert result["rows"] == 2
    assert result["questions"] == 4
    assert result["flips"] == 2  # r1/q1 (gap 0.04) and r2/q1 (before gap 0.90)
    assert result["flips_over_gap"] == 1
    assert result["max_dp"] == pytest.approx(0.75)
    assert result["median_dp"] == pytest.approx(0.085)  # dp: 0.02, 0.07, 0.10, 0.75
    assert result["by_type"] == {"choice": 2, "noul": 2}


def test_agreement_skips_questions_without_matching_options():
    before = {"r": {"q1": choice(0.6, 0.4), "q2": noul(0.5)}}
    after = {"r": {"q1": {"type": "choice", "probabilities": {"A": 0.4, "C": 0.6}}}}
    assert agreement(before, after)["questions"] == 0


def test_agreement_without_shared_rows_is_empty():
    result = agreement({"a": {}}, {"b": {}})
    assert result == {
        "rows": 0,
        "questions": 0,
        "flips": 0,
        "flips_over_gap": 0,
        "max_dp": 0.0,
        "median_dp": 0.0,
        "by_type": {},
    }


def write(path, runs):
    path.write_text("".join(line(run_id, answers) + "\n" for run_id, answers in runs.items()))
    return str(path)


def test_main_exits_one_on_a_flip_over_the_gap(tmp_path, capsys):
    before, after = write(tmp_path / "before.jsonl", BEFORE), write(tmp_path / "after.jsonl", AFTER)
    assert main([before, after]) == 1
    out = capsys.readouterr().out
    assert "rows compared: 2" in out
    assert "top-answer flips: 2" in out
    assert "flips with before top-two gap > 0.10: 1" in out
    assert "max 0.7500" in out


def test_main_exits_zero_when_flips_are_within_the_gap(tmp_path):
    before = write(tmp_path / "before.jsonl", {"r": {"q": choice(0.52, 0.48)}})
    after = write(tmp_path / "after.jsonl", {"r": {"q": choice(0.45, 0.55)}})
    assert main([before, after]) == 0
