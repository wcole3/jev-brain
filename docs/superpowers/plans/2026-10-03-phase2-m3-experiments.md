# Phase 2 M3: experiments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure option-order and layout arms offline, recommend per-profile defaults, check
rounding ties, and report each profile against the Decision Index board.

**Architecture:**
- Every arm is computed offline from the collected logprobs (`.cache/collect/<profile>/<split>.jsonl.gz`).
  These hold every order of `collect.ARMS` for all three layouts.
- Each arm gets its own temperature, fitted on the calib split with the same code `calibrate.py`
  uses, so arms are compared on equal terms.
- Comparisons are paired on the same `(row id, question id)` keys, with bootstrap CIs.
- `scripts/m3.py` writes one report per experiment. `scripts/phase2_report.py` builds the
  closing table from committed results.

**Tech Stack:** Python 3.12, uv, pytest, ruff. Existing modules: `scripts/offline.py`,
`scripts/metrics.py`, `scripts/fit.py`, `scripts/calibrate.py`, `scripts/board.py`,
`gateway/orders.py`.

**Spec:** `docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md`, sections
"Experiments (M3)", "Changing a default", "Index runs and latency" and the M3 milestone row.

## Global Constraints

- **Code style:** code reads like a tutorial, with small files, obvious names and comments of
  at most 2 lines.
- **Checks:** `uv run pytest -q`, `uv run pytest tests/parity -q` and `uv run ruff check .`
  pass after every task.
- **Never fit, tune or select on Jev outputs.**
  - Temperatures are fitted on `calib` only.
  - Arms are judged on `index-dev` and `eval`.
  - No choice is made from full Index rows: the final Index run only confirms.
- **Paired bootstrap:** 95% CI, 2,000 resamples, seed 0 (`scripts.fit.bootstrap_diff`).
- **Option-order arms** (spec): `identity`, `identity+reversed`, `cyclic:2`, `cyclic:3`,
  `cyclic:4`, `pride`.
  - PriDe estimates a per-position prior from a 5% slice using the cyclic reads, then divides
    it out of identity-only reads.
- **Order metrics:**
  - accuracy, ECE and NLL;
  - flip rate (identity vs reversed top answer);
  - a chosen-position vs gold-position histogram;
  - AUROC of identity-vs-reversed TVD as a predictor of errors.

  Report them per type and per option-count bucket: `2`, `3-5`, `6-26`, `27+`.
- **Layout arms:** `decider_chat`, `header` and `question_first`, each with its own fitted T.
  - Report by type and by state-length bucket on `input_tokens`: `<512`, `512-2k`, `2k-8k`,
    `>8k`.
  - The long slice is `jevbench/invoices`, `jevbench/invoice_processing`, `index/ContractNLI`,
    `index/NLI4CT`, `index/BRIGHT`, and `decisionbench` rows over 2,000 tokens.
- **Auto-switch rule:** a bucket may switch layout only where its winner differs from the
  overall winner with a CI clear of zero.
- **Changing a default:** a default changes only on a paired-bootstrap gain in accuracy or ECE
  on held-out rows, with the latency cost stated. The final full Index run then confirms it.
  The owner decides.
- **Results folders:** `docs/results/<profile>/<UTC YYYY-MM-DDTHHMMSSZ>-<name>/summary.md`.
  The names are `m3-orders-<layout>`, `m3-layouts` and `ties`.
- **Commits:**
  - caveman Conventional Commits, subject ≤ 50 chars, explicit paths (never `git add -A`);
  - trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## File map

| File | Responsibility |
|---|---|
| `scripts/offline.py` (modify) | `questions` also yields the question id; new `keyed(...)` |
| `scripts/calibrate.py` (modify) | follow the new `questions` tuple |
| `scripts/experiments.py` (new) | buckets, the long slice, `fit_arm`, `compare` |
| `scripts/order_stats.py` (new) | flip rate, position histogram, disagreement AUROC, PriDe, noul lean |
| `scripts/m3.py` (new) | CLI: `orders`, `layouts`, `ties`; writes reports |
| `scripts/m3_report.py` (new) | markdown rendering for `m3.py` |
| `scripts/ties.py` (new) | rounding-tie rate on Index `results.jsonl` ranking groups |
| `scripts/phase2_report.py` (new) | per-profile closing table from committed results; README table |
| `tests/unit/test_experiments.py`, `test_order_stats.py`, `test_ties.py`, `test_m3.py`, `test_phase2_report.py` (new) | unit tests |

---

### Task 1: keyed offline items

**Files:**
- Modify: `scripts/offline.py` (`questions`, `scored`; add `keyed`)
- Modify: `scripts/calibrate.py:39-52` (`questions_by_type`)
- Test: `tests/unit/test_offline.py`

**Interfaces:**
- Produces: `offline.questions(...) -> Iterator[tuple[str, str, list, int]]` yielding
  `(qid, type, chosen, gold)`.
