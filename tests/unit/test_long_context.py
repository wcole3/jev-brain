from scripts.long_context import INSTRUCTION, build_prompt, render


class FakeTokenizer:
    """One token per whitespace-separated word."""

    def __call__(self, texts, add_special_tokens=False):
        return {"input_ids": [[hash(w) for w in t.split()] for t in texts]}

    def decode(self, ids):
        return " ".join("w" for _ in ids)


def test_prompt_hits_target_within_margin():
    filler = " ".join(f"word{i}" for i in range(37))
    prompt, tokens = build_prompt(FakeTokenizer(), filler, target=1000, margin=20)
    assert 1000 - 20 - 5 <= tokens <= 1000
    assert prompt.endswith(INSTRUCTION)


def test_summary_renders_from_raw():
    raw = {
        "long": {"prompt_tokens": 199000, "completion_tokens": 40, "ttft_s": 123.4, "decode_tok_s": 17.5},
        "idle": {"chat": [{"ttft_ms": 50.0}], "decision": [{"ms": 80.0}]},
        "during": {"chat": [{"error": "ReadTimeout"}], "decision": [{"ms": 900.0}, {"ms": 1100.0}]},
    }
    text = render(raw, {"profile": "p", "max_model_len": 262144, "systemone_max_len": 32768})
    assert "- max_model_len: 262144" in text
    assert "| 199000 | 40 | 123.4 | 17.5 |" in text
    assert "| 50 / 50 / 1 |" in text
    assert "no samples (1 errors)" in text
    assert "1000 / 1100 / 2" in text
