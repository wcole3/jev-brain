"""Per-profile closing table: our latest Index and latency next to the Decision Index board.

usage: uv run python scripts/phase2_report.py [--readme]
Reads committed summaries only. Writes docs/results/phase2-report.md; --readme also
replaces the table between the phase2-table markers in README.md.
"""

import argparse
import json
from pathlib import Path

from gateway.config import ROOT, read_env_file
from scripts.board import BOARD, MATCHES, fmt

RESULTS = ROOT / "docs" / "results"
README = ROOT / "README.md"
START, END = "<!-- phase2-table -->", "<!-- /phase2-table -->"


def latest(profile: str, suffix: str) -> Path | None:
    """Newest `<UTC stamp>-<suffix>` dir; `-index` matches `-vast-index` but not `-index-subset`."""
    dirs = sorted((RESULTS / profile).glob(f"*-{suffix}"))
    return dirs[-1] if dirs else None


def number(cell: str) -> float | None:
    return None if cell.strip() == "n/a" else float(cell)


def ours_row(summary: Path, prefix: str) -> list[str]:
    """Cells of the summary table row that starts with `prefix`."""
    line = next(x for x in summary.read_text().splitlines() if x.startswith(prefix))
    return [c.strip() for c in line.strip("|").split("|")]


def index_part(profile: str) -> dict:
    run = latest(profile, "index")
    if run is None:
        return {"index": None, "ece": None, "coverage": None, "index_run": None}
    _, index, ece, _, coverage = ours_row(run / "summary.md", "| **ours: ")
    return {"index": number(index), "ece": number(ece), "coverage": number(coverage), "index_run": run.name}


def latency_part(profile: str) -> dict:
    run = latest(profile, "latency")
    if run is None:
        return {"median_ms": None, "p95_ms": None, "latency_run": None}
    _, median, p95 = ours_row(run / "summary.md", "| **ours** ")
    return {"median_ms": number(median), "p95_ms": number(p95), "latency_run": run.name}


def shipped_part(profile: str) -> dict:
    env = read_env_file(ROOT / "profiles" / f"{profile}.env")
    layout = env["PROMPT_LAYOUT"]
    file = ROOT / "data" / profile / layout / "calibration.json"
    return {"layout": layout, "orders": env["OPTION_ORDERS"], "calibration": json.loads(file.read_text())["version"]}


def profile_row(profile: str) -> dict:
    return {"profile": profile, **index_part(profile), **latency_part(profile), **shipped_part(profile)}


def markdown(rows: list[dict]) -> str:
    head = ["| entry | Index | ECE | coverage | median ms | p95 ms | layout | orders | calibration |",
            "|---|---|---|---|---|---|---|---|---|"]
    lines = list(head)
    for r in rows:
        lines.append(f"| **{r['profile']}** | {fmt(r['index'], 2)} | {fmt(r['ece'], 3)} | {fmt(r['coverage'], 3)} "
                     f"| {fmt(r['median_ms'], 1)} | {fmt(r['p95_ms'], 1)} | {r['layout']} | {r['orders']} "
                     f"| v{r['calibration']} |")
        for key in MATCHES[r["profile"]]:
            e = BOARD[key]
            lines.append(f"| {e['name']} | {e['index']:.2f} | {e['ece']:.3f} | board | {e['median_ms']:.1f} | n/a | | | |")
    return "\n".join(lines) + "\n"


def replace_between_markers(text: str, table: str) -> str:
    """Swap the text between the markers; everything outside them stays byte-identical."""
    before, start, rest = text.partition(START)
    _, end, after = rest.partition(END)
    if not (start and end):
        raise SystemExit(f"README is missing the {START} / {END} markers")
    return f"{before}{start}\n{table}{end}{after}"


def main(argv=None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--readme", action="store_true", help="also update the table in README.md")
    args = p.parse_args(argv)
    table = markdown([profile_row(profile) for profile in MATCHES])
    (RESULTS / "phase2-report.md").write_text(table)
    if args.readme:
        README.write_bytes(replace_between_markers(README.read_bytes().decode(), table).encode())
    print(table, end="")


if __name__ == "__main__":
    main()
