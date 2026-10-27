"""Per-profile closing table: our latest Index and latency next to the Decision Index board.

usage: uv run python scripts/phase2_report.py [--readme]
Reads committed summaries only. Each row shows the settings its run used (from the summary's
Provenance), marked when they differ from what ships now. Writes docs/results/phase2-report.md;
--readme also replaces the table between the phase2-table markers in README.md.
"""

import argparse
import ast
import json
import re
from pathlib import Path

from gateway.calibration import FLOOR
from gateway.config import ROOT, Settings, read_env_file
from scripts.board import BOARD, MATCHES, fmt

RESULTS = ROOT / "docs" / "results"
README = ROOT / "README.md"
START, END = "<!-- phase2-table -->", "<!-- /phase2-table -->"
TYPES = ("choice", "score", "noul")
NOTES = {
    "†": "† the run's layout, orders or calibration differ from what ships now (or the calibration file is newer).",
    "‡": "‡ the latency run's layout, orders or calibration differ from the Index run's.",
    "T": "Calibration T is listed as choice/score/noul, a choice curve as (a+b ln n) for n options; b is the noul yes-offset.",
}


def latest(profile: str, suffix: str) -> Path | None:
    """Newest `<UTC stamp>-<suffix>` dir; Index runs are top level, latency runs live in archive/."""
    where = RESULTS / "archive" if suffix == "latency" else RESULTS
    dirs = sorted((where / profile).glob(f"*-{suffix}"))
    return dirs[-1] if dirs else None


def read_summary(run: Path) -> list[str]:
    path = run / "summary.md"
    if not path.exists():
        raise SystemExit(f"{path}: summary.md is missing")
    return path.read_text(encoding="utf-8").splitlines()


def table_row(run: Path, prefix: str) -> dict[str, str]:
    """The summary row starting with `prefix`, keyed by its table's header names."""
    lines = read_summary(run)
    header = next((x for x in lines if x.startswith("| entry")), None)
    row = next((x for x in lines if x.startswith(prefix)), None)
    if header is None or row is None:
        raise SystemExit(f"{run / 'summary.md'}: no table header or no row {prefix!r}")
    return dict(zip(cells(header), cells(row), strict=True))


def cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def number(row: dict[str, str], column: str, run: Path) -> float | None:
    if column not in row:
        raise SystemExit(f"{run / 'summary.md'}: row has no column {column!r} (has {list(row)})")
    return None if row[column] == "n/a" else float(row[column])


def provenance(run: Path) -> dict[str, str]:
    """The `- key: value` lines above the first table."""
    meta = {}
    for line in read_summary(run):
        if line.startswith("|"):
            break
        key, sep, value = line.removeprefix("- ").partition(": ")
        if line.startswith("- ") and sep:
            meta[key] = value
    return meta


def run_settings(run: Path) -> dict:
    """Layout, orders and T/b the run used: `calibration:` (new runs) or `temperatures:` (old runs)."""
    meta = provenance(run)
    try:
        layout = meta["prompt_layout"]
        raw = ast.literal_eval(meta.get("calibration") or meta["temperatures"])[layout]
    except (KeyError, ValueError, SyntaxError) as e:
        raise SystemExit(f"{run / 'summary.md'}: provenance lacks usable run settings ({e!r})") from e
    T, b = (raw["T"], raw.get("b", 0.0)) if "T" in raw else (raw, 0.0)
    return {"layout": layout, "orders": meta["option_orders"], "T": T, "b": b, "stamp": digits(meta["timestamp"])}


def digits(stamp: str) -> str:
    """'2026-10-02T124707Z' and '2026-10-03T00:39:27Z' both become sortable digit strings."""
    return re.sub(r"\D", "", stamp)


def shipped_settings(profile: str) -> dict:
    env = read_env_file(ROOT / "profiles" / f"{profile}.env")
    layout = env["PROMPT_LAYOUT"]
    s = Settings.from_env({**env, "DATA_ROOT": str(ROOT / "data")})
    data = json.loads(s.calibration_path(layout).read_text())
    T = {t: data["types"][t]["T"] for t in TYPES}
    return {"layout": layout, "orders": env["OPTION_ORDERS"], "T": T, "b": data["types"]["noul"].get("b", 0.0),
            "version": data["version"], "stamp": digits(data["date"])}


