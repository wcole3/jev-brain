"""Token ids for one question per row, built part by part like decider so shared prefixes match exactly."""

from dataclasses import dataclass
from itertools import takewhile

from gateway.labels import NARROW, Labels
from gateway.layouts import Layout
from gateway.padding import OFF, Padding
from gateway.questions import Rendered
from gateway.spread import spread

SENTINEL = "@@USER_CONTENT@@"
CLOSE_THINKING = {"<think>\n": "</think>\n\n", "<think>": "</think>\n\n", "<|channel>thought\n": "<channel|>"}


def encode(tok, text: str) -> list[int]:
    return tok.encode(text, add_special_tokens=False)


def encode_each(tok, texts: list[str]) -> list[list[int]]:
    """Each text encoded on its own, in one tokenizer call (per-call overhead dominates short texts)."""
    return tok(texts, add_special_tokens=False)["input_ids"]


@dataclass(frozen=True)
class ChatFrame:
    head: list[int]  # chat template before the user content
    tail: list[int]  # after it: end of user turn, assistant turn opened with thinking closed


def chat_frame(tok, layout: Layout) -> ChatFrame:
    """decider's ChatTemplate: one user turn, no system prompt, thinking off."""
    kwargs = {"enable_thinking": False} if "enable_thinking" in str(tok.chat_template) else {}
    text = tok.apply_chat_template(
        [{"role": "user", "content": SENTINEL}], tokenize=False, add_generation_prompt=True, **kwargs
    )
    head, tail = text.split(SENTINEL)
    for opened, closed in CLOSE_THINKING.items():
        if tail.endswith(opened):
            tail += closed
            break
    frame = ChatFrame(encode(tok, head), encode(tok, tail))
    if encode(tok, tail + layout.answer) != frame.tail + encode(tok, layout.answer):
        raise ValueError(f"layout {layout.name}: the chat template tail merges with the answer slot")
    return frame


@dataclass(frozen=True)
class Row:
    question_id: str
    perm: list[int]  # perm[j] = index of the caller's option shown at position j
    ids: list[int]  # the full prompt, ending at the answer slot
    label_ids: list[int]  # tokens to read at the last position, one per shown option


@dataclass(frozen=True)
class Batch:
    rows: list[Row]
    shared_len: int  # leading tokens that every row has in common, pad included
    unpadded_len: int  # the same prefix as it is without padding

    @property
    def input_tokens(self) -> int:
        """Shared prefix counted once, like Jev counts the state once. Padding is our overhead, so it is left out."""
        return self.unpadded_len + sum(len(r.ids) - self.shared_len for r in self.rows)

    @property
    def longest(self) -> int:
        return max(len(r.ids) for r in self.rows)


def option_ids(tok, layout: Layout, labels: Labels, texts: list[str]) -> list[int]:
    """Up to 10 options: one text encode. More: label token ids spliced in so every label is one token."""
    if len(texts) <= NARROW:
        return encode(tok, "".join(layout.option.format(label=labels.names[j], text=t) for j, t in enumerate(texts)))
    opening = encode(tok, layout.option_open)
    closings = encode_each(tok, [layout.option_close.format(text=text) for text in texts])
    ids = []
    for j, closing in enumerate(closings):
        ids += opening + [labels.ids[j]] + closing
    return ids


def shared_parts(layout: Layout) -> list[str]:
    """The parts placed before the first per-question part: every row starts with the head and these."""
    return list(takewhile(lambda part: part not in ("question", "options"), layout.order))


def joined(parts: dict[str, list[int]], names: list[str]) -> list[int]:
    return [i for name in names for i in parts[name]]


def pad_site(
    tok, frame: ChatFrame, layout: Layout, parts: dict[str, list[int]], state: str, mode: str
) -> tuple[list[int], list[int], list[int]] | None:
    """The shared prefix cut in three, the pad spread through the middle piece (one run where it is empty): after the
    chat head (front), after the last shared part (end), before the state (middle) or through it (spread)."""
    shared = shared_parts(layout)
    if mode == "front":
        return frame.head, [], joined(parts, shared)
    if mode == "end":
        return frame.head + joined(parts, shared), [], []
    if mode in ("middle", "spread") and "context" in shared:
        # label and state are encoded apart around the pad, so tokens at their join may differ from one encode
        label, after = layout.context.format(state=SENTINEL).split(SENTINEL)
        at = shared.index("context")
        before = frame.head + joined(parts, shared[:at]) + encode(tok, label)
        state_ids, rest = encode(tok, state + after), joined(parts, shared[at + 1 :])
        return (before, [], state_ids + rest) if mode == "middle" else (before, state_ids, rest)
    return None


def shared_prefix(
    tok, frame: ChatFrame, layout: Layout, parts: dict[str, list[int]], state: str, padding: Padding, rows: int
) -> tuple[list[int], int]:
    """The ids every row starts with, padded to a block boundary when that pays, and their unpadded length."""
    plain = frame.head + joined(parts, shared_parts(layout))
    site = pad_site(tok, frame, layout, parts, state, padding.mode) if padding.enabled else None
    if site is not None:
        before, middle, after = site
        pad = padding.size(len(before) + len(middle) + len(after))
        if padding.pays(rows, len(plain), pad):
            return before + spread(tok, middle, pad, padding.token) + after, len(plain)
    return plain, len(plain)


def build_rows(
    tok,
    frame: ChatFrame,
    layout: Layout,
    labels: Labels,
    state: str,
    questions: dict[str, Rendered],
    perms: dict[str, list[list[int]]],
    padding: Padding = OFF,
) -> Batch:
    """One row per (question, option order). Parts shared by all rows are encoded once."""
    parts = {"context": encode(tok, layout.context.format(state=state))}
    if "questions" in layout.order:
        listed = "\n".join(layout.question_item.format(question=q.text) for q in questions.values())
        parts["questions"] = encode(tok, layout.questions.format(questions=listed))
    n_rows = sum(len(perms[qid]) for qid in questions)
    prefix, unpadded_len = shared_prefix(tok, frame, layout, parts, state, padding, n_rows)
    rest = layout.order[len(shared_parts(layout)) :]  # the parts after the shared prefix
    answer = encode(tok, layout.answer)
    rows = []
    for qid, q in questions.items():
        parts["question"] = encode(tok, layout.question.format(question=q.text))
        for perm in perms[qid]:
            shown = [q.options[i] for i in perm]
            parts["options"] = option_ids(tok, layout, labels, shown)
            ids = list(prefix)
            for part in rest:
                ids += parts[part]
            rows.append(Row(qid, perm, ids + frame.tail + answer, labels.ids[: len(shown)]))
    return Batch(rows, len(prefix), unpadded_len)
