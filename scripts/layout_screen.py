"""Round-4 pair screen: one collected prompt arm against another on the same questions, on CPU.

usage:
  uv run python scripts/layout_screen.py --profile P --arm A --control C
T per type on each arm's calib-600 identity reads (mean-prob, b = 0), then index-dev-2k (text) and image dev on every
question both arms answered, paired against the control. Never reads holdout rows.
"""

import argparse
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from gateway.layouts import Layout, load_layout, load_layouts
from scripts import host_info
from scripts import label_screen as ls
from scripts.bench import git_revision
from scripts.evaluate import now
from scripts.experiment_layouts import repo_relative
from scripts.splits import rows_for
from scripts.vision_offline import split_config

TITLE = "R4 pair screen"
SPLITS = ("calib-600", "index-dev-2k")
SAME_IMAGE = ("profile", "split", "env")  # image collect config keys both arms must share


@dataclass(frozen=True)
class Arm:
    text: str  # text collects are TEXT/<profile>/<split>-<text>.jsonl.gz
    image: str  # the image collect is VISION/<profile>/<image>/dev.jsonl.gz
    layout: str  # the layout name its records carry


ARMS = {"letters": Arm("letters", "labels-letters", "labels-letters"),
        "decider": Arm("decider", "r4-decider", "decider_chat"),
        "blurb-header": Arm("blurb-header", "r4-blurb-header", "blurb-header"),
        "blurb-decider": Arm("blurb-decider", "r4-blurb-decider", "blurb-decider")}


def layout_of(name: str) -> Layout:
    served = load_layouts()
    return served[name] if name in served else load_layout(ls.EXPERIMENTS / f"{name}.toml")


def text_arms(profile: str, names: tuple[str, ...]) -> tuple[dict, dict, dict]:
    """Each arm's calib-600 and index-dev-2k questions, keyed by arm name in the order given."""
    rows = {split: {r["id"]: r for r in rows_for(split)} for split in SPLITS}
    paths = {(a, split): ls.TEXT / profile / f"{split}-{ARMS[a].text}.jsonl.gz" for a in names for split in SPLITS}
    recs = {key: ls.load(path, ARMS[key[0]].layout) for key, path in paths.items()}
    for a in names:
        ls.same_stamp(recs[(a, "calib-600")], recs[(a, "index-dev-2k")], f"{a} text collects")
    layouts = {a: layout_of(ARMS[a].layout) for a in names}
    calib, dev = ({a: ls.text_items(recs[(a, split)], rows[split], layouts[a]) for a in names} for split in SPLITS)
    return calib, dev, {f"{a} {split}": repo_relative(path) for (a, split), path in paths.items()}


def image_arms(profile: str, names: tuple[str, ...]) -> dict[str, tuple[list, dict, str]]:
    out = {}
    for a in names:
        path = ls.VISION / profile / ARMS[a].image / "dev.jsonl.gz"
        config = split_config(path)
        if config["split"] != "dev":
            raise SystemExit(f"{path} is split {config['split']!r}: the screen reads image dev only")
        out[a] = (ls.load(path, ARMS[a].layout), config, repo_relative(path))
    (_, first, _), (_, second, _) = out.values()
    if diff := [k for k in SAME_IMAGE if first.get(k) != second.get(k)]:
        raise SystemExit(f"image collects of {' and '.join(names)} differ in {diff}")
    return out


def pair(profile: str, arm: str, control: str, pmap=map) -> tuple[Path, Path]:
    if arm == control:
        raise SystemExit(f"--arm and --control are both {arm}")
    start, stamp, names = time.monotonic(), now(), (control, arm)
    calib, dev, paths = text_arms(profile, names)
    dev_image = image_arms(profile, names)  # refuses before the slow part
    text = ls.text_report(calib, dev, pmap, base=control, pure=False)
    meta = {"timestamp": stamp, "repo commit": git_revision(), "host": host_info.summary(), "profile": profile,
            "title": TITLE, "set": arm, "control": control, **{f"collect {k}": v for k, v in paths.items()},
            **{f"collect {a} image dev": p for a, (_, _, p) in dev_image.items()},
            "fits": "T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T",
            "subsets": "all = every question both arms answered"}
    name = f"{stamp}-r4-pair-{arm}-vs-{control}-{profile}"
    text_dir, image_dir = ls.ARCHIVE / name, ls.IMAGE_OUT / name
    image_dir.mkdir(parents=True)
    image = ls.image_report({a: text["fits"][a] for a in names}, dev_image, image_dir, base=control, pure=False)
    text = {"meta": meta | {"run time": f"{time.monotonic() - start:.0f} s"}, **text}
    ls.write_summaries(text_dir, text, image_dir, {"meta": meta, **image})
    return text_dir, image_dir


def main(argv=None) -> dict:
    p = argparse.ArgumentParser(description="R4 pair screen: two collected prompt arms on the same questions")
    p.add_argument("--profile", required=True)
    p.add_argument("--arm", required=True, choices=ARMS)
    p.add_argument("--control", required=True, choices=ARMS)
    args = p.parse_args(argv)
    with ProcessPoolExecutor() as pool:  # the paired bootstraps dominate the run time
        text_dir, image_dir = pair(args.profile, args.arm, args.control, pool.map)
    print(text_dir / "summary.md", image_dir / "summary.md", sep="\n")
    return {"text": text_dir, "image": image_dir}


if __name__ == "__main__":
    main()
