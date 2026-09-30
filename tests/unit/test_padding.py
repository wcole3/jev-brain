from itertools import pairwise

import pytest

from gateway.config import Settings
from gateway.padding import OFF, Padding, load_padding, newline_token
from gateway.prompts import chat_frame, encode
from gateway.spread import pad_points, word_starts
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


# one line, so no "\n" in the state is mistaken for a pad; ids like "customer17" split mid-word
LONG_STATE = " ".join(f"Order {i} for customer{i} failed with code E{i * 7} again." for i in range(300))


def spread_pads(tok, layout_name: str, state: str, block: int):
    """Plain and spread batches, the padded state ids and the indexes of the pads in them."""
    plain = batch_for(tok, layout_name, state=state)
    padded = batch_for(tok, layout_name, padding=padding(tok, "spread", block, always=True), state=state)
    at = plain.shared_len - len(encode(tok, state))  # the state ends the shared prefix
    state_ids, seg = plain.rows[0].ids[at : plain.shared_len], padded.rows[0].ids[at : padded.shared_len]
    pads, j = [], 0
    for i, t in enumerate(seg):
        if j < len(state_ids) and t == state_ids[j]:
            j += 1
        else:
            pads.append(i)
    assert j == len(state_ids) and all(seg[i] == newline_token(tok) for i in pads)
    return plain, padded, seg, pads


def splits_no_word(tok, seg: list[int], pads: list[int]) -> bool:
    text = tok.batch_decode([[t] for t in seg])
    words = [i for i in range(len(seg)) if i not in set(pads)]
    for i in pads:
        prev, nxt = max(w for w in words if w < i), min(w for w in words if w > i)
        if not (text[nxt][:1].isspace() or text[prev].endswith("\n")):
            return False
    return True


@pytest.mark.parametrize("layout_name", ["decider_chat", "header"])
@pytest.mark.parametrize("state", [STATE, LONG_STATE])
def test_spread_pads_the_shared_prefix_between_words(qwen_tok, layout_name, state):
    block = 32 if state == STATE else batch_for(qwen_tok, layout_name, state=state).shared_len + 200
    plain, padded, seg, pads = spread_pads(qwen_tok, layout_name, state, block)
    assert padded.shared_len % block == 0
    assert len(pads) == padded.shared_len - plain.shared_len > 0
    shared = padded.rows[0].ids[: padded.shared_len]
    assert all(r.ids[: padded.shared_len] == shared for r in padded.rows)
    for p, q in zip(plain.rows, padded.rows, strict=True):
        assert q.ids[padded.shared_len :] == p.ids[plain.shared_len :]
    assert len(set(pads)) == len(pads) and 0 < pads[0] and pads[-1] < len(seg) - 1
    assert splits_no_word(qwen_tok, seg, pads)
    assert padded.unpadded_len == plain.shared_len
    assert padded.input_tokens == plain.input_tokens


def test_spread_spaces_the_pads_evenly(qwen_tok):
    block = batch_for(qwen_tok, "decider_chat", state=LONG_STATE).shared_len + 200
    _, _, seg, pads = spread_pads(qwen_tok, "decider_chat", LONG_STATE, block)
    gaps = [b - a for a, b in pairwise(pads)]
    assert len(pads) == 200 and max(gaps) <= 2 * len(seg) / len(pads)


def test_spread_falls_back_to_even_spacing_without_word_starts(qwen_tok):
    assert pad_points(12, 3, []) == [2, 6, 10]
    state = "a1b2c3d4" * 40
    assert word_starts(qwen_tok, encode(qwen_tok, state)) == []
    _, _, seg, pads = spread_pads(qwen_tok, "decider_chat", state, 64)
    gaps = [b - a for a, b in pairwise(pads)]
    assert len(pads) > 1 and max(gaps) - min(gaps) <= 1
    assert not splits_no_word(qwen_tok, seg, pads)  # so the word check can fail


def test_spread_stacks_pads_only_when_word_starts_run_out():
    assert pad_points(100, 3, [10, 50, 90]) == [10, 50, 90]
    assert pad_points(100, 5, [10, 50]) == [10, 10, 10, 50, 50]
    assert pad_points(100, 3, [10, 11, 12, 90]) == [11, 12, 90]  # distinct, though crowded


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


@pytest.mark.parametrize("mode", ["middle", "spread"])
def test_middle_and_spread_need_a_shared_context(qwen_tok, mode):
    """question_first puts the state after each question, so no shared prefix holds it."""
    padded = batch_for(qwen_tok, "question_first", padding=padding(qwen_tok, mode, always=True))
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
