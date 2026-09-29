import pytest

from scripts.bench_report import provenance, qwk, summary


def bench_row(kind: str, correct: bool, metric: str = "exact", gold: str = "0", pred: str | None = "0") -> dict:
    return {
        "test": "jevbench",
        "type": kind,
        "eval_metric": metric,
        "gold": gold,
        "pred": pred,
        "correct": correct,
        "ms": 10,
    }


def test_summary_ignores_errors_and_reports_their_count():
    records = [
        {"test": "cold", "state_tokens": 256, "questions": 1, "options": 2, "ms": 100},
        {"test": "throughput", "error": "ReadTimeout"},
        {"test": "throughput", "workers": 1, "requests_per_s": 0.5},
        {"test": "chat_load", "error": "ConnectError"},
    ]
    out = summary(records)
    assert "| cold | 256 | 1 | 2 | 100 | 100 |" in out
    assert "| 1 | 0.5 |" in out
    assert "Errors: chat_load 1, throughput 1" in out


def test_summary_omits_chat_table_when_no_chat_records():
    records = [{"test": "cold", "state_tokens": 256, "questions": 1, "options": 2, "ms": 100}]
    assert "chat prompt" not in summary(records)


def test_qwk_perfect_agreement_is_one():
    assert qwk([0, 1, 2, 2], [0, 1, 2, 2]) == 1.0


def test_qwk_hand_checked_case():
    # n=3: observed 0.5, expected 5.5 / 4 = 1.375, so 1 - 0.5 / 1.375
    assert qwk([0, 1, 2, 2], [0, 2, 2, 1]) == pytest.approx(7 / 11)


def test_qwk_degenerate_is_none():
    assert qwk([1, 1], [1, 1]) is None


def test_jevbench_counts_errors_as_wrong_and_splits_by_type():
    records = [
        bench_row("choice", True),
        bench_row("choice", False),
        bench_row("noul", True),
        {
            "test": "jevbench",
            "type": "noul",
            "eval_metric": "exact",
            "gold": "yes",
            "pred": None,
            "correct": False,
            "error": "ReadTimeout",
        },
    ]
    out = summary(records)
    assert "| 4 | 1 | 50.0 | 50.0 | 50.0 | n/a | 0.000 | 10 | 10 |" in out
    assert "Errors: jevbench 1" in out


def test_jevbench_score_rows_report_qwk_and_mae():
    records = [bench_row("score", True, "ordinal", "0", "0"), bench_row("score", False, "ordinal", "2", "0")]
    out = summary(records)
    assert "| 2 | 0 | 50.0 | n/a | n/a | 0.000 | 1.000 | 10 | 10 |" in out


def test_jevbench_only_run_has_no_latency_or_throughput_tables():
    out = summary([bench_row("choice", True)])
    assert "state tokens" not in out
    assert "workers" not in out


def test_provenance_renders_bullets_in_order():
    assert provenance({"b": 1, "a": "x"}) == "## Provenance\n\n- b: 1\n- a: x\n"


def vllm_row(phase: str, prompt: int, cached: int) -> dict:
    return {
        "test": "vllm",
        "phase": phase,
        "prompt_tokens": prompt,
        "cached_prompt_tokens": cached,
        "generation_tokens": 7,
        "preemptions": 2,
        "kv_peak": 0.5,
        "kv_mean": 0.25,
        "waiting_peak": 3,
        "running_peak": 4,
    }


def test_vllm_table_sets_usage_beside_prompt_computed_and_cached():
    records = [
        {
            "test": "warm",
            "phase": "warm",
            "state_tokens": 1,
            "questions": 1,
            "options": 2,
            "ms": 5,
            "input_tokens": 300,
        },
        {"test": "warmup", "phase": "warm", "input_tokens": 200},
        vllm_row("warm", 1000, 750),
        vllm_row("chat", 0, 0),
    ]
    out = summary(records)
    assert "| phase | usage input tokens | vLLM prompt tokens | computed tokens | cached % |" in out
    assert "| warm | 500 | 1000 | 250 | 75.0 | 7 | 50.0 | 25.0 | 3 | 2 |" in out
    assert "| chat | 0 | 0 | 0 | n/a | 7 | 50.0 | 25.0 | 3 | 2 |" in out


def test_vllm_table_is_omitted_without_vllm_records_and_samples_are_ignored():
    sample = {"test": "vllm_sample", "phase": "cold", "t": 0.1, "kv": 0.2, "running": 1, "waiting": 0}
    out = summary([bench_row("choice", True), sample])
    assert "vLLM prompt tokens" not in out
    assert out == summary([bench_row("choice", True)])


def test_jev_summary_reports_input_tokens_and_cost():
    records = [{**bench_row("choice", True), "phase": "jevbench", "input_tokens": 500_000}]
    assert "Jev usage: 500000 input tokens, about $0.02 at $0.042 per million." in summary(records, jev=True)
    assert "Jev usage" not in summary(records)
