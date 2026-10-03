import dataclasses

import pytest

from gateway.calibration import UNCALIBRATED
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
    """qwen3.6-27b settings on decider_chat (pinned, so profile defaults can move) with fresh label tables."""
    s = dataclasses.replace(Settings.from_profile("qwen3.6-27b"), data_root=tmp_path, prompt_layout="decider_chat")
    for name, layout in load_layouts().items():
        save_labels(s.data_dir(name) / "labels.json", build_labels(qwen_tok, layout))
    return s


@pytest.fixture
def engine(qwen_tok):
    layouts = load_layouts()
    return Engine(
        settings=dataclasses.replace(Settings.from_profile("qwen3.6-27b"), prompt_layout="decider_chat"),
        tokenizer=qwen_tok,
        layouts=layouts,
        frames={n: chat_frame(qwen_tok, l) for n, l in layouts.items()},
        labels={n: label_table(qwen_tok) for n in layouts},
        calibration={n: UNCALIBRATED for n in layouts},
        readout=FavourFirstLabel(),
    )
