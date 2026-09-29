from scripts.bench import summary


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
