"""Experiment layouts kept outside prompts/ (prompts/experiments/), registered in a collect's engine at run time."""

import hashlib
import json
from pathlib import Path

from gateway.calibration import UNCALIBRATED
from gateway.config import ROOT
from gateway.labels import labels_from_table
from gateway.layouts import load_layout
from gateway.prompts import chat_frame
from scripts.build_labels import table_for


def add_layout_file(engine, path: Path) -> str:
    """Register an experiment layout in the engine, labels built in memory; returns the table's sha256."""
    try:
        layout = load_layout(path)
        if layout.name in engine.layouts:
            raise SystemExit(f"{path}: {layout.name!r} is a prompts/ layout name; rename the experiment file")
        table = table_for(engine.tokenizer, layout, engine.settings)
        frame = chat_frame(engine.tokenizer, layout)
    except (OSError, ValueError) as e:  # a bad file, or a label or frame that merges with the answer text
        raise SystemExit(f"{path}: {e}") from e
    engine.layouts[layout.name] = layout
    engine.frames[layout.name] = frame
    engine.labels[layout.name] = labels_from_table(table)
    engine.calibration[layout.name] = UNCALIBRATED
    # the bytes build_labels.py would write, so it matches a labels.json built on disk later
    return hashlib.sha256((json.dumps(table, indent=1) + "\n").encode()).hexdigest()


def label_tags(engine, layout: str, batch) -> dict:
    """{"label_tags": {qid: "set" | "fallback"}} for an experiment label set; nothing for letters."""
    if engine.labels[layout].set == "letters":
        return {}
    return {"label_tags": {row.question_id: row.label_tag for row in batch.rows}}


def repo_relative(path: str) -> str:
    p = Path(path).resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
