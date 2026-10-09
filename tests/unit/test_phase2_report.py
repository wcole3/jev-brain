import json

import pytest

from scripts import phase2_report as report

T1 = {"choice": 1.0, "score": 1.0, "noul": 1.0}


def summary(index_cells="| **ours: p** | 51.61 | 0.022 | 352.7 | 1.000 |", temps=None, calibration=None,
            layout="decider_chat", timestamp="2026-10-02T124707Z", head="| entry | Index | ECE | median ms | coverage |"):
    cal = f"- calibration: {calibration}" if calibration else f"- temperatures: {temps or {layout: T1}}"
    return (f"# p\n\n## Provenance\n\n- timestamp: {timestamp}\n- prompt_layout: {layout}\n- option_orders: identity\n"
            f"{cal}\n\n{head}\n|---|---|---|---|---|\n{index_cells}\n| other | 1 | 2 | 3 | board |\n"
            "\n- ECE: a note that must not be read as provenance\n")


def write(root, profile, name, text, archive=False):
    run = root / "docs" / "results" / ("archive" if archive else "") / profile / name
    run.mkdir(parents=True)
    (run / "summary.md").write_text(text)
    return run


@pytest.fixture
def tree(tmp_path, monkeypatch):
    monkeypatch.setattr(report, "RESULTS", tmp_path / "docs" / "results")
    monkeypatch.setattr(report, "ROOT", tmp_path)
    (tmp_path / "profiles").mkdir()
    (tmp_path / "profiles" / "p.env").write_text("PROFILE=p\nHF_MODEL=m\nHF_REVISION=r\nSERVED_MODEL=s\nMAX_MODEL_LEN=1024\nPROMPT_LAYOUT=decider_chat\nOPTION_ORDERS=identity\n")
    calibration = tmp_path / "data" / "p" / "decider_chat"
    calibration.mkdir(parents=True)
    types = {"choice": {"T": 1.5}, "score": {"T": 1.6}, "noul": {"T": 1.2, "b": 0.0}}
    (calibration / "calibration.json").write_text(
        json.dumps({"version": 6, "date": "2026-10-03T00:39:27Z", "types": types}))
    return tmp_path


def test_latest_picks_newest_exact_suffix_and_ignores_subset(tree):
    for name in ("2026-10-01T000000Z-index", "2026-10-02T000000Z-vast-index",
                 "2026-10-03T000000Z-index-subset", "2026-10-04T000000Z-index-replaced"):
        write(tree, "p", name, "")
    assert report.latest("p", "index").name == "2026-10-02T000000Z-vast-index"
    assert report.latest("p", "latency") is None


def test_latest_latency_looks_only_in_archive(tree):
    write(tree, "p", "2026-10-01T000000Z-latency", "")
    assert report.latest("p", "latency") is None
    write(tree, "p", "2026-10-02T000000Z-latency", "", archive=True)
    assert report.latest("p", "latency").parent.name == "p" and report.latest("p", "latency").parent.parent.name == "archive"


def test_row_reports_the_runs_own_settings_and_marks_it_when_shipped_differs(tree):
    write(tree, "p", "2026-10-02T124707Z-index", summary())
    lat = ("| entry | median ms | p95 ms |", "| **ours** | 126.7 | 657.4 |")
    write(tree, "p", "2026-10-02T130000Z-latency", summary(lat[1], head=lat[0]).replace("|---|---|---|---|---|", "|---|---|---|"),
          archive=True)
    row = report.profile_row("p")
    assert (row["index"], row["ece"], row["coverage"]) == (51.61, 0.022, 1.0)
    assert (row["median_ms"], row["p95_ms"]) == (126.7, 657.4)
    assert row["run"]["T"] == T1 and row["shipped"]["version"] == 6
    assert row["stale"] and not row["latency_differs"]
    out = report.markdown([row | {"profile": "qwen3.6-27b"}])
    assert "**qwen3.6-27b** †" in out and "T=1 (none)" in out and "decider_chat / identity / v6" in out
    assert "2026-10-02T130000Z-latency |" in out and "‡" not in out.splitlines()[2]


def test_run_matching_shipped_settings_is_unmarked_unless_calibration_is_newer(tree):
    shipped = {"decider_chat": {"T": {"choice": 1.5, "score": 1.6, "noul": 1.2}, "b": 0.0}}
    write(tree, "p", "2026-10-04T000000Z-index", summary(calibration=shipped, timestamp="2026-10-04T000000Z"))
    assert not report.profile_row("p")["stale"]
    (tree / "docs" / "results" / "p" / "2026-10-04T000000Z-index" / "summary.md").write_text(
        summary(calibration=shipped, timestamp="2026-10-02T000000Z"))
    assert report.profile_row("p")["stale"]


