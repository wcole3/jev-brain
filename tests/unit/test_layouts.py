import pytest

from gateway.layouts import PROMPTS_DIR, load_layout, load_layouts


def test_shipped_layouts_load():
    layouts = load_layouts()
    assert set(layouts) == {"decider_chat", "header", "question_first"}
    assert layouts["decider_chat"].order == ("context", "question", "options")
    assert layouts["header"].order == ("questions", "context", "question", "options")
    assert layouts["question_first"].order == ("question", "options", "context")


def test_decider_chat_text_matches_decider():
    d = load_layouts()["decider_chat"]
    assert d.context.format(state="S") == "Context:\nS"
    assert d.question.format(question="Q") == "\n\nQuestion: Q\nOptions:"
    assert (d.option_open, d.option_close) == ("\n(", ") {text}")
    assert d.answer == "Answer: ("
    assert d.described.format(name="billing", description="Payments") == "billing: Payments"
    assert d.noul == ("no", "yes")
    assert d.noul_question == "Which answer fits the context?"


def test_missing_placeholder_is_rejected(tmp_path):
    bad = (PROMPTS_DIR / "decider_chat.toml").read_text().replace("{state}", "")
    (tmp_path / "bad.toml").write_text(bad)
    with pytest.raises(ValueError, match="state"):
        load_layout(tmp_path / "bad.toml")


def test_hash_follows_the_text(tmp_path):
    text = (PROMPTS_DIR / "decider_chat.toml").read_text()
    (tmp_path / "a.toml").write_text(text)
    (tmp_path / "b.toml").write_text(text.replace("Question:", "Q:"))
    assert load_layout(tmp_path / "a.toml").sha256 != load_layout(tmp_path / "b.toml").sha256
