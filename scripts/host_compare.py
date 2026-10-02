"""Compare hosts: time the same latency, throughput and Index-subset work, then lay results side by side.

usage: uv run python scripts/host_compare.py make-ids | run PROFILE [--gateway URL] [--vllm URL] | report DIR...
"""

import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

from scripts import decision_rows, gpu_telemetry, host_info
from scripts.bench import git_revision
from scripts.bench_report import percentile

ROOT = Path(__file__).resolve().parent.parent
IDS = Path("data/splits/compare-2k.json")
UTC = "%Y-%m-%dT%H:%M:%S"
PHASES = {"latency": "*-latency", "bench": "*-quick", "index": "*-index-subset"}


def make_ids(meta: list[dict], dev_ids: list[str], target: int = 2000) -> list[str]:
    """Every k-th whole group of the dev split, k chosen so the row count lands nearest the target."""
    dev = set(dev_ids)
    groups: dict[tuple, list[dict]] = {}
    for m in meta:
        if m["id"] in dev:
            groups.setdefault((m["meta"]["catalog_id"], m["meta"]["group_id"]), []).append(m)
    ordered = sorted(groups.values(), key=lambda g: (g[0]["meta"]["catalog_id"], g[0]["meta"]["payload_chars"], g[0]["id"]))
    picks = [[m["id"] for g in ordered[::k] for m in g] for k in range(1, len(ordered) + 1)]
    return min(picks, key=lambda ids: abs(len(ids) - target))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def parse_latency(raw: Path) -> dict:
    ms = [r["ms"] for r in read_jsonl(raw) if r.get("status") == 200]
    return {"median_ms": percentile(ms, 0.5), "p95_ms": percentile(ms, 0.95)}


def parse_bench(raw: Path) -> dict:
    return {f"x{r['workers']}": r["requests_per_s"] for r in read_jsonl(raw)
            if r.get("test") == "throughput" and "requests_per_s" in r}


def utc_now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime(UTC)


def result_dirs(profile: str, pattern: str) -> set[Path]:
    return set((ROOT / "docs" / "results" / profile).glob(pattern))


def created_since(profile: str, pattern: str, before: set[Path]) -> Path:
    """The newest result dir a step added; fail loudly rather than pick up an older run's."""
    if not (new := result_dirs(profile, pattern) - before):
        raise SystemExit(f"{pattern}: the step created no result dir under docs/results/{profile}")
    return max(new)


def merged_rows(profile: str, subset_dir: Path) -> int:
    """Rows the Index subset run actually produced (ok or unsupported), from its merged results."""
    merged = ROOT / ".cache" / "index-runs" / profile / subset_dir.name.removesuffix("-index-subset") / "merged"
    return sum(r["status"] in ("ok", "unsupported") for r in read_jsonl(merged / "results.jsonl"))


def script(name: str, *args: str) -> list[str]:
    return [sys.executable, str(ROOT / "scripts" / name), *args]


