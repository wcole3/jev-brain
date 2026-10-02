"""Full Decision Index runs: the pinned harness, unchanged, sharded across processes against the gateway."""

import asyncio
import gzip
import json
from collections import Counter
from contextlib import ExitStack
from pathlib import Path

from scripts.index_suite import EDITION, PYTHON, SRC, SUITE
from scripts.metrics import Scored


def write_shards(rows_path: Path, n: int, out_dir: Path, ids: set[str] | None = None) -> list[Path]:
    """Round-robin rows into n files; with ids, only those rows (the length study's long rows)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [out_dir / f"shard-{i}.jsonl.gz" for i in range(n)]
    with ExitStack() as stack, gzip.open(rows_path, "rt", encoding="utf-8") as rows:
        files = [stack.enter_context(gzip.open(p, "wt", encoding="utf-8")) for p in paths]
        k = 0
        for line in rows:
            if ids is None or json.loads(line)["_evaluation"]["run_id"] in ids:
                files[k % n].write(line)
                k += 1
    return paths


def shard_command(shard: Path, out: Path, gateway: str) -> list[str]:
    """Absolute paths: the harness runs with cwd=SRC."""
    return [
        str(PYTHON), "-m", "decision_index", "run", "--engine", "http",
        "--option", f"base_url={gateway}", "--option", "model=jev-latest",
        "--rows", str(shard.resolve()), "--out", str(out.resolve()), "--compact",
    ]


async def run_all(commands: list[list[str]], env: dict) -> list[int]:
    procs = [await asyncio.create_subprocess_exec(*c, cwd=SRC, env=env) for c in commands]
    return [await p.wait() for p in procs]


def last_attempts(paths: list[Path]) -> dict[str, dict]:
    """The harness appends a retry after an error, so the last line per run_id is the answer."""
    latest: dict[str, dict] = {}
    for path in paths:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if not line.endswith("\n"):  # unflushed tail after a host crash, like the harness reader
                    break
                if line.strip():
                    r = json.loads(line)
                    latest[r["run_id"]] = r
    return latest


def write_results(results: dict[str, dict], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results.values()), encoding="utf-8")


def merge(shard_dirs: list[Path], out: Path) -> dict[str, int]:
    results = last_attempts([d / "results.jsonl" for d in shard_dirs if (d / "results.jsonl").exists()])
    write_results(results, out)
    return dict(Counter(r["status"] for r in results.values()))


def replace(base: Path, override: Path, out: Path) -> int:
    """Base results with override's rows swapped in by run_id (long rows rerun at a higher cap)."""
    results, new = last_attempts([base]), last_attempts([override])
    results.update({k: v for k, v in new.items() if k in results})
    write_results(results, out)
    return sum(k in results for k in new)


def score_command(results: Path, out: Path) -> list[str]:
    return [str(PYTHON), "-m", "decision_index", "score", "--edition", EDITION,
            "--results", str(results.resolve()), "--suite-dir", str(SUITE), "--out", str(out.resolve())]


def index_scored(results: Path, rows_by_id: dict[str, dict]) -> list[Scored]:
    """Gold-labelled choice/noul answers from a results file, for our ECE (the harness reports none)."""
    items = []
    for r in last_attempts([results]).values():
        row = rows_by_id.get(r["run_id"])
        if r["status"] != "ok" or row is None:
            continue
        for qid, a in r["response"]["answers"].items():
            gold, q = row["gold"].get(qid), row["questions"][qid]
            if gold is None:
                continue
            if q["type"] == "noul":
                items.append(Scored("index", row["family"], "noul", int(gold), [1 - a["noul"], a["noul"]]))
            elif q["type"] == "choice":
                names = list(q["criteria"])
                items.append(Scored("index", row["family"], "choice", names.index(gold),
                                    [a["probabilities"][n] for n in names]))
    return items
