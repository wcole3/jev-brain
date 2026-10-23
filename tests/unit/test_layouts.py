import hashlib

import pytest

from gateway.layouts import LABEL_SETS, PROMPTS_DIR, load_layout, load_layouts


def test_shipped_layouts_load():
    layouts = load_layouts()
    assert set(layouts) == {"blurb_header", "blurb_header_reread", "decider_chat", "header", "question_first"}
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


EXPERIMENTS = PROMPTS_DIR / "experiments"


def test_image_label_needs_n(tmp_path):
    bad = (PROMPTS_DIR / "header.toml").read_text() + 'image_label = "Image:\\n"\n'
    (tmp_path / "bad.toml").write_text(bad)
    with pytest.raises(ValueError, match="image_label"):
        load_layout(tmp_path / "bad.toml")


@pytest.mark.parametrize("label", ["Image {n} of {total}:\\n", "Image {n} {0}:\\n", "Image {n} {:\\n"])
def test_image_label_formats_with_n_only(tmp_path, label):
    bad = (PROMPTS_DIR / "header.toml").read_text() + f'image_label = "{label}"\n'
    (tmp_path / "bad.toml").write_text(bad)
    with pytest.raises(ValueError, match="bad.toml: image_label must format with {n} only"):
        load_layout(tmp_path / "bad.toml")


def test_gateway_does_not_load_experiment_layouts():
    assert sorted(load_layouts()) == ["blurb_header", "blurb_header_reread", "decider_chat", "header", "question_first"]


def test_experiment_layouts_load_and_share_the_header_prefix_rule():
    from gateway.prompts import shared_parts

    layouts = load_layouts(EXPERIMENTS)
    assert {"header-imgfirst", "header-imgfirst-worded", "header-worded"} <= set(layouts)
    assert shared_parts(layouts["header-imgfirst"]) == ["context", "questions"]
    assert shared_parts(layouts["header-worded"]) == ["questions", "context"]
    assert layouts["header-worded"].image_label == "Image {n}:\n"
    assert layouts["header-imgfirst"].image_label == ""


def test_served_layouts_have_no_new_keys_and_same_hash():
    for name, layout in load_layouts().items():
        assert layout.labels == "letters" and layout.answer_label == "{label}"
        assert layout.sha256 == hashlib.sha256((PROMPTS_DIR / f"{name}.toml").read_bytes()).hexdigest()


def test_unknown_label_set_refused(tmp_path):
    bad = 'labels = "emoji"\n' + (PROMPTS_DIR / "header.toml").read_text()
    (tmp_path / "bad.toml").write_text(bad)
    with pytest.raises(ValueError, match="labels must be one of") as e:
        load_layout(tmp_path / "bad.toml")
    assert str(LABEL_SETS) in str(e.value)


def test_answer_label_needs_label(tmp_path):
    bad = 'answer_label = "x"\n' + (PROMPTS_DIR / "header.toml").read_text()
    (tmp_path / "bad.toml").write_text(bad)
    with pytest.raises(ValueError, match="answer_label needs"):
        load_layout(tmp_path / "bad.toml")
