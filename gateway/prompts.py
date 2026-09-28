"""Token ids for one question per row, built part by part like decider so shared prefixes match exactly."""
from dataclasses import dataclass

from gateway.labels import NARROW, Labels
from gateway.layouts import Layout
from gateway.questions import Rendered

SENTINEL = "@@USER_CONTENT@@"
CLOSE_THINKING = {"<think>\n": "</think>\n\n", "<think>": "</think>\n\n", "<|channel>thought\n": "<channel|>"}


def encode(tok, text: str) -> list[int]:
    return tok.encode(text, add_special_tokens=False)


@dataclass(frozen=True)
class ChatFrame:
    head: list[int]  # chat template before the user content
    tail: list[int]  # after it: end of user turn, assistant turn opened with thinking closed


def chat_frame(tok, layout: Layout) -> ChatFrame:
    """decider's ChatTemplate: one user turn, no system prompt, thinking off."""
    kwargs = {"enable_thinking": False} if "enable_thinking" in str(tok.chat_template) else {}
    text = tok.apply_chat_template([{"role": "user", "content": SENTINEL}], tokenize=False,
                                   add_generation_prompt=True, **kwargs)
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
    shared_len: int  # leading tokens that every row has in common

    @property
    def input_tokens(self) -> int:
        """Shared prefix counted once, like Jev counts the state once."""
        return self.shared_len + sum(len(r.ids) - self.shared_len for r in self.rows)


def option_ids(tok, layout: Layout, labels: Labels, texts: list[str]) -> list[int]:
    """Up to 10 options: one text encode. More: label token ids spliced in so every label is one token."""
    if len(texts) <= NARROW:
        return encode(tok, "".join(layout.option.format(label=labels.names[j], text=t) for j, t in enumerate(texts)))
    ids = []
    for j, text in enumerate(texts):
        ids += encode(tok, layout.option_open) + [labels.ids[j]] + encode(tok, layout.option_close.format(text=text))
    return ids


def shared_len(frame: ChatFrame, layout: Layout, parts: dict[str, list[int]]) -> int:
    """Head plus every part placed before the first per-question part."""
    n = len(frame.head)
    for part in layout.order:
        if part in ("question", "options"):
            return n
        n += len(parts[part])
    return n


def build_rows(tok, frame: ChatFrame, layout: Layout, labels: Labels, state: str,
               questions: dict[str, Rendered], perms: dict[str, list[list[int]]]) -> Batch:
    """One row per (question, option order). Parts shared by all rows are encoded once."""
    parts = {"context": encode(tok, layout.context.format(state=state))}
    if "questions" in layout.order:
        listed = "\n".join(layout.question_item.format(question=q.text) for q in questions.values())
        parts["questions"] = encode(tok, layout.questions.format(questions=listed))
    answer = encode(tok, layout.answer)
    rows = []
    for qid, q in questions.items():
        parts["question"] = encode(tok, layout.question.format(question=q.text))
        for perm in perms[qid]:
            shown = [q.options[i] for i in perm]
            parts["options"] = option_ids(tok, layout, labels, shown)
            ids = list(frame.head)
            for part in layout.order:
                ids += parts[part]
            rows.append(Row(qid, perm, ids + frame.tail + answer, labels.ids[:len(shown)]))
    return Batch(rows, shared_len(frame, layout, parts))
