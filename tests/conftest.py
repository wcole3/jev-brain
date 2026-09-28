import dataclasses

import pytest

from gateway.config import Settings
from gateway.labels import build_labels, save_labels
from gateway.layouts import load_layouts
from tests.helpers import tokenizer_for


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
