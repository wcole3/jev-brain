"""Round-3 answer-label screen: each experiment label set against today's letters on the same questions, on CPU.

usage:
  uv run python scripts/label_screen.py check --profile P
  uv run python scripts/label_screen.py screen --profile P --set S
check: the letters experiment collects against the control collects on 200 seeded rows per split, by identity top
answer; exits non-zero below 0.98. screen: T per type on each arm's calib-600 identity reads (mean-prob, b = 0),
then index-dev-2k (text) and image dev on the pure (set-tagged) and all questions. Never reads holdout rows.
"""

import argparse
import gzip
import json
import random
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from gateway.calibration import TYPES
from gateway.config import ROOT
from gateway.layouts import Layout, load_layout, load_layouts
from gateway.questions import render_question
from gateway.schema import Question
from scripts import collect, host_info, vision_collect, vision_compare, vision_splits
from scripts.bench import git_revision
from scripts.evaluate import now
from scripts.experiment_layouts import repo_relative
from scripts.experiments import BY_OPTIONS, compare_groups, per_group, summary
from scripts.label_screen_report import check_markdown, image_markdown, text_markdown
from scripts.metrics import Scored
from scripts.offline import gold_index
from scripts.order_policies import combine, fit_types, lookup
from scripts.order_stats import flip_rate, position_histogram
from scripts.splits import rows_for
from scripts.vision_offline import bare_stamp, input_tokens, require_choice, split_config, usable

TEXT, VISION = collect.COLLECT, vision_collect.COLLECT
ARCHIVE, IMAGE_OUT = ROOT / "docs" / "results" / "archive", vision_compare.OUT_ROOT
EXPERIMENTS = ROOT / "prompts" / "experiments"
CONTROL_LAYOUT, BASE = "header", "letters"
CONTROL = {"calib-600": "calib", "index-dev-2k": "index-dev"}  # the existing letters collect holding each split's rows
CHECK_ROWS, CHECK_SEED, CHECK_MIN = 200, 0, 0.98
Key = tuple[str, str]


@dataclass(frozen=True)
class Q:
    source: str
    family: str
    type: str
    gold: int
    n: int
    reads: dict[tuple[int, ...], list[float]]
    tag: str  # set | fallback: the labels the set run showed (letters runs have no tags: all "set")


def load(path: Path, layout: str) -> list[dict]:
    recs = [r for r in collect.records(path) if r["layout"] == layout]
    if not recs:
        raise SystemExit(f"no {layout} records in {path}: collect it first")
    return recs


def questions_of(rec: dict) -> dict[str, list[dict]]:
    """Text records hold reads per question; image records hold the answer question's reads."""
    return rec["questions"] if "questions" in rec else {"answer": rec["reads"]}


def tops(recs: list[dict]) -> dict[str, tuple[str, dict[str, int]]]:
    """Per row: its status and, when ok, the identity read's top answer for each question."""
    out = {}
    for rec in recs:
        answers = {}
        for qid, reads in (questions_of(rec) if rec["status"] == "ok" else {}).items():
            lp = next((r["logprobs"] for r in reads if r["perm"] == sorted(r["perm"])), None)
            if lp is None:
                raise SystemExit(f"{rec['id']}/{qid}: no identity read")
            answers[qid] = max(range(len(lp)), key=lp.__getitem__)
        out[rec["id"]] = rec["status"], answers
    return out


def agreement(control: dict, other: dict, rows: int = CHECK_ROWS, seed: int = CHECK_SEED) -> dict:
    """Seeded rows both files hold (any status); a status mismatch or a one-sided question counts as disagreement."""
    ids = sorted(control.keys() & other.keys())
    picked = random.Random(seed).sample(ids, min(rows, len(ids)))
    units = agree = status_mismatches = one_sided = 0
    for rid in picked:
        (status_c, c), (status_o, o) = control[rid], other[rid]
        keys = c.keys() | o.keys()
        units += max(len(keys), status_c != status_o)  # two different refusals still count once
        agree += sum(c[k] == o[k] for k in c.keys() & o.keys())
        status_mismatches += status_c != status_o
        one_sided += len(keys - (c.keys() & o.keys())) if status_c == status_o else 0
    return {"rows": len(picked), "questions": units, "agree": agree, "status_mismatches": status_mismatches,
            "one_sided": one_sided, "agreement": agree / units if units else None}


def check_paths(profile: str) -> dict[str, tuple[Path, Path]]:
    text = {split: (TEXT / profile / f"{control}.jsonl.gz", TEXT / profile / f"{split}-letters.jsonl.gz")
            for split, control in CONTROL.items()}
    image = (VISION / profile / "baseline" / "dev.jsonl.gz", VISION / profile / "labels-letters" / "dev.jsonl.gz")
    return text | {"image dev": image}


