import dataclasses

import pytest

from gateway.config import Settings
from gateway.decide import Engine
from gateway.labels import build_labels, label_table, save_labels
from gateway.layouts import load_layouts
from gateway.prompts import chat_frame
from tests.helpers import FavourFirstLabel, tokenizer_for


@pytest.fixture(scope="session")
def qwen_tok():
    return tokenizer_for("qwen3.6-27b")


@pytest.fixture
def qwen_settings(tmp_path, qwen_tok):
    """qwen3.6-27b settings whose data dir is a temp folder holding fresh label tables."""
    s = dataclasses.replace(Settings.from_profile("qwen3.6-27b"), data_root=tmp_path)
    for name, layout in load_layouts().items():
        save_labels(s.data_dir(name) / "labels.json", build_labels(qwen_tok, layout))
    return s


@pytest.fixture
def engine(qwen_tok):
    layouts = load_layouts()
    return Engine(
        settings=Settings.from_profile("qwen3.6-27b"),
        tokenizer=qwen_tok,
        layouts=layouts,
        frames={n: chat_frame(qwen_tok, l) for n, l in layouts.items()},
        labels={n: label_table(qwen_tok) for n in layouts},
        temperatures={n: {"choice": 1.0, "score": 1.0, "noul": 1.0} for n in layouts},
        readout=FavourFirstLabel(),
    )
