"""Sample GPU clocks, power and throttle reasons to a CSV, then summarize a time window.

usage: python scripts/gpu_telemetry.py sample --out CSV [--interval 5]   (runs until killed)
"""

import argparse
import csv
import datetime
import statistics
import subprocess
import time
from pathlib import Path

QUERY = "utilization.gpu,clocks.sm,clocks.mem,power.draw,power.limit,temperature.gpu,clocks_event_reasons.active"
HEADER = ["utc", "util", "sm_clock", "mem_clock", "power_draw", "power_limit", "temp", "throttle"]
THROTTLE_MASK = 0x4 | 0x8 | 0x20 | 0x40  # sw power cap, hw slowdown, sw thermal, hw thermal


def parse_sample(text: str) -> list[str]:
    return [p.strip() for p in text.strip().splitlines()[0].split(",")]


def sample_once() -> list[str]:
    done = subprocess.run(["nvidia-smi", f"--query-gpu={QUERY}", "--format=csv,noheader,nounits"],
                          capture_output=True, text=True, timeout=20, check=True)
    return parse_sample(done.stdout)


def sample(out: Path, interval: float) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fresh = not out.exists()
    with out.open("a", newline="") as f:
        writer = csv.writer(f)
        if fresh:
            writer.writerow(HEADER)
        while True:
            utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
            try:
                writer.writerow([utc, *sample_once()])
            except (OSError, subprocess.SubprocessError, IndexError):
                pass  # a missed sample is fine
            f.flush()
            time.sleep(interval)


def summarize(csv_path: Path, since: str | None = None, until: str | None = None) -> dict:
    with open(csv_path, newline="") as f:
        rows = [r for r in csv.DictReader(f) if (not since or r["utc"] >= since) and (not until or r["utc"] <= until)]
    if not rows:
        return {"samples": 0}

    def median(key):
        return statistics.median(float(r[key]) for r in rows)

    throttled = sum(1 for r in rows if int(r["throttle"], 16) & THROTTLE_MASK)
    return {"samples": len(rows), "median_sm_clock": median("sm_clock"), "median_power": median("power_draw"),
            "median_temp": median("temp"), "median_util": median("util"), "throttled_share": throttled / len(rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["sample"])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args()
    sample(args.out, args.interval)
