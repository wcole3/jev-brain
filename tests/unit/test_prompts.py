from pathlib import Path

import pytest

from gateway.labels import label_table
from gateway.padding import Padding, newline_token
from gateway.prompts import chat_frame, encode, encode_each, image_context
from gateway.schema import ImageError
from gateway.vision import Vision
from tests.helpers import LAYOUTS, PROFILES, batch_for, image_batch, img, tokenizer_for

GOLDEN = Path(__file__).parent / "golden"
GEMMA_VISION = Vision(placeholder=(258880,), soft_tokens=lambda w, h: 100)


def assert_golden(name: str, text: str) -> None:
    path = GOLDEN / name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        pytest.fail(f"wrote new golden {path}; review it, then rerun")
    assert text == path.read_text()


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize("layout_name", sorted(LAYOUTS))
def test_prompts_match_golden(profile, layout_name):
    tok = tokenizer_for(profile)
    batch = batch_for(tok, layout_name)
    assert_golden(f"{profile}/{layout_name}.txt", "\n=====\n".join(tok.decode(r.ids) for r in batch.rows))


@pytest.mark.parametrize("layout_name", sorted(LAYOUTS))
def test_rows_share_the_reported_prefix(qwen_tok, layout_name):
    batch = batch_for(qwen_tok, layout_name)
    first = batch.rows[0].ids[: batch.shared_len]
    assert all(r.ids[: batch.shared_len] == first for r in batch.rows)
    assert batch.input_tokens == batch.shared_len + sum(len(r.ids) - batch.shared_len for r in batch.rows)


def test_prefix_sharing_by_layout(qwen_tok):
    head = len(chat_frame(qwen_tok, LAYOUTS["question_first"]).head)
    assert batch_for(qwen_tok, "question_first").shared_len == head
    assert batch_for(qwen_tok, "header").shared_len > batch_for(qwen_tok, "decider_chat").shared_len > head


def test_rows_end_at_the_answer_slot_with_one_label_per_option(qwen_tok):
    batch = batch_for(qwen_tok, "decider_chat")
    for row in batch.rows:
        assert qwen_tok.decode(row.ids[-4:]).endswith("Answer: (")
    assert [len(r.label_ids) for r in batch.rows] == [3, 3, 2]


def test_wide_choice_splices_label_tokens(qwen_tok):
    labels = label_table(qwen_tok)
    wide = {"q": {"type": "choice", "instructions": "Pick", "criteria": {f"opt{i}": None for i in range(12)}}}
    row = batch_for(qwen_tok, "decider_chat", wide).rows[0]
    for token in labels.ids[:12]:
        assert token in row.ids
    assert row.label_ids == labels.ids[:12]


def test_reversed_order_shows_options_reversed(qwen_tok):
    two = {"q": {"type": "choice", "instructions": "Pick", "criteria": {"first": None, "second": None}}}
    row = batch_for(qwen_tok, "decider_chat", two, orders=[[1, 0]]).rows[0]
    assert "(A) second\n(B) first" in qwen_tok.decode(row.ids)
    assert row.perm == [1, 0]


@pytest.mark.parametrize("profile", PROFILES)
def test_encode_each_matches_one_encode_per_text(profile):
    tok = tokenizer_for(profile)
    texts = [") billing", ")  two  spaces", ") naïve café ☕", ") \n", ') code_7: {"a": 1}', ")", ") 東京"]
    assert encode_each(tok, texts) == [encode(tok, t) for t in texts]


def test_image_context_keeps_item_order(gemma_tok):
    ctx = image_context(gemma_tok, LAYOUTS["header"], [img(), "Pick the red one", img()], GEMMA_VISION)
    expected = encode(gemma_tok, "Context:\n") + [258880] + encode(gemma_tok, "\nPick the red one\n") + [258880]
    assert ctx.ids == expected
    assert ctx.added == 2 * 101 and len(ctx.images) == 2


def test_image_rows_count_expanded_tokens(gemma_tok):
    b = image_batch(gemma_tok, "header", questions=2)  # one image, added 101
    assert b.images_shared and b.shared_tokens == b.shared_len + 101
    assert b.longest == max(len(r.ids) for r in b.rows) + 101
    assert b.input_tokens == b.unpadded_len + sum(len(r.ids) - b.shared_len for r in b.rows) + 101


def test_images_after_the_question_count_per_row(gemma_tok):
    b = image_batch(gemma_tok, "question_first", questions=2)
    once = b.unpadded_len + sum(len(r.ids) - b.shared_len for r in b.rows)
    assert not b.images_shared and b.input_tokens == once + 101 * len(b.rows)


def test_qwen_pads_on_expanded_lengths(qwen_tok):
    pad = Padding("front", 800, always=True, token=newline_token(qwen_tok))
    b = image_batch(qwen_tok, "header", questions=8, padding=pad)
    assert (b.shared_len + b.images.added) % 800 == 0


def test_middle_padding_skips_image_rows(qwen_tok):
    pad = Padding("middle", 800, always=True, token=newline_token(qwen_tok))
    b = image_batch(qwen_tok, "header", questions=8, padding=pad)
    assert b.shared_len == b.unpadded_len


def test_placeholder_text_in_an_image_request_is_refused(gemma_tok):
    with pytest.raises(ImageError, match="placeholder"):
        image_batch(gemma_tok, "header", questions=1, instructions="Is <|image|> blue?")


def test_qwen_placeholder_text_in_an_image_request_is_refused(qwen_tok):
    with pytest.raises(ImageError, match="placeholder"):
        image_batch(qwen_tok, "decider_chat", questions=1, instructions="Is <|image_pad|> blue?")


def test_the_same_image_twice_gets_two_placeholders(gemma_tok):
    ctx = image_context(gemma_tok, LAYOUTS["header"], [img(), img()], GEMMA_VISION)
    assert ctx.ids.count(258880) == 2
