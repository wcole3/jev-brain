import gzip
import json

import pytest

from gateway.layouts import load_layout, load_layouts
from scripts import label_screen as ls
from scripts import vision_splits as vs
from scripts.label_screen import Q

DIGITS = load_layout(ls.EXPERIMENTS / "labels-digits.toml")
HEADER = load_layouts()["header"]
CONFIG = {"profile": "p", "label": "x", "layout": "header", "orders": "identity+reversed", "env": {}, "split": "dev",
          "commit": "c1"}


def reads(scores: list[float]) -> list[dict]:
    """Identity and reversed reads of caller-order scores: shown position j holds option perm[j]."""
    n = len(scores)
    return [{"perm": p, "logprobs": [scores[p[j]] for j in range(n)]} for p in (list(range(n)), list(range(n))[::-1])]


def onehot(n: int, top: int) -> list[float]:
    return [2.0 * (k == top) for k in range(n)]


def write(path, recs: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in recs)
    return path


def text_rec(i: int, layout: str, top: int, **extra) -> dict:
    rec = {"id": f"r{i}", "layout": layout, "status": "ok", "stamp": {}, "questions": {"c": reads(onehot(3, top))}}
    return rec | extra


def image_rec(i: int, layout: str, top: int, **extra) -> dict:
    return {"id": f"r{i}", "benchmark": "BLINK" if i % 2 else "CV-Bench", "group": f"g{i // 2}", "layout": layout,
            "names": ["A", "B", "C"], "gold": i % 3, "input_tokens": 700, "shared_len": 30, "padded": False,
            "unpadded_len": 30, "image_tokens": 500, "images_shared": True, "status": "ok", "stamp": {},
            "reads": [r | {"suffix_len": 20} for r in reads(onehot(3, top))]} | extra


@pytest.fixture
def roots(tmp_path, monkeypatch):
    monkeypatch.setattr(ls, "TEXT", tmp_path / "collect")
    monkeypatch.setattr(ls, "VISION", tmp_path / "vision-collect")
    monkeypatch.setattr(ls, "ARCHIVE", tmp_path / "archive")
    return tmp_path


def check_collects(tmp, changed: int, count: int = 50) -> None:
    """Control and letters-experiment collects that agree except for `changed` index-dev-2k questions."""
    text, image = tmp / "collect" / "p", tmp / "vision-collect" / "p"
    for control, split in (("calib", "calib-600"), ("index-dev", "index-dev-2k")):
        write(text / f"{control}.jsonl.gz", [text_rec(i, "header", i % 3) for i in range(count)]
              + [text_rec(i, "decider_chat", 0) for i in range(count)])
        moved = changed if split == "index-dev-2k" else 0
        write(text / f"{split}-letters.jsonl.gz",
              [text_rec(i, "labels-letters", (i % 3 + (i < moved)) % 3) for i in range(count)])
    write(image / "baseline" / "dev.jsonl.gz", [image_rec(i, "header", i % 3) for i in range(count)])
    write(image / "labels-letters" / "dev.jsonl.gz", [image_rec(i, "labels-letters", i % 3) for i in range(count)])


def test_check_agreement(roots):
    check_collects(roots, changed=1)
    report = ls.main(["check", "--profile", "p"])
    got = report["splits"]["index-dev-2k"]
    assert got["agreement"] == 0.98 and got["questions"] == 50 and got["rows"] == 50
    assert report["splits"]["calib-600"]["agreement"] == 1 and report["splits"]["image dev"]["agreement"] == 1
    (out,) = (roots / "archive").iterdir()
    assert out.name.endswith("-r3-labels-check-p") and (out / "summary.md").exists()
    assert json.loads((out / "summary.json").read_text())["passed"] is True

    check_collects(roots, changed=2)
    ls.ARCHIVE = roots / "archive-2"  # a second run can land in the same second
    with pytest.raises(SystemExit, match="index-dev-2k"):
        ls.main(["check", "--profile", "p"])


def test_check_samples_rows_present_in_both():
    control = {(f"r{i}", "c"): 0 for i in range(300)}
    other = {(f"r{i}", "c"): 0 for i in range(100, 400)}
    got = ls.agreement(control, other)
    assert got == {"rows": 200, "questions": 200, "agreement": 1.0}
    assert ls.agreement(control, other) == got  # seeded


def row(i: int) -> dict:
    n = 3 + 9 * (i % 2)  # 12 options overflow the 9 digit labels: those questions fall back to letters
    criteria = {f"o{k}": None for k in range(n)}
    return {"id": f"r{i}", "source": "index", "family": "f", "state": "s",
            "questions": {"c": {"type": "choice", "instructions": "pick", "criteria": criteria},
                          "y": {"type": "noul", "instructions": "is it?"}},
            "gold": {"c": f"o{i % 3}", "y": i % 3 == 0}}


