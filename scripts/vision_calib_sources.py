"""The calibration set's public sources: pinned Hugging Face train splits read as normalized Items."""

import json
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.errors import (
    EntryNotFoundError,
    GatedRepoError,
    RepositoryNotFoundError,
    RevisionNotFoundError,
)

from gateway.config import ROOT

RAW = ROOT / ".cache/vision-calib/raw"


@dataclass(frozen=True)
class Item:
    """One normalized source question: choices in source order, answer an index into them."""

    source_id: str
    question: str
    choices: list[str]
    answer: int
    image: bytes


class Unavailable(Exception):
    """A source that cannot be used: gated, missing, or without a train split."""


@dataclass(frozen=True)
class Source:
    name: str
    repo: str
    revision: str
    split: str
    note: str
    read: Callable[[], Iterator[Item]]


def parquet_files(repo: str, revision: str, prefix: str) -> list[Path]:
    """The split's parquet files at a pinned revision, downloaded anonymously; a gated repo is refused."""
    try:
        info = HfApi(token=False).dataset_info(repo, revision=revision)
        if info.gated:
            raise Unavailable(f"{repo} is gated")
        names = sorted(s.rfilename for s in info.siblings if s.rfilename.startswith(prefix)
                       and s.rfilename.endswith(".parquet"))
        if not names:
            raise Unavailable(f"{repo}@{revision} has no {prefix}*.parquet (no train split)")
        return [Path(hf_hub_download(repo, n, repo_type="dataset", revision=revision, token=False,
                                     local_dir=RAW / repo)) for n in names]
    except (GatedRepoError, RepositoryNotFoundError, RevisionNotFoundError, EntryNotFoundError) as e:
        raise Unavailable(f"{repo}: {type(e).__name__}") from e


def records(files: list[Path], columns: list[str]) -> Iterator[dict]:
    for f in files:
        for batch in pq.ParquetFile(f).iter_batches(batch_size=256, columns=columns):
            yield from batch.to_pylist()


SCIENCEQA = ("derek-thomas/ScienceQA", "f18b0a70359ebfb41f658fd564208d0355b013f4")
AI2D = ("tasksource/ai2d", "24013c0e6bb313a1fc4dfa79f9db936072f6a3af")
AOKVQA = ("HuggingFaceM4/A-OKVQA", "d1b0efa3a436e9101dfbde3752db7607da696c35")


def scienceqa() -> Iterator[Item]:
    """Image questions only; id is the train row index. A non-empty hint goes before the question as context."""
    rows = records(parquet_files(*SCIENCEQA, "data/train-"), ["image", "question", "choices", "answer", "hint"])
    for n, r in enumerate(rows):
        if r["image"] and r["image"]["bytes"]:
            question = f"Context: {r['hint']}\n{r['question']}" if r["hint"] else r["question"]
            yield Item(str(n), question, r["choices"], r["answer"], r["image"]["bytes"])


def ai2d() -> Iterator[Item]:
    """Every question of every diagram; id is the Cauldron's `<diagram>:<question>`."""
    for r in records(parquet_files(*AI2D, "data/train-"), ["images", "qa"]):
        for qa in r["qa"]:
            source_id = json.loads(qa["metadata"])["id"].removeprefix("ai2d:")
            yield Item(source_id, qa["inputs"], qa["choices_list"], qa["labels"], r["images"][0]["bytes"])


def aokvqa() -> Iterator[Item]:
    columns = ["image", "question_id", "question", "choices", "correct_choice_idx"]
    for r in records(parquet_files(*AOKVQA, "data/train-"), columns):
        yield Item(r["question_id"], r["question"], r["choices"], r["correct_choice_idx"], r["image"]["bytes"])


SOURCES = [
    Source("scienceqa", *SCIENCEQA, "train", "rows with an image; hint prefixed as 'Context:'", scienceqa),
    Source("ai2d", *AI2D, "train", "AI2D train via HuggingFaceM4/the_cauldron@847a98a7, choices parsed by "
           "tasksource (6 ambiguous-gold questions excluded upstream)", ai2d),
    Source("aokvqa", *AOKVQA, "train", "multiple-choice: choices + correct_choice_idx; COCO 2017 images", aokvqa),
]
