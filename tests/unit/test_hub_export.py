import gzip
import json

import pytest

from scripts import hub_export


def row(run_id, status="ok", answer="a", sha="h"):
    return json.dumps({"run_id": run_id, "payload_sha256": sha + run_id, "status": status, "answer": answer}).encode() + b"\n"


SUITE = {r: {"run_id": r, "payload_sha256": "h" + r} for r in ("r1", "r2")}


def test_clean_results_are_kept_byte_for_byte():
    lines = [row("r2", answer="é"), row("r1", status="unsupported")]
    kept, dropped, problems, counts = hub_export.select(lines, SUITE, retries=False)
    assert kept == lines and not dropped and not problems
    assert counts == {"ok": 1, "unsupported": 1}


def test_text_duplicates_fail_even_when_identical():
    _, _, problems, _ = hub_export.select([row("r1"), row("r1"), row("r2")], SUITE, retries=False)
    assert len(problems) == 1 and "duplicate" in problems[0]


def test_vision_drops_a_superseded_error_and_keeps_the_retry():
    lines = [row("r1", status="error"), row("r2"), row("r1")]
    kept, dropped, problems, _ = hub_export.select(lines, SUITE, retries=True)
    assert kept == [row("r1"), row("r2")] and len(dropped) == 1 and not problems


def test_vision_drops_identical_repeats_but_not_differing_ones():
    _, dropped, problems, _ = hub_export.select([row("r1"), row("r1"), row("r2")], SUITE, retries=True)
    assert len(dropped) == 1 and not problems
    _, _, problems, _ = hub_export.select([row("r1", answer="x"), row("r1"), row("r2")], SUITE, retries=True)
    assert "content differs" in problems[0]


def test_a_trailing_error_is_not_forgiven():
    _, _, problems, _ = hub_export.select([row("r1"), row("r1", status="error"), row("r2")], SUITE, retries=True)
    assert any("content differs" in p for p in problems) and any("'error'" in p for p in problems)


def test_extra_missing_and_foreign_rows_are_reported():
    lines = [row("r1"), row("r3"), row("r2", sha="other")]
    _, _, problems, _ = hub_export.select(lines, SUITE, retries=False)
    assert any("r3: not in the suite" in p for p in problems)
    assert any("r2: payload" in p for p in problems)
    _, _, problems, _ = hub_export.select([row("r1")], SUITE, retries=False)
    assert any("1 suite run_ids missing" in p for p in problems)


def test_blank_and_broken_lines_are_problems():
    _, _, problems, _ = hub_export.select([row("r1"), b"\n", b"{oops\n", row("r2")], SUITE, retries=False)
    assert len(problems) == 2


def test_scores_must_be_complete_and_cover_the_rows():
    assert hub_export.check_scores({"complete": True, "completed": 2}, 2) == []
    assert len(hub_export.check_scores({"complete": False}, 2)) == 1
    assert len(hub_export.check_scores({"complete": True, "completed": 3}, 2)) == 1
    assert len(hub_export.check_scores({"complete": True, "missing_rows": 1}, 2)) == 1


def make_run(tmp_path, kind, lines, scores):
    run = tmp_path / f"run-{kind}"
    for dest, src in hub_export.FILES[kind].items():
        (run / src).parent.mkdir(parents=True, exist_ok=True)
        (run / src).write_text(json.dumps(scores) if dest.endswith("scores.json") else "{}")
    (run / hub_export.RESULTS[kind]).write_bytes(b"".join(lines))
    for i in range(2):
        (run / f"shard-{i}").mkdir()
        (run / f"shard-{i}" / "environment.json").write_text("{}")
        (run / f"shard-{i}" / "status.json").write_text("{}")
    return run


def args_for(tmp_path, kind, run):
    return hub_export.parse_args([kind, str(run), "--name", "n", "--out", str(tmp_path / "out"), "--no-rescore"])


@pytest.fixture
def suite_file(tmp_path, monkeypatch):
    path = tmp_path / "rows.jsonl"
    path.write_text("".join(json.dumps({"_evaluation": e}) + "\n" for e in SUITE.values()))
    monkeypatch.setitem(hub_export.SUITES, "text", path)
    monkeypatch.setitem(hub_export.SUITES, "vision", path)


def test_text_export_writes_exactly_the_board_files(tmp_path, suite_file):
    lines = [row("r1"), row("r2")]
    run = make_run(tmp_path, "text", lines, {"complete": True, "completed": 2})
    report: list[str] = []
    assert hub_export.export(args_for(tmp_path, "text", run), report) == []
    dest = tmp_path / "out" / "runs" / "n"
    files = sorted(str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file())
    assert files == ["benchmark-summary.json", "index.json", "results.jsonl.gz", "scores.json",
                     "shards/shard-0/environment.json", "shards/shard-0/status.json",
                     "shards/shard-1/environment.json", "shards/shard-1/status.json"]
    assert gzip.decompress((dest / "results.jsonl.gz").read_bytes()) == b"".join(lines)
    assert any(x.startswith("results.jsonl.gz sha256") for x in report)


def test_vision_export_cleans_retries_and_failure_writes_no_folder(tmp_path, suite_file):
    run = make_run(tmp_path, "vision", [row("r1", status="error"), row("r1"), row("r2")], {"complete": True})
    assert hub_export.export(args_for(tmp_path, "vision", run), []) == []
    dest = tmp_path / "out" / "runs" / "n"
    assert gzip.decompress((dest / "results.jsonl.gz").read_bytes()) == row("r1") + row("r2")
    assert sorted(p.name for p in dest.iterdir()) == ["environment.json", "results.jsonl.gz", "status.json", "vision-scores.json"]
    bad = make_run(tmp_path / "b", "vision", [row("r1", status="error"), row("r2")], {"complete": True})
    args = hub_export.parse_args(["vision", str(bad), "--name", "n", "--out", str(tmp_path / "out2"), "--no-rescore"])
    assert hub_export.export(args, []) and not (tmp_path / "out2" / "runs").exists()


def test_main_exits_nonzero_and_writes_the_report(tmp_path, suite_file):
    run = make_run(tmp_path, "text", [row("r1")], {"complete": False})
    argv = ["text", str(run), "--name", "n", "--out", str(tmp_path / "out"), "--no-rescore"]
    with pytest.raises(SystemExit) as e:
        hub_export.main(argv)
    assert e.value.code == 1
    assert "FAILED" in (tmp_path / "out" / "n.export.txt").read_text()
