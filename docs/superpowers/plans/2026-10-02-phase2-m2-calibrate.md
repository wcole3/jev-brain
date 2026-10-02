# Phase 2 M2 (calibrate) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fit our own calibration from collected logprobs (a temperature per profile, layout and question type, plus an optional yes/no offset), store it as a stamped `calibration.json` v2 the gateway refuses when stale, and fit qwen3.6 now (qwen3.8 and gemma when their collects land).

**Architecture:**
- `gateway/calibration.py` grows a small `Calibration` value (`T` per type, noul offset `b`, source) and a v2 loader that checks a stamp, as `labels.json` loading does.
- The gateway applies `b` to the word "yes" inside `blend`, per option order and before averaging, so offline answers still equal live ones.
- `scripts/fit.py` holds the pure numeric fits (NLL search, bootstrap of a metric difference).
- `scripts/calibrate.py` reads the calib and eval collects, fits, applies the spec's shipping rule for `b`, and writes the JSON plus a report.

**Tech Stack:** Python 3.12, no new dependencies (pure Python search; the data is a few thousand questions).

**Spec:** `docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md`, section "Calibration (M2)". DS-002 "Next tests from DS-020", item 2.

## Global Constraints

- Code reads like a tutorial: small files, obvious names, comments ≤ 2 lines. `uv run pytest -q` and `uv run ruff check .` pass after every task.
- **Never fit on Jev outputs.** Fits use only `data/splits/calib.json` (JevBench gold + filtered DecisionBench). `eval` judges; Index rows are never used for fitting.
- **Model (spec):**
  - `p = softmax(lp / T)` for `choice` and `score`.
  - For `noul`, `p(yes) = σ(Δ/T + b)`, with `b` added per order before `average_back`.
- **Fit:**
  - minimise mean NLL of the gold option;
  - T searched on log T ∈ [log 0.05, log 20];
  - noul is a 2-D search over (T, b), with b ∈ [−10, 10].
