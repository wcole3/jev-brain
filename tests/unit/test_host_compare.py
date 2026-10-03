import json
from pathlib import Path

import pytest

from scripts import host_compare


def meta(catalog, group, n_rows, start=0):
    return [{"id": f"{catalog}:{group}:{i}", "meta": {"catalog_id": catalog, "group_id": group, "payload_chars": i}}
            for i in range(start, start + n_rows)]


def fake_meta():
    rows = []
    for g in range(100):
        rows += meta(1 + g % 3, f"g{g}", 1 + g % 4)
    return rows


def test_make_ids_is_deterministic_whole_groups_near_target():
    rows = fake_meta()
    dev = [r["id"] for r in rows]
    a = host_compare.make_ids(rows, dev, target=100)
    assert a == host_compare.make_ids(rows, dev, target=100)
    assert abs(len(a) - 100) <= 20 and len(a) < len(dev)
    chosen = set(a)
    for r in rows:  # a group is in or out as a whole
        group = {x["id"] for x in rows if x["meta"]["group_id"] == r["meta"]["group_id"]
                 and x["meta"]["catalog_id"] == r["meta"]["catalog_id"]}
        assert group <= chosen or not group & chosen


def test_make_ids_only_uses_dev_ids():
    rows = fake_meta()
    dev = [r["id"] for r in rows[:150]]
    assert set(host_compare.make_ids(rows, dev, target=50)) <= set(dev)


def write_jsonl(path, records):
    path.write_text("".join(json.dumps(r) + "\n" for r in records))


def test_parse_latency_median_p95_skips_errors(tmp_path):
    f = tmp_path / "raw.jsonl"
    write_jsonl(f, [{"status": 200, "ms": ms} for ms in range(1, 101)] + [{"status": 500, "ms": 9999}])
    assert host_compare.parse_latency(f) == {"median_ms": 51, "p95_ms": 96}


def test_parse_bench_throughput_by_workers(tmp_path):
    f = tmp_path / "raw.jsonl"
    write_jsonl(f, [{"test": "latency", "ms": 3}, {"test": "throughput", "error": "X"},
                    {"test": "throughput", "workers": 1, "requests_per_s": 1.5},
                    {"test": "throughput", "workers": 4, "requests_per_s": 4.0},
                    {"test": "throughput", "workers": 16, "requests_per_s": 9.25}])
    assert host_compare.parse_bench(f) == {"x1": 1.5, "x4": 4.0, "x16": 9.25}


def host(name, gpu, median, rows_per_min):
    return {"fingerprint": {"hostname": name, "gpu_name": gpu, "power_limit_w": 600},
            "phases": {"index": {"wall_s": 600, "telemetry": {"median_sm_clock": 2400, "throttled_share": 0.0}}},
            "latency": {"median_ms": median, "p95_ms": median * 2},
            "throughput": {"x1": 1.0, "x4": 3.0, "x16": 8.0}, "index_rows_per_min": rows_per_min}


def test_report_side_by_side(tmp_path):
    dirs = []
    for name, gpu, med, rpm in (("home", "RTX PRO 6000", 120.0, 200.0), ("vast", "H100", 80.0, 310.5)):
        d = tmp_path / name
        d.mkdir()
        (d / "host.json").write_text(json.dumps(host(name, gpu, med, rpm)))
        dirs.append(d)
    table = host_compare.report(dirs)
    lines = table.splitlines()
    assert lines[0].startswith("| metric |") and "home" in lines[0] and "vast" in lines[0]
    row = next(line for line in lines if line.startswith("| latency median"))
    assert "120" in row and "80" in row
    assert any(line.startswith("| index rows/min") and "310.5" in line for line in lines)


