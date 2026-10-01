import gzip
import json
from pathlib import Path

from scripts import index_run
from scripts.evaluate import parse_args
from scripts.metrics import Scored


def write_rows(path, n):
    with gzip.open(path, "wt") as f:
        for i in range(n):
            f.write(json.dumps({"_evaluation": {"run_id": f"r{i}"}, "state": "", "questions": {}}) + "\n")


def run_ids(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(line)["_evaluation"]["run_id"] for line in f]


def test_shards_partition_the_rows(tmp_path):
    write_rows(tmp_path / "rows.jsonl.gz", 10)
    shards = index_run.write_shards(tmp_path / "rows.jsonl.gz", 3, tmp_path / "s")
    ids = [i for s in shards for i in run_ids(s)]
    assert sorted(ids) == sorted(f"r{i}" for i in range(10)) and len(shards) == 3


def test_shards_can_be_limited_to_ids(tmp_path):
    write_rows(tmp_path / "rows.jsonl.gz", 10)
    shards = index_run.write_shards(tmp_path / "rows.jsonl.gz", 2, tmp_path / "s", ids={"r3", "r7"})
    assert sorted(i for s in shards for i in run_ids(s)) == ["r3", "r7"]


def test_merge_keeps_the_last_attempt(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(), b.mkdir()
    (a / "results.jsonl").write_text(
        json.dumps({"run_id": "r1", "status": "error"}) + "\n" + json.dumps({"run_id": "r1", "status": "ok"}) + "\n")
    (b / "results.jsonl").write_text(json.dumps({"run_id": "r2", "status": "unsupported"}) + "\n")
    counts = index_run.merge([a, b], tmp_path / "m")
    assert counts == {"ok": 1, "unsupported": 1}
    assert len((tmp_path / "m" / "results.jsonl").read_text().splitlines()) == 2


def test_replace_overrides_by_run_id(tmp_path):
    base, over = tmp_path / "base.jsonl", tmp_path / "over.jsonl"
    base.write_text("".join(json.dumps({"run_id": f"r{i}", "status": "unsupported"}) + "\n" for i in range(3)))
    over.write_text(json.dumps({"run_id": "r1", "status": "ok"}) + "\n")
    assert index_run.replace(base, over, tmp_path / "out") == 1
    statuses = [json.loads(x)["status"] for x in (tmp_path / "out" / "results.jsonl").read_text().splitlines()]
    assert statuses == ["unsupported", "ok", "unsupported"]


def test_shard_command_drives_the_http_engine(tmp_path):
    cmd = index_run.shard_command(tmp_path / "s.jsonl.gz", tmp_path / "out", "http://127.0.0.1:9000")
    assert cmd[1:5] == ["-m", "decision_index", "run", "--engine"] and "base_url=http://127.0.0.1:9000" in cmd
    assert "--compact" in cmd


def test_harness_commands_get_absolute_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # the harness runs with cwd=SRC, so relative paths would resolve there
    shard = index_run.shard_command(Path("s.jsonl.gz"), Path("out"), "http://127.0.0.1:9000")
    score = index_run.score_command(Path("merged/results.jsonl"), Path("merged"))
    assert str(tmp_path / "s.jsonl.gz") in shard and str(tmp_path / "out") in shard
    assert str(tmp_path / "merged" / "results.jsonl") in score and str(tmp_path / "merged") in score


def test_index_scored_reads_choice_and_noul_answers(tmp_path):
    rows = {"r1": {"source": "index", "family": "X", "gold": {"a": "k", "b": True},
                   "questions": {"a": {"type": "choice", "criteria": {"j": "", "k": ""}}, "b": {"type": "noul"}}}}
    result = {"run_id": "r1", "status": "ok", "response": {"answers": {
        "a": {"type": "choice", "choice": "k", "probabilities": {"j": 0.2, "k": 0.8}},
        "b": {"type": "noul", "noul": 0.3}}}}
    (tmp_path / "results.jsonl").write_text(json.dumps(result) + "\n")
    items = index_run.index_scored(tmp_path / "results.jsonl", rows)
    assert items == [Scored("index", "X", "choice", 1, [0.2, 0.8]), Scored("index", "X", "noul", 1, [0.7, 0.3])]


def test_evaluate_cli_parses_each_command():
    assert parse_args(["offline", "--profile", "p", "--split", "eval"]).orders == "identity"
    assert parse_args(["index", "--profile", "p"]).shards == 8
    assert parse_args(["replace", "--profile", "p", "--base", "a", "--override", "b"]).command == "replace"
