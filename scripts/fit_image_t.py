"""Fit T_image, the choice temperature for image requests, on the non-suite vision calibration set.

usage: uv run python scripts/fit_image_t.py --collect FILE --profile P [--write] [--dev DEV_COLLECT [--out DIR]]
FILE is a vision_collect.py --rows collect of the vision-calib rows; suite collects are refused. T is fitted
under the profile's OPTION_ORDERS (the reads the gateway makes), so the collect must hold them.
Prints T and the NLL and ECE before (text T) and after. --write adds or replaces the image block of the
profile's header calibration file (Settings.calibration_path) and appends a comment; else nothing is written.
--dev scores a dev collect under the text T and T_image (ECE, NLL, accuracy); --out DIR also writes dev.json.
"""

import argparse
import json
from pathlib import Path

from gateway.calibration import IMAGE_STAMP_KEYS, STAMP_KEYS, load_calibration
from gateway.config import ROOT, Settings
from gateway.decide import blend
from scripts import metrics
from scripts.calibrate import history, now_iso
from scripts.calibrate_report import at_edge
from scripts.collect import records
from scripts.fit import LOG_T, fit_temperature
from scripts.vision_offline import MIN_FIT, Item, bare_stamp, items_of, split_config

MANIFEST = ROOT / "data" / "splits" / "vision-calib.json"
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


def check_text_stamp(collected: dict, file_stamp: dict, path: Path, collect: Path) -> None:
    """The collect must match the text calibration's stamp, so both describe the same prompts and weights."""
    if diff := [k for k in STAMP_KEYS if collected.get(k) != file_stamp.get(k)]:
        raise SystemExit(f"{collect} was collected under another stamp than {path}: {diff}")


def profile_settings(profile: str) -> Settings:
    return Settings.from_profile(profile)


def check_image_settings(collected: dict, s: Settings, collect: Path) -> None:
    """A block stamped with other image settings than the profile runs would stop the gateway at startup."""
    if collected.get("mm_processor_kwargs") != s.mm_processor_kwargs:
        raise SystemExit(f"{collect}: collected with mm_processor_kwargs {collected.get('mm_processor_kwargs')}, "
                         f"profile {s.profile} runs {s.mm_processor_kwargs}")


def served_items(recs: list[dict], orders: str, collect: Path) -> tuple[list[Item], dict[str, int]]:
    """The reads the gateway makes under the profile's orders; a collect without them is refused."""
    try:
        return items_of(recs, orders)
    except ValueError as e:
        raise SystemExit(f"{collect}: the profile serves orders {orders!r}; {e}") from e


def dev_records(dev: Path, profile: str, calib_stamp: dict) -> list[dict]:
    """A dev suite collect read like the calib one: same profile, header layout and stamp (commit aside)."""
    config = split_config(dev)
    if config.get("split") != "dev":
        raise SystemExit(f"--dev {dev} is split {config.get('split')!r}, not dev")
    if config.get("profile") != profile:
        raise SystemExit(f"--dev {dev}: collected on profile {config.get('profile')!r}, not {profile!r}")
    if config.get("layout") != LAYOUT or config.get("layout_file"):
        raise SystemExit(f"--dev {dev}: layout {config.get('layout')!r} is not {LAYOUT!r}")
    recs = list(records(dev))
    if not recs:
        raise SystemExit(f"--dev {dev}: no records")
    have = bare_stamp(recs, dev)
    if diff := sorted(k for k in have.keys() | calib_stamp.keys() if have.get(k) != calib_stamp.get(k)):
        raise SystemExit(f"--dev {dev} was collected under other stamps than the calib collect: {diff}")
    return recs


def dev_scores(recs: list[dict], orders: str, dev: Path, text_T: float, T: float) -> dict:
    items, skipped = served_items(recs, orders, dev)
    arms = {name: {"T": t} | {m: f(scored(items, t)) for m, f in (("ece", metrics.ece), ("nll", metrics.nll),
                                                                 ("accuracy", metrics.accuracy))}
            for name, t in (("text", text_T), ("image", T))}
    return {"collect": str(dev), "orders": orders, "rows": len(items), "skipped": skipped} | arms


def print_dev(d: dict) -> None:
    print(f"dev {d['rows']} rows, orders {d['orders']}:")
    for name in ("text", "image"):
        a = d[name]
        print(f"  {name} T {a['T']:.3f}: ECE {a['ece']:.4f}, NLL {a['nll']:.4f}, accuracy {a['accuracy']:.4f}")


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
    s = profile_settings(args.profile)
    path = s.calibration_path(LAYOUT)
    if not path.exists():
        raise SystemExit(f"{path} missing: T_image is added to a text calibration file")
    text_T = load_calibration(path, expect=None).T["choice"]
    data = json.loads(path.read_text())
    collected = bare_stamp(recs, args.collect)
    check_text_stamp(collected, data["stamp"], path, args.collect)
    check_image_settings(collected, s, args.collect)
    orders = s.option_orders
    dev = dev_records(args.dev, args.profile, collected) if args.dev else None
    items, skipped = served_items(recs, orders, args.collect)
    if len(items) < MIN_FIT:
        raise SystemExit(f"{args.collect}: {len(items)} scorable rows, fewer than {MIN_FIT}")
    T = fit_temperature([(i.reads, i.rec["gold"]) for i in items])
    edge = at_edge(T, LOG_T, log=True)
    moves = before_after(items, text_T, T)
    out = {"T": T, "edge": edge, "text_T": text_T, "rows": len(items), "skipped": skipped, "orders": orders} | moves
    print(f"T_image {T:.3f}{' (edge)' if edge else ''} on {len(items)} rows (skipped {skipped}), orders {orders}; "
          f"text T {text_T:.3f}")
    for name in ("nll", "ece"):
        print(f"{name.upper()} {moves[name]['before']:.4f} -> {moves[name]['after']:.4f}")
    if dev is not None:
        out["dev"] = dev_scores(dev, orders, args.dev, text_T, T)
        print_dev(out["dev"])
        if args.out:
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / "dev.json").write_text(json.dumps(out["dev"], indent=1) + "\n")
    if args.write:
        fit = {"source": "vision-calib", "rows": len(items), "orders": orders, "rows_sha256": config["rows_sha256"],
               "label": config["label"], "text_T": text_T, "edge": edge} | moves
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
    p.add_argument("--dev", type=Path, help="dev collect scored under the text T and the fitted T_image")
    p.add_argument("--out", type=Path, help="with --dev: directory for dev.json (else printed only)")
    return p.parse_args(argv)


def main(argv=None) -> dict:
    return run(parse_args(argv))


if __name__ == "__main__":
    main()
