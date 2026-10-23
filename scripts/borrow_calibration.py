"""Give a quantized profile its bf16 base's calibration (same T per type, noul b and fit), stamped for the quant.

usage: uv run python scripts/borrow_calibration.py --profile qwen3.8-27b-fp8 --layout blurb_header_reread
       [--from BASE] [--dry-run]
CPU only. Refuses a missing or stale base file, and never overwrites a quant's own fit.
"""

import argparse
import datetime
import json
from pathlib import Path

from gateway.calibration import STAMP_KEYS, stamp_for
from gateway.config import Settings
from gateway.layouts import load_layouts
from scripts.board import QUANTIZED
from scripts.m3_layouts import load_tokenizer


def stamp_of(profile: str, s: Settings, layout) -> dict:
    return stamp_for(load_tokenizer(profile), layout, s)


def borrowed(base: dict, base_profile: str, name: str, base_now: dict, quant_stamp: dict, date: str) -> dict:
    """The base file with the quant's stamp and a record of where it came from."""
    if base.get("format") != 2 or {k: base.get("stamp", {}).get(k) for k in STAMP_KEYS} != base_now:
        raise SystemExit(f"{base_profile}/{name}: stale or not a v2 file; recalibrate the base first")
    if quant_stamp["layout_sha256"] != base_now["layout_sha256"]:
        raise SystemExit(f"{name}: base and quant see different layout files")
    text = f"borrowed from {base_profile}/{name}"
    source = {"profile": base_profile, "file": name, "stamp": base["stamp"], "date": date}
    return base | {"stamp": quant_stamp, "borrowed": source,
                   "comments": [*base.get("comments", []), {"version": base.get("version", 0), "date": date, "text": text}]}


def refuse_overwrite(path: Path) -> None:
    """A quant's own fit stays; only an earlier borrow is replaced."""
    if path.exists() and "borrowed" not in json.loads(path.read_text()):
        raise SystemExit(f"{path} is the quant's own fit; move it aside to borrow instead")


def main(argv=None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True, help="the quantized profile")
    p.add_argument("--layout", required=True)
    p.add_argument("--from", dest="base", help="base profile (default: the one in scripts/board.py QUANTIZED)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    base_profile = args.base or QUANTIZED.get(args.profile)
    if base_profile is None:
        raise SystemExit(f"{args.profile} is not in QUANTIZED; pass --from BASE")
    layout = load_layouts()[args.layout]
    base_s, quant_s = Settings.from_profile(base_profile), Settings.from_profile(args.profile)
    base_files = sorted(base_s.data_dir(args.layout).glob("calibration*.json"))
    if not base_files:
        raise SystemExit(f"{base_profile} has no calibration for {args.layout}; calibrate it first")
    base_now, quant_stamp = stamp_of(base_profile, base_s, layout), stamp_of(args.profile, quant_s, layout)
    date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    for src in base_files:
        out = quant_s.data_dir(args.layout) / src.name
        data = borrowed(json.loads(src.read_text()), base_profile, src.name, base_now, quant_stamp, date)
        refuse_overwrite(out)
        if not args.dry_run:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(data, indent=1) + "\n")
        print(f"{'would write' if args.dry_run else 'wrote'} {out}")


if __name__ == "__main__":
    main()