- Produces: `offline.keyed(recs, rows_by_id, arm, layouts) -> dict[tuple[str, str], Scored]`,
  keyed by `(row id, qid)`, over ok records of `arm.layout`.

- [ ] **Step 1: Write the failing test** (append to `tests/unit/test_offline.py`; reuse its `ROW`, `REC` and `LAYOUTS`):

```python
from scripts.offline import keyed


def test_keyed_maps_row_and_question_to_scored():
    got = keyed([REC], {"r1": ROW}, Arm(), LAYOUTS)
    assert set(got) == {("r1", "c"), ("r1", "n")}
    assert got[("r1", "c")].type == "choice" and got[("r1", "n")].type == "noul"


def test_keyed_skips_other_layouts_and_refusals():
    other = REC | {"layout": "header"}
    refused = REC | {"id": "r2", "status": "unsupported"}
    assert keyed([other, refused], {"r1": ROW, "r2": ROW}, Arm(), LAYOUTS) == {}
```

- [ ] **Step 2: Run it.** `uv run pytest tests/unit/test_offline.py -q`. Expected: FAIL with `ImportError: cannot import name 'keyed'`.

- [ ] **Step 3: Implement.** In `scripts/offline.py`:

```python
def questions(record: dict, row: dict, layout: str, orders: str, layouts: dict) -> Iterator[tuple[str, str, list, int]]:
    """(qid, type, chosen reads, gold) for each gold-labelled question of an ok record of this layout."""
    if record["status"] != "ok" or record["layout"] != layout:
        return
    for qid, reads in record["questions"].items():
        q = render_question(Question(**row["questions"][qid]), layouts[layout])
        gold = gold_index(q, row["gold"].get(qid))
        if gold is None:
            continue
        try:
            chosen = chosen_reads(q, reads, orders)
        except ValueError as e:
            raise ValueError(f"{record['id']}/{qid}: {e}") from None
        yield qid, q.type, chosen, gold


def scored(record: dict, row: dict, arm: Arm, layouts: dict) -> list[Scored]:
    """One Scored per gold-labelled question, as the gateway would answer it under this arm."""
    return [Scored(row["source"], row["family"], t, gold, probabilities(chosen, t, arm.calibration))
            for _, t, chosen, gold in questions(record, row, arm.layout, arm.orders, layouts)]


def keyed(recs: Iterable[dict], rows_by_id: dict[str, dict], arm: Arm, layouts: dict) -> dict[tuple[str, str], Scored]:
    """Scored answers by (row id, question id), so two arms can be paired on the same questions."""
    out = {}
    for rec in recs:
        row = rows_by_id[rec["id"]]
        for qid, t, chosen, gold in questions(rec, row, arm.layout, arm.orders, layouts):
            out[(rec["id"], qid)] = Scored(row["source"], row["family"], t, gold,
                                           probabilities(chosen, t, arm.calibration))
    return out
```

In `scripts/calibrate.py` `questions_by_type`, change the loop to
`for _, q_type, chosen, gold in offline.questions(...)`. Then grep for every other caller with
`grep -rn "questions(" scripts tests | grep offline` and update them the same way.

- [ ] **Step 4: Run.** `uv run pytest -q && uv run pytest tests/parity -q && uv run ruff check .`. Expected: all pass.

- [ ] **Step 5: Commit.**

```bash
git add scripts/offline.py scripts/calibrate.py tests/unit/test_offline.py
git commit -m "feat(offline): key scored answers by question"
```

---

### Task 2: experiment helpers

**Files:**
- Create: `scripts/experiments.py`
- Test: `tests/unit/test_experiments.py`

**Interfaces:**
- Consumes: `offline.keyed`, `calibrate.questions_by_type(recs, rows, layout, orders) -> (by_type, stamp)`, `calibrate.fit_layout(by_type) -> dict`, `fit.bootstrap_diff`.
- Produces:
  - `option_bucket(k: int) -> str`
  - `length_bucket(tokens: int) -> str`
  - `is_long(source: str, family: str, tokens: int) -> bool`
  - `fit_arm(calib_recs: list[dict], calib_rows: dict, layout: str, orders: str) -> Calibration`
  - `paired(a: dict, b: dict, keep=None) -> tuple[list[Scored], list[Scored]]`
  - `compare(a: dict, b: dict, keep=None) -> dict` returning `{"n": int, "accuracy": (d, lo, hi), "ece": (...), "nll": (...)}`, each being metric(b) − metric(a).

- [ ] **Step 1: Write the failing tests** in `tests/unit/test_experiments.py`:

