import json

from scripts import phase2_report as report


def test_latest_picks_newest_exact_suffix_and_ignores_subset(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "RESULTS", tmp_path)
    for name in ("2026-10-01T000000Z-index", "2026-10-02T000000Z-vast-index",
                 "2026-10-03T000000Z-index-subset", "2026-10-04T000000Z-index-replaced"):
        (tmp_path / "p" / name).mkdir(parents=True)
    assert report.latest("p", "index").name == "2026-10-02T000000Z-vast-index"
    assert report.latest("p", "latency") is None


def test_profile_row_parses_summaries_and_shipped_config(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "RESULTS", tmp_path)
    monkeypatch.setattr(report, "ROOT", tmp_path)
    run = tmp_path / "p" / "2026-10-01T000000Z-index"
    run.mkdir(parents=True)
    (run / "summary.md").write_text("| entry | Index |\n|---|---|\n"
                                    "| **ours: p** | 51.61 | 0.022 | 352.7 | 1.000 |\n| other | 1 | 2 | 3 | board |\n")
    lat = tmp_path / "p" / "2026-10-01T010000Z-latency"
    lat.mkdir()
    (lat / "summary.md").write_text("| entry | median ms | p95 ms |\n|---|---|---|\n| **ours** | 126.7 | 657.4 |\n")
    (tmp_path / "profiles").mkdir()
    (tmp_path / "profiles" / "p.env").write_text("PROMPT_LAYOUT=header\nOPTION_ORDERS=identity\n")
    (tmp_path / "data" / "p" / "header").mkdir(parents=True)
    (tmp_path / "data" / "p" / "header" / "calibration.json").write_text(json.dumps({"version": 6}))
    row = report.profile_row("p")
    assert (row["index"], row["ece"], row["coverage"]) == (51.61, 0.022, 1.0)
    assert (row["median_ms"], row["p95_ms"]) == (126.7, 657.4)
    assert (row["layout"], row["orders"], row["calibration"]) == ("header", "identity", 6)


def test_markdown_lists_every_board_match_after_the_profile_row():
    row = {"profile": "qwen3.8-27b", "index": None, "ece": None, "coverage": None, "median_ms": None,
           "p95_ms": None, "layout": "decider_chat", "orders": "identity", "calibration": 2}
    lines = report.markdown([row]).splitlines()
    assert lines[2].startswith("| **qwen3.8-27b** | n/a")
    assert [x.split(" | ")[0] for x in lines[3:]] == [
        "| simple-jev · Qwen3.8-27B", "| reflex 27B", "| Jevfire (Qwen3.8-27B-FP8)"]


def test_readme_replacement_keeps_outside_text_byte_identical():
    before, after = "intro\r\n\n## Where it stands\n", "\ntail  \n\n"
    text = f"{before}{report.START}\nold table\n{report.END}{after}"
    out = report.replace_between_markers(text, "| new |\n")
    assert out.startswith(before + report.START) and out.endswith(report.END + after)
    assert "old table" not in out and "| new |" in out
