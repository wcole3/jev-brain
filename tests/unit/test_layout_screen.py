import json

import pytest

from scripts import label_screen as ls
from scripts import layout_screen as lsc
from scripts import vision_splits as vs
from tests.unit.test_label_screen import image_rec, text_rec, write

COUNT = 20
CONFIG = {"profile": "p", "label": "x", "layout": "x", "layout_file": "x.toml", "orders": "identity+reversed",
          "env": {}, "split": "dev", "commit": "c1"}
TOPS = {"letters": lambda i: 0, "blurb-header": lambda i: i % 3}  # letters picks option 0, blurb-header the gold


def row(i: int) -> dict:
    criteria = {f"o{k}": None for k in range(3)}
    return {"id": f"r{i}", "source": "index", "family": "f", "state": "s",
            "questions": {"c": {"type": "choice", "instructions": "pick", "criteria": criteria}},
            "gold": {"c": f"o{i % 3}"}}


@pytest.fixture
def roots(tmp_path, monkeypatch):
    for name, sub in (("TEXT", "collect"), ("VISION", "vision-collect"), ("ARCHIVE", "archive"),
                      ("IMAGE_OUT", "image-out")):
        monkeypatch.setattr(ls, name, tmp_path / sub)
    monkeypatch.setattr(lsc, "rows_for", lambda split: [row(i) for i in range(COUNT)])
    splits = tmp_path / "splits"
    splits.mkdir()
    ids = [f"r{i}" for i in range(COUNT)]
    (splits / "vision-dev.json").write_text(json.dumps({"meta": {"suite_sha256": "x"}, "ids": ids}))
    monkeypatch.setattr(vs, "SPLITS", splits)
    monkeypatch.setattr(vs, "suite_hash", lambda: "x")
    return tmp_path


def collects(tmp, missing: int = 0, configs: dict | None = None) -> None:
    """Each arm's text and image collects, each file also holding always-wrong decider_chat records; blurb-header
    lacks the last `missing` index-dev-2k rows."""
    for arm, top in TOPS.items():
        a = lsc.ARMS[arm]
        for split in lsc.SPLITS:
            n = COUNT - missing if (arm, split) == ("blurb-header", "index-dev-2k") else COUNT
            noise = [text_rec(i, "decider_chat", (i + 1) % 3) for i in range(COUNT)]
            write(tmp / "collect" / "p" / f"{split}-{a.text}.jsonl.gz", [text_rec(i, a.layout, top(i)) for i in range(n)]
                  + noise)
        path = tmp / "vision-collect" / "p" / a.image / "dev.jsonl.gz"
        noise = [image_rec(i, "decider_chat", (i + 1) % 3) for i in range(COUNT)]
        write(path, [image_rec(i, a.layout, top(i)) for i in range(COUNT)] + noise)
        path.with_name("dev.config.json").write_text(json.dumps(CONFIG | (configs or {}).get(arm, {})))


def run(tmp, **kw) -> tuple:
    collects(tmp, **kw)
    text_dir, image_dir = lsc.pair("p", "blurb-header", "letters")
    return text_dir, image_dir, *(json.loads((d / "summary.json").read_text()) for d in (text_dir, image_dir))


def test_pair_reads_each_arms_layout(roots):
    _, _, text, image = run(roots)
    arms = text["subsets"]["all"]["arms"]
    assert list(arms) == ["letters", "blurb-header"]
    assert arms["blurb-header"]["overall"]["all"]["accuracy"] == 1.0
    assert arms["letters"]["overall"]["all"]["accuracy"] == 7 / 20  # rows 0, 3, ..., 18 have gold 0
    configs = image["subsets"]["all"]["compare"]["configs"]
    assert configs["blurb-header"]["accuracy"] == 1.0 and configs["letters"]["accuracy"] == 7 / 20
    assert set(text["subsets"]["all"]["vs_base"]) == {"blurb-header"}


def test_pair_has_no_pure_subset(roots):
    _, _, text, image = run(roots)
    for report in (text, image):
        assert report["subsets"].keys() == {"all"} and "fallback_share" not in report


def test_pair_pairs_shared_rows_only(roots):
    _, _, text, _ = run(roots, missing=3)
    every = text["subsets"]["all"]
    assert every["n"] == 17 and every["arms"]["letters"]["overall"]["all"]["n"] == 17
    assert text["questions"]["dev"] == {"letters": 20, "blurb-header": 17}


def test_pair_refuses_mismatched_image_configs(roots):
    collects(roots, configs={"letters": {"env": {"VLLM_X": "1"}}})
    with pytest.raises(SystemExit, match="env"):
        lsc.pair("p", "blurb-header", "letters")
    other = {"label": "y", "layout": "y", "layout_file": "y.toml", "commit": "c2"}
    _, _, _, image = run(roots, configs={"letters": other})
    assert image["subsets"]["all"]["n"] == COUNT


def test_pair_names_dirs(roots):
    text_dir, image_dir, text, _ = run(roots)
    for d in (text_dir, image_dir):
        assert d.name.endswith("-r4-pair-blurb-header-vs-letters-p")
        assert (d / "summary.md").read_text().startswith("# p R4 pair screen: blurb-header vs letters, ")
    assert text_dir.parent == ls.ARCHIVE and image_dir.parent == ls.IMAGE_OUT
    assert text["meta"]["title"] == "R4 pair screen" and text["meta"]["control"] == "letters"