```python
from scripts.experiments import compare, is_long, length_bucket, option_bucket, paired
from scripts.metrics import Scored


def s(gold, probs, t="choice", source="index", family="f"):
    return Scored(source, family, t, gold, probs)


def test_buckets():
    assert [option_bucket(k) for k in (2, 3, 5, 6, 26, 27)] == ["2", "3-5", "3-5", "6-26", "6-26", "27+"]
    assert [length_bucket(n) for n in (10, 511, 512, 2047, 2048, 8191, 8192)] == [
        "<512", "<512", "512-2k", "512-2k", "2k-8k", "2k-8k", ">8k"]


def test_long_slice():
    assert is_long("index", "ContractNLI", 100) and is_long("jevbench", "invoices", 100)
    assert is_long("decisionbench", "x", 2001) and not is_long("decisionbench", "x", 2000)
    assert not is_long("index", "MMLU", 50_000)


def test_paired_uses_shared_keys_in_order_and_keep_filter():
    a = {("r1", "q"): s(0, [0.9, 0.1]), ("r2", "q"): s(0, [0.4, 0.6])}
    b = {("r2", "q"): s(0, [0.7, 0.3]), ("r3", "q"): s(0, [0.5, 0.5])}
    xa, xb = paired(a, b)
    assert len(xa) == len(xb) == 1 and xa[0].probs == [0.4, 0.6] and xb[0].probs == [0.7, 0.3]
    assert paired(a, b, keep=lambda key, item: key[0] != "r2") == ([], [])


def test_compare_reports_b_minus_a():
    a = {(f"r{i}", "q"): s(0, [0.4, 0.6]) for i in range(40)}
    b = {(f"r{i}", "q"): s(0, [0.8, 0.2]) for i in range(40)}
    got = compare(a, b)
    assert got["n"] == 40 and got["accuracy"][0] == 1.0 and got["nll"][0] < 0
```

- [ ] **Step 2: Run it.** `uv run pytest tests/unit/test_experiments.py -q`. Expected: FAIL with `ModuleNotFoundError: scripts.experiments`.

- [ ] **Step 3: Implement** `scripts/experiments.py`:

```python
"""Shared pieces of the M3 experiments: buckets, the long slice, per-arm temperatures, paired comparisons."""

from gateway.calibration import Calibration
from scripts import calibrate, metrics
from scripts import fit as fits

LONG_FAMILIES = {("jevbench", "invoices"), ("jevbench", "invoice_processing"), ("index", "ContractNLI"),
                 ("index", "NLI4CT"), ("index", "BRIGHT")}


def option_bucket(k: int) -> str:
    return "2" if k == 2 else "3-5" if k <= 5 else "6-26" if k <= 26 else "27+"


def length_bucket(tokens: int) -> str:
    return "<512" if tokens < 512 else "512-2k" if tokens < 2048 else "2k-8k" if tokens < 8192 else ">8k"


def is_long(source: str, family: str, tokens: int) -> bool:
    return (source, family) in LONG_FAMILIES or (source == "decisionbench" and tokens > 2000)


def fit_arm(calib_recs: list[dict], calib_rows: dict, layout: str, orders: str) -> Calibration:
    """This arm's own T per type, fitted on calib like calibrate.py (b = 0, no gate), so arms compare fairly."""
    by_type, _ = calibrate.questions_by_type(calib_recs, calib_rows, layout, orders)
    fit = calibrate.fit_layout(by_type)
    return Calibration({"choice": fit["choice"]["T"], "score": fit["score"]["T"], "noul": fit["noul_b0"]["T"]},
                       source=f"calib fit {layout} {orders}")


def paired(a: dict, b: dict, keep=None) -> tuple[list, list]:
    keys = sorted(k for k in a.keys() & b.keys() if keep is None or keep(k, a[k]))
    return [a[k] for k in keys], [b[k] for k in keys]


def compare(a: dict, b: dict, keep=None) -> dict:
    """metric(b) - metric(a) with 95% paired-bootstrap intervals, over the questions both arms answered."""
    xa, xb = paired(a, b, keep)
    out = {"n": len(xa)}
    for name, metric in (("accuracy", metrics.accuracy), ("ece", metrics.ece), ("nll", metrics.nll)):
        out[name] = fits.bootstrap_diff(xa, xb, metric) if xa else None
    return out
```

Check that `Calibration` accepts `source=` as a keyword (`gateway/calibration.py`). If its
field order differs, pass the arguments by name.

- [ ] **Step 4: Run.** `uv run pytest tests/unit/test_experiments.py -q && uv run ruff check .`. Expected: PASS.

- [ ] **Step 5: Commit.**

```bash
git add scripts/experiments.py tests/unit/test_experiments.py
git commit -m "feat(m3): buckets, per-arm T, paired compare"
```

---

### Task 3: order diagnostics and PriDe

**Files:**
- Create: `scripts/order_stats.py`
- Test: `tests/unit/test_order_stats.py`

