import pytest

from gateway.config import Settings
from gateway.padding import OFF, Padding, load_padding, newline_token
from gateway.prompts import chat_frame, encode
from tests.helpers import LAYOUTS, PROFILES, STATE, batch_for, tokenizer_for

BLOCK = 32  # small, so the short quickstart prefix (23 tokens) pads to one block
ONE = {"q": {"type": "noul", "instructions": "Is it urgent?"}}


def padding(tok, mode="end", block=BLOCK, always=False) -> Padding:
    return Padding(mode, block, always, newline_token(tok))


def settings(**kw) -> Settings:
    return Settings(profile="p", hf_model="m", hf_revision="r", served_model="s", max_model_len=1024, **kw)


def pad_position(tok, layout_name: str, mode: str, plain_shared_len: int) -> int:
    """Where each placement puts the pad in the quickstart rows (the state ends the shared prefix)."""
    return {
        "front": len(chat_frame(tok, LAYOUTS[layout_name]).head),
        "end": plain_shared_len,
        "middle": plain_shared_len - len(encode(tok, STATE)),
    }[mode]


@pytest.mark.parametrize("layout_name", ["decider_chat", "header"])
@pytest.mark.parametrize("mode", ["end", "front", "middle"])
def test_each_placement_pads_the_shared_prefix_to_a_block(qwen_tok, layout_name, mode):
    plain = batch_for(qwen_tok, layout_name)
    padded = batch_for(qwen_tok, layout_name, padding=padding(qwen_tok, mode))
    pad = padded.shared_len - plain.shared_len
    assert padded.shared_len % BLOCK == 0 and pad > 0
    shared = padded.rows[0].ids[: padded.shared_len]
    assert all(r.ids[: padded.shared_len] == shared for r in padded.rows)
    at = pad_position(qwen_tok, layout_name, mode, plain.shared_len)
    for p, q in zip(plain.rows, padded.rows, strict=True):
        assert q.ids[at : at + pad] == [newline_token(qwen_tok)] * pad
        assert q.ids[:at] + q.ids[at + pad :] == p.ids  # the ids on either side are unchanged
    assert padded.unpadded_len == plain.shared_len
    assert padded.input_tokens == plain.input_tokens


@pytest.mark.parametrize(
    ("mode", "before", "after"),
    [
        ("front", "<|im_start|>user\n", "Context:\n"),
        ("end", STATE, "\n\nQuestion:"),
        ("middle", "Context:\n", STATE),
    ],
)
def test_pad_sits_between_the_expected_texts(qwen_tok, mode, before, after):
    plain = batch_for(qwen_tok, "decider_chat")
    padded = batch_for(qwen_tok, "decider_chat", padding=padding(qwen_tok, mode))
    at, pad = pad_position(qwen_tok, "decider_chat", mode, plain.shared_len), padded.shared_len - plain.shared_len
    row = padded.rows[0].ids
    assert qwen_tok.decode(row[:at]).endswith(before)
    assert qwen_tok.decode(row[at + pad :]).startswith(after)


def test_single_question_is_not_padded(qwen_tok):
    plain = batch_for(qwen_tok, "decider_chat", ONE)
    assert batch_for(qwen_tok, "decider_chat", ONE, padding=padding(qwen_tok)) == plain


def test_padding_that_costs_more_than_it_saves_is_skipped(qwen_tok):
    # two later rows would each save 23 tokens; padding 23 to 784 costs 761
    padded = batch_for(qwen_tok, "decider_chat", padding=padding(qwen_tok, block=784))
    assert padded == batch_for(qwen_tok, "decider_chat")


def test_block_zero_never_pads(qwen_tok):
    padded = batch_for(qwen_tok, "decider_chat", padding=padding(qwen_tok, block=0, always=True))
    assert padded == batch_for(qwen_tok, "decider_chat")


def test_always_pads_a_single_row(qwen_tok):
    plain = batch_for(qwen_tok, "decider_chat", ONE)
    padded = batch_for(qwen_tok, "decider_chat", ONE, padding=padding(qwen_tok, always=True))
    assert padded.shared_len % BLOCK == 0 and padded.shared_len > plain.shared_len
    assert padded.input_tokens == plain.input_tokens


def test_middle_needs_a_shared_context(qwen_tok):
    """question_first puts the state after each question, so no shared prefix holds it."""
    padded = batch_for(qwen_tok, "question_first", padding=padding(qwen_tok, "middle", always=True))
    assert padded == batch_for(qwen_tok, "question_first")


def test_padding_pays_when_later_rows_save_more_than_the_pad():
    p = Padding("end", 784)
    assert p.size(2064) == 288
    assert p.pays(rows=16, unpadded_len=2064, pad=288)  # 15 rows stop recomputing 496 tokens each
    assert not p.pays(rows=1, unpadded_len=2064, pad=288)
    assert not p.pays(rows=2, unpadded_len=790, pad=778)


@pytest.mark.parametrize("profile", PROFILES)
def test_newline_is_one_token_for_every_profile(profile):
    tok = tokenizer_for(profile)
    assert [newline_token(tok)] == tok.encode("\n", add_special_tokens=False)


class TwoTokenNewline:
    def encode(self, text, add_special_tokens=False):
        return [1, 2]


def test_padding_refuses_a_newline_that_is_not_one_token():
    with pytest.raises(ValueError, match="one token"):
        load_padding(settings(prefix_pad="end", prefix_block=784), TwoTokenNewline())


def test_padding_off_needs_no_newline_check():
    assert load_padding(settings(), TwoTokenNewline()) == OFF
    assert not load_padding(settings(prefix_pad="end"), TwoTokenNewline()).enabled  # block 0


@pytest.mark.parametrize("bad", [{"prefix_pad": "left"}, {"prefix_pad": "end", "prefix_block": -1}])
def test_padding_refuses_bad_settings(qwen_tok, bad):
    with pytest.raises(ValueError, match="PREFIX_PAD"):
        load_padding(settings(**bad), qwen_tok)