def check(profile: str) -> dict:
    paths = check_paths(profile)
    splits = {split: agreement(tops(load(control, CONTROL_LAYOUT)), tops(load(other, "labels-letters")))
              for split, (control, other) in paths.items()}
    passed = all(s["agreement"] is not None and s["agreement"] >= CHECK_MIN for s in splits.values())
    meta = {"timestamp": now(), "repo commit": git_revision(), "profile": profile,
            "rule": (f"identity top answer on {CHECK_ROWS} rows (seed {CHECK_SEED}) both collects hold, any status,"
                     f" ≥ {CHECK_MIN}; a status mismatch or a question on one side only counts as disagreement"),
            **{f"collects {split}": f"{repo_relative(c)} vs {repo_relative(o)}" for split, (c, o) in paths.items()}}
    return {"meta": meta, "splits": splits, "passed": passed}


def by_perm(reads: list[dict]) -> dict[tuple[int, ...], list[float]]:
    return {tuple(r["perm"]): r["logprobs"] for r in reads}


def text_items(recs: list[dict], rows: dict, layout: Layout) -> dict[Key, Q]:
    """Every gold-labelled question of the ok records of this layout whose row is in rows."""
    out = {}
    for rec in recs:
        if rec["status"] != "ok" or rec["layout"] != layout.name or rec["id"] not in rows:
            continue
        row, tags = rows[rec["id"]], rec.get("label_tags", {})
        for qid, reads in rec["questions"].items():
            q = render_question(Question(**row["questions"][qid]), layout)
            gold = gold_index(q, row["gold"].get(qid))
            if gold is not None:
                out[(rec["id"], qid)] = Q(row["source"], row["family"], q.type, gold, len(q.options), by_perm(reads),
                                         tags.get(qid, "set"))
    return out


def image_items(recs: list[dict]) -> dict[Key, Q]:
    keep, _ = usable(recs)
    try:
        for r in keep:
            require_choice(r)
    except ValueError as e:
        raise SystemExit(str(e)) from e
    return {(r["id"], "answer"): Q(r["benchmark"], r["group"], "choice", r["gold"], len(r["names"]),
                                   by_perm(r["reads"]), r.get("label_tags", {}).get("answer", "set")) for r in keep}


def read(q: Q, order: str) -> tuple[list[float], list[int]]:
    perm = list(range(q.n)) if order == "identity" else list(range(q.n))[::-1]
    return lookup(q.reads, perm), perm


def fit_T(items: dict[Key, Q]) -> dict[str, float]:
    """T per type on the identity reads, mean-prob (ruling R2)."""
    by_type = {t: [] for t in TYPES}
    for q in items.values():
        by_type[q.type].append(([read(q, "identity")], q.gold, q.n))
    return fit_types(by_type, "mean-prob")


def scored(items: dict[Key, Q], keys: list[Key], T: dict, order: str = "identity") -> dict[Key, Scored]:
    out = {}
    for k in keys:
        q = items[k]
        out[k] = Scored(q.source, q.family, q.type, q.gold, combine([read(q, order)], "mean-prob", T[q.type], None))
    return out


def subsets(base: dict[Key, Q], other: dict[Key, Q]) -> dict[str, list[Key]]:
    """all: every question both arms answered; pure: those the set run showed with its own labels."""
    keys = sorted(base.keys() & other.keys())
    return {"all": keys, "pure": [k for k in keys if other[k].tag == "set"]}


def arm_view(items: dict[Key, Q], keys: list[Key], T: dict) -> dict:
    """The identity answers, the identity/reversed flip rate and the predicted vs gold position (noul left out)."""
    identity, reversed_ = scored(items, keys, T), scored(items, keys, T, "reversed")
    choices = {k: s for k, s in identity.items() if s.type != "noul"}
    return {"identity": identity, "flips": per_group(choices, BY_OPTIONS, lambda part: flip_rate(part, reversed_)),
            "histogram": position_histogram(list(identity.values()))}


def fallback_share(items: dict[Key, Q], answers: dict[Key, Scored]) -> dict:
    return per_group(answers, BY_OPTIONS, lambda part: sum(items[k].tag == "fallback" for k in part) / len(part))


def views_of(dev: dict[str, dict[Key, Q]], keys: list[Key], fits: dict) -> tuple[dict, dict]:
    views = {arm: arm_view(items, keys, fits[arm]) for arm, items in dev.items()}
    diag = {"flips": {a: v["flips"] for a, v in views.items()}, "histograms": {a: v["histogram"] for a, v in views.items()}}
    return views, diag