- **Shipping b:** b ≠ 0 ships only when a paired bootstrap (95% CI, 2,000 resamples, seed 0) on the **eval** split's noul questions shows one of:
  - an accuracy gain (CI low > 0) without an ECE loss beyond its CI (the ECE-increase CI's low end ≤ 0);
  - an ECE gain (the ECE-decrease CI's high end < 0) without an accuracy loss beyond its CI (the accuracy-change CI's high end ≥ 0).

  Otherwise b = 0, and noul's T is refitted with b = 0.
- **File v2 (spec, plus owner's informational fields):**

  ```json
  {"format": 2,
   "version": 3,
   "date": "2026-10-02T15:10:00Z",
   "comments": [{"version": 1, "date": "...", "text": "..."}],
   "stamp": {"tokenizer_sha256", "layout_sha256", "hf_revision", "prefix_pad", "prefix_block"},
   "types": {"choice": {"T": x}, "score": {"T": x}, "noul": {"T": x, "b": x}},
   "fit": {...}}
  ```
- **Format vs version (owner decision, 2026-10-02):**
  - `format` is the schema marker the loader checks: v1 has no `format`, so v1 is refused.
  - `version`, `date` and `comments` are **informational only**, never read by the gateway.
    `version` counts refits of this file (1, 2, 3 …). `date` is the UTC time of the latest fit.
    `comments` is the change history, one `{"version", "date", "text"}` entry per fit, oldest first.
  - A refit carries the existing `comments` forward and appends one entry. With no readable v2
    file there is no history to carry, and the history restarts at version 1.
- **Gateway:**
  - a stamp mismatch, or a v1 or unstamped file, refuses startup with a message naming the field;
  - a missing file means a warning plus T = 1 and b = 0;
  - the borrowed decider v1 file (`data/qwen3.6-27b/decider_chat/calibration.json`, T = 1.943) is replaced by our fit in this milestone.
- **A fit is valid for one model, precision, layout and option-order setting.** The fit records the orders it used (`identity` today; the profiles' `OPTION_ORDERS`).
- **Results folder:** `docs/results/<profile>/<UTC YYYY-MM-DDTHHMMSSZ>-calibrate/summary.md` (repo naming convention).
- **Commits:** caveman Conventional Commits, subject ≤ 50 chars, explicit paths, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## File map

| File | Responsibility |
|---|---|
| `gateway/calibration.py` (rewrite) | `Calibration`, `softmax`, `load_calibration(path, expect)`, `stamp_for(tok, layout, settings)`, `UNCALIBRATED` |
| `gateway/decide.py` (modify) | `Engine.calibration: dict[str, Calibration]`; `blend(reads, temperature, yes_offset=0.0)`; `probabilities(reads, q_type, cal)`; `answers_for(questions, reads, cal)` |
| `gateway/app.py` (modify) | load v2 per layout with the expected stamp; `/health` key `calibration` |
| `scripts/offline.py` (modify) | `Arm.calibration: Calibration` |
| `scripts/evaluate.py`, `scripts/latency.py` (modify) | provenance key `calibration`; offline arm loads v2 against the collected stamp |
| `tests/live/test_offline_matches_live.py` (modify) | drift check and math use `calibration` |
| `scripts/fit.py` (new) | `golden_min`, `fit_temperature`, `fit_noul`, `bootstrap_diff` |
| `scripts/calibrate.py` (new) | CLI: fit per layout and type from collects, apply the b rule, write v2 JSON and report |
| `docs/background/calibration.md`, `README.md` (modify) | document v2 + `calibrate.py` |

---

### Task 1: gateway `Calibration`, v2 loader with stamp, yes-offset in `blend`

**Files:**
- Modify: `gateway/calibration.py`, `gateway/decide.py`, `gateway/app.py`
- Modify tests: `tests/unit/test_calibration.py`, `tests/unit/test_decide.py`, `tests/unit/test_app.py`, `tests/conftest.py` (engine fixture)

**Interfaces:**
- **Produces, in `gateway/calibration.py`:**
  ```python
  TYPES = ("choice", "score", "noul")
  STAMP_KEYS = ("tokenizer_sha256", "layout_sha256", "hf_revision", "prefix_pad", "prefix_block")

  @dataclass(frozen=True)
  class Calibration:
      T: dict[str, float]          # per question type
      b: float = 0.0               # noul: added to the "yes" logit after dividing by T
      source: str = "uncalibrated" # "uncalibrated" | "<file path>"
      def as_dict(self) -> dict: return {"T": dict(self.T), "b": self.b, "source": self.source}

  UNCALIBRATED = Calibration({t: 1.0 for t in TYPES})
  def softmax(logprobs: list[float], temperature: float) -> list[float]  # unchanged
  def stamp_for(tok, layout, settings) -> dict  # the STAMP_KEYS values for this tokenizer, layout and settings
  def load_calibration(path: Path, expect: dict | None) -> Calibration
  ```
- **`load_calibration` rules:**
  - missing file: `log.warning(...)`, return `UNCALIBRATED`;
  - `format != 2` or no `stamp`: `RuntimeError(f"{path}: not a v2 calibration file; rerun scripts/calibrate.py")`;
  - `version`, `date` and `comments` are not read;
  - when `expect` is given, the first differing key raises `RuntimeError(f"{path}: {key} changed ({file} != {expect}); rerun scripts/calibrate.py")`;
  - otherwise return `Calibration(T={t: types[t]["T"]}, b=types["noul"].get("b", 0.0), source=str(path))`.
- **Produces, in `gateway/decide.py`:**
  - `Engine.calibration: dict[str, Calibration]` replaces `Engine.temperatures`.
  - `def blend(reads, temperature: float, yes_offset: float = 0.0) -> list[float]`. For each order, it adds `yes_offset * temperature` to the logprob at the shown position whose `perm[j] == 1` (caller option 1 is "yes" in noul), then softmax at T, then `average_back`. With `yes_offset == 0` it is exactly today's math.
  - `def probabilities(reads, q_type: str, cal: Calibration) -> list[float]`: `blend(reads, cal.T[q_type], cal.b if q_type == "noul" else 0.0)`.
  - `def answers_for(questions, reads, cal: Calibration) -> dict`, which uses `probabilities`.
  - `decide()` passes `engine.calibration[r.layout]`.
- **Produces, in `gateway/app.py`:**
  - `calibration={name: load_calibration(s.data_dir(name) / "calibration.json", stamp_for(tok, layout, s)) for name, layout in layouts.items()}`;
  - `/health` key `"calibration": {name: cal.as_dict() for ...}`, replacing `"temperatures"`.

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_calibration.py`. Replace the two `load_temperatures` tests and keep the softmax test:

```python
import json
import math

import pytest

from gateway.calibration import UNCALIBRATED, Calibration, load_calibration, softmax

STAMP = {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "r", "prefix_pad": "off", "prefix_block": 0}


def v2(tmp_path, **over):
    data = {"format": 2, "version": 1, "date": "2026-10-02T00:00:00Z", "comments": [], "stamp": dict(STAMP),
            "types": {"choice": {"T": 1.5}, "score": {"T": 2.0}, "noul": {"T": 0.8, "b": 0.3}}, "fit": {}}
    data.update(over)
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps(data))
    return path


def test_softmax_with_temperature():
    assert softmax([0.0, math.log(3)], 1.0) == pytest.approx([0.25, 0.75])
    assert softmax([0.0, 2.0], 2.0) == pytest.approx(softmax([0.0, 1.0], 1.0))


def test_missing_file_means_uncalibrated(tmp_path):
    assert load_calibration(tmp_path / "calibration.json", STAMP) == UNCALIBRATED


def test_v2_file_loads_temperatures_and_offset(tmp_path):
    cal = load_calibration(v2(tmp_path), STAMP)
    assert cal.T == {"choice": 1.5, "score": 2.0, "noul": 0.8} and cal.b == 0.3 and cal.source.endswith(".json")


def test_v1_or_unstamped_file_is_refused(tmp_path):
    path = tmp_path / "calibration.json"
    path.write_text(json.dumps({"choice": 1.943, "score": 1.943, "noul": 1.943}))
    with pytest.raises(RuntimeError, match="not a v2"):
        load_calibration(path, STAMP)


def test_stale_stamp_is_refused_naming_the_field(tmp_path):
    with pytest.raises(RuntimeError, match="hf_revision changed"):
        load_calibration(v2(tmp_path), STAMP | {"hf_revision": "new"})


def test_no_expectation_skips_the_stamp_check(tmp_path):
    assert load_calibration(v2(tmp_path), None).b == 0.3


def test_as_dict_round_trips_through_json():
    cal = Calibration({"choice": 1.0, "score": 1.0, "noul": 2.0}, 0.5, "x")
    assert json.loads(json.dumps(cal.as_dict())) == cal.as_dict()
```

In `tests/unit/test_decide.py`, append:

```python
from gateway.calibration import Calibration
from gateway.decide import probabilities


def test_yes_offset_shifts_noul_toward_yes_in_every_order():
    reads = [([0.0, 0.0], [0, 1]), ([0.0, 0.0], [1, 0])]  # no/yes even in both orders
    p = probabilities(reads, "noul", Calibration({"choice": 1, "score": 1, "noul": 2.0}, b=1.0))
    assert p[1] == pytest.approx(1 / (1 + math.exp(-1.0)))  # sigma(0/T + b)


def test_offset_is_ignored_for_choice_and_zero_keeps_old_math():
    reads = [([0.0, -1.0, -2.0], [0, 1, 2])]
    cal = Calibration({"choice": 1.0, "score": 1.0, "noul": 1.0}, b=3.0)
    assert probabilities(reads, "choice", cal) == pytest.approx(softmax([0.0, -1.0, -2.0], 1.0))
```

(Add `import math` and import `softmax` if missing.) Update `test_decide_is_read_rows_then_answers_for` to pass `engine.calibration["decider_chat"]`.

In `tests/conftest.py`, change the engine fixture to `calibration={n: UNCALIBRATED for n in layouts}` (import it from `gateway.calibration`). In `tests/unit/test_app.py:105`, change to `assert body["calibration"] == {k: c.as_dict() for k, c in client.app.state.engine.calibration.items()}`.

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_calibration.py tests/unit/test_decide.py tests/unit/test_app.py -q`
Expected: FAIL with ImportError (`Calibration`, `load_calibration`, `probabilities`).

- [ ] **Step 3: Implement**

`gateway/calibration.py` (whole file):

```python
"""Calibration per profile and layout: a temperature per question type and a yes-offset for noul (phase 2)."""

import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path

from gateway.labels import tokenizer_sha256

log = logging.getLogger(__name__)
TYPES = ("choice", "score", "noul")
STAMP_KEYS = ("tokenizer_sha256", "layout_sha256", "hf_revision", "prefix_pad", "prefix_block")


@dataclass(frozen=True)
class Calibration:
    T: dict[str, float]
    b: float = 0.0  # noul: added to the "yes" logit after dividing by T
    source: str = "uncalibrated"

    def as_dict(self) -> dict:
        return {"T": dict(self.T), "b": self.b, "source": self.source}


UNCALIBRATED = Calibration({t: 1.0 for t in TYPES})


def softmax(logprobs: list[float], temperature: float) -> list[float]:
    top = max(logprobs)
    weights = [math.exp((x - top) / temperature) for x in logprobs]
    total = sum(weights)
    return [w / total for w in weights]


def stamp_for(tok, layout, settings) -> dict:
    """What a fit depends on: the prompt tokens (tokenizer, layout, padding) and the weights."""
    return {
        "tokenizer_sha256": tokenizer_sha256(tok),
        "layout_sha256": layout.sha256,
        "hf_revision": settings.hf_revision,
        "prefix_pad": settings.prefix_pad,
        "prefix_block": settings.prefix_block,
    }


def load_calibration(path: Path, expect: dict | None) -> Calibration:
    """Refuse v1, unstamped or stale files; with no file, run uncalibrated."""
    if not path.exists():
        log.warning("%s missing: uncalibrated (T = 1, no yes-offset)", path)
        return UNCALIBRATED
    data = json.loads(path.read_text())
    if data.get("format") != 2 or "stamp" not in data:  # version/date/comments are informational only
        raise RuntimeError(f"{path}: not a v2 calibration file; rerun scripts/calibrate.py")
    for key in STAMP_KEYS if expect is not None else ():
        if data["stamp"].get(key) != expect[key]:
            raise RuntimeError(f"{path}: {key} changed ({data['stamp'].get(key)} != {expect[key]}); rerun scripts/calibrate.py")
    types = data["types"]
    return Calibration({t: float(types[t]["T"]) for t in TYPES}, float(types["noul"].get("b", 0.0)), str(path))
```

`gateway/decide.py`:
- import `Calibration` from `gateway.calibration`;
- rename the Engine field to `calibration: dict[str, Calibration]`;
- replace `blend` and `answers_for`, and add `probabilities`:

```python
def blend(reads: list[tuple[list[float], list[int]]], temperature: float, yes_offset: float = 0.0) -> list[float]:
    """Softmax each order at T (noul: "yes" shifted by yes_offset after /T), then average back to caller order."""
    probs = []
    for lp, perm in reads:
        shifted = [x + yes_offset * temperature if perm[j] == 1 else x for j, x in enumerate(lp)] if yes_offset else lp
        probs.append(softmax(shifted, temperature))
    return average_back(probs, [perm for _, perm in reads])


def probabilities(reads: list[tuple[list[float], list[int]]], q_type: str, cal: Calibration) -> list[float]:
    return blend(reads, cal.T[q_type], cal.b if q_type == "noul" else 0.0)


def answers_for(questions: dict[str, Rendered], reads: dict, cal: Calibration) -> dict:
    return {qid: answer(q, probabilities(reads[qid], q.type, cal)) for qid, q in questions.items()}
```

and in `decide()`, use `answers_for(r.questions, r.reads, engine.calibration[r.layout])`.

`gateway/app.py`:
- import `load_calibration` and `stamp_for` instead of `load_temperatures`;
- in `load_engine`, replace the `temperatures=` line with:

```python
        calibration={name: load_calibration(s.data_dir(name) / "calibration.json", stamp_for(tok, layout, s))
                     for name, layout in layouts.items()},
```

- in `/health`, replace `"temperatures": engine.temperatures,` with `"calibration": {name: cal.as_dict() for name, cal in engine.calibration.items()},`.

- [ ] **Step 4: Run the focused tests, then the suite**

Run: `uv run pytest tests/unit/test_calibration.py tests/unit/test_decide.py tests/unit/test_app.py -q`. Expected: PASS.

Then run `uv run pytest -q`. Expected failures, all fixed in Task 2:
- `scripts/offline.py`, `scripts/evaluate.py` and `scripts/latency.py` still import or use `temperatures`;
- **parity**: `tests/parity` should pass, since the token-level parity is unchanged.

**Important:** the committed v1 file `data/qwen3.6-27b/decider_chat/calibration.json` makes the gateway refuse to start for qwen3.6 until Task 5 replaces it. Any test that builds a real qwen3.6 engine from `data/` must use the `qwen_settings` fixture (tmp data root), which has no calibration file. Check with `grep -rn "Settings.from_profile" tests/unit | grep -v tmp` and fix any test that loads the real `data/` calibration.

- [ ] **Step 5: Commit**

Commit after Task 2 makes the suite green: Tasks 1 and 2 land as one commit, because the rename touches both.

---

### Task 2: callers use `Calibration` (offline arms, evaluate, latency, live test)

**Files:**
- Modify: `scripts/offline.py`, `scripts/evaluate.py`, `scripts/latency.py`, `tests/live/test_offline_matches_live.py`, `tests/unit/test_offline.py`

**Interfaces:**
- **Consumes:** Task 1's `Calibration`, `UNCALIBRATED`, `load_calibration` and `probabilities`.
- **Produces:**
  - `scripts.offline.Arm(layout="decider_chat", orders="identity", calibration=UNCALIBRATED)`. The field `temperatures` is gone. Its report's `arm` dict carries `calibration: cal.as_dict()`.
  - `scored()` uses `probabilities(chosen, q.type, arm.calibration)`.
  - `evaluate.py offline` keeps `--uncalibrated`, which gives `UNCALIBRATED`. Otherwise it calls `load_calibration(path, expect=<stamp of the first collected record for that layout, restricted to STAMP_KEYS>)`, so an offline arm refuses a calibration fitted on a different collect.
  - Provenance keys in `evaluate.py index` and `latency.py` read `"calibration"` from `/health` instead of `"temperatures"`.
  - In the live test, the `drift` check compares `{"calibration": {k: c.as_dict()}}` with `health["calibration"]`, and `offline_answers` uses `probabilities(chosen, q.type, engine.calibration[layout])`.

- [ ] **Step 1: Update the tests first**

In `tests/unit/test_offline.py`, change the temperature test to:

```python
from gateway.calibration import Calibration

    warm = next(i for i in scored(REC, ROW, Arm(calibration=Calibration({"choice": 1, "score": 1, "noul": 4.0})), LAYOUTS)
                if i.type == "noul")
```

and add:

```python
def test_yes_offset_reaches_offline_arms():
    base = next(i for i in scored(REC, ROW, Arm(), LAYOUTS) if i.type == "noul")
    pushed = next(i for i in scored(REC, ROW, Arm(calibration=Calibration({"choice": 1, "score": 1, "noul": 1}, b=2.0)), LAYOUTS)
                  if i.type == "noul")
    assert pushed.probs[1] > base.probs[1]
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_offline.py -q`
Expected: FAIL (`Arm` has no field `calibration`).

- [ ] **Step 3: Implement**

`scripts/offline.py`:
- `from gateway.calibration import UNCALIBRATED, Calibration`;
- `from gateway.decide import probabilities` (drop the `blend` import);
- `Arm.calibration: Calibration = UNCALIBRATED`;
- in `scored`, `probabilities(chosen, q.type, arm.calibration)`;
- in `evaluate`, `"arm": {"layout": arm.layout, "orders": arm.orders, "calibration": arm.calibration.as_dict()}`;
- delete the local `UNCALIBRATED` dict.

`scripts/evaluate.py`:
- import `UNCALIBRATED`, `STAMP_KEYS` and `load_calibration` from `gateway.calibration`.
- In `cmd_offline`, replace the temps line with:

```python
    collected = COLLECT / args.profile / f"{args.split}.jsonl.gz"
    stamp = next((r["stamp"] for r in records(collected) if r["layout"] == args.layout), None)
    expect = {k: stamp[k] for k in STAMP_KEYS} if stamp else None
    cal = UNCALIBRATED if args.uncalibrated else load_calibration(s.data_dir(args.layout) / "calibration.json", expect)
    arm = Arm(args.layout, args.orders, cal)
```

- In the index provenance `keys`, replace `"temperatures"` with `"calibration"`.

`scripts/latency.py`: replace `"temperatures"` with `"calibration"` in its health keys.

`tests/live/test_offline_matches_live.py`:
- in `drift`: `ours = {...} | {"calibration": {k: c.as_dict() for k, c in engine.calibration.items()}}`;
- in `offline_answers`: `answer(q, probabilities(chosen, q.type, engine.calibration[layout]))`;
- import `probabilities` in place of `blend`.

- [ ] **Step 4: Run the full suite and lint**

Run: `uv run pytest -q && uv run pytest tests/parity -q && uv run ruff check .`
Expected: all pass. The live test is collected and deselected.

- [ ] **Step 5: Commit (Tasks 1+2)**

```bash
git add gateway/calibration.py gateway/decide.py gateway/app.py scripts/offline.py scripts/evaluate.py \
  scripts/latency.py tests/conftest.py tests/unit/test_calibration.py tests/unit/test_decide.py \
  tests/unit/test_app.py tests/unit/test_offline.py tests/live/test_offline_matches_live.py
git commit -F - <<'EOF'
feat(gateway): stamped calibration v2 + yes-offset

Calibration carries T per type and a noul yes-offset b, applied per
order before averaging. v1/unstamped/stale files refuse startup.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: numeric fits (`scripts/fit.py`)

**Files:**
- Create: `scripts/fit.py`, `tests/unit/test_fit.py`

**Interfaces:**
- **Consumes:** `gateway.decide.blend`, `gateway.calibration.softmax`, `scripts.metrics.Scored`, `ece`, `accuracy`.
- **Produces:**
  ```python
  Question = tuple[list[tuple[list[float], list[int]]], int]  # (reads: (logprobs, perm) per order, gold caller index)

  def golden_min(f, lo: float, hi: float, tol: float = 1e-4) -> float          # argmin of a unimodal f on [lo, hi]
  def nll(questions: list[Question], T: float, b: float = 0.0, noul: bool = False) -> float
  def fit_temperature(questions: list[Question]) -> float                       # argmin NLL over log T in [log .05, log 20]
  def fit_noul(questions: list[Question]) -> tuple[float, float]                # (T, b), coordinate descent on log T and b in [-10, 10]
  def bootstrap_diff(a: list, b: list, metric, resamples: int = 2000, seed: int = 0) -> tuple[float, float, float]
      # metric(items) -> float; returns (metric(b) - metric(a), 2.5%, 97.5%) over paired resamples of indices
  ```
  - `nll` uses `blend(reads, T, b if noul else 0.0)` and the probability of `gold`, floored at 1e-12, averaged.
  - `fit_noul` alternates `golden_min` over log T (b fixed) and over b (T fixed), starting at T = 1 and b = 0, for 8 rounds or until the NLL change is < 1e-7.

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_fit.py`)

```python
import math
import random

import pytest

from scripts.fit import bootstrap_diff, fit_noul, fit_temperature, golden_min, nll


def sample_choice(true_T, n=4000, k=4, seed=0):
    """Logits drawn at random; gold drawn from softmax(logits / true_T): the fit should recover true_T."""
    rng, qs = random.Random(seed), []
    for _ in range(n):
        lp = [rng.gauss(0, 2) for _ in range(k)]
        w = [math.exp(x / true_T) for x in lp]
        gold = rng.choices(range(k), weights=w)[0]
        qs.append(([(lp, list(range(k)))], gold))
    return qs


def sample_noul(true_T, true_b, n=6000, seed=1):
    rng, qs = random.Random(seed), []
    for _ in range(n):
        delta = rng.gauss(0, 3)
        p_yes = 1 / (1 + math.exp(-(delta / true_T + true_b)))
        qs.append(([([0.0, delta], [0, 1])], int(rng.random() < p_yes)))
    return qs


def test_golden_min_finds_a_parabola_minimum():
    assert golden_min(lambda x: (x - 1.3) ** 2, -5, 5) == pytest.approx(1.3, abs=1e-3)


def test_fit_temperature_recovers_the_true_temperature():
    assert fit_temperature(sample_choice(2.0)) == pytest.approx(2.0, rel=0.1)


def test_fit_noul_recovers_temperature_and_offset():
    T, b = fit_noul(sample_noul(1.5, 0.8))
    assert T == pytest.approx(1.5, rel=0.15) and b == pytest.approx(0.8, abs=0.15)


def test_fitted_nll_beats_t_equal_one():
    qs = sample_choice(3.0)
    assert nll(qs, fit_temperature(qs)) < nll(qs, 1.0)


def test_bootstrap_diff_sees_a_clear_difference():
    a, b = [0.0] * 300, [1.0] * 150 + [0.0] * 150
    mean, lo, hi = bootstrap_diff(a, b, lambda xs: sum(xs) / len(xs))
    assert mean == pytest.approx(0.5) and lo > 0.4 and hi < 0.6
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_fit.py -q`. Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement** (`scripts/fit.py`)

```python
"""Pure fits for calibration: golden-section search on NLL, and a paired bootstrap of any metric difference."""

import math
import random

from gateway.decide import blend

Question = tuple[list[tuple[list[float], list[int]]], int]
LOG_T = (math.log(0.05), math.log(20.0))
B_RANGE = (-10.0, 10.0)
RATIO = (math.sqrt(5) - 1) / 2


def golden_min(f, lo: float, hi: float, tol: float = 1e-4) -> float:
    a, b = lo, hi
    c, d = b - RATIO * (b - a), a + RATIO * (b - a)
    fc, fd = f(c), f(d)
    while b - a > tol:
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - RATIO * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + RATIO * (b - a)
            fd = f(d)
    return (a + b) / 2


def nll(questions: list[Question], T: float, b: float = 0.0, noul: bool = False) -> float:
    return sum(-math.log(max(blend(reads, T, b if noul else 0.0)[gold], 1e-12)) for reads, gold in questions) / len(questions)


def fit_temperature(questions: list[Question]) -> float:
    return math.exp(golden_min(lambda lt: nll(questions, math.exp(lt)), *LOG_T))


def fit_noul(questions: list[Question]) -> tuple[float, float]:
    """Coordinate descent: log T with b fixed, then b with T fixed, until the NLL stops moving."""
    T, b, last = 1.0, 0.0, math.inf
    for _ in range(8):
        T = math.exp(golden_min(lambda lt: nll(questions, math.exp(lt), b, noul=True), *LOG_T))
        b = golden_min(lambda x: nll(questions, T, x, noul=True), *B_RANGE)
        now = nll(questions, T, b, noul=True)
        if last - now < 1e-7:
            break
        last = now
    return T, b


def bootstrap_diff(a: list, b: list, metric, resamples: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    """metric(b) - metric(a) with a 95% interval from resampling the paired items."""
    rng, n = random.Random(seed), len(a)
    diffs = []
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(metric([b[i] for i in idx]) - metric([a[i] for i in idx]))
    diffs.sort()
    return metric(b) - metric(a), diffs[int(0.025 * resamples)], diffs[int(0.975 * resamples) - 1]
```

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest tests/unit/test_fit.py -q && uv run ruff check scripts/fit.py`. Expected: PASS. The recovery tests use fixed seeds and should finish in seconds; if they take over 20 s, reduce `n`.

- [ ] **Step 5: Commit**

```bash
git add scripts/fit.py tests/unit/test_fit.py
git commit -F - <<'EOF'
feat(scripts): NLL fits and metric bootstrap

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: `scripts/calibrate.py`

**Files:**
- Create: `scripts/calibrate.py`, `tests/unit/test_calibrate.py`

**Interfaces:**
- **Consumes:** `scripts.fit` (Task 3); `scripts.collect.records`, `COLLECT`; `scripts.splits.rows_for`, `load_split`, `SPLITS`; `gateway.calibration` (`STAMP_KEYS`, `Calibration`, `UNCALIBRATED`); `scripts.offline.gold_index`; `gateway.questions.render_question`; `gateway.layouts.load_layouts`; `gateway.orders.option_orders`; `scripts.metrics.Scored`, `ece`, `accuracy`, `nll`; `gateway.decide.probabilities`.
- **Produces:**
  ```python
  def questions_by_type(recs, rows, layout: str, orders: str) -> tuple[dict[str, list[Question]], dict]
      # {type: [(reads, gold)]} for ok records of this layout, plus the records' stamp (STAMP_KEYS);
      # raises SystemExit when the records of this layout disagree on the stamp.
  def fit_layout(calib: dict[str, list[Question]]) -> dict
      # {"choice": {"T"}, "score": {"T"}, "noul": {"T", "b"}, "noul_b0": {"T"}}; a type with < 30 questions keeps T = 1.0
  def ship_offset(eval_noul: list[Question], with_b: tuple[float, float], without_b: float) -> tuple[bool, dict]
      # the spec rule on eval noul questions; returns (ship, {"acc": (mean, lo, hi), "ece": (mean, lo, hi)})
  def history(path: Path) -> tuple[int, list[dict]]
      # (last version, comments) from an existing v2 file; (0, []) when missing, v1 or unreadable
  def calibration_file(fit: dict, stamp: dict, orders: str, calib_n: dict, before_after: dict, decision: dict,
                       previous: tuple[int, list[dict]], comment: str, date: str) -> dict
      # version = previous[0] + 1; comments = previous[1] + [{"version", "date", "text": comment}]
  def main(argv=None) -> None
      # CLI: calibrate.py --profile P [--layouts a,b] [--orders identity] [--comment TEXT] [--dry-run]
      # default comment: "refit on calib (orders <orders>)"; when replacing a v1 file:
      # "first own fit; replaces v1 file (T=<its choice T>)"
  ```
- **Behaviour of `main`:**
  - It loads the calib and eval records from `COLLECT/<P>/{calib,eval}.jsonl.gz` and the rows from `rows_for("calib")`/`rows_for("eval")`.
  - For each layout:
    1. it checks the calib and eval stamps agree;
    2. it fits on calib;
    3. it decides `b` on eval;
    4. it writes `data/<P>/<layout>/calibration.json`, unless `--dry-run`.
  - It writes one report `docs/results/<P>/<UTC>-calibrate/summary.md`. Per layout and type, the report gives:
    - n (calib/eval);
    - T and b;
    - NLL and ECE before (T = 1, b = 0) and after, on calib and on eval;
    - accuracy (eval);
    - the b decision with both CIs.

    Provenance comes from `bench_report.provenance`: repo commit, profile, orders, `split_sha256` of `data/splits/calib.json`, and the collect files.
- The `fit` block of the JSON:

  ```json
  {"split": "data/splits/calib.json",
   "split_sha256": "<sha of that file>",
   "orders": "<orders>",
   "n": {...},
   "nll": {"before": {type: x}, "after": {type: x}},
   "ece": {"before": {type: x}, "after": {type: x}},
   "b_decision": {"ship": bool, "acc": [m, lo, hi], "ece": [m, lo, hi], "b_fitted": x}}
  ```

  `before` and `after` are measured on the **eval** split, so the numbers in the file are held-out.

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_calibrate.py`)

```python
import json

from scripts import calibrate

LAYOUT = "decider_chat"
STAMP = {"tokenizer_sha256": "t", "layout_sha256": "l", "hf_revision": "r", "prefix_pad": "off", "prefix_block": 0}


def rec(i, lp, perm, qtype="choice", layout=LAYOUT, stamp=STAMP):
    return {"id": f"r{i}", "layout": layout, "status": "ok", "stamp": stamp,
            "questions": {"q": [{"perm": perm, "logprobs": lp}]}}


def row(i, qtype, gold):
    q = ({"type": "noul", "instructions": "is it?"} if qtype == "noul"
         else {"type": "choice", "instructions": "pick", "criteria": {"a": None, "b": None}})
    return {"id": f"r{i}", "source": "s", "family": "f", "state": "x", "questions": {"q": q}, "gold": {"q": gold}}


def test_questions_by_type_groups_and_reads_the_stamp():
    recs = [rec(0, [0.0, -1.0], [0, 1]), rec(1, [-1.0, 0.0], [0, 1])]
    rows = {"r0": row(0, "choice", "a"), "r1": row(1, "noul", True)}
    by_type, stamp = calibrate.questions_by_type(recs, rows, LAYOUT, "identity")
    assert len(by_type["choice"]) == 1 and len(by_type["noul"]) == 1 and stamp == STAMP
    assert by_type["noul"][0][1] == 1  # gold yes is caller index 1


def test_mixed_stamps_are_refused():
    recs = [rec(0, [0.0, -1.0], [0, 1]), rec(1, [0.0, -1.0], [0, 1], stamp=STAMP | {"hf_revision": "x"})]
    rows = {"r0": row(0, "choice", "a"), "r1": row(1, "choice", "a")}
    try:
        calibrate.questions_by_type(recs, rows, LAYOUT, "identity")
    except SystemExit as e:
        assert "hf_revision" in str(e)
    else:
        raise AssertionError("expected SystemExit")


def test_small_types_keep_temperature_one():
    fit = calibrate.fit_layout({"choice": [([([0.0, -1.0], [0, 1])], 0)] * 5, "score": [], "noul": []})
    assert fit["choice"]["T"] == 1.0 and fit["noul"] == {"T": 1.0, "b": 0.0}


def test_offset_not_shipped_without_a_gain():
    qs = [([([0.0, 0.5], [0, 1])], 1), ([([0.0, -0.5], [0, 1])], 0)] * 100  # already well separated
    ship, stats = calibrate.ship_offset(qs, with_b=(1.0, 0.0), without_b=1.0)
    assert ship is False and stats["acc"][0] == 0.0


FIT = {"choice": {"T": 1.2}, "score": {"T": 1.4}, "noul": {"T": 0.9, "b": 0.0}}


def write(path, previous, comment, date):
    data = calibrate.calibration_file(FIT, STAMP, "identity", {"choice": 1}, {"nll": {}, "ece": {}}, {"ship": False},
                                      previous, comment, date)
    path.write_text(json.dumps(data))
    return data


def test_calibration_file_is_v2_and_loadable(tmp_path):
    from gateway.calibration import load_calibration

    path = tmp_path / "calibration.json"
    write(path, (0, []), "first fit", "2026-10-02T00:00:00Z")
    cal = load_calibration(path, STAMP)
    assert cal.T == {"choice": 1.2, "score": 1.4, "noul": 0.9} and cal.b == 0.0


def test_refit_bumps_version_and_keeps_the_comment_history(tmp_path):
    path = tmp_path / "calibration.json"
    write(path, calibrate.history(path), "first fit", "2026-10-02T00:00:00Z")
    data = write(path, calibrate.history(path), "refit after layout change", "2026-10-03T00:00:00Z")
    assert data["format"] == 2 and data["version"] == 2 and data["date"] == "2026-10-03T00:00:00Z"
    assert [c["text"] for c in data["comments"]] == ["first fit", "refit after layout change"]
    assert [c["version"] for c in data["comments"]] == [1, 2]


def test_v1_or_missing_file_starts_history_at_zero(tmp_path):
    path = tmp_path / "calibration.json"
    assert calibrate.history(path) == (0, [])
    path.write_text(json.dumps({"choice": 1.943, "score": 1.943, "noul": 1.943}))
    assert calibrate.history(path) == (0, [])
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_calibrate.py -q`. Expected: ModuleNotFoundError.

- [ ] **Step 3: Implement** (`scripts/calibrate.py`)

```python
"""Fit calibration from collected logprobs: T per type (+ noul yes-offset when it earns its place on eval).

usage: uv run python scripts/calibrate.py --profile qwen3.6-27b [--layouts decider_chat,header] [--orders identity] [--dry-run]
Fits on data/splits/calib.json only (never Jev outputs, never Index rows); judges on eval.
"""

import argparse
import datetime
import hashlib
import json
from pathlib import Path

from gateway.calibration import STAMP_KEYS, Calibration
from gateway.config import ROOT, Settings
from gateway.decide import probabilities
from gateway.layouts import load_layouts
from gateway.orders import option_orders
from gateway.questions import render_question
from gateway.schema import Question as Q
from scripts import fit as fits
from scripts import metrics
from scripts.bench import git_revision
from scripts.bench_report import provenance
from scripts.collect import COLLECT, records
from scripts.metrics import Scored
from scripts.offline import gold_index
from scripts.splits import SPLITS, rows_for

MIN_QUESTIONS = 30  # fewer and the fitted T is mostly noise: keep 1.0
TYPES = ("choice", "score", "noul")


def questions_by_type(recs, rows, layout: str, orders: str):
    layouts, by_type, stamp = load_layouts(), {t: [] for t in TYPES}, None
    for rec in recs:
        if rec["layout"] != layout or rec["status"] != "ok":
            continue
        this = {k: rec["stamp"].get(k) for k in STAMP_KEYS}
        if stamp is None:
            stamp = this
        elif this != stamp:
            changed = [k for k in STAMP_KEYS if this[k] != stamp[k]]
            raise SystemExit(f"{layout}: records disagree on {', '.join(changed)}; recollect before fitting")
        row = rows[rec["id"]]
        for qid, reads in rec["questions"].items():
            q = render_question(Q(**row["questions"][qid]), layouts[layout])
            gold = gold_index(q, row["gold"].get(qid))
            if gold is None:
                continue
            wanted = option_orders(len(q.options), orders)
            chosen = [(r["logprobs"], r["perm"]) for r in reads if r["perm"] in wanted]
            by_type[q.type].append((chosen, gold))
    return by_type, stamp


def fit_layout(calib: dict) -> dict:
    out = {}
    for t in ("choice", "score"):
        out[t] = {"T": fits.fit_temperature(calib[t]) if len(calib[t]) >= MIN_QUESTIONS else 1.0}
    if len(calib["noul"]) >= MIN_QUESTIONS:
        T, b = fits.fit_noul(calib["noul"])
        out["noul"], out["noul_b0"] = {"T": T, "b": b}, {"T": fits.fit_temperature(calib["noul"])}
    else:
        out["noul"], out["noul_b0"] = {"T": 1.0, "b": 0.0}, {"T": 1.0}
    return out


def scored(questions, q_type: str, cal: Calibration) -> list[Scored]:
    return [Scored("s", "f", q_type, gold, probabilities(reads, q_type, cal)) for reads, gold in questions]


def ship_offset(eval_noul, with_b: tuple[float, float], without_b: float) -> tuple[bool, dict]:
    """The spec rule: ship b only for an accuracy or ECE gain without a loss in the other beyond its CI."""
    a = scored(eval_noul, "noul", Calibration({"choice": 1, "score": 1, "noul": without_b}))
    b = scored(eval_noul, "noul", Calibration({"choice": 1, "score": 1, "noul": with_b[0]}, with_b[1]))
    acc = fits.bootstrap_diff(a, b, metrics.accuracy)
    ece = fits.bootstrap_diff(a, b, metrics.ece)
    ship = (acc[1] > 0 and ece[1] <= 0) or (ece[2] < 0 and acc[2] >= 0)
    return ship, {"acc": acc, "ece": ece}


def history(path: Path) -> tuple[int, list[dict]]:
    """Last version and comment history of an existing v2 file; a v1, missing or unreadable file starts fresh."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return 0, []
    if data.get("format") != 2:
        return 0, []
    return int(data.get("version", 0)), list(data.get("comments", []))


def calibration_file(fit: dict, stamp: dict, orders: str, calib_n: dict, before_after: dict, decision: dict,
                     previous: tuple[int, list[dict]], comment: str, date: str) -> dict:
    split = SPLITS / "calib.json"
    version = previous[0] + 1
    return {
        "format": 2,
        "version": version,  # version, date and comments are informational; the gateway never reads them
        "date": date,
        "comments": [*previous[1], {"version": version, "date": date, "text": comment}],
        "stamp": stamp,
        "types": {"choice": fit["choice"], "score": fit["score"], "noul": fit["noul"]},
        "fit": {"split": str(split.relative_to(ROOT)) if split.is_absolute() else str(split),
                "split_sha256": hashlib.sha256(split.read_bytes()).hexdigest() if split.exists() else None,
                "orders": orders, "n": calib_n, **before_after, "b_decision": decision},
    }


def summarize(questions, q_type: str, cal: Calibration) -> dict:
    items = scored(questions, q_type, cal)
    return metrics.summary(items) if items else {"n": 0, "accuracy": None, "ece": None, "nll": None, "brier": None}


def fmt(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def default_comment(path: Path, orders: str) -> str:
    """Says when a fit replaces a v1 file, so the history starts with where the old numbers came from."""
    try:
        old = json.loads(path.read_text())
    except (OSError, ValueError):
        old = None
    if isinstance(old, dict) and old.get("format") != 2 and "choice" in old:
        return f"first own fit; replaces v1 file (T={old['choice']})"
    return f"refit on calib (orders {orders})"


def main(argv=None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--layouts")
    p.add_argument("--orders", default="identity")
    p.add_argument("--comment", help="one line for this file's change history")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    s = Settings.from_profile(args.profile)
    calib_rows, eval_rows = {r["id"]: r for r in rows_for("calib")}, {r["id"]: r for r in rows_for("eval")}
    calib_recs = list(records(COLLECT / args.profile / "calib.jsonl.gz"))
    eval_recs = list(records(COLLECT / args.profile / "eval.jsonl.gz"))
    layouts = args.layouts.split(",") if args.layouts else sorted(load_layouts())
    stamp_utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")
    lines = []
    for layout in layouts:
        calib, stamp = questions_by_type(calib_recs, calib_rows, layout, args.orders)
        held, eval_stamp = questions_by_type(eval_recs, eval_rows, layout, args.orders)
        if stamp != eval_stamp:
            raise SystemExit(f"{layout}: calib and eval were collected under different stamps")
        fit = fit_layout(calib)
        ship, stats = ship_offset(held["noul"], (fit["noul"]["T"], fit["noul"]["b"]), fit["noul_b0"]["T"]) \
            if held["noul"] else (False, {"acc": (0, 0, 0), "ece": (0, 0, 0)})
        b_fitted = fit["noul"]["b"]
        if not ship:
            fit["noul"] = {"T": fit["noul_b0"]["T"], "b": 0.0}
        cal = Calibration({t: fit[t]["T"] for t in TYPES}, fit["noul"]["b"])
        before = {t: summarize(held[t], t, Calibration({x: 1.0 for x in TYPES})) for t in TYPES}
        after = {t: summarize(held[t], t, cal) for t in TYPES}
        before_after = {"nll": {"before": {t: before[t]["nll"] for t in TYPES}, "after": {t: after[t]["nll"] for t in TYPES}},
                        "ece": {"before": {t: before[t]["ece"] for t in TYPES}, "after": {t: after[t]["ece"] for t in TYPES}}}
        decision = {"ship": ship, "acc": list(stats["acc"]), "ece": list(stats["ece"]), "b_fitted": b_fitted}
        path = s.data_dir(layout) / "calibration.json"
        previous = history(path)
        data = calibration_file(fit, stamp, args.orders, {t: len(calib[t]) for t in TYPES}, before_after, decision,
                                previous, args.comment or default_comment(path, args.orders), now_iso())
        if not args.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=1) + "\n")
        lines += [f"## {layout}", "", "| type | n calib/eval | T | b | eval NLL before → after | eval ECE before → after | eval acc |",
                  "|---|---|---|---|---|---|---|"]
        for t in TYPES:
            b_text = f"{fit['noul']['b']:+.3f}" if t == "noul" else ""
            lines.append(f"| {t} | {len(calib[t])}/{len(held[t])} | {fit[t]['T']:.3f} | {b_text} | {fmt(before[t]['nll'])} → "
                         f"{fmt(after[t]['nll'])} | {fmt(before[t]['ece'])} → {fmt(after[t]['ece'])} | {fmt(after[t]['accuracy'])} |")
        acc, ece = stats["acc"], stats["ece"]
        lines += ["", f"noul offset: fitted b = {b_fitted:+.3f}; eval accuracy change {acc[0]:+.4f} [{acc[1]:+.4f}, {acc[2]:+.4f}], "
                  f"ECE change {ece[0]:+.4f} [{ece[1]:+.4f}, {ece[2]:+.4f}] → {'shipped' if ship else 'not shipped (b = 0)'}", ""]
    meta = {"timestamp": stamp_utc, "repo commit": git_revision(), "profile": args.profile, "orders": args.orders,
            "calib split sha256": hashlib.sha256((SPLITS / "calib.json").read_bytes()).hexdigest(),
            "collect": f".cache/collect/{args.profile}/{{calib,eval}}.jsonl.gz", "written": not args.dry_run}
    out = ROOT / "docs" / "results" / args.profile / f"{stamp_utc}-calibrate"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.md").write_text(f"# {args.profile} calibration\n\n{provenance(meta)}\n" + "\n".join(lines) + "\n")
    print(out / "summary.md")


if __name__ == "__main__":
    main()
```

Notes for the implementer:
- `SPLITS` in `scripts/splits.py` is `ROOT / "data" / "splits"`. Keep the stored split path relative to ROOT; the code above handles both forms.
- Keep `calibrate.py` near this size. If a function grows past about 25 lines, split it into a helper with a clear name.

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest tests/unit/test_calibrate.py -q && uv run pytest -q && uv run ruff check .`. Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/calibrate.py tests/unit/test_calibrate.py
git commit -F - <<'EOF'
feat(scripts): calibrate.py fits T + noul offset

Fits on calib, judges on eval, ships b only on a held-out gain;
writes stamped calibration.json v2 and a report.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 5: fit qwen3.6, replace the borrowed file, document

Owner context: this step is CPU-only and needs no ok. qwen3.8 and gemma get the same run once their collects are pulled (DS-002 runbook).

**Files:**
- Replace: `data/qwen3.6-27b/{decider_chat,header,question_first}/calibration.json`
- Create: `docs/results/qwen3.6-27b/<UTC>-calibrate/summary.md`
- Modify: `docs/background/calibration.md` (section "How the gateway calibrates today" and "The phase-2 plan"), `README.md` ("When you change prompts or tokenizers": point at `scripts/calibrate.py`)

- [ ] **Step 1: Dry run, then the real fit**

```bash
uv run python scripts/calibrate.py --profile qwen3.6-27b --dry-run
uv run python scripts/calibrate.py --profile qwen3.6-27b
```

For `decider_chat`, the default comment records "first own fit; replaces v1 file (T=1.943)". The other layouts had no file and start at version 1 with "refit on calib (orders identity)". Check that each file has `format: 2`, `version: 1`, a UTC `date` and one comment.

Expected checks:
1. Every type's eval NLL after ≤ before (T only lowers NLL in expectation; a small rise on eval means overfit, so stop and report it).
2. Eval accuracy is unchanged for choice and score. noul's accuracy changes only if b shipped.
3. The three JSON files load: `uv run python -c "from pathlib import Path; from gateway.calibration import load_calibration; [print(load_calibration(Path(f'data/qwen3.6-27b/{l}/calibration.json'), None)) for l in ('decider_chat','header','question_first')]"`.

- [ ] **Step 2: Offline check with the new calibration**

```bash
uv run python scripts/evaluate.py offline --profile qwen3.6-27b --split eval --layout decider_chat
uv run python scripts/evaluate.py offline --profile qwen3.6-27b --split index-dev --layout decider_chat
```

Expected: both load the new v2 file against the collected stamp without error. Index-dev ECE (a transfer check, never fitted on) is reported in the summary. Delete these two offline result dirs unless they're kept as M2 evidence; they are evidence, so keep and commit them.

- [ ] **Step 3: Update the docs**

In `docs/background/calibration.md`:
- replace the "How the gateway calibrates today" table and its bullets with the fitted values from the report;
- note that v2 files are stamped and refused when stale;
- mark the phase-2 plan items 2, 3 and 5 as done, pointing to the report.

In README, under "When you change prompts or tokenizers", replace "Phase 2 refits them." with: `rerun uv run python scripts/calibrate.py --profile <profile> (needs a fresh collect of the calib and eval splits).`

- [ ] **Step 4: Full suite, then commit**

Run: `uv run pytest -q && uv run pytest tests/parity -q && uv run ruff check .`

```bash
git add data/qwen3.6-27b/decider_chat/calibration.json data/qwen3.6-27b/header/calibration.json \
  data/qwen3.6-27b/question_first/calibration.json docs/results/qwen3.6-27b/<UTC>-calibrate \
  docs/results/qwen3.6-27b/<UTC>-offline-eval-decider_chat-identity docs/results/qwen3.6-27b/<UTC>-offline-index-dev-decider_chat-identity \
  docs/background/calibration.md README.md
git commit -F - <<'EOF'
feat(data): qwen3.6 calibration v2 (own fit)

Replaces decider's borrowed T=1.943 with fits on our calib split for
all three layouts; held-out eval NLL/ECE in the report.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

## Out of scope (tracked elsewhere)

- **qwen3.8 and gemma fits:** rerun Task 5's commands when `.cache/collect/<profile>/{calib,eval}.jsonl.gz` are complete (box queues, DS-019).
- **4-decimal rounding ties** (DS-002 next test 2, second half): needs an Index rerun of ToolRet/BRIGHT after a fit, so it goes into the M3 plan.
- **Refits for a new default order or layout:** M3 reruns `calibrate.py --orders <arm>` if it changes `OPTION_ORDERS` or `PROMPT_LAYOUT`.
- **Index ECE with a fitted T:** comes with the final full Index run per profile (M3).