def test_run_phases_in_order_and_writes_host_json(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(host_compare, "ROOT", tmp_path)
    monkeypatch.setattr(host_compare, "git_revision", lambda: "abc")
    ids = tmp_path / "data/splits"
    ids.mkdir(parents=True)
    (ids / "compare-2k.json").write_text(json.dumps({"ids": ["a", "b", "c"]}))
    results = tmp_path / "docs/results/archive/p"
    for old in ("1999-latency", "1999-quick", "1999-index-subset"):  # earlier runs must be ignored
        (results / old).mkdir(parents=True)
    summarized = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        script = cmd[1].rsplit("/", 1)[-1]
        if script == "latency.py":
            d = results / "2026-latency"
            d.mkdir(parents=True)
            write_jsonl(d / "raw.jsonl", [{"status": 200, "ms": 10}])
        elif script == "bench.py":
            d = results / "2026-quick"
            d.mkdir(parents=True, exist_ok=True)
            write_jsonl(d / "raw.jsonl", [{"test": "throughput", "workers": 1, "requests_per_s": 2.0}])
        elif script == "evaluate.py":
            (results / "2026-index-subset").mkdir(parents=True)
            merged = tmp_path / ".cache/index-runs/p/2026/merged"
            merged.mkdir(parents=True)
            write_jsonl(merged / "results.jsonl", [{"status": "ok"}, {"status": "unsupported"}, {"status": "error"}])

    class Sampler:
        def poll(self):
            return None

        def terminate(self):
            calls.append("stop")

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(host_compare.subprocess, "run", fake_run)
    monkeypatch.setattr(host_compare.subprocess, "Popen", lambda cmd, **kw: calls.append(cmd) or Path(cmd[cmd.index("--out") + 1]).touch() or Sampler())
    monkeypatch.setattr(host_compare.host_info, "collect", lambda: {"hostname": "h"})
    monkeypatch.setattr(host_compare.gpu_telemetry, "summarize", lambda csv, since, until: summarized.append((since, until)) or {"samples": 1, "median_sm_clock": 2400, "throttled_share": 0.0})
    out = host_compare.run("p", "http://g", "http://v")
    names = [c[1].rsplit("/", 1)[-1] for c in calls if isinstance(c, list)]
    assert names == ["gpu_telemetry.py", "latency.py", "bench.py", "evaluate.py"] and calls[-1] == "stop"
    data = json.loads((out / "host.json").read_text())
    assert data["latency"]["median_ms"] == 10 and data["throughput"]["x1"] == 2.0
    assert set(data["phases"]) == {"latency", "bench", "index"} and data["index_rows_per_min"] > 0
    assert data["index_rows"] == 2 and data["index_rows_listed"] == 3
    assert data["phases"]["latency"]["dir"].endswith("2026-latency")
    assert summarized == [(data["phases"][n]["start"], data["phases"][n]["end"]) for n in ("latency", "bench", "index")]
    assert (out / "summary.md").exists() and out.name.endswith("-host")


def test_run_without_new_result_dir_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(host_compare, "ROOT", tmp_path)
    (tmp_path / "docs/results/archive/p/1999-latency").mkdir(parents=True)
    monkeypatch.setattr(host_compare.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(host_compare.subprocess, "Popen", lambda *a, **k: type("S", (), {
        "poll": lambda s: None, "terminate": lambda s: None, "wait": lambda s, timeout=None: 0})())
    with pytest.raises(SystemExit, match="created no result dir"):
        host_compare.run("p", "g", "v")


def test_run_marks_telemetry_unavailable_when_sampler_died(tmp_path, monkeypatch):
    results = tmp_path / "docs/results/archive/p"
    monkeypatch.setattr(host_compare, "ROOT", tmp_path)
    monkeypatch.setattr(host_compare, "git_revision", lambda: "abc")
    (tmp_path / "data/splits").mkdir(parents=True)
    (tmp_path / "data/splits/compare-2k.json").write_text(json.dumps({"ids": ["a"]}))

    def fake_run(cmd, **kw):
        name = cmd[1].rsplit("/", 1)[-1]
        d = results / {"latency.py": "2-latency", "bench.py": "2-quick", "evaluate.py": "2-index-subset"}[name]
        d.mkdir(parents=True)
        write_jsonl(d / "raw.jsonl", [{"status": 200, "ms": 1, "test": "throughput", "workers": 1, "requests_per_s": 1}])
        if name == "evaluate.py":
            (tmp_path / ".cache/index-runs/p/2/merged").mkdir(parents=True)
            write_jsonl(tmp_path / ".cache/index-runs/p/2/merged/results.jsonl", [{"status": "ok"}])

    dead = type("S", (), {"poll": lambda s: 1, "terminate": lambda s: None, "wait": lambda s, timeout=None: 0})()
    monkeypatch.setattr(host_compare.subprocess, "run", fake_run)
    monkeypatch.setattr(host_compare.subprocess, "Popen", lambda *a, **k: dead)
    monkeypatch.setattr(host_compare.host_info, "collect", lambda: {"hostname": "h"})
    data = json.loads((host_compare.run("p", "g", "v") / "host.json").read_text())
    assert data["phases"]["index"]["telemetry"] == "unavailable (sampler died)"