**Interfaces:**
- Consumes: `metrics.Scored`, `gateway.calibration.softmax(logprobs, T)`, `gateway.orders.option_orders`, `offline.questions`.
- Produces:
  - `flip_rate(identity: dict, reversed_: dict) -> float`: share of shared choice and score keys whose top answer differs.
  - `position_histogram(items: list[Scored]) -> dict[str, dict[str, list[int]]]`: per option bucket, `{"chosen": counts by position, "gold": counts by position}` (identity order, so position = caller index; buckets `27+` truncate to the first 27 positions).
  - `disagreement_auroc(identity: dict, reversed_: dict, averaged: dict) -> float | None`: AUROC of TVD(identity, reversed) predicting that `averaged` is wrong, using the rank-sum formula with ties counted as half. Returns None when one class is empty.
  - `noul_lean(identity: dict, reversed_: dict) -> dict`: mean p(yes) under each order, plus the gold yes rate, over shared noul keys.
  - `in_prior_slice(row_id: str) -> bool`: `int(sha256(row_id).hexdigest(), 16) % 20 == 0` (5%).
  - `pride_prior(recs, rows_by_id, layout: str, cal: Calibration, layouts) -> dict[int, list[float]]`: per option count K, the mean probability at each shown position over the `cyclic:4` reads. It uses choice and score questions of slice rows only, keeps only K with ≥ 20 questions, and computes softmax at `cal.T[type]`.
  - `reversed_keyed(recs, rows_by_id, layout, cal, layouts) -> dict[tuple[str, str], Scored]`: the reversed read alone, mapped back to caller order.
  - `pride_keyed(recs, rows_by_id, layout, cal, prior, layouts) -> dict[tuple[str, str], Scored]`: identity reads of non-slice rows, as softmax at T divided by `prior[K]` and renormalised. Questions whose K has no prior pass through unchanged. Noul passes through unchanged.

- [ ] **Step 1: Write the failing tests** in `tests/unit/test_order_stats.py`:

```python
from scripts.metrics import Scored
from scripts.order_stats import disagreement_auroc, flip_rate, in_prior_slice, noul_lean, position_histogram


def s(gold, probs, t="choice"):
    return Scored("index", "f", t, gold, probs)


def test_flip_rate_counts_changed_top_answers():
    ident = {("r1", "q"): s(0, [0.6, 0.4]), ("r2", "q"): s(0, [0.6, 0.4])}
    rev = {("r1", "q"): s(0, [0.3, 0.7]), ("r2", "q"): s(0, [0.9, 0.1])}
    assert flip_rate(ident, rev) == 0.5


def test_position_histogram_by_bucket():
    h = position_histogram([s(1, [0.7, 0.3]), s(0, [0.8, 0.2]), s(2, [0.1, 0.1, 0.8])])
    assert h["2"] == {"chosen": [2, 0], "gold": [1, 1]}
    assert h["3-5"]["chosen"] == [0, 0, 1]


def test_auroc_is_one_when_disagreement_marks_every_error():
    ident = {("a", "q"): s(0, [0.9, 0.1]), ("b", "q"): s(0, [0.9, 0.1])}
    rev = {("a", "q"): s(0, [0.9, 0.1]), ("b", "q"): s(0, [0.1, 0.9])}
    avg = {("a", "q"): s(0, [0.9, 0.1]), ("b", "q"): s(0, [0.4, 0.6])}
    assert disagreement_auroc(ident, rev, avg) == 1.0
    assert disagreement_auroc(ident, ident, ident) is None


def test_noul_lean():
    ident = {("a", "n"): s(1, [0.2, 0.8], "noul")}
    rev = {("a", "n"): s(1, [0.4, 0.6], "noul")}
    assert noul_lean(ident, rev) == {"n": 1, "p_yes_identity": 0.8, "p_yes_reversed": 0.6, "gold_yes": 1.0}


def test_prior_slice_is_stable_and_about_five_percent():
    share = sum(in_prior_slice(f"row{i}") for i in range(4000)) / 4000
    assert 0.03 < share < 0.07 and in_prior_slice("row7") == in_prior_slice("row7")
```

Add one PriDe test built from a two-option fixture. The record holds `cyclic:4` reads for a
slice row (find an id where `in_prior_slice` is true by looping over `f"row{i}"`) and identity
reads for a non-slice row. The test asserts:
- that `pride_prior` returns `{2: [p0, p1]}`, given `MIN_PRIOR = 1` passed as a keyword;
- that `pride_keyed` divides the non-slice identity probabilities by that prior and renormalises.

Give `pride_prior` a `min_questions: int = 20` keyword so the test can lower it.

- [ ] **Step 2: Run it.** `uv run pytest tests/unit/test_order_stats.py -q`. Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement** `scripts/order_stats.py`:

```python
"""Order diagnostics: flips, position histograms, disagreement as an error signal, noul lean, and PriDe."""

import hashlib
from collections import defaultdict

from gateway.calibration import Calibration, softmax
from gateway.orders import option_orders
from gateway.questions import render_question
from gateway.schema import Question
from scripts import offline
from scripts.experiments import option_bucket
from scripts.metrics import Scored


def flip_rate(identity: dict, reversed_: dict) -> float:
    keys = [k for k in identity.keys() & reversed_.keys() if identity[k].type != "noul"]
    return sum(identity[k].pred != reversed_[k].pred for k in keys) / len(keys) if keys else 0.0


def position_histogram(items: list[Scored]) -> dict[str, dict[str, list[int]]]:
    out = {}
    for i in items:
        if i.type == "noul":
            continue
        width = min(len(i.probs), 27)
        h = out.setdefault(option_bucket(len(i.probs)), {"chosen": [0] * width, "gold": [0] * width})
        for name, pos in (("chosen", i.pred), ("gold", i.gold)):
            if pos < len(h[name]):
                h[name][pos] += 1
    return out


def tvd(p: list[float], q: list[float]) -> float:
    return sum(abs(a - b) for a, b in zip(p, q, strict=True)) / 2


def disagreement_auroc(identity: dict, reversed_: dict, averaged: dict) -> float | None:
    """Chance that a wrong answer shows more identity-vs-reversed disagreement than a right one (ties half)."""
    keys = identity.keys() & reversed_.keys() & averaged.keys()
    wrong = [tvd(identity[k].probs, reversed_[k].probs) for k in keys if not averaged[k].correct]
    right = [tvd(identity[k].probs, reversed_[k].probs) for k in keys if averaged[k].correct]
    if not wrong or not right:
        return None
    wins = sum((w > r) + 0.5 * (w == r) for w in wrong for r in right)
    return wins / (len(wrong) * len(right))


def noul_lean(identity: dict, reversed_: dict) -> dict:
    """p(yes) moving with the order is a position lean; staying put is a lean to the word."""
    keys = [k for k in identity.keys() & reversed_.keys() if identity[k].type == "noul"]
    n = len(keys)
    mean = lambda items: sum(items) / n if n else None  # noqa: E731
    return {"n": n, "p_yes_identity": mean([identity[k].probs[1] for k in keys]),
            "p_yes_reversed": mean([reversed_[k].probs[1] for k in keys]),
            "gold_yes": mean([identity[k].gold for k in keys])}


def in_prior_slice(row_id: str) -> bool:
    return int(hashlib.sha256(row_id.encode()).hexdigest(), 16) % 20 == 0


def pride_prior(recs, rows_by_id, layout: str, cal: Calibration, layouts, min_questions: int = 20) -> dict[int, list[float]]:
    """Mean probability at each shown position over the cyclic:4 reads of the 5% slice, per option count."""
    sums, counts = {}, defaultdict(int)
    for rec in recs:
        if not in_prior_slice(rec["id"]):
            continue
        for _, t, chosen, _ in offline.questions(rec, rows_by_id[rec["id"]], layout, "cyclic:4", layouts):
            if t == "noul":
                continue
            k = len(chosen[0][0])
            avg = [sum(softmax(lp, cal.T[t])[j] for lp, _ in chosen) / len(chosen) for j in range(k)]  # by shown position
            sums[k] = avg if k not in sums else [a + b for a, b in zip(sums[k], avg, strict=True)]
            counts[k] += 1
    return {k: [x / counts[k] for x in v] for k, v in sums.items() if counts[k] >= min_questions}


def pride_keyed(recs, rows_by_id, layout: str, cal: Calibration, prior: dict, layouts) -> dict:
    """Identity reads of the rows outside the slice, with the position prior divided out (noul unchanged)."""
    out = {}
    for rec in recs:
        if in_prior_slice(rec["id"]):
            continue
        row = rows_by_id[rec["id"]]
        for qid, t, chosen, gold in offline.questions(rec, row, layout, "identity", layouts):
            p = probabilities(chosen, t, cal)
            if t != "noul" and len(p) in prior:
                p = [x / max(prior[len(p)][j], 1e-9) for j, x in enumerate(p)]
                p = [x / sum(p) for x in p]
            out[(rec["id"], qid)] = Scored(row["source"], row["family"], t, gold, p)
    return out


def reversed_keyed(recs, rows_by_id, layout: str, cal: Calibration, layouts) -> dict:
    """The reversed read alone, back in caller order: the partner of identity for flips and disagreement."""
    out = {}
    for rec in recs:
        row = rows_by_id[rec["id"]]
        for qid, t, chosen, gold in offline.questions(rec, row, layout, "identity+reversed", layouts):
            rev = [c for c in chosen if c[1] != sorted(c[1])]  # the non-identity read
            out[(rec["id"], qid)] = Scored(row["source"], row["family"], t, gold, probabilities(rev, t, cal))
    return out
```