def screen_recs(layout: str, count: int, tagged: bool, unsupported=()) -> list[dict]:
    out = []
    for i in range(count):
        r = row(i)
        n = len(r["questions"]["c"]["criteria"])
        qs = {"c": reads([1.5 * (k == i % 3) + 0.3 * (k == 0) for k in range(n)]), "y": reads([0.0, 0.5 * (i % 2)])}
        rec = {"id": r["id"], "layout": layout, "status": "ok", "stamp": {}, "questions": qs}
        if tagged:
            rec["label_tags"] = {"c": "fallback" if n > 9 else "set", "y": "set"}
        if i in unsupported:
            rec = {"id": r["id"], "layout": layout, "status": "unsupported", "stamp": {}, "error": "too long"}
        out.append(rec)
    return out


def text_report(count: int = 20, unsupported=()):
    rows = {f"r{i}": row(i) for i in range(count)}

    def arms(unsupported=()):
        return {"letters": ls.text_items(screen_recs("header", count, False), rows, HEADER),
                "labels-digits": ls.text_items(screen_recs("labels-digits", count, True, unsupported), rows, DIGITS)}
    return ls.text_report(arms(), arms(unsupported))


def test_pure_subset_excludes_fallback():
    report = text_report()
    pure, every = report["subsets"]["pure"], report["subsets"]["all"]
    assert every["n"] == 40 and pure["n"] == 30  # the 10 twelve-option choice questions are fallback
    assert every["arms"]["labels-digits"]["options"]["6-26"]["n"] == 10
    assert "6-26" not in pure["arms"]["labels-digits"]["options"]
    assert pure["arms"]["letters"]["overall"]["all"]["n"] == 30
    assert report["fallback_share"]["overall"]["all"] == 0.25
    assert report["fallback_share"]["options"] == {"2": 0.0, "3-5": 0.0, "6-26": 1.0}
    assert set(pure["vs_letters"]) == {"labels-digits"} and pure["vs_letters"]["labels-digits"]["overall"]["all"]["n"] == 30


def test_pairs_only_shared_questions():
    report = text_report(unsupported={4})
    every = report["subsets"]["all"]
    assert every["n"] == 38
    assert every["arms"]["letters"]["overall"]["all"]["n"] == 38
    assert every["vs_letters"]["labels-digits"]["overall"]["all"]["n"] == 38
    assert report["questions"]["dev"] == {"letters": 40, "labels-digits": 38}


def test_flip_rate_and_histogram():
    tops = [(0, 0), (1, 2), (2, 2), (0, 1)]  # (identity top, reversed top): two flips in four
    items = {}
    for k, (i_top, r_top) in enumerate(tops):
        ident, rev = onehot(3, i_top), onehot(3, r_top)
        by_perm = {(0, 1, 2): ident, (2, 1, 0): [rev[2], rev[1], rev[0]]}
        items[(f"r{k}", "c")] = Q("index", "f", "choice", k % 3, 3, by_perm, "set")
    items[("r9", "y")] = Q("index", "f", "noul", 1, 2, {(0, 1): [0.0, 2.0], (1, 0): [0.0, 2.0]}, "set")
    view = ls.arm_view(items, sorted(items), {"choice": 1.0, "score": 1.0, "noul": 1.0})
    assert view["flips"]["overall"]["all"] == 0.5 and view["flips"]["options"]["3-5"] == 0.5
    assert view["histogram"] == {"3-5": {"chosen": [2, 1, 1, 0, 0], "gold": [2, 1, 1, 0, 0]}}


def test_image_arms_pair_shared_rows(tmp_path, monkeypatch):
    splits = tmp_path / "splits"
    splits.mkdir()
    (splits / "vision-dev.json").write_text(json.dumps({"meta": {"suite_sha256": "x"}, "ids": [f"r{i}" for i in range(20)]}))
    monkeypatch.setattr(vs, "SPLITS", splits)
    monkeypatch.setattr(vs, "suite_hash", lambda: "x")
    base = [image_rec(i, "header", i % 3) for i in range(20)]
    other = [image_rec(i, "labels-digits", (i + (i % 4 == 0)) % 3, label_tags={"answer": "fallback" if i < 4 else "set"})
             for i in range(20)]
    other[7] |= {"status": "unsupported", "reads": []}
    dev = {"letters": (base, CONFIG, "base.jsonl.gz"), "labels-digits": (other, CONFIG, "other.jsonl.gz")}
    T = {"choice": 1.0, "score": 1.0, "noul": 1.0}
    report = ls.image_report({"letters": T, "labels-digits": T}, dev, tmp_path / "out")
    assert report["subsets"]["all"]["n"] == 19 and report["subsets"]["pure"]["n"] == 15
    assert report["fallback_share"]["overall"]["all"] == pytest.approx(4 / 19)
    compare = report["subsets"]["pure"]["compare"]
    assert set(compare["configs"]) == {"letters", "labels-digits"} and compare["paired"]["labels-digits"]["agreement"] < 1
    scored = tmp_path / "out" / "arms" / "pure" / "letters" / "scored.jsonl.gz"
    with gzip.open(scored, "rt") as f:
        assert len(f.readlines()) == 15