def text_report(calib: dict[str, dict[Key, Q]], dev: dict[str, dict[Key, Q]], pmap=map) -> dict:
    """Arms keyed letters first: T fitted on calib, then dev on both subsets, paired against letters."""
    fits = {arm: fit_T(items) for arm, items in calib.items()}
    other = next(arm for arm in dev if arm != BASE)
    subs, out = subsets(dev[BASE], dev[other]), {}
    for name, keys in subs.items():
        views, diag = views_of(dev, keys, fits)
        identity = {arm: v["identity"] for arm, v in views.items()}
        out[name] = {"n": len(keys), "arms": {arm: per_group(s, BY_OPTIONS, summary) for arm, s in identity.items()},
                     "vs_letters": compare_groups(identity[BASE], {other: identity[other]}, BY_OPTIONS, pmap), **diag}
    return {"fits": fits, "questions": {"calib": {a: len(i) for a, i in calib.items()},
                                        "dev": {a: len(i) for a, i in dev.items()}},
            "fallback_share": fallback_share(dev[other], scored(dev[other], subs["all"], fits[other])), "subsets": out}


def arm_rows(recs: dict[str, dict], items: dict[Key, Q], answers: dict[Key, Scored]) -> list[dict]:
    """vision_offline's scored rows; input_tokens counts the identity read alone."""
    return [{"id": k[0], "benchmark": recs[k[0]]["benchmark"], "group": recs[k[0]]["group"], "gold": s.gold,
             "probs": s.probs, "chance": 1 / len(s.probs),
             "input_tokens": input_tokens(recs[k[0]], [read(items[k], "identity")])} for k, s in answers.items()]


def write_arm(folder: Path, rows: list[dict], arm: dict) -> Path:
    folder.mkdir(parents=True)
    with gzip.open(folder / "scored.jsonl.gz", "wt", encoding="utf-8") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    (folder / "arm.json").write_text(json.dumps(arm, indent=1) + "\n")
    return folder


def compare(dirs: dict[str, Path], label: str, out: Path) -> dict:
    """vision_compare.py with letters as the baseline; its results dir lands inside out."""
    before = set(out.glob(f"*-{label}"))
    s = vision_compare.main(["--baseline", f"{BASE}={dirs[BASE]}", *(f"{a}={d}" for a, d in dirs.items() if a != BASE),
                             "--out-label", label, "--out-root", str(out)])
    (made,) = set(out.glob(f"*-{label}")) - before
    return {"dir": made.name, "configs": {a: {k: c[k] for k in ("index", "accuracy", "ece", "nll")}
                                          for a, c in s["configs"].items()},
            "paired": {a: {k: p[k] for k in ("delta_index", "ci", "delta_ece", "delta_nll", "agreement", "mcnemar_p")}
                       for a, p in s["paired"].items()}}


def image_report(fits: dict[str, dict], dev: dict[str, tuple[list, dict, str]], out: Path) -> dict:
    """dev: per arm (records, collect config, path), letters first; arm dirs and compares go under out."""
    items = {arm: image_items(recs) for arm, (recs, _, _) in dev.items()}
    by_id = {arm: {r["id"]: r for r in recs} for arm, (recs, _, _) in dev.items()}
    other = next(arm for arm in dev if arm != BASE)
    subs, data, commit = subsets(items[BASE], items[other]), {}, vision_splits.commit()
    for name, keys in subs.items():
        views, diag = views_of(items, keys, fits)
        data[name] = {"n": len(keys), **diag}
        if not keys:
            continue
        dirs = {}
        for arm, (recs, config, path) in dev.items():
            skipped = usable(recs)[1] | {"outside_subset": len(items[arm]) - len(keys)}
            about = {"arm": arm, "orders": "identity", "skipped": skipped, "fallbacks": [], "fit_on": None,
                     "T": fits[arm]["choice"], "fit": "choice T on the arm's text calib-600 identity reads",
                     "subset": name, "collect": str(path), "collect_config": config, "commit": commit}
            rows = arm_rows(by_id[arm], items[arm], views[arm]["identity"])
            dirs[arm] = write_arm(out / "arms" / name / arm, rows, about)
        data[name]["compare"] = compare(dirs, f"compare-{name}", out)
    return {"T": {arm: f["choice"] for arm, f in fits.items()},
            "fallback_share": fallback_share(items[other], scored(items[other], subs["all"], fits[other])),
            "subsets": data}


def same_stamp(a: list[dict], b: list[dict], what: str) -> None:
    sa, sb = bare_stamp(a, Path(what)), bare_stamp(b, Path(what))
    if diff := sorted(k for k in sa.keys() | sb.keys() if sa.get(k) != sb.get(k)):
        raise SystemExit(f"{what}: calib-600 and index-dev-2k were collected under other {diff}")