`offline.questions` with `"cyclic:4"` raises if a question lacks one of its shifts. Collects
hold every order of `collect.ARMS`, so that doesn't happen on real data. Remove the unused
imports (`option_orders`, `render_question`, `Question`) that ruff flags, and import
`probabilities` from `gateway.decide`.

- [ ] **Step 4: Run.** `uv run pytest tests/unit/test_order_stats.py -q && uv run ruff check .`. Expected: PASS.

- [ ] **Step 5: Commit.**

```bash
git add scripts/order_stats.py tests/unit/test_order_stats.py
git commit -m "feat(m3): order diagnostics and PriDe"
```

---

### Task 4: `m3.py orders` and `m3.py layouts` reports

**Files:**
- Create: `scripts/m3.py` (CLI and data assembly), `scripts/m3_report.py` (markdown)
- Test: `tests/unit/test_m3.py`

**Interfaces:**
- Consumes: Tasks 1–3, `scripts.collect.records`, `scripts.splits.rows_for`, `gateway.layouts.load_layouts`, `scripts.evaluate.results_dir(profile, name) -> Path` and `scripts.evaluate.now()`. Check those two helper names in `scripts/evaluate.py:42-50` and reuse them.
- Produces:
  - `ORDER_ARMS = ("identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4")`, plus the `"pride"` arm built from Task 3.
  - `orders_report(profile, layout) -> dict` and `layouts_report(profile) -> dict`. Each holds a `"splits"` entry for `index-dev` and `eval`, with per-arm summaries and comparisons against the baseline arm.
  - Each command writes `summary.md` and `report.json` to `results_dir(profile, f"m3-orders-{layout}")` or `results_dir(profile, "m3-layouts")`.
  - CLI: `uv run python scripts/m3.py orders --profile P --layout L` and `uv run python scripts/m3.py layouts --profile P`. Both take `--dry-run`, which prints the markdown and writes nothing.

**Report content (orders):** per split, for every arm:
- overall accuracy/ECE/NLL, by type and by option bucket, plus the comparison against `identity` (`experiments.compare`) for the same groups;
- the flip rate (`identity` arm vs `reversed_keyed` at the identity fit) and the AUROC (those two plus the `identity+reversed` arm items);
- the position histogram of `identity` and of the best arm;
- the noul lean;
- the read cost per question (1, 2, 2, 3 or 4, 1).

Each arm uses `fit_arm(calib_recs, calib_rows, layout, orders)`. PriDe uses the `identity` fit
and is compared to `identity` only on the non-slice keys: pass `keep=lambda key, _: not in_prior_slice(key[0])`.

**Report content (layouts):** per split:
- each layout at `identity` with its own `fit_arm`;
- `header` and `question_first` compared against `decider_chat`, overall, by type, by length bucket (on `input_tokens` of the record), and on the long slice;
- per-bucket accuracy winners, with the auto-switch flag set only when that bucket's winner differs from the overall winner and its accuracy CI against the overall winner excludes zero.

**Recommendation line** (both reports, index-dev and eval must agree):
- Name the arm or layout that beats the current default with an accuracy CI low > 0, or an ECE CI high < 0, without the other metric getting worse beyond its CI.
- Otherwise say "keep the default".
- Always print the read cost.

The owner makes the final call.

- [ ] **Step 1: Write the failing tests** in `tests/unit/test_m3.py`. Build a tiny in-memory dataset by reusing `tests/unit/test_offline.py`'s `ROW` and `REC` shapes:
  - 40 rows;
  - choice questions with 2 options;
  - every order in `collect.all_orders(2)`;
  - all three layouts;
  - calib and eval sets passed in directly.

  Test `m3.orders_data(calib_recs, calib_rows, split_recs, split_rows, layout)`:
  - it returns all six arms, and each arm's `n` equals the question count;
  - `identity` compared with itself gives accuracy diff 0.0.

  Test `m3.layouts_data(...)`: it returns three layouts and the long-slice group.

  Test `m3.recommend(comparisons, default)`:
  - it returns `"keep the default"` when no CI clears zero;
  - it returns the arm name when one does.

  Put all file I/O in thin `orders_report` / `layouts_report` wrappers that load the collects
  and call these pure functions. The tests cover only the pure functions.

```python
from scripts.m3 import recommend


def test_recommend_needs_a_ci_clear_of_zero():
    flat = {"accuracy": (0.01, -0.002, 0.02), "ece": (0.0, -0.01, 0.01), "nll": (0.0, -0.01, 0.01)}
    win = {"accuracy": (0.02, 0.01, 0.03), "ece": (0.0, -0.01, 0.01), "nll": (-0.01, -0.02, 0.0)}
    assert recommend({"cyclic:2": flat}, "identity") == "keep the default"
    assert recommend({"cyclic:2": flat, "identity+reversed": win}, "identity") == "identity+reversed"
```

