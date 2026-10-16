"""Fit T_image, the choice temperature for image requests, on the non-suite vision calibration set.

usage: uv run python scripts/fit_image_t.py --collect FILE --profile P [--write]
FILE is a vision_collect.py --rows collect of the vision-calib rows; suite collects are refused.
Prints T and the NLL and ECE before (text T) and after. --write adds or replaces the image block
of data/<P>/header/calibration.json and appends a comment; without it nothing is written.
"""

import argparse
import json
from pathlib import Path

from gateway.calibration import IMAGE_STAMP_KEYS, STAMP_KEYS, load_calibration
from gateway.config import ROOT
from gateway.decide import blend
from scripts import metrics
from scripts.calibrate import history, now_iso
from scripts.collect import records
from scripts.fit import fit_temperature
from scripts.vision_offline import MIN_FIT, Item, bare_stamp, items_of, split_config

MANIFEST = ROOT / "data" / "splits" / "vision-calib.json"
DATA = ROOT / "data"
LAYOUT = "header"  # the shipped layout whose calibration file carries the image block


def check_config(config: dict, profile: str, collect: Path) -> None:
    """Only the vetted non-suite set can fit a shipping T_image, read with the profile's header layout."""
    if "rows" not in config:
        raise SystemExit(f"{collect}: not a --rows collect (split {config.get('split')!r}); "
                         "T_image fits on the vision-calib rows only")
    want = json.loads(MANIFEST.read_text())["meta"]["rows_sha256"]
    if config.get("rows_sha256") != want:
        raise SystemExit(f"{collect}: rows_sha256 {config.get('rows_sha256')} is not the vision-calib "
                         f"manifest's {want} ({MANIFEST})")
    if config.get("profile") != profile:
        raise SystemExit(f"{collect}: collected on profile {config.get('profile')!r}, not {profile!r}")
    if config.get("layout") != LAYOUT or config.get("layout_file"):
        raise SystemExit(f"{collect}: layout {config.get('layout')!r} is not the file's layout {LAYOUT!r}")


def check_stamp(collected: dict, file_stamp: dict, path: Path, collect: Path) -> None:
    """The collect must match the text calibration's stamp, so both describe the same prompts and weights."""
    if diff := [k for k in STAMP_KEYS if collected.get(k) != file_stamp.get(k)]:
        raise SystemExit(f"{collect} was collected under another stamp than {path}: {diff}")


def scored(items: list[Item], T: float) -> list[metrics.Scored]:
    return [metrics.Scored("vision-calib", i.rec["benchmark"], "choice", i.rec["gold"], blend(i.reads, T))
            for i in items]


def before_after(items: list[Item], text_T: float, T: float) -> dict:
    before, after = scored(items, text_T), scored(items, T)
    return {name: {"before": f(before), "after": f(after)} for name, f in (("nll", metrics.nll), ("ece", metrics.ece))}


def write_block(path: Path, data: dict, block: dict, text: str) -> None:
    version, comments = history(path)
    version, date = version + 1, now_iso()
    comments.append({"version": version, "date": date, "text": text})
    data |= {"version": version, "date": date, "comments": comments, "image": block}
    path.write_text(json.dumps(data, indent=1) + "\n")


def run(args) -> dict:
    config = split_config(args.collect)
    check_config(config, args.profile, args.collect)
    recs = list(records(args.collect))
    if not recs:
        raise SystemExit(f"{args.collect}: no records")
    path = DATA / args.profile / LAYOUT / "calibration.json"
    if not path.exists():
        raise SystemExit(f"{path} missing: T_image is added to a text calibration file")
    text_T = load_calibration(path, expect=None).T["choice"]
    data = json.loads(path.read_text())
    collected = bare_stamp(recs, args.collect)
    check_stamp(collected, data["stamp"], path, args.collect)
    orders = config["orders"]
    try:
        items, skipped = items_of(recs, orders)
    except ValueError as e:
        raise SystemExit(str(e)) from e
    if len(items) < MIN_FIT:
        raise SystemExit(f"{args.collect}: {len(items)} scorable rows, fewer than {MIN_FIT}")
    T = fit_temperature([(i.reads, i.rec["gold"]) for i in items])
    moves = before_after(items, text_T, T)
    out = {"T": T, "text_T": text_T, "rows": len(items), "skipped": skipped, "orders": orders} | moves
    print(f"T_image {T:.3f} on {len(items)} rows (skipped {skipped}), orders {orders}; text T {text_T:.3f}")
    for name in ("nll", "ece"):
        print(f"{name.upper()} {moves[name]['before']:.4f} -> {moves[name]['after']:.4f}")
    if args.write:
        fit = {"source": "vision-calib", "rows": len(items), "orders": orders, "rows_sha256": config["rows_sha256"],
               "label": config["label"], "text_T": text_T} | moves
        block = {"T": T, "stamp": {k: collected[k] for k in IMAGE_STAMP_KEYS}, "fit": fit}
        text = f"T_image {T:.3f} fitted on vision-calib ({len(items)} rows, orders {orders})"
        write_block(path, data, block, text)
        print(f"wrote the image block to {path}")
    return out


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--collect", type=Path, required=True)
    p.add_argument("--profile", required=True)
    p.add_argument("--write", action="store_true", help="add the image block to the profile's header calibration")
    return p.parse_args(argv)


def main(argv=None) -> dict:
    return run(parse_args(argv))


if __name__ == "__main__":
    main()