def text_arms(profile: str, set_name: str) -> tuple[dict, dict, dict]:
    """Each arm's calib-600 and index-dev-2k questions; letters reads come from the control collects."""
    layout, header = load_layout(EXPERIMENTS / f"labels-{set_name}.toml"), load_layouts()[CONTROL_LAYOUT]
    rows = {split: {r["id"]: r for r in rows_for(split)} for split in CONTROL}
    paths = {(BASE, split): (TEXT / profile / f"{control}.jsonl.gz", header) for split, control in CONTROL.items()}
    paths |= {(layout.name, split): (TEXT / profile / f"{split}-{set_name}.jsonl.gz", layout) for split in CONTROL}
    recs = {key: load(path, lay.name) for key, (path, lay) in paths.items()}
    for arm in (BASE, layout.name):
        same_stamp(recs[(arm, "calib-600")], recs[(arm, "index-dev-2k")], f"{arm} text collects")
    items = {key: text_items(recs[key], rows[key[1]], lay) for key, (_, lay) in paths.items()}
    split_of = {split: {arm: items[(arm, split)] for arm in (BASE, layout.name)} for split in CONTROL}
    shown = {f"{arm} {split}": repo_relative(path) for (arm, split), (path, _) in paths.items()}
    return split_of["calib-600"], split_of["index-dev-2k"], shown


def image_arms(profile: str, set_name: str) -> dict[str, tuple[list, dict, str]]:
    out = {}
    for arm, folder in ((BASE, "baseline"), (f"labels-{set_name}", f"labels-{set_name}")):
        path = VISION / profile / folder / "dev.jsonl.gz"
        config = split_config(path)
        if config["split"] != "dev":
            raise SystemExit(f"{path} is split {config['split']!r}: the screen reads image dev only")
        out[arm] = (load(path, CONTROL_LAYOUT if arm == BASE else arm), config, repo_relative(path))
    return out


def screen(profile: str, set_name: str, pmap=map) -> tuple[Path, Path]:
    start, stamp = time.monotonic(), now()
    calib, dev, paths = text_arms(profile, set_name)
    dev_image = image_arms(profile, set_name)  # refuses a missing or non-dev image collect before the slow part
    text = text_report(calib, dev, pmap)
    meta = {"timestamp": stamp, "repo commit": git_revision(), "host": host_info.summary(), "profile": profile,
            "set": set_name, **{f"collect {k}": v for k, v in paths.items()},
            **{f"collect {a} image dev": p for a, (_, _, p) in dev_image.items()},
            "fits": "T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T",
            "subsets": "all = every question both arms answered; pure = those the set run tagged `set`"}
    name = f"{stamp}-r3-labels-{set_name}-{profile}"
    text_dir, image_dir = ARCHIVE / name, IMAGE_OUT / name
    image_dir.mkdir(parents=True)
    image = {"meta": meta, **image_report({a: text["fits"][a] for a in dev_image}, dev_image, image_dir)}
    text = {"meta": meta | {"run time": f"{time.monotonic() - start:.0f} s"}, **text}
    for out, report, markdown in ((text_dir, text, text_markdown), (image_dir, image, image_markdown)):
        out.mkdir(parents=True, exist_ok=True)
        (out / "summary.json").write_text(json.dumps(report, indent=1) + "\n")
        (out / "summary.md").write_text(markdown(report))
    return text_dir, image_dir


def write_check(report: dict) -> Path:
    out = ARCHIVE / f"{report['meta']['timestamp']}-r3-labels-check-{report['meta']['profile']}"
    out.mkdir(parents=True)
    (out / "summary.json").write_text(json.dumps(report, indent=1) + "\n")
    (out / "summary.md").write_text(check_markdown(report))
    return out


def main(argv=None) -> dict:
    p = argparse.ArgumentParser(description="R3 answer-label pipeline check and screens")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("check", "screen"):
        sub.add_parser(name).add_argument("--profile", required=True)
    sub.choices["screen"].add_argument("--set", required=True, dest="set_name")
    args = p.parse_args(argv)
    if args.command == "screen":
        with ProcessPoolExecutor() as pool:  # the paired bootstraps dominate the run time
            text_dir, image_dir = screen(args.profile, args.set_name, pool.map)
        print(text_dir / "summary.md", image_dir / "summary.md", sep="\n")
        return {"text": text_dir, "image": image_dir}
    report = check(args.profile)
    print(check_markdown(report), write_check(report) / "summary.md", sep="\n")
    if not report["passed"]:
        low = [s for s, r in report["splits"].items() if r["agreement"] is None or r["agreement"] < CHECK_MIN]
        raise SystemExit(f"pipeline check below {CHECK_MIN}: {', '.join(low)}")
    return report


if __name__ == "__main__":
    main()
