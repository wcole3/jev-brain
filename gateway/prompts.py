"""Token ids for one question per row, built part by part like decider so shared prefixes match exactly."""

from dataclasses import dataclass
from itertools import takewhile

from gateway.images import Image
from gateway.labels import NARROW, Labels
from gateway.layouts import Layout
from gateway.padding import OFF, Padding
from gateway.questions import Rendered
from gateway.schema import ImageError
from gateway.vision import Vision

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
class ImageContext:
    ids: list[int]  # the context part, one placeholder per image
    images: tuple[Image, ...]  # in placeholder order
    placeholder: tuple[int, ...]
    added: int  # ids vLLM adds to a row when it expands every image


def around_images(items: list[str | Image]) -> list[str]:
    """The text before, between and after the images, items joined by newlines."""
    texts = [""]
    for n, item in enumerate(items):
        texts[-1] += ("\n" if n else "") + ("" if isinstance(item, Image) else item)
        if isinstance(item, Image):
            texts.append("")
    return texts


def image_context(tok, layout: Layout, items: list[str | Image], vision: Vision) -> ImageContext:
    """The context part with the model's placeholder ids where each image sits. User text is never split or
    formatted, so text that spells the sentinel stays text."""
    label, after = layout.context.format(state=SENTINEL).split(SENTINEL)
    texts = around_images(items)
    texts[0] = label + texts[0]
    texts[-1] += after
    pieces = encode_each(tok, texts)
    ids = list(pieces[0])
    for piece in pieces[1:]:
        ids += list(vision.placeholder) + piece
    images = tuple(item for item in items if isinstance(item, Image))
    return ImageContext(ids, images, vision.placeholder, sum(vision.added(image) for image in images))


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
    images: ImageContext | None = None
    images_shared: bool = False  # the images sit in the shared prefix

    @property
    def added(self) -> int:
        """Ids vLLM adds to each row when it expands the images."""
        return self.images.added if self.images is not None else 0

    @property
    def shared_tokens(self) -> int:
        """The shared prefix as vLLM sees it, images expanded."""
        return self.shared_len + (self.added if self.images_shared else 0)

    @property
    def input_tokens(self) -> int:
        """Shared prefix counted once, like Jev counts the state once. Padding is our overhead, so it is left out.
        Expanded images count once when shared, else once per row."""
        text = self.unpadded_len + sum(len(r.ids) - self.shared_len for r in self.rows)
        return text + self.added * (1 if self.images_shared else len(self.rows))

    @property
    def longest(self) -> int:
        return max(len(r.ids) for r in self.rows) + self.added


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
) -> tuple[list[int], list[int]] | None:
    """The shared prefix cut where the pad goes: after the chat head (front), after the last shared part (end)
    or between the context label and the state (middle). None when the layout has no such place."""
    # Spreading pads through the state was tried and dropped: 8.6% answer flips (docs/results/archive/experiments/ds-008).
    shared = shared_parts(layout)
    if mode == "front":
        return frame.head, joined(parts, shared)
    if mode == "end":
        return frame.head + joined(parts, shared), []
    if mode == "middle" and "context" in shared:
        # label and state are encoded apart around the pad, so tokens at their join may differ from one encode
        label, after = layout.context.format(state=SENTINEL).split(SENTINEL)
        at = shared.index("context")
        before = frame.head + joined(parts, shared[:at]) + encode(tok, label)
        return before, encode(tok, state + after) + joined(parts, shared[at + 1 :])
    return None


def shared_prefix(
    tok,
    frame: ChatFrame,
    layout: Layout,
    parts: dict[str, list[int]],
    state: str,
    padding: Padding,
    rows: int,
    added: int = 0,
) -> tuple[list[int], int]:
    """The ids every row starts with, padded to a block boundary when that pays, and their unpadded length.
    added: ids vLLM adds to this prefix when it expands the images in it; the pad counts them."""
    plain = frame.head + joined(parts, shared_parts(layout))
    site = pad_site(tok, frame, layout, parts, state, padding.mode) if padding.enabled else None
    if site is not None:
        before, after = site
        pad = padding.size(len(before) + len(after) + added)
        if padding.pays(rows, len(plain) + added, pad):
            return before + [padding.token] * pad + after, len(plain)
    return plain, len(plain)


def check_placeholders(prefix: list[int], rows: list[Row], images: ImageContext) -> None:
    """Every row must hold exactly the images' placeholder ids: text that spells one would mislead vLLM."""
    for token in set(images.placeholder):
        want = len(images.images) * images.placeholder.count(token)
        in_prefix = prefix.count(token)
        if any(in_prefix + row.ids[len(prefix) :].count(token) != want for row in rows):
            raise ImageError("text must not contain image placeholder tokens")


def build_rows(
    tok,
    frame: ChatFrame,
    layout: Layout,
    labels: Labels,
    state: str,
    questions: dict[str, Rendered],
    perms: dict[str, list[list[int]]],
    padding: Padding = OFF,
    pad_rows: int | None = None,
    images: ImageContext | None = None,
) -> Batch:
    """One row per (question, option order). Parts shared by all rows are encoded once.
    pad_rows, when given, is the row count the padding decision assumes instead of the real one."""
    context = images.ids if images is not None else encode(tok, layout.context.format(state=state))
    parts = {"context": context}
    if "questions" in layout.order:
        listed = "\n".join(layout.question_item.format(question=q.text) for q in questions.values())
        parts["questions"] = encode(tok, layout.questions.format(questions=listed))
    n_rows = sum(len(perms[qid]) for qid in questions) if pad_rows is None else pad_rows
    images_shared = images is not None and "context" in shared_parts(layout)
    if images is not None and padding.mode == "middle":
        padding = OFF  # middle cuts the state text around the pad, and image rows have none
    added = images.added if images_shared else 0
    prefix, unpadded_len = shared_prefix(tok, frame, layout, parts, state, padding, n_rows, added)
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
    if images is not None:
        check_placeholders(prefix, rows, images)
    return Batch(rows, len(prefix), unpadded_len, images, images_shared)