def run(profile: str, gateway: str, vllm: str) -> Path:
    out = ROOT / "docs" / "results" / profile / f"{datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H%M%SZ')}-host"
    out.mkdir(parents=True)
    csv = out / "telemetry.csv"
    steps = {
        "latency": script("latency.py", "--profile", profile, "--gateway", gateway),
        "bench": script("bench.py", "--profile", profile, "--quick", "--gateway", gateway, "--vllm", vllm),
        "index": script("evaluate.py", "index", "--profile", profile, "--ids", str(ROOT / IDS), "--shards", "4",
                        "--gateway", gateway, "--vllm", vllm),
    }
    sampler = subprocess.Popen(script("gpu_telemetry.py", "sample", "--out", str(csv), "--interval", "5"), cwd=ROOT)
    phases = {}
    try:
        for name, cmd in steps.items():
            before = result_dirs(profile, PHASES[name])
            start, began = utc_now(), time.monotonic()
            subprocess.run(cmd, cwd=ROOT, check=True)
            phases[name] = {"start": start, "end": utc_now(), "wall_s": time.monotonic() - began,
                            "dir": str(created_since(profile, PHASES[name], before).relative_to(ROOT))}
        sampler_died = sampler.poll() is not None
    finally:
        sampler.terminate()
        sampler.wait(timeout=30)
    for p in phases.values():
        p["telemetry"] = gpu_telemetry.summarize(csv, p["start"], p["end"]) if csv.exists() else {"samples": 0}
        if sampler_died or not p["telemetry"]["samples"]:
            p["telemetry"] = "unavailable (" + ("sampler died" if sampler_died else "no samples in window") + ")"
    listed = len(json.loads((ROOT / IDS).read_text())["ids"])
    rows = merged_rows(profile, ROOT / phases["index"]["dir"])
    host = {
        "profile": profile, "repo commit": git_revision(), "fingerprint": host_info.collect(), "phases": phases,
        "latency": parse_latency(ROOT / phases["latency"]["dir"] / "raw.jsonl"),
        "throughput": parse_bench(ROOT / phases["bench"]["dir"] / "raw.jsonl"),
        "index_rows_listed": listed, "index_rows": rows, "index_rows_per_min": rows / (max(phases["index"]["wall_s"], 1) / 60),
    }
    (out / "host.json").write_text(json.dumps(host, indent=2) + "\n")
    (out / "summary.md").write_text(f"# {profile} host run\n\n{host_info.summary_line(host['fingerprint'])}\n\n"
                                    f"{report([out])}\n")
    print(out)
    return out


def metrics(host: dict) -> dict[str, str]:
    fp, lat, thr = host["fingerprint"], host["latency"], host["throughput"]
    out = {"gpu": str(fp.get("gpu_name")), "power limit (W)": str(fp.get("power_limit_w")),
           "latency median (ms)": f"{lat['median_ms']:.0f}", "latency p95 (ms)": f"{lat['p95_ms']:.0f}"}
    out |= {f"throughput {k} (req/s)": f"{thr[k]:.2f}" for k in ("x1", "x4", "x16") if k in thr}
    out["index rows/min"] = f"{host['index_rows_per_min']:.1f}"
    for name, phase in host["phases"].items():
        t = phase["telemetry"]
        if isinstance(t, dict) and t.get("samples"):
            out[f"{name} sm clock (MHz)"] = f"{t['median_sm_clock']:.0f}"
            out[f"{name} throttled"] = f"{t['throttled_share']:.0%}"
    return out


def report(dirs: list[Path]) -> str:
    hosts = [json.loads((Path(d) / "host.json").read_text()) for d in dirs]
    columns = [metrics(h) for h in hosts]
    names = [h["fingerprint"].get("hostname") or Path(d).name for h, d in zip(hosts, dirs, strict=True)]
    keys = list(dict.fromkeys(k for c in columns for k in c))
    lines = ["| metric | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    lines += [f"| {k} | " + " | ".join(c.get(k, "n/a") for c in columns) + " |" for k in keys]
    return "\n".join(lines)


def cmd_make_ids(_args) -> None:
    dev = json.loads((ROOT / "data/splits/index-dev.json").read_text())
    ids = make_ids(decision_rows.index_meta(), dev["ids"])
    meta = {"from": "index-dev", "rule": "every k-th whole linked group, ordered by benchmark and payload length",
            "rows": len(ids), "edition": dev["meta"].get("edition")}
    (ROOT / IDS).write_text(json.dumps({"meta": meta, "ids": ids}, indent=0) + "\n")
    print(f"{IDS}: {len(ids)} rows")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("make-ids")
    r = sub.add_parser("run")
    r.add_argument("profile")
    r.add_argument("--gateway", default="http://127.0.0.1:9000")
    r.add_argument("--vllm", default="http://127.0.0.1:8000")
    sub.add_parser("report").add_argument("dirs", nargs="+", type=Path)
    args = p.parse_args(argv)
    if args.command == "make-ids":
        cmd_make_ids(args)
    elif args.command == "run":
        run(args.profile, args.gateway, args.vllm)
    else:
        print(report(args.dirs))


if __name__ == "__main__":
    main()