`recommend` takes `{arm: overall comparison vs default}` for one split. The report calls it
for each split, and if the two splits disagree the recommendation becomes
`"no change: splits disagree (<a> vs <b>)"`.

- [ ] **Step 2: Run it.** `uv run pytest tests/unit/test_m3.py -q`. Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement** `scripts/m3.py` with these pure functions, then their thin wrappers and `argparse` subcommands:
  - `orders_data(calib_recs, calib_rows, recs, rows, layout) -> dict`;
  - `layouts_data(calib_recs, calib_rows, recs, rows) -> dict`;
  - `recommend(comps, default) -> str`.

  Implement `scripts/m3_report.py` as `orders_markdown(report) -> str` and
  `layouts_markdown(report) -> str`, with tables in the style of `offline.table`. Reuse
  `offline.fmt`. Print each CI as `+0.012 [+0.004, +0.020]`.

  The provenance block at the top must include:
  - timestamp, repo commit (reuse the provenance helper the other reports use; grep `repo commit` in `scripts/`), profile and layout;
  - each collect path;
  - each arm's fitted T.

  `recommend`:

```python
def recommend(comps: dict[str, dict], default: str) -> str:
    """An arm beats the default on accuracy or ECE with a CI clear of zero, and loses neither beyond its CI."""
    def wins(c):
        acc, ece = c["accuracy"], c["ece"]
        better_acc = acc[1] > 0 and ece[1] <= 0
        better_ece = ece[2] < 0 and acc[2] >= 0
        return better_acc or better_ece
    winners = [arm for arm, c in comps.items() if arm != default and c and wins(c)]
    if not winners:
        return "keep the default"
    return max(winners, key=lambda arm: comps[arm]["accuracy"][0])
```

- [ ] **Step 4: Run.** `uv run pytest -q && uv run ruff check .`. Expected: PASS.

- [ ] **Step 5: Smoke run (CPU).** Run `uv run python scripts/m3.py orders --profile qwen3.6-27b --layout decider_chat --dry-run`. `--dry-run` prints the markdown to stdout and writes nothing. Check that every table is filled. Expected: the identity accuracy on index-dev matches `docs/results/qwen3.6-27b/*-offline-index-dev-decider_chat-identity-uncalibrated/summary.md` to 3 decimals, because accuracy doesn't depend on T with one order.

- [ ] **Step 6: Commit.**

```bash
git add scripts/m3.py scripts/m3_report.py tests/unit/test_m3.py
git commit -m "feat(m3): orders and layouts reports"
```

---

### Task 5: rounding ties on ranking benchmarks

**Files:**
- Create: `scripts/ties.py`
- Test: `tests/unit/test_ties.py`

**Context:** ToolRet and BRIGHT rows in the Index `results.jsonl` (an Index run's `merged/`
dir, e.g. `.cache/index-runs/gemma-4-31b/2026-10-02T034046Z-vast/merged/results.jsonl`) have:
- a `dataset`, a `group_id` and `status`;
- `response.answers` with one `{"type": "choice", "probabilities": {"no": p, "yes": q}}` per document (`doc_0`, `doc_1`, …).

The harness ranks every document of a group by p(yes), and `gateway/answers.py` rounds to
`DECIMALS = 4`.

**Interfaces:**
- Produces:
  - `tie_stats(results: Iterable[dict], datasets=("ToolRet", "BRIGHT")) -> dict[str, dict]`, per dataset `{"groups", "docs", "tied_docs", "saturated_docs"}`.
    - A doc is tied when another doc of its group has the same p(yes).
    - A doc is saturated when p(yes) is 0.0 or 1.0.
    - Rows whose status isn't `ok` are skipped, and so are lines that aren't valid JSON (crash tails).
  - CLI: `uv run python scripts/ties.py --profile P --run <merged dir>`, which writes `results_dir(P, "ties")/summary.md` with one row per dataset (shares as %).

- [ ] **Step 1: Write the failing test:**

```python
from scripts.ties import tie_stats


def row(group, probs, dataset="ToolRet", status="ok"):
    answers = {f"doc_{i}": {"type": "choice", "probabilities": {"no": 1 - p, "yes": p}} for i, p in enumerate(probs)}
    return {"dataset": dataset, "group_id": group, "status": status, "response": {"answers": answers}}


def test_tie_stats_counts_tied_and_saturated_docs_per_group():
    rows = [row("g1", [1.0, 1.0, 0.5]), row("g1", [0.25]), row("g2", [0.0, 0.3]), row("g3", [0.9], status="error"),
            row("g4", [0.5, 0.5], dataset="MMLU")]
    got = tie_stats(rows)
    assert got["ToolRet"] == {"groups": 2, "docs": 6, "tied_docs": 2, "saturated_docs": 3}
    assert "MMLU" not in got
```