def test_latency_run_with_other_settings_is_flagged(tree):
    write(tree, "p", "2026-10-02T124707Z-index", summary())
    other = summary("| **ours** | 1.0 | 2.0 |", temps={"decider_chat": {**T1, "choice": 2.0}},
                    head="| entry | median ms | p95 ms |").replace("|---|---|---|---|---|", "|---|---|---|")
    write(tree, "p", "2026-10-02T130000Z-latency", other, archive=True)
    assert report.profile_row("p")["latency_differs"]


def test_cells_are_mapped_by_header_name_and_errors_name_the_file(tree):
    reordered = summary("| **ours: p** | 0.022 | 51.61 | 1.000 | 352.7 |", head="| entry | ECE | Index | coverage | median ms |")
    run = write(tree, "p", "2026-10-02T124707Z-index", reordered)
    assert report.profile_row("p")["index"] == 51.61
    (run / "summary.md").write_text(summary("| nobody | 1 | 2 | 3 | 4 |"))
    with pytest.raises(SystemExit, match=r"summary\.md: no table header or no row"):
        report.profile_row("p")
    (run / "summary.md").write_text(summary(head="| entry | Index | ECE | median ms | cover |",
                                            index_cells="| **ours: p** | 1 | 2 | 3 | 4 |"))
    with pytest.raises(SystemExit, match="no column 'coverage'"):
        report.profile_row("p")


def test_missing_summary_and_missing_provenance_fail_loudly(tree):
    run = write(tree, "p", "2026-10-02T124707Z-index", summary())
    (run / "summary.md").unlink()
    with pytest.raises(SystemExit, match="summary.md is missing"):
        report.profile_row("p")
    (run / "summary.md").write_text("| entry | Index | ECE | median ms | coverage |\n|---|\n| **ours: p** | 1 | 2 | 3 | 4 |\n")
    with pytest.raises(SystemExit, match="provenance lacks usable run settings"):
        report.profile_row("p")


def test_markdown_lists_every_board_match_after_the_profile_row(tree):
    for profile, entries in report.MATCHES.items():
        shipped = {"layout": "decider_chat", "orders": "identity", "T": T1, "b": 0.0, "version": 2}
        row = {"profile": profile, "shipped": shipped, "index": None, "ece": None, "coverage": None, "run": None,
               "median_ms": None, "p95_ms": None, "latency_run": None, "latency_differs": False, "stale": False}
        lines = report.markdown([row]).splitlines()
        assert lines[2].startswith(f"| **{profile}** | n/a")
        assert [x.split(" | ")[0] for x in lines[3 : 3 + len(entries)]] == [f"| {report.BOARD[k]['name']}" for k in entries]


def test_main_writes_the_report_file(tree, monkeypatch, capsys):
    monkeypatch.setattr(report, "MATCHES", {"p": []})
    report.RESULTS.mkdir(parents=True)
    report.main([])
    assert (tree / "docs" / "results" / "phase2-report.md").read_text() == capsys.readouterr().out


def test_readme_replacement_keeps_outside_text_byte_identical():
    before, after = "intro\r\n\n## Where it stands\n", "\ntail  \n\n"
    text = f"{before}{report.START}\nold table\n{report.END}{after}"
    out = report.replace_between_markers(text, "| new |\n")
    assert out.startswith(before + report.START) and out.endswith(report.END + after)
    assert "old table" not in out and "| new |" in out


def test_phase2_table_shows_0_3_public_and_full(tree):
    shipped = {"layout": "header", "orders": "identity", "T": T1, "b": 0.0, "version": 3}
    row = {"profile": "gemma-4-31b", "shipped": shipped, "index": 61.6, "ece": 0.1, "coverage": 1.0, "run": None,
           "median_ms": None, "p95_ms": None, "latency_run": None, "latency_differs": False, "stale": False}
    lines = report.markdown([row]).splitlines()
    assert lines[0].startswith("| entry | Index | Full |")
    assert lines[2].startswith("| **gemma-4-31b** | 61.60 | — |")
    assert lines[3].startswith("| Decider chat · Gemma-4-31B | 57.79 | 57.62 |")
