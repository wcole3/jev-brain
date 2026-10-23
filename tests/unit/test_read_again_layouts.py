from dataclasses import asdict

import pytest

from gateway.layouts import PROMPTS_DIR, load_layout
from gateway.padding import Padding, newline_token
from gateway.prompts import chat_frame, encode
from tests.helpers import HLE, LAYOUTS, ORDERS, STATE, batch_for, image_batch

AGAIN = "\n\nHmm, I should read that again before answer\n\n"
ARMS = {"blurb-header-again-b": "B", "blurb-header-again-d": "D", "blurb-header-again-bd": "BD"}


def experiment(name):
    return load_layout(PROMPTS_DIR / "experiments" / f"{name}.toml")


@pytest.fixture
def with_arms(monkeypatch):
    for name in ARMS:
        monkeypatch.setitem(LAYOUTS, name, experiment(name))


def pieces(tok, batch):
    """The shared prefix after the chat head, and each row after the prefix without the chat tail and answer."""
    frame = chat_frame(tok, LAYOUTS["blurb_header"])
    end = len(frame.tail) + len(encode(tok, "Answer: ("))
    return batch.rows[0].ids[len(frame.head) : batch.shared_len], [r.ids[batch.shared_len : -end] for r in batch.rows]


@pytest.mark.parametrize("name", ARMS)
def test_arms_differ_from_blurb_header_only_by_order_and_again(name):
    arm, served = asdict(experiment(name)), asdict(LAYOUTS["blurb_header"])
    for d in (arm, served):
        del d["name"], d["sha256"], d["order"]
    assert (arm.pop("again"), served.pop("again")) == (AGAIN, "")
    assert arm == served


@pytest.mark.parametrize("name", ARMS)
@pytest.mark.parametrize("tok_name", ["qwen_tok", "gemma_tok"])
def test_arm_rows_stack_the_served_parts(name, tok_name, request, with_arms):
    tok = request.getfixturevalue(tok_name)
    again = encode(tok, AGAIN)
    served, arm = batch_for(tok, "blurb_header", HLE, ORDERS), batch_for(tok, name, HLE, ORDERS)
    block, asked = pieces(tok, served)
    shared, arm_asked = pieces(tok, arm)
    tight = encode(tok, AGAIN.removesuffix("\n\n"))  # the question part opens on its own blank line
    assert shared == (block + again + block if "B" in ARMS[name] else block)
    assert arm_asked == [a + tight + a if "D" in ARMS[name] else a for a in asked]
    assert all(r.ids[: arm.shared_len] == arm.rows[0].ids[: arm.shared_len] for r in arm.rows)
    assert [(r.perm, r.label_ids) for r in arm.rows] == [(r.perm, r.label_ids) for r in served.rows]


def test_read_again_text(gemma_tok, with_arms):
    row = batch_for(gemma_tok, "blurb-header-again-bd", {"hle": HLE["hle"]}, [[4, 3, 2, 1, 0]]).rows[0]
    text = gemma_tok.decode(row.ids)
    block = text[text.index("You will be asked") : text.index(AGAIN)]
    assert block.endswith("Context:\n" + STATE) and text.count(block + AGAIN + block + "\n\nQuestion:") == 1
    tight = AGAIN.removesuffix("\n\n")
    asked = text[text.index("\n\nQuestion:") : text.rindex(tight)]
    assert asked.endswith("\n(E) A: Increase temperature")
    assert text.count(asked + tight + asked + "<turn|>") == 1 and "\n\n\n" not in text
    assert "\nOptions:\n(A) E: None of the above\n(B) D: Decrease" in asked


def test_padded_arms_share_one_prefix(qwen_tok, with_arms):
    pad = Padding("front", 800, always=True, token=newline_token(qwen_tok))
    for name in ARMS:
        batch = batch_for(qwen_tok, name, HLE, ORDERS, padding=pad)
        assert batch.shared_len % 800 == 0
        assert all(r.ids[: batch.shared_len] == batch.rows[0].ids[: batch.shared_len] for r in batch.rows)


def test_middle_padding_skips_a_repeated_context(qwen_tok, with_arms):
    pad = Padding("middle", 800, always=True, token=newline_token(qwen_tok))
    padded = batch_for(qwen_tok, "blurb-header-again-b", padding=pad)
    assert padded.shared_len == padded.unpadded_len
    assert batch_for(qwen_tok, "blurb-header-again-d", padding=pad).shared_len % 800 == 0


def test_images_refuse_a_repeated_context(gemma_tok, with_arms):
    with pytest.raises(ValueError, match="images are shown once"):
        image_batch(gemma_tok, "blurb-header-again-b")
    assert image_batch(gemma_tok, "blurb-header-again-d").images_shared


@pytest.mark.parametrize(
    ("order", "extra", "message"),
    [
        ('["questions", "context", "context", "question", "options"]', "", "repeat only"),
        ('["context", "again", "context", "question", "options"]', "", "again text"),
        ('["context", "question", "options", "again", "question", "options"]', 'again = ""\n', "again text"),
    ],
)
def test_bad_repeats_refused(tmp_path, order, extra, message):
    text = (
        (PROMPTS_DIR / "blurb_header.toml")
        .read_text()
        .replace('["questions", "context", "question", "options"]', order)
    )
    (tmp_path / "bad.toml").write_text(text + extra)
    with pytest.raises(ValueError, match=message):
        load_layout(tmp_path / "bad.toml")