- [ ] **Step 2: Run it.** `uv run pytest tests/unit/test_ties.py -q`. Expected: FAIL.

- [ ] **Step 3: Implement** `scripts/ties.py`. Group docs by `(dataset, group_id)`, count the p(yes) values with `Counter`, and call a doc tied when its value's count is > 1. Read the file with a line loop that skips JSON errors.

- [ ] **Step 4: Run.** `uv run pytest -q && uv run ruff check .`. Then run the CLI on gemma's baseline (`.cache/index-runs/gemma-4-31b/2026-10-02T034046Z-vast/merged`) as a smoke check. Expected: high tied and saturated shares, because gemma was uncalibrated.

- [ ] **Step 5: Commit** the code and tests only, without the smoke-run output.

```bash
git add scripts/ties.py tests/unit/test_ties.py
git commit -m "feat(m3): rounding tie check for ranking sets"
```

---

### Task 6: phase-2 report and README table

**Files:**
- Create: `scripts/phase2_report.py`
- Modify: `README.md` ("Where it stands" section)
- Test: `tests/unit/test_phase2_report.py`

**Interfaces:**
- Consumes: `scripts.board.BOARD` and `MATCHES`, and committed result folders.
- Produces:
  - `latest(profile: str, suffix: str) -> Path | None`: the newest `docs/results/<profile>/*-<suffix>` dir. The suffix is exact, so `-index` must not match `-index-subset` or `-index-replaced`, but must match `-vast-index`.
  - `profile_row(profile) -> dict`:
    - index, ECE and coverage from the latest `index` / `vast-index` summary (reuse the parsing helpers `board.py` / `evaluate.py` already have for `index.json`; read `index.json` from the run's merged dir when the summary links it);
    - latency median and p95 from the latest `latency` summary (`**ours**` row);
    - the shipped layout, orders and calibration version from the profile env and `data/<P>/<layout>/calibration.json`.
  - `markdown(rows) -> str`: one table, each profile next to its `MATCHES` board entries.
  - The CLI writes `docs/results/phase2-report.md`. `--readme` replaces the table between the
    markers `<!-- phase2-table -->` and `<!-- /phase2-table -->` in `README.md`. Add the
    markers in this task.

- [ ] **Step 1: Write the failing tests:**
  - `latest` picks the newest exact-suffix dir from a tmp tree, and ignores `-index-subset`.
  - `markdown` puts every board entry of `MATCHES[profile]` on rows after the profile's own row.
  - The README marker replacement keeps the text outside the markers byte-identical.

  Use `tmp_path` and monkeypatch the results root.

- [ ] **Step 2: Run it** and confirm the tests fail.

- [ ] **Step 3: Implement** it as small functions with a `RESULTS = ROOT / "docs" / "results"` module constant, so tests can monkeypatch it.

- [ ] **Step 4: Run.** `uv run pytest -q && uv run ruff check .`. Then run `uv run python scripts/phase2_report.py` once on the current tree. It should print the table of the existing baselines.

- [ ] **Step 5: Commit.**

```bash
git add scripts/phase2_report.py tests/unit/test_phase2_report.py README.md
git commit -m "feat(m3): phase-2 report and README table"
```

---

### Task 7 (controller, CPU): run the experiments and recommend

This task has no subagent code. The controller runs these commands and commits each results
folder by explicit path.

1. **Orders:** `uv run python scripts/m3.py orders --profile P --layout L` for every profile P in qwen3.6-27b, qwen3.8-27b and gemma-4-31b, and L in decider_chat and header.
2. **Layouts:** `uv run python scripts/m3.py layouts --profile P` for each profile.
3. **Recommendations:** write `docs/results/m3-recommendations.md`, with one line per profile:
   - the layout and orders to ship, with the CIs and the read cost;
   - any auto-switch flags.

   Then ask the owner to decide.
4. **On the owner's decision:**
   - edit `profiles/<P>.env` (`PROMPT_LAYOUT`, `OPTION_ORDERS`);
   - if the orders change, refit with `uv run python scripts/calibrate.py --profile P --orders <arm> --comment "..."`;
   - commit.

### Task 8 (controller, GPU): latency, final Index, report

1. **Live latency:** for each changed default, run `uv run python scripts/latency.py --profile P --layout L --option-orders O` on the local GPU (about 5 min each).
2. **Final full Index per profile, with the new defaults:**
   - Spread the runs over rented vast.ai boxes with `scripts/remote/` (runbook in `docs/remote-gpu.md`), one box per profile, about 8 h each.
   - Give each box a job file with `stack` plus `index` only.
   - The owner approves renting and the destroys.
3. **Ties check:** run `scripts/ties.py` on each final Index's merged dir.
4. **Report:**
   - run `uv run python scripts/phase2_report.py --readme`;
   - commit the results and README;
   - update DS-002 and tick its tasks.
