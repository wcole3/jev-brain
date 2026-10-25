"""Token ids for one question per row, built part by part like decider so shared prefixes match exactly."""

from dataclasses import dataclass, replace
from itertools import takewhile

from gateway.images import Image
from gateway.labels import NARROW, Labels, question_labels
from gateway.layouts import PER_QUESTION, Layout
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
    """decider's ChatTemplate: one user turn (after the layout's system turn, if any), thinking off."""
    kwargs = {"enable_thinking": False} if "enable_thinking" in str(tok.chat_template) else {}
    system = [{"role": "system", "content": layout.system}] if layout.system else []
    text = tok.apply_chat_template(
        [*system, {"role": "user", "content": SENTINEL}], tokenize=False, add_generation_prompt=True, **kwargs
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
    count = len(texts) - 1
    labels = [layout.image_label.format(n=k) for k in range(1, count + 1)] if layout.image_label else []
    pieces = encode_each(tok, texts + labels)
    ids = list(pieces[0])
    for k, piece in enumerate(pieces[1 : count + 1]):
        ids += (list(pieces[count + 1 + k]) if labels else []) + list(vision.placeholder) + piece
    images = tuple(item for item in items if isinstance(item, Image))
    return ImageContext(ids, images, vision.placeholder, sum(vision.added(image) for image in images))


@dataclass(frozen=True)
class Row:
    question_id: str
    perm: list[int]  # perm[j] = index of the caller's option shown at position j
    ids: list[int]  # the full prompt, ending at the answer slot
    label_ids: list[int]  # tokens to read at the last position, one per shown option
    label_tag: str = "set"  # "fallback" when an experiment set could not label this question


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


def spliced(tok, layout: Layout, label_ids: list[int], texts: list[str]) -> list[int]:
    """Option lines with each label's token id spliced in, so every label is one token."""
    opening = encode(tok, layout.option_open)
    closings = encode_each(tok, [layout.option_close.format(text=text) for text in texts])
    return [i for label, closing in zip(label_ids, closings) for i in opening + [label] + closing]


def option_ids(tok, layout: Layout, labels: Labels, texts: list[str]) -> list[int]:
    """Up to 10 options: one text encode. More: label token ids spliced in so every label is one token."""
    if len(texts) <= NARROW:
        return encode(tok, "".join(layout.option.format(label=labels.names[j], text=t) for j, t in enumerate(texts)))
    return spliced(tok, layout, labels.ids, texts)


def options_and_reads(tok, layout: Layout, labels: Labels, texts: list[str]) -> tuple[list[int], list[int], str]:
    """The options part, the ids to read and the label tag. Experiment sets encode each option line on its own."""
    if layout.labels == "letters":
        return option_ids(tok, layout, labels, texts), labels.ids[: len(texts)], "set"
    names, reads, tag = question_labels(tok, layout, labels, texts)
    if layout.labels == "unused" and tag == "set":
        return spliced(tok, layout, reads, texts), reads, tag
    lines = encode_each(tok, [layout.option.format(label=n, text=t) for n, t in zip(names, texts)])
    return [i for line in lines for i in line], reads, tag


def opens_blank(layout: Layout, part: str) -> bool:
    template = {"options": layout.option, "plain_options": layout.plain_option}.get(part) or getattr(layout, part)
    return template.startswith("\n\n")


def spelled_order(layout: Layout) -> list[str]:
    """The order, with each again joiner before a part that opens on a blank line in its tight form."""
    after = [*layout.order[1:], None]
    return ["again-tight" if p == "again" and n and opens_blank(layout, n) else p for p, n in zip(layout.order, after)]


def shared_parts(layout: Layout) -> list[str]:
    """The parts placed before the first per-question part: every row starts with the head and these."""
    return list(takewhile(lambda part: part not in PER_QUESTION, spelled_order(layout)))


def reads_twice(mode: str, questions: int, images: bool) -> bool:
    """A read-twice gate for one request: always, or one-question with exactly one question."""
    if images:  # images are shown once, and image requests keep the layout they were measured with
        return False
    return mode == "always" or (mode == "one-question" and questions == 1)


def as_read(layout: Layout, questions: int, images: bool) -> Layout:
    """The layout one request reads: the shared parts and/or each row's question and options again after the joiner."""
    order = layout.order
    if reads_twice(layout.read_question_twice, questions, images):
        first = next(i for i, part in enumerate(order) if part in PER_QUESTION)
        order = (*order, "again", *order[first:])
    if reads_twice(layout.read_twice, questions, images):
        order = (*shared_parts(layout), "again", *order)
    return layout if order == layout.order else replace(layout, order=order)


def joined(parts: dict[str, list[int]], names: list[str]) -> list[int]:
    return [i for name in names for i in parts[name]]


def pad_site(
    tok, frame: ChatFrame, layout: Layout, parts: dict[str, list[int]], state: str, mode: str
) -> tuple[list[int], list[int]] | None:
    """The shared prefix cut where the pad goes: after the chat head (front), after the last shared part (end)
    or between the context label and the state (middle). None when the layout has no such place: middle has
    none when the context is read twice."""
    # Spreading pads through the state was tried and dropped: 8.6% answer flips (docs/results/archive/experiments/ds-008).
    shared = shared_parts(layout)
    if mode == "front":
        return frame.head, joined(parts, shared)
    if mode == "end":
        return frame.head + joined(parts, shared), []
    if mode == "middle" and shared.count("context") == 1:
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
    layout = as_read(layout, len(questions), images is not None)
    if images is not None and layout.order.count("context") > 1:
        raise ValueError(f"layout {layout.name}: images are shown once, and this layout repeats the context")
    context = images.ids if images is not None else encode(tok, layout.context.format(state=state))
    parts = {"context": context}
    if "again" in layout.order:
        parts["again"] = encode(tok, layout.again)
        parts["again-tight"] = encode(tok, layout.again.removesuffix("\n\n"))  # the next part brings its own
    if "questions" in layout.order:
        listed = "\n".join(layout.question_item.format(question=q.text) for q in questions.values())
        parts["questions"] = encode(tok, layout.questions.format(questions=listed))
    n_rows = sum(len(perms[qid]) for qid in questions) if pad_rows is None else pad_rows
    images_shared = images is not None and "context" in shared_parts(layout)
    if images is not None and padding.mode == "middle":
        padding = OFF  # middle cuts the state text around the pad, and image rows have none
    added = images.added if images_shared else 0
    prefix, unpadded_len = shared_prefix(tok, frame, layout, parts, state, padding, n_rows, added)
    rest = spelled_order(layout)[len(shared_parts(layout)) :]  # the parts after the shared prefix
    answer = encode(tok, layout.answer)
    rows = []
    for qid, q in questions.items():
        parts["question"] = encode(tok, layout.question.format(question=q.text))
        if "plain_options" in layout.order:  # one encode in caller order, so every order of the question shares it
            parts["plain_options"] = encode(tok, "".join(layout.plain_option.format(text=o) for o in q.options))
        for perm in perms[qid]:
            shown = [q.options[i] for i in perm]
            parts["options"], reads, tag = options_and_reads(tok, layout, labels, shown)
            ids = list(prefix)
            for part in rest:
                ids += parts[part]
            rows.append(Row(qid, perm, ids + frame.tail + answer, reads, tag))
    if images is not None:
        check_placeholders(prefix, rows, images)
    return Batch(rows, len(prefix), unpadded_len, images, images_shared)
