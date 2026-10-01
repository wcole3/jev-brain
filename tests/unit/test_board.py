from scripts import board


def test_every_profile_has_a_matching_entry_and_qwen36_has_the_parity_gate():
    assert set(board.MATCHES) == {"qwen3.6-27b", "qwen3.8-27b", "gemma-4-31b"}
    assert all(e in board.BOARD for entries in board.MATCHES.values() for e in entries)
    assert board.PARITY["qwen3.6-27b"] == ("decider-chat-qwen3.6-27b", 1.5)


def test_comparison_flags_a_parity_miss():
    lines = board.comparison("qwen3.6-27b", {"index": 48.0, "ece": 0.03, "median_ms": 80.0, "coverage": 0.99})
    assert any("MISS" in line for line in lines)
    ok = board.comparison("qwen3.6-27b", {"index": 51.0, "ece": 0.03, "median_ms": 80.0, "coverage": 0.99})
    assert any("pass" in line for line in ok)


def test_subset_and_incomplete_runs_get_no_parity_verdict():
    ours = {"index": 51.0, "ece": 0.03, "median_ms": 80.0, "coverage": 0.99}
    for reason in ("subset run", "run incomplete: 9000 rows"):
        parity = next(x for x in board.comparison("qwen3.6-27b", ours, reason) if x.startswith("Parity gate"))
        assert f"not judged ({reason})" in parity and "pass" not in parity and "MISS" not in parity
