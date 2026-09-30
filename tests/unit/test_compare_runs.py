import json

from scripts.compare_runs import load_rows, main, report


def row(i, pred, gold="A", p=None):
    r = {"test": "jevbench", "id": i, "gold": gold, "pred": pred, "correct": pred == gold}
    return r | ({"probabilities": p} if p else {})


def write(folder, rows):
    folder.mkdir()
    (folder / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return folder


def test_flips_and_probability_drift(tmp_path):
    base = write(
        tmp_path / "b",
        [
            row("1", "A", p={"A": 0.6, "B": 0.4}),
            row("2", "B", p={"A": 0.4, "B": 0.6}),
            row("3", "A", p={"A": 0.9, "B": 0.1}),
            row("4", "A"),
        ],
    )
    cand = write(
        tmp_path / "c",
        [
            row("1", "B", p={"A": 0.4, "B": 0.6}),
            row("2", "A", p={"A": 0.5, "B": 0.5}),
            row("3", "A", p={"A": 0.85, "B": 0.15}),
            row("5", "A"),
        ],
    )
    text = report(load_rows(base), load_rows(cand))
    assert "rows in common: 3" in text
    assert "answer flips: 2 (66.7%): wrong→right 1, right→wrong 1, wrong→wrong 0" in text
    assert "max |Δp|: 0.2000" in text
    assert "| 1 | A | A | B | 0.200 |" in text


def test_old_runs_degrade_gracefully(tmp_path, capsys):
    old = write(tmp_path / "o", [{"test": "jevbench", "gold": "A", "pred": "A", "correct": True}])
    assert "No rows in common" in report(load_rows(old), load_rows(old))
    a = write(tmp_path / "a", [row("1", "A")])
    b = write(tmp_path / "b", [row("1", "B")])
    main([str(a), str(b), "--out", str(tmp_path / "out.md")])
    assert "Probability sections skipped" in (tmp_path / "out.md").read_text()