def rounded(T: float | dict) -> float | tuple:
    """A constant T, or a choice curve {a, b, floor} as a tuple, rounded so files and summaries compare equal."""
    return tuple(round(T.get(k, FLOOR), 6) for k in ("a", "b", "floor")) if isinstance(T, dict) else round(T, 6)


def settings_key(s: dict) -> tuple:
    return s["layout"], s["orders"], tuple(rounded(s["T"][t]) for t in TYPES), round(s["b"], 6)


def same_settings(a: dict, b: dict) -> bool:
    return settings_key(a) == settings_key(b)


def profile_row(profile: str) -> dict:
    shipped = shipped_settings(profile)
    row = {"profile": profile, "shipped": shipped, "index": None, "ece": None, "coverage": None, "run": None,
           "median_ms": None, "p95_ms": None, "latency_run": None, "latency_differs": False, "stale": False}
    if index_dir := latest(profile, "index"):
        cells = table_row(index_dir, "| **ours: ")
        row |= {"index": number(cells, "Index", index_dir), "ece": number(cells, "ECE", index_dir),
                "coverage": number(cells, "coverage", index_dir), "run": run_settings(index_dir)}
        row["stale"] = not same_settings(row["run"], shipped) or shipped["stamp"] > row["run"]["stamp"]
    if latency_dir := latest(profile, "latency"):
        cells = table_row(latency_dir, "| **ours** ")
        row |= {"median_ms": number(cells, "median ms", latency_dir), "p95_ms": number(cells, "p95 ms", latency_dir),
                "latency_run": latency_dir.name}
        row["latency_differs"] = row["run"] is not None and not same_settings(run_settings(latency_dir), row["run"])
    return row


def t_text(T: float | dict) -> str:
    return f"({T['a']:.3g}{T['b']:+.3g} ln n)" if isinstance(T, dict) else f"{T:.3g}"


def calibration_cell(s: dict) -> str:
    T = [s["T"][t] for t in TYPES]
    if all(x == 1.0 for x in T):
        text = "T=1 (none)"
    elif all(x == T[0] for x in T) and not isinstance(T[0], dict):
        text = f"T={T[0]:.4g}"
    else:
        text = "T=" + "/".join(t_text(x) for x in T)
    return text + (f", b={s['b']:.2f}" if s["b"] else "")


def run_cells(row: dict) -> str:
    run = row["run"]
    if run is None:
        return "n/a | n/a"
    return f"{run['layout']} / {run['orders']} | {calibration_cell(run)}"


def markdown(rows: list[dict]) -> str:
    head = "| entry | Index | Full | ECE | coverage | median ms | p95 ms | run layout / orders | run calibration "
    lines = [head + "| shipped now | latency run |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        s = r["shipped"]
        shipped = f"{s['layout']} / {s['orders']} / v{s['version']}"
        latency = (r["latency_run"] or "n/a") + (" ‡" if r["latency_differs"] else "")
        lines.append(f"| **{r['profile']}**{' †' if r['stale'] else ''} | {fmt(r['index'], 2)} | — | {fmt(r['ece'], 3)} "
                     f"| {fmt(r['coverage'], 3)} | {fmt(r['median_ms'], 1)} | {fmt(r['p95_ms'], 1)} "
                     f"| {run_cells(r)} | {shipped} | {latency} |")
        for key in MATCHES.get(r["profile"], []):
            e = BOARD[key]
            lines.append(f"| {e['name']} | {e['index']:.2f} | {e['full']:.2f} | {e['ece']:.3f} | board | {e['median_ms']:.1f} | n/a | | | | |")
    used = ["T"] + [m for m, flag in (("†", "stale"), ("‡", "latency_differs")) if any(r[flag] for r in rows)]
    return "\n".join(lines) + "\n\n" + "\n".join(f"- {NOTES[k]}" for k in used) + "\n"


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
    (RESULTS / "phase2-report.md").write_text(table, encoding="utf-8")
    if args.readme:
        README.write_bytes(replace_between_markers(README.read_bytes().decode("utf-8"), table).encode("utf-8"))
    print(table, end="")


if __name__ == "__main__":
    main()
