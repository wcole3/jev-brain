# Phase 2 M1 (evaluate) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the phase-2 evaluation pipeline (data → splits → raw-logprob collection → offline metrics, sharded Decision Index runs, latency-v1-design runs, decision length-cap study) and produce the baseline per profile.

**Architecture:** Every labelled source loads into one *decision row* shape. Committed split files choose the rows. `collect.py` reads raw letter logprobs for every (row, layout, option order) through the gateway's own modules straight from vLLM. `offline.py` turns them into answers and metrics for any experiment arm. Full Index runs use the pinned upstream harness unchanged, sharded across processes, against the live gateway. Latency uses one sequential client.

**Tech Stack:** Python 3.12, uv, httpx, pydantic v2, transformers (tokenizer only), pyarrow (DecisionBench parquet, dev only), pytest, ruff. Upstream harness `apolinario/decision-index` at `87d4650b42b377c0291a89c1f1a879f9b31082bf` in its own venv.

**Spec:** `docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md`

## Global Constraints

- Code reads like a tutorial: small focused files, obvious names. Comments at most two lines.
- `uv run ruff check .` and `uv run pytest -q` pass after every task.
- **Every long run (GPU minutes+, downloads, full Index, collect, profile switch) waits for an explicit "ok" from the owner**, with an estimate of time, GPU and disk. Tasks 1–14 only run unit tests; Task 15 is the runbook.
- **Never read, train, calibrate or tune on Jev outputs.** No code path may read `.cache/jev-results/`.
- Commits: caveman style, Conventional Commits, subject ≤ 50 chars, stage explicit paths only (never `git add -A`). End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Decision length cap default: `SYSTEMONE_MAX_LEN` = 32768 (or `MAX_MODEL_LEN` if smaller); it must be ≤ `MAX_MODEL_LEN`.
- Pins: harness `87d4650b42b377c0291a89c1f1a879f9b31082bf`, edition `0.2.1`; JevBench `fcec62f13ce961115af0d16317f0ff15986a9a25` (already in `scripts/bench_data.py`); DecisionBench dataset revision `071b7b2d2e1504c89e1e5a811a3f82e1bfe3aedb`.
- Splits: JevBench gold + filtered DecisionBench 50/50 calib/eval, stratified; Index rows are eval only.
- latency-v1 design: seed `20260926`, 750 timed + 10 warm-up, systematic over (benchmark, payload length), SimpleBench (catalog 34) excluded.
- Parity gate: qwen3.6-27b `decider_chat` Index within ±1.5 of 51.35.

## Deviations from the spec (decided while planning)

- **`scripts/decision_rows.py` instead of `scripts/datasets.py`.** Running `python scripts/x.py` puts `scripts/` on `sys.path`, so a module named `datasets` would shadow Hugging Face `datasets` inside transformers.
- **`evaluate.py` is a thin CLI** over `scripts/offline.py` and `scripts/index_run.py`, to keep each file small.
- **DecisionBench is capped at 300 rows per `task_id`** (lowest hash first). The 2,222-row tasks would otherwise dominate the fits, and the cap bounds collect time.
- **DecisionBench binary rows become `noul` only when true/false is unambiguous.** That means candidate ids `true`/`false` or `label-0`/`label-1`, or labels yes/no or true/false (DecisionBench's own `public_hf._binary_candidate_ids` rule). Otherwise they become a 2-option `choice`.
- **Index ECE is computed by `metrics.py`.** The harness `score` has no ECE, and the board's calibration block cannot be reproduced exactly. Reports say so.
- **The harness is installed editable from a clone.** `suite import` reads `hub/` relative to the repository (`download.py: HUB = Path(__file__).parents[2] / "hub"`), so a wheel install would not find it.
- **The DecisionBench parquet sha256 has to be confirmed at the pinned revision.** The file we inspected hashes to `d9dd5be8e0944a7ceadfcac6cf8f9d17aab256093acff23c6de6a037ad6e55f6`, while the dataset's own summary says `6c97d3f3…`. Task 5 pins whatever the pinned revision serves, after the owner confirms.

## File map

| File | Responsibility |
|---|---|
| `gateway/config.py` (modify) | `systemone_max_len` setting |
| `gateway/app.py` (modify) | startup check cap ≤ `max_model_len`; `/health` shows the cap |
| `gateway/decide.py` (modify) | `build_batch` / `read_rows` / `blend` / `answers_for` / `decide` |
| `compose.yaml` (modify) | pass `SYSTEMONE_MAX_LEN` to the gateway |
| `scripts/metrics.py` | `Scored`, accuracy, ECE, NLL, Brier, noul bias, paired bootstrap |
| `scripts/bench_report.py` (modify) | `ece` delegates to `metrics.ece_of` |
| `scripts/decision_rows.py` | JevBench, DecisionBench, Index → decision rows; `state_key` |
| `scripts/index_suite.py` | harness clone + venv, suite rebuild/import, export |
| `scripts/harness_export.py` | runs under the harness venv: writes the scoreable 0.2.1 rows |
| `scripts/splits.py` | calib/eval, index-dev, latency-v1 split files |
| `scripts/collect.py` | raw letter logprobs per (row, layout, order) |
| `scripts/offline.py` | arms → `Scored` → metrics → markdown |
| `scripts/board.py` | board entries we compare against |
| `scripts/index_run.py` | shards, harness subprocesses, merge, replace, score, Index ECE |
| `scripts/evaluate.py` | CLI: `offline`, `index`, `replace`, `lengths` |
| `scripts/latency.py` | latency-v1-design run |
| `data/splits/*.json` | committed split id lists |
| `tests/conftest.py`, `tests/helpers.py` (modify) | shared fake-readout `engine` fixture |
| `tests/unit/test_*.py` | one test file per new module |
| `tests/live/test_offline_matches_live.py` | offline ≡ live spot check |

---

### Task 1: `SYSTEMONE_MAX_LEN` decision cap (DS-018)

Move DS-018 to Working before starting:
`sh ~/.claude/skills/dostuff-tickets/scripts/dostuff.sh call update_ticket_status '{"id":"DS-018","status":"Working"}'`

**Files:**
- Modify: `gateway/config.py` (Settings field + `from_env`)
- Modify: `gateway/app.py` (`load_engine` check, `/health`)
- Modify: `gateway/decide.py:54-58` (use the cap)
- Modify: `compose.yaml` (gateway environment, next to `MAX_MODEL_LEN` at line 47)
- Modify: `README.md` (Run a model section)
- Test: `tests/unit/test_config.py`, `tests/unit/test_decide.py`, `tests/unit/test_app.py`, `tests/unit/test_refusals.py` (new)

**Interfaces:**
- Produces: `Settings.systemone_max_len: int`. Decisions whose longest prompt is ≥ it are refused with `RequestError("prompt is longer than the maximum context length (N >= CAP tokens)")`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/unit/test_config.py`:

```python
REQUIRED = {"PROFILE": "p", "HF_MODEL": "m", "HF_REVISION": "r", "SERVED_MODEL": "s"}


def test_systemone_cap_defaults_to_32k_below_a_larger_model_limit():
    assert Settings.from_env(REQUIRED | {"MAX_MODEL_LEN": "262144"}).systemone_max_len == 32768


def test_systemone_cap_never_defaults_above_the_model_limit():
    assert Settings.from_env(REQUIRED | {"MAX_MODEL_LEN": "16384"}).systemone_max_len == 16384


def test_systemone_cap_from_env():
    env = REQUIRED | {"MAX_MODEL_LEN": "262144", "SYSTEMONE_MAX_LEN": "8192"}
    assert Settings.from_env(env).systemone_max_len == 8192
```

(If `test_config.py` already imports `Settings`, don't import it twice.)

In `tests/unit/test_decide.py`, change the two existing length tests to use the new field, and add one:

```python
async def test_too_long_prompt_is_refused_before_vllm(engine):
    small = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, systemone_max_len=50))
    with pytest.raises(RequestError, match="maximum context length"):
        await decide(small, request())
    assert engine.readout.calls == []


async def test_decision_cap_applies_below_the_model_limit(engine):
    s = dataclasses.replace(engine.settings, max_model_len=262144, systemone_max_len=50)
    with pytest.raises(RequestError, match=r"\(\d+ >= 50 tokens\)"):
        await decide(dataclasses.replace(engine, settings=s), request())
```

and in `test_padding_never_refuses_a_request_that_fits_without_it` replace `max_model_len=200` with `systemone_max_len=200`.

Append to `tests/unit/test_app.py`:

```python
def test_startup_refuses_a_decision_cap_above_the_model_limit(qwen_settings):
    bad = dataclasses.replace(qwen_settings, systemone_max_len=qwen_settings.max_model_len + 1)
    with pytest.raises(ValueError, match="SYSTEMONE_MAX_LEN"):
        load_engine(bad, None)
```

(Import `dataclasses` and `load_engine` from `gateway.app` if the file doesn't already.)

Create `tests/unit/test_refusals.py`:

```python
"""Capacity refusals must carry a decision-index harness marker, or the harness records them as errors."""

import dataclasses

import pytest

from gateway.decide import decide
from gateway.schema import RequestError, SystemOneRequest
from tests.helpers import STATE

# decision_index/engines/http.py at 87d4650: 400/413/422 bodies containing one of these become `unsupported`
HARNESS_MARKERS = (
    "options per choice",
    "a choice needs at least two options",
    "a score takes 2 to 10 levels",
    "the canvas holds",
    "maximum context length",
    "maximum model length",
    "longer than the maximum model length",
    "context window",
    "too many tokens",
)

TOO_MANY = {"q": {"type": "choice", "instructions": "pick", "criteria": {f"o{i}": None for i in range(256)}}}
TOO_FEW = {"q": {"type": "choice", "instructions": "pick", "criteria": {"only": None}}}
TOO_MANY_LEVELS = {"q": {"type": "score", "instructions": "rate", "criteria": [str(i) for i in range(11)]}}
FITS = {"q": {"type": "noul", "instructions": "is it?"}}


@pytest.mark.parametrize("questions", [TOO_MANY, TOO_FEW, TOO_MANY_LEVELS])
async def test_capacity_refusals_carry_a_marker(engine, questions):
    with pytest.raises(RequestError) as refused:
        await decide(engine, SystemOneRequest.model_validate({"state": STATE, "questions": questions}))
    assert any(m in str(refused.value) for m in HARNESS_MARKERS)


async def test_length_refusal_carries_a_marker(engine):
    small = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, systemone_max_len=10))
    with pytest.raises(RequestError) as refused:
        await decide(small, SystemOneRequest.model_validate({"state": STATE, "questions": FITS}))
    assert any(m in str(refused.value) for m in HARNESS_MARKERS)
```

`test_refusals.py` uses the `engine` fixture, which lives in `test_decide.py` today. Move `FavourFirstLabel` into `tests/helpers.py` and the `engine` fixture into `tests/conftest.py`, unchanged. Then delete them from `test_decide.py` and import `FavourFirstLabel` from `tests.helpers` where needed. Later tasks reuse the fixture.

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_config.py tests/unit/test_decide.py tests/unit/test_app.py tests/unit/test_refusals.py -q`
Expected: FAIL. `Settings` has no `systemone_max_len`.

- [ ] **Step 3: Implement**

`gateway/config.py`: add the field after `max_model_len`'s neighbours, with a default so existing constructors keep working:

```python
    systemone_max_len: int = 32768  # decisions refuse prompts this long; <= max_model_len (DS-018)
```

and in `from_env`, compute the model limit once and use it twice:

```python
        max_model_len = int(e["MAX_MODEL_LEN"])
        return cls(
            ...
            max_model_len=max_model_len,
            systemone_max_len=int(e.get("SYSTEMONE_MAX_LEN") or min(32768, max_model_len)),
            ...
        )
```

`gateway/app.py`, first lines of `load_engine` (before the tokenizer loads, so the check is cheap):

```python
def load_engine(s: Settings, client: httpx.AsyncClient) -> Engine:
    if s.systemone_max_len > s.max_model_len:
        raise ValueError(f"SYSTEMONE_MAX_LEN {s.systemone_max_len} exceeds MAX_MODEL_LEN {s.max_model_len}")
    tok = AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
```

and in `/health` add `"systemone_max_len": s.systemone_max_len,` after `"prefix_pad_always"`. If a `test_app.py` test compares the whole health body, add the key there too.

`gateway/decide.py`: in the two places that compare against `s.max_model_len`, use `s.systemone_max_len`. The refusal becomes:

```python
        raise RequestError(f"prompt is longer than the maximum context length ({longest} >= {s.systemone_max_len} tokens)")
```

`compose.yaml`: in the gateway service's `environment`, below `MAX_MODEL_LEN: ${MAX_MODEL_LEN}`:

```yaml
      SYSTEMONE_MAX_LEN: ${SYSTEMONE_MAX_LEN:-}
```

`README.md`: in "Run a model", after the bullet about switching models, add:

```markdown
- **Decision length cap:** `SYSTEMONE_MAX_LEN` (default 32,768, or `MAX_MODEL_LEN` if smaller)
  caps `/v1/systemone` prompts separately from chat. Long decisions compete with chat and
  coding agents for KV cache and prefill, so keep it below `MAX_MODEL_LEN` unless you need
  them. Over the cap is a 422 "maximum context length".
```

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest -q && uv run ruff check .`
Expected: all pass.

- [ ] **Step 5: Commit and update DS-018**

```bash
git add gateway/config.py gateway/app.py gateway/decide.py compose.yaml README.md \
  tests/unit/test_config.py tests/unit/test_decide.py tests/unit/test_app.py tests/unit/test_refusals.py \
  tests/conftest.py tests/helpers.py
git commit -F - <<'EOF'
feat(gateway): SYSTEMONE_MAX_LEN decision cap

Decisions get own context cap so vLLM limit can rise for agents.
Refusals keep harness marker text.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

Tick all four DS-018 tasks with `update_ticket_progress`, recording the sha. Move DS-018 to Verification, then `request_ticket_complete`.

---

### Task 2: split `decide` into build → read → answer

**Files:**
- Modify: `gateway/decide.py`
- Test: `tests/unit/test_decide.py`

**Interfaces:**
- Consumes: `Settings.systemone_max_len` (Task 1).
- Produces (in `gateway/decide.py`):
  - `OrderFn = Callable[[int], list[list[int]]]`: option count → permutations.
  - `@dataclass(frozen=True) class Reads: layout: str; questions: dict[str, Rendered]; reads: dict[str, list[tuple[list[float], list[int]]]]; input_tokens: int`. Each entry in `reads[qid]` is `(raw letter logprobs in shown order, perm)`.
  - `async def build_batch(engine, request, orders: OrderFn | None = None) -> tuple[str, dict[str, Rendered], Batch]`: renders and tokenizes; never refuses on length.
  - `async def read_rows(engine, request, orders: OrderFn | None = None) -> Reads`: refuses ≥ cap, then reads vLLM.
  - `def blend(reads: list[tuple[list[float], list[int]]], temperature: float) -> list[float]`: probabilities in the caller's order.
  - `def answers_for(questions, reads, temperatures: dict[str, float]) -> dict`
  - `async def decide(engine, request) -> dict` (unchanged behaviour).

- [ ] **Step 1: Write the failing tests** (append to `tests/unit/test_decide.py`)

```python
from gateway.decide import answers_for, blend, read_rows


async def test_read_rows_keeps_raw_logprobs_per_order(engine):
    r = await read_rows(engine, request(option_orders="identity+reversed"))
    assert r.layout == "decider_chat"
    assert [perm for _, perm in r.reads["department"]] == [[0, 1, 2], [2, 1, 0]]
    assert r.reads["department"][0][0] == [0.0, -1.0, -2.0]  # raw: no temperature applied


async def test_orders_function_overrides_the_setting(engine):
    r = await read_rows(engine, request(), orders=lambda n: [list(range(n))[::-1]])
    assert r.reads["department"][0][1] == [2, 1, 0]
    assert r.reads["is_urgent"][0][1] == [1, 0]


async def test_decide_is_read_rows_then_answers_for(engine):
    r = await read_rows(engine, request())
    out = await decide(engine, request())
    assert out["answers"] == answers_for(r.questions, r.reads, engine.temperatures["decider_chat"])
    assert out["usage"] == {"input_tokens": r.input_tokens, "output_tokens": 0}


def test_blend_maps_a_reversed_order_back():
    q = softmax([0.0, -1.0], 2.0)
    assert blend([([0.0, -1.0], [0, 1])], 2.0) == pytest.approx(q)
    assert blend([([0.0, -1.0], [1, 0])], 2.0) == pytest.approx([q[1], q[0]])
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_decide.py -q`
Expected: FAIL with `ImportError: cannot import name 'answers_for'`.

- [ ] **Step 3: Implement** (replace the body of `gateway/decide.py` below the `Engine` dataclass)

```python
OrderFn = Callable[[int], list[list[int]]]


@dataclass(frozen=True)
class Reads:
    layout: str
    questions: dict[str, Rendered]
    reads: dict[str, list[tuple[list[float], list[int]]]]  # per question: (raw letter logprobs, perm) per order
    input_tokens: int


async def build_batch(engine: Engine, request: SystemOneRequest, orders: OrderFn | None = None):
    """Render and tokenize every row. Refuses bad requests, but not long ones: read_rows does that."""
    s = engine.settings
    if not request.questions:
        raise RequestError("questions must not be empty")
    name = request.layout or s.prompt_layout
    if name not in engine.layouts:
        raise RequestError(f"unknown layout {name!r}; available: {sorted(engine.layouts)}")
    layout = engine.layouts[name]
    questions = {qid: render_question(q, layout) for qid, q in request.questions.items()}
    if orders is None:
        orders = functools.partial(option_orders, setting=request.option_orders or s.option_orders)
    try:
        perms = {qid: orders(len(q.options)) for qid, q in questions.items()}
    except ValueError as e:
        raise RequestError(str(e)) from e
    state = render_state(request.state)
    rows = functools.partial(
        build_rows, engine.tokenizer, engine.frames[name], layout, engine.labels[name], state, questions, perms
    )
    batch = await asyncio.to_thread(rows, engine.padding)
    if batch.longest >= s.systemone_max_len and engine.padding.enabled:
        batch = await asyncio.to_thread(rows, OFF)  # the pad must never refuse a request that fits without it
    return name, questions, batch


async def read_rows(engine: Engine, request: SystemOneRequest, orders: OrderFn | None = None) -> Reads:
    name, questions, batch = await build_batch(engine, request, orders)
    limit = engine.settings.systemone_max_len
    if batch.longest >= limit:
        raise RequestError(f"prompt is longer than the maximum context length ({batch.longest} >= {limit} tokens)")
    logprobs = await engine.readout.letter_logprobs(
        [r.ids for r in batch.rows], [r.label_ids for r in batch.rows], batch.shared_len
    )
    reads: dict[str, list] = {qid: [] for qid in questions}
    for row, lp in zip(batch.rows, logprobs, strict=True):
        reads[row.question_id].append((lp, row.perm))
    return Reads(name, questions, reads, batch.input_tokens)


def blend(reads: list[tuple[list[float], list[int]]], temperature: float) -> list[float]:
    """Softmax each order's logprobs at this temperature, then average back to the caller's option order."""
    return average_back([softmax(lp, temperature) for lp, _ in reads], [perm for _, perm in reads])


def answers_for(questions: dict[str, Rendered], reads: dict, temperatures: dict[str, float]) -> dict:
    return {qid: answer(q, blend(reads[qid], temperatures[q.type])) for qid, q in questions.items()}


async def decide(engine: Engine, request: SystemOneRequest) -> dict:
    r = await read_rows(engine, request)
    return {
        "model": engine.settings.served_model,
        "answers": answers_for(r.questions, r.reads, engine.temperatures[r.layout]),
        "usage": {"input_tokens": r.input_tokens, "output_tokens": 0},
    }
```

Imports to add or adjust at the top: `from collections.abc import Callable`, `from gateway.prompts import ChatFrame, build_rows` (unchanged), `from gateway.questions import Rendered, render_question, render_state`. Keep the module docstring.

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest -q && uv run ruff check .`
Expected: all pass, including the existing decide, app, disconnect and parity tests.

- [ ] **Step 5: Commit**

```bash
git add gateway/decide.py tests/unit/test_decide.py
git commit -F - <<'EOF'
refactor(gateway): split decide into read + answer

read_rows returns raw letter logprobs so phase-2 collect reuses
gateway code path exactly.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 3: shared metrics module

**Files:**
- Create: `scripts/metrics.py`
- Modify: `scripts/bench_report.py` (`ece`)
- Test: `tests/unit/test_metrics.py`

**Interfaces:**
- Produces (in `scripts/metrics.py`):
  - `@dataclass(frozen=True) class Scored: source: str; family: str; type: str; gold: int; probs: list[float]`, with properties `pred: int` (noul: yes when `probs[1] >= 0.5`), `correct: bool` and `confidence: float`.
  - `ece_of(confidences: list[float], correct: list[bool], bins: int = 15) -> float`
  - `accuracy(items) -> float`, `ece(items) -> float`, `nll(items) -> float`, `brier(items) -> float`
  - `noul_bias(items) -> dict[str, int]` with keys `rows`, `said_yes`, `gold_yes`, `false_no`, `false_yes`
  - `summary(items) -> dict` with keys `n`, `accuracy`, `ece`, `nll`, `brier`
  - `paired_bootstrap(a: list[float], b: list[float], resamples: int = 2000, seed: int = 0) -> tuple[float, float, float]`: mean of b − a and its 95% interval.

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_metrics.py`)

```python
import math

import pytest

from scripts.metrics import Scored, brier, ece_of, nll, noul_bias, paired_bootstrap, summary


def test_ece_matches_the_worked_example_in_calibration_md():
    conf = [0.57] * 100 + [0.90] * 300 + [0.98] * 600
    correct = [True] * 55 + [False] * 45 + [True] * 234 + [False] * 66 + [True] * 558 + [False] * 42
    assert ece_of(conf, correct) == pytest.approx(0.068, abs=1e-9)


def test_brier_and_nll_worked_examples():
    right = Scored("s", "f", "choice", 0, [0.7, 0.2, 0.1])
    wrong = Scored("s", "f", "choice", 1, [0.7, 0.2, 0.1])
    assert brier([right]) == pytest.approx(0.14)
    assert brier([wrong]) == pytest.approx(1.14)
    assert nll([Scored("s", "f", "noul", 1, [0.5, 0.5])]) == pytest.approx(math.log(2))


def test_noul_predicts_yes_at_one_half():
    tie = Scored("s", "f", "noul", 1, [0.5, 0.5])
    assert tie.pred == 1 and tie.correct and tie.confidence == 0.5


def test_noul_bias_counts():
    items = [
        Scored("s", "f", "noul", 1, [0.8, 0.2]),  # gold yes, said no
        Scored("s", "f", "noul", 0, [0.3, 0.7]),  # gold no, said yes
        Scored("s", "f", "noul", 1, [0.1, 0.9]),
        Scored("s", "f", "choice", 0, [0.9, 0.1]),  # ignored
    ]
    assert noul_bias(items) == {"rows": 3, "said_yes": 2, "gold_yes": 2, "false_no": 1, "false_yes": 1}


def test_summary_keys_and_accuracy():
    s = summary([Scored("s", "f", "choice", 0, [0.9, 0.1]), Scored("s", "f", "choice", 1, [0.9, 0.1])])
    assert s["n"] == 2 and s["accuracy"] == 0.5 and set(s) == {"n", "accuracy", "ece", "nll", "brier"}


def test_paired_bootstrap_sees_a_clear_gain_and_no_gain():
    a, b = [0.0] * 200, [1.0] * 100 + [0.0] * 100
    mean, lo, hi = paired_bootstrap(a, b)
    assert mean == pytest.approx(0.5) and lo > 0.3 and hi < 0.7
    _, lo, hi = paired_bootstrap(a, a)
    assert lo == hi == 0.0
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_metrics.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.metrics'`.

- [ ] **Step 3: Implement** (`scripts/metrics.py`)

```python
"""Scores for probability answers: accuracy, ECE, NLL, Brier, noul bias, and paired bootstrap intervals."""

import math
import random
from dataclasses import dataclass

EPS = 1e-12  # floor for log(p) so a confident miss costs a large but finite NLL


@dataclass(frozen=True)
class Scored:
    source: str
    family: str
    type: str  # choice | score | noul
    gold: int  # index of the gold option in the caller's order (noul: 0 = no, 1 = yes)
    probs: list[float]  # caller's order, sums to 1

    @property
    def pred(self) -> int:
        if self.type == "noul":
            return int(self.probs[1] >= 0.5)  # the gateway answers yes at p(yes) >= 0.5
        return max(range(len(self.probs)), key=self.probs.__getitem__)

    @property
    def correct(self) -> bool:
        return self.pred == self.gold

    @property
    def confidence(self) -> float:
        return self.probs[self.pred]


def ece_of(confidences: list[float], correct: list[bool], bins: int = 15) -> float:
    """Row-weighted mean |accuracy - confidence| over equal-width bins; confidence 1.0 goes in the top bin."""
    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for conf, ok in zip(confidences, correct, strict=True):
        buckets[min(int(conf * bins), bins - 1)].append((conf, ok))
    n = len(confidences)
    return sum(len(b) / n * abs(sum(c for c, _ in b) / len(b) - sum(o for _, o in b) / len(b)) for b in buckets if b)


def accuracy(items: list[Scored]) -> float:
    return sum(i.correct for i in items) / len(items)


def ece(items: list[Scored]) -> float:
    return ece_of([i.confidence for i in items], [i.correct for i in items])


def nll(items: list[Scored]) -> float:
    return sum(-math.log(max(i.probs[i.gold], EPS)) for i in items) / len(items)


def brier(items: list[Scored]) -> float:
    return sum(sum((p - (k == i.gold)) ** 2 for k, p in enumerate(i.probs)) for i in items) / len(items)


def noul_bias(items: list[Scored]) -> dict[str, int]:
    noul = [i for i in items if i.type == "noul"]
    return {
        "rows": len(noul),
        "said_yes": sum(i.pred == 1 for i in noul),
        "gold_yes": sum(i.gold == 1 for i in noul),
        "false_no": sum(i.gold == 1 and i.pred == 0 for i in noul),
        "false_yes": sum(i.gold == 0 and i.pred == 1 for i in noul),
    }


def summary(items: list[Scored]) -> dict:
    if not items:
        return {"n": 0, "accuracy": None, "ece": None, "nll": None, "brier": None}
    return {"n": len(items), "accuracy": accuracy(items), "ece": ece(items), "nll": nll(items), "brier": brier(items)}


def paired_bootstrap(a: list[float], b: list[float], resamples: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    """Mean of b - a over paired rows, with a 95% percentile interval from resampling the rows."""
    diffs = [y - x for x, y in zip(a, b, strict=True)]
    rng, n = random.Random(seed), len(diffs)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples))
    return sum(diffs) / n, means[int(0.025 * resamples)], means[int(0.975 * resamples) - 1]
```

In `scripts/bench_report.py`, replace the body of `ece` (keep its signature and docstring) and import at the top:

```python
from scripts.metrics import ece_of
...
def ece(rows: list[dict], bins: int = 15) -> float:
    """Expected calibration error: confidence is the probability of the predicted answer."""
    return ece_of([max(r["probabilities"].values()) for r in rows], [r["correct"] for r in rows], bins)
```

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest -q && uv run ruff check .`
Expected: all pass, including the existing `test_bench_report.py`.

- [ ] **Step 5: Commit**

```bash
git add scripts/metrics.py scripts/bench_report.py tests/unit/test_metrics.py
git commit -F - <<'EOF'
feat(scripts): shared metrics module

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 4: decision rows from JevBench

**Files:**
- Create: `scripts/decision_rows.py`
- Test: `tests/unit/test_decision_rows.py`

**Interfaces:**
- Consumes: `scripts.bench_data.jevbench_rows`, `jevbench_request`, `JEVBENCH_SHA`.
- Produces:
  - **Decision row** = `dict` with keys:
    - `id: str` (globally unique, prefixed by source);
    - `source: str` (`jevbench` | `decisionbench` | `index`);
    - `family: str`;
    - `state`;
    - `questions: dict[str, dict]` (Jev question JSON);
    - `gold: dict[str, str | bool | int | None]` (choice key, noul bool, score level; `None` means not scored);
    - `meta: dict`.
  - `state_key(state) -> str`: hash of the rendered, whitespace-normalised, casefolded state (16 hex chars).
  - `jevbench() -> list[dict]`

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_decision_rows.py`)

```python
from scripts import decision_rows

JEV = [
    {"id": "panoramic:invoices:1", "source": "panoramic", "domain": "invoices", "type": "noul", "state": "s1",
     "question": {"type": "noul", "instructions": "Total matches?"}, "label": "yes", "eval_metric": "exact"},
    {"id": "banking:3", "source": "banking77", "domain": "banking", "type": "choice", "state": "s2",
     "question": {"type": "choice", "instructions": "Intent?", "options": {"a": "A", "b": "B"}}, "label": "b",
     "eval_metric": "exact"},
    {"id": "typed_decisions:cs:9", "source": "typed_decisions", "domain": "customer_service", "type": "score",
     "state": "s3", "question": {"type": "score", "instructions": "Urgency?", "levels": ["lo", "mid", "hi"]},
     "label": "2", "eval_metric": "ordinal"},
]


def test_jevbench_rows_become_decision_rows(monkeypatch):
    monkeypatch.setattr(decision_rows, "jevbench_rows", lambda: JEV)
    rows = decision_rows.jevbench()
    assert [r["gold"]["q"] for r in rows] == [True, "b", 2]
    assert rows[0]["id"] == "jevbench:panoramic:invoices:1"
    assert rows[0]["source"] == "jevbench" and rows[0]["family"] == "invoices"
    assert rows[1]["questions"]["q"]["criteria"] == {"a": "A", "b": "B"}
    assert rows[2]["meta"] == {"eval_metric": "ordinal", "upstream_source": "typed_decisions"}


def test_state_key_ignores_whitespace_and_case():
    assert decision_rows.state_key("Hello  World\n") == decision_rows.state_key("hello world")
    assert decision_rows.state_key({"a": 1}) != decision_rows.state_key({"a": 2})
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_decision_rows.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement** (`scripts/decision_rows.py`)

```python
"""Every labelled source as one decision-row shape, so collect and evaluate never branch on the source."""

import hashlib

from gateway.questions import render_state
from scripts.bench_data import jevbench_request, jevbench_rows


def state_key(state) -> str:
    """Same text after whitespace and case are normalised = same key; used to dedupe across sources."""
    text = " ".join(render_state(state).split()).casefold()
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def jevbench_gold(question: dict, label: str):
    if question["type"] == "noul":
        return label == "yes"
    if question["type"] == "score":
        return int(label)
    return label


def jevbench() -> list[dict]:
    """JevBench gold rows (pinned in bench_data); one question per row."""
    rows = []
    for r in jevbench_rows():
        request, label = jevbench_request(r)
        question = request["questions"]["q"]
        rows.append({
            "id": f"jevbench:{r['id']}",
            "source": "jevbench",
            "family": r["domain"],
            "state": r["state"],
            "questions": {"q": question},
            "gold": {"q": jevbench_gold(question, label)},
            "meta": {"eval_metric": r["eval_metric"], "upstream_source": r["source"]},
        })
    return rows
```

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest tests/unit/test_decision_rows.py -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/decision_rows.py tests/unit/test_decision_rows.py
git commit -F - <<'EOF'
feat(scripts): decision rows from JevBench

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 5: decision rows from DecisionBench

**Files:**
- Modify: `scripts/decision_rows.py`
- Modify: `pyproject.toml` (dev dependency `pyarrow`)
- Test: `tests/unit/test_decision_rows.py`

**Interfaces:**
- Produces:
  - `DECISIONBENCH_REPO = "Hanno-Labs/decision-bench"`
  - `DECISIONBENCH_SHA = "071b7b2d2e1504c89e1e5a811a3f82e1bfe3aedb"`
  - `DECISIONBENCH_FILE = "data/eval-00000-of-00001.parquet"`
  - `DECISIONBENCH_SHA256: str`: the parquet hash at that revision, confirmed in Step 6.
  - `keep_decisionbench(rec: dict) -> bool`
  - `decisionbench_row(rec: dict) -> dict | None`
  - `decisionbench() -> list[dict]`

- [ ] **Step 1: Add the dependency**

Run: `uv add --dev pyarrow`
Expected: `pyproject.toml` dev group gains `pyarrow`; `uv.lock` updated.

- [ ] **Step 2: Write the failing tests** (append to `tests/unit/test_decision_rows.py`)

```python
import json


def rec(primitive, candidates, gold, source=None, **extra):
    return {
        "row_id": "r1", "task_id": f"dom/fam/{primitive}/task", "primitive": primitive,
        "reasoning_required": extra.pop("reasoning", False), "instruction": "Decide.",
        "state_json": json.dumps({"text": "hello"}), "candidates_json": json.dumps(candidates),
        "gold_candidate_id": gold, "source_json": json.dumps(source or {"source": {"dataset": "x/y"}}),
    }


def cand(cid, label, ordinal=None, description=None):
    return {"id": cid, "label": label, "description": description, "ordinal_value": ordinal}


def test_filters_drop_synthetic_unlicensed_and_index_sources():
    keep = decision_rows.keep_decisionbench
    assert keep(rec("candidate_selection", [], "c0"))
    assert not keep(rec("candidate_selection", [], "c0", {"kind": "synthetic_from_public_decision_contract"}))
    assert not keep(rec("candidate_selection", [], "c0", {"license": "No license declared"}))
    assert not keep(rec("candidate_selection", [], "c0", {"source": {"dataset": "PolyAI/banking77"}}))


def test_choice_row():
    row = decision_rows.decisionbench_row(
        rec("candidate_selection", [cand("c0", "Billing"), cand("c1", "Tech", description="Bugs")], "c1"))
    assert row["questions"]["q"] == {"type": "choice", "instructions": "Decide.",
                                     "criteria": {"c0": "Billing", "c1": "Tech: Bugs"}}
    assert row["gold"]["q"] == "c1" and row["id"] == "decisionbench:r1" and row["family"] == "dom/fam/candidate_selection/task"


def test_unambiguous_binary_becomes_noul():
    row = decision_rows.decisionbench_row(rec("binary_classification", [cand("c0", "No"), cand("c1", "Yes")], "c1"))
    assert row["questions"]["q"] == {"type": "noul", "instructions": "Decide."} and row["gold"]["q"] is True


def test_ambiguous_binary_stays_a_two_option_choice():
    row = decision_rows.decisionbench_row(
        rec("binary_classification", [cand("c0", "Reject"), cand("c1", "Approve")], "c0"))
    assert row["questions"]["q"]["type"] == "choice" and row["gold"]["q"] == "c0"


def test_ordinal_levels_are_sorted_by_value():
    cands = [cand("c0", "Low", 1.0), cand("c1", "High", 2.0), cand("c2", "None", 0.0)]
    row = decision_rows.decisionbench_row(rec("ordinal_scoring", cands, "c1"))
    assert row["questions"]["q"]["criteria"] == ["None", "Low", "High"] and row["gold"]["q"] == 2


def test_reasoning_rows_are_flagged():
    row = decision_rows.decisionbench_row(
        rec("candidate_selection", [cand("c0", "A"), cand("c1", "B")], "c0", reasoning=True))
    assert row["meta"]["reasoning"] is True
```

- [ ] **Step 3: Run to verify failure**

Run: `uv run pytest tests/unit/test_decision_rows.py -q`
Expected: FAIL with `AttributeError: ... keep_decisionbench`.

- [ ] **Step 4: Implement** (append to `scripts/decision_rows.py`; merge the imports at the top)

```python
import json

from huggingface_hub import hf_hub_download

from gateway.schema import MAX_LEVELS

DECISIONBENCH_REPO = "Hanno-Labs/decision-bench"
DECISIONBENCH_SHA = "071b7b2d2e1504c89e1e5a811a3f82e1bfe3aedb"
DECISIONBENCH_FILE = "data/eval-00000-of-00001.parquet"
DECISIONBENCH_SHA256 = "d9dd5be8e0944a7ceadfcac6cf8f9d17aab256093acff23c6de6a037ad6e55f6"  # confirmed in Task 5 Step 6
DROPPED_LICENCES = {"No license declared", "MIT with additional rider", "Functional Source License 1.1"}
INDEX_SOURCES = {"PolyAI/banking77", "clinc/clinc_oos", "tasksource/esci"}  # also Decision Index benchmarks


def keep_decisionbench(rec: dict) -> bool:
    """Public-gold rows only: no rows synthesised by Qwen3.8-27B-NVFP4, no unclear licences, no Index sources."""
    source = json.loads(rec["source_json"])
    upstream = source.get("source")
    dataset = upstream.get("dataset") if isinstance(upstream, dict) else None
    return "kind" not in source and source.get("license") not in DROPPED_LICENCES and dataset not in INDEX_SOURCES


def candidate_text(c: dict) -> str:
    return c["label"] if c.get("description") in (None, "") else f"{c['label']}: {c['description']}"


def binary_ids(cands: list[dict]) -> tuple[str, str] | None:
    """(false id, true id) when the two candidates clearly mean no/yes (DecisionBench's public_hf rule)."""
    by_id = {c["id"].casefold(): c["id"] for c in cands}
    for no, yes in (("false", "true"), ("label-0", "label-1")):
        if set(by_id) == {no, yes}:
            return by_id[no], by_id[yes]
    by_label = {c["label"].strip().casefold(): c["id"] for c in cands}
    no, yes = by_label.get("no") or by_label.get("false"), by_label.get("yes") or by_label.get("true")
    return (no, yes) if no and yes and no != yes else None


def decisionbench_question(rec: dict, cands: list[dict]) -> tuple[dict, object]:
    instructions, gold = rec["instruction"], rec["gold_candidate_id"]
    if rec["primitive"] == "binary_classification" and (ids := binary_ids(cands)):
        return {"type": "noul", "instructions": instructions}, gold == ids[1]
    if rec["primitive"] == "ordinal_scoring" and 2 <= len(cands) <= MAX_LEVELS:
        ordered = sorted(cands, key=lambda c: float(c["ordinal_value"] or 0.0))
        levels = [candidate_text(c) for c in ordered]
        return {"type": "score", "instructions": instructions, "criteria": levels}, [c["id"] for c in ordered].index(gold)
    criteria = {c["id"]: candidate_text(c) for c in cands}
    return {"type": "choice", "instructions": instructions, "criteria": criteria}, gold


def decisionbench_row(rec: dict) -> dict | None:
    if not rec.get("gold_candidate_id"):
        return None
    question, gold = decisionbench_question(rec, json.loads(rec["candidates_json"]))
    upstream = json.loads(rec["source_json"]).get("source")
    return {
        "id": f"decisionbench:{rec['row_id']}",
        "source": "decisionbench",
        "family": rec["task_id"],
        "state": json.loads(rec["state_json"]),
        "questions": {"q": question},
        "gold": {"q": gold},
        "meta": {
            "primitive": rec["primitive"],
            "reasoning": bool(rec["reasoning_required"]),
            "dataset": upstream.get("dataset") if isinstance(upstream, dict) else None,
        },
    }


def decisionbench() -> list[dict]:
    """The filtered rows at the pinned revision; the parquet is cached by huggingface_hub and hash-checked."""
    import pyarrow.parquet as pq  # dev-only dependency, only needed here

    path = hf_hub_download(DECISIONBENCH_REPO, DECISIONBENCH_FILE, repo_type="dataset", revision=DECISIONBENCH_SHA)
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if digest != DECISIONBENCH_SHA256:
        raise SystemExit(f"DecisionBench parquet sha256 {digest} != pinned {DECISIONBENCH_SHA256}")
    records = pq.read_table(path).to_pylist()
    return [row for rec in records if keep_decisionbench(rec) and (row := decisionbench_row(rec))]
```

- [ ] **Step 5: Run to verify pass**

Run: `uv run pytest tests/unit/test_decision_rows.py -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 6: Confirm the pinned parquet hash (short download, ~56 MB, no GPU)**

Run: `uv run python -c "from scripts.decision_rows import decisionbench; rows = decisionbench(); print(len(rows))"`
- If it prints a count (expected around 16,756: 20,000 canonical − 1,145 − 1,077 − 2,222, plus 1,200 reasoning), the hash matched.
- If it exits with a sha mismatch, **stop and show the owner both hashes** before changing `DECISIONBENCH_SHA256`.

- [ ] **Step 7: Commit**

```bash
git add scripts/decision_rows.py tests/unit/test_decision_rows.py pyproject.toml uv.lock
git commit -F - <<'EOF'
feat(scripts): DecisionBench decision rows

Public-gold rows only; drops Qwen-synthesised, unclear-licence and
Index-overlapping sources. Pinned revision + parquet sha256.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 6: pinned Decision Index harness, suite export, Index rows

**Files:**
- Create: `scripts/index_suite.py`
- Create: `scripts/harness_export.py`
- Modify: `scripts/decision_rows.py` (Index loader)
- Test: `tests/unit/test_index_suite.py`, `tests/unit/test_decision_rows.py`

**Interfaces:**
- Produces in `scripts/index_suite.py`:
  - constants `HARNESS_REPO`, `HARNESS_SHA`, `WORK` (`.cache/decision-index`), `SRC` (`WORK/src`, the clone), `VENV`, `PYTHON`, `SUITE` (`WORK/suite-0.2`), `EXPORT` (`WORK/rows-0.2.1.jsonl.gz`), `EDITION = "0.2.1"`;
  - `setup_commands() -> list[list[str]]`, `rebuild_commands() -> list[list[str]]`, `export_command() -> list[str]`, `harness_env() -> dict[str, str]`.
- Produces in `scripts/decision_rows.py`:
  - `index_gold(question: dict, expected) -> str | bool | None`
  - `index_row(raw: dict) -> dict`, whose meta holds `catalog_id`, `group_id`, `proxy_tokens` and `payload_chars`;
  - `index_rows(ids: set[str] | None = None, path=EXPORT) -> list[dict]`: streams, keeping only `ids` when given;
  - `index_meta(path=EXPORT) -> list[dict]`: rows without `state`/`questions`, with an added `state_key`.

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_index_suite.py`:

```python
from scripts import index_suite


def test_setup_clones_the_pinned_commit_into_an_editable_venv():
    cmds = index_suite.setup_commands()
    assert ["git", "-C", str(index_suite.SRC), "checkout", index_suite.HARNESS_SHA] in cmds
    assert cmds[-1][-2:] == ["-e", f"{index_suite.SRC}[rebuild]"]


def test_rebuild_then_import_into_the_work_dir():
    rebuild, imported = index_suite.rebuild_commands()
    assert rebuild[-4:] == ["suite", "rebuild", "--work", str(index_suite.WORK / "work")]
    assert "--added-rows" in imported and str(index_suite.SUITE) in imported


def test_token_is_read_from_the_secret_file(tmp_path, monkeypatch):
    secret = tmp_path / ".hf-token"
    secret.write_text("hf_abc\n")
    monkeypatch.setattr(index_suite, "HF_TOKEN_FILE", secret)
    env = index_suite.harness_env()
    assert env["HF_TOKEN"] == "hf_abc" and env["HF_HUB_DISABLE_XET"] == "1"
```

Append to `tests/unit/test_decision_rows.py`:

```python
import gzip

RAW = {
    "state": "s", "expected": {"a": "yes", "b": "opt2", "c": None},
    "questions": {
        "a": {"type": "noul", "instructions": "x"},
        "b": {"type": "choice", "instructions": "y", "criteria": {"opt1": "1", "opt2": "2"}},
        "c": {"type": "choice", "instructions": "z", "criteria": {"k": "1", "l": "2"}},
    },
    "_evaluation": {"run_id": "run-1", "dataset": "HoVer", "catalog_id": 61, "group_id": "g1", "proxy_tokens": 42},
}


def test_index_row_keeps_scoreable_gold_only():
    row = decision_rows.index_row(RAW)
    assert row["id"] == "run-1" and row["source"] == "index" and row["family"] == "HoVer"
    assert row["gold"] == {"a": True, "b": "opt2", "c": None}
    assert row["meta"]["catalog_id"] == 61 and row["meta"]["proxy_tokens"] == 42 and row["meta"]["payload_chars"] > 0


def test_index_rows_stream_and_filter(tmp_path):
    path = tmp_path / "rows.jsonl.gz"
    other = RAW | {"_evaluation": RAW["_evaluation"] | {"run_id": "run-2"}}
    with gzip.open(path, "wt") as f:
        f.write(json.dumps(RAW) + "\n" + json.dumps(other) + "\n")
    assert [r["id"] for r in decision_rows.index_rows({"run-2"}, path)] == ["run-2"]
    meta = decision_rows.index_meta(path)
    assert "state" not in meta[0] and meta[0]["state_key"] == decision_rows.state_key("s")
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_index_suite.py tests/unit/test_decision_rows.py -q`
Expected: FAIL with `ImportError` / `AttributeError`.

- [ ] **Step 3: Implement**

`scripts/index_suite.py`:

```python
"""The pinned Decision Index harness in its own venv: install, rebuild the suite, export the scoreable rows.

usage: uv run python scripts/index_suite.py setup|rebuild|export
"""

import os
import subprocess
import sys

from gateway.config import ROOT

HARNESS_REPO = "https://github.com/apolinario/decision-index"
HARNESS_SHA = "87d4650b42b377c0291a89c1f1a879f9b31082bf"
EDITION = "0.2.1"
WORK = ROOT / ".cache" / "decision-index"
SRC = WORK / "src"  # a clone: `suite import` reads hub/ relative to the repository
VENV = ROOT / ".cache" / "decision-index-venv"
PYTHON = VENV / "bin" / "python"
SUITE = WORK / "suite-0.2"
EXPORT = WORK / f"rows-{EDITION}.jsonl.gz"
REBUILT = WORK / "work" / "artifacts" / "benchmark-suite" / "release-v2-rebuilt"
HF_TOKEN_FILE = ROOT / "secrets" / ".hf-token"


def setup_commands() -> list[list[str]]:
    return [
        ["git", "clone", HARNESS_REPO, str(SRC)],
        ["git", "-C", str(SRC), "checkout", HARNESS_SHA],
        ["uv", "venv", "--python", "3.12", str(VENV)],
        ["uv", "pip", "install", "--python", str(PYTHON), "-e", f"{SRC}[rebuild]"],
    ]


def rebuild_commands() -> list[list[str]]:
    harness = [str(PYTHON), "-m", "decision_index"]
    return [
        harness + ["suite", "rebuild", "--work", str(WORK / "work")],
        harness + [
            "suite", "import", "--edition", EDITION, "--dir", str(SUITE),
            "--rows", str(REBUILT / "selected-rows.jsonl.gz"), "--added-rows", str(REBUILT / "added-rows.jsonl.gz"),
        ],
    ]


def export_command() -> list[str]:
    return [str(PYTHON), str(ROOT / "scripts" / "harness_export.py"), str(SUITE), str(EXPORT)]


def harness_env() -> dict[str, str]:
    """The HF token comes from secrets/ (HLE is gated); it is never printed or logged."""
    env = dict(os.environ, HF_HUB_DISABLE_XET="1")
    if HF_TOKEN_FILE.exists():
        env["HF_TOKEN"] = HF_TOKEN_FILE.read_text().strip()
    return env


def run(commands: list[list[str]]) -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    for command in commands:
        subprocess.run(command, cwd=SRC if SRC.exists() else WORK, env=harness_env(), check=True)


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    steps = {"setup": setup_commands, "rebuild": rebuild_commands, "export": lambda: [export_command()]}
    if step not in steps:
        raise SystemExit(__doc__)
    run(steps[step]())
```

`scripts/harness_export.py` (runs under the harness venv, so it must not import `gateway` or `scripts`):

```python
"""Run with the harness venv: verify the 0.2.1 suite, then write its scoreable rows to one file.

usage: .cache/decision-index-venv/bin/python scripts/harness_export.py SUITE_DIR OUT.jsonl.gz
"""

import gzip
import json
import sys

from decision_index.suite.io import Suite

suite_dir, out = sys.argv[1], sys.argv[2]
suite = Suite(suite_dir, "0.2.1")
report = suite.verify(strict=True)
n = 0
with gzip.open(out, "wt", encoding="utf-8") as f:
    for row in suite.rows(apply_exclusions=True):  # exclusions and the 0.2.1 subsets, as scoring sees them
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        n += 1
print(json.dumps({"rows": n, "suite_sha256": report["sha256"], "match": report["match"]}))
```

Append to `scripts/decision_rows.py`:

```python
import gzip

from scripts.index_suite import EXPORT


def index_gold(question: dict, expected):
    """Single gold answers only: a choice key in the criteria, or yes/no. Rankings and multi-answers are None."""
    if question["type"] == "noul":
        return {"yes": True, "no": False, "true": True, "false": False}.get(str(expected).casefold())
    if question["type"] == "choice" and isinstance(expected, str) and expected in (question.get("criteria") or {}):
        return expected
    return None


def index_row(raw: dict) -> dict:
    e, questions = raw["_evaluation"], raw["questions"]
    expected = raw.get("expected") or {}
    return {
        "id": e["run_id"],
        "source": "index",
        "family": e["dataset"],
        "state": raw["state"],
        "questions": questions,
        "gold": {k: index_gold(q, expected.get(k)) for k, q in questions.items()},
        "meta": {
            "catalog_id": e["catalog_id"],
            "group_id": e["group_id"],
            "proxy_tokens": e.get("proxy_tokens"),
            "payload_chars": len(json.dumps({"state": raw["state"], "questions": questions}, ensure_ascii=False)),
        },
    }


def read_export(path=EXPORT):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def index_rows(ids: set[str] | None = None, path=EXPORT) -> list[dict]:
    return [index_row(raw) for raw in read_export(path) if ids is None or raw["_evaluation"]["run_id"] in ids]


def index_meta(path=EXPORT) -> list[dict]:
    """Every Index row without its text (the full export is GBs), plus the state key for dedupe."""
    rows = []
    for raw in read_export(path):
        row = index_row(raw)
        key = state_key(row.pop("state"))
        del row["questions"]
        rows.append(row | {"state_key": key})
    return rows
```

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/index_suite.py scripts/harness_export.py scripts/decision_rows.py \
  tests/unit/test_index_suite.py tests/unit/test_decision_rows.py
git commit -F - <<'EOF'
feat(scripts): pinned Decision Index harness

Clone at 87d4650 in own venv; rebuild/import/export of 0.2.1 rows;
Index rows as decision rows.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 7: committed splits

**Files:**
- Create: `scripts/splits.py`
- Test: `tests/unit/test_splits.py`

**Interfaces:**
- Consumes: `decision_rows.jevbench()`, `decisionbench()`, `index_meta()`, `index_rows()`, `state_key()`.
- Produces:
  - `SPLITS = ROOT / "data" / "splits"`, `CAP_PER_TASK = 300`, `LATENCY_SEED = 20260926`, `SIMPLEBENCH = 34`;
  - `unit(key: str) -> float` in [0, 1), stable;
  - `cap_per_family(rows, cap) -> list[dict]`;
  - `split_extras(rows, index_keys: set[str]) -> dict[str, list[str]]` with keys `calib` and `eval`;
  - `systematic(n_items: int, n: int, rng) -> list[int]`;
  - `index_dev(meta, n_rows=8000, seed=0) -> list[str]`;
  - `latency_sample(meta, timed=750, warmup=10, seed=LATENCY_SEED) -> dict[str, list[str]]` with keys `warmup` and `timed`;
  - `load_split(name) -> dict`;
  - `rows_for(name) -> list[dict]` for `calib`, `eval`, `index-dev` and `latency-v1`. Latency returns warm-up rows first, then timed, in file order.

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_splits.py`)

```python
import random

from scripts import splits
from scripts.decision_rows import state_key


def row(i, source="jevbench", family="f", qtype="choice", state=None, **meta):
    return {"id": f"{source}:{i}", "source": source, "family": family, "state": state or f"state {i}",
            "questions": {"q": {"type": qtype}}, "gold": {"q": "a"}, "meta": meta}


def test_split_is_deterministic_disjoint_and_balanced():
    rows = [row(i) for i in range(100)]
    a, b = splits.split_extras(rows, set()), splits.split_extras(list(reversed(rows)), set())
    assert a == b
    assert not set(a["calib"]) & set(a["eval"]) and len(a["calib"]) == len(a["eval"]) == 50


def test_index_overlap_and_reasoning_rows_go_to_eval():
    rows = [row(i) for i in range(10)] + [row(99, source="decisionbench", reasoning=True)]
    out = splits.split_extras(rows, {state_key("state 3")})
    assert "jevbench:3" in out["eval"] and "decisionbench:99" in out["eval"]


def test_duplicate_states_keep_one_row():
    out = splits.split_extras([row(1, state="same"), row(2, state="Same ")], set())
    assert len(out["calib"]) + len(out["eval"]) == 1


def test_cap_per_family_keeps_the_lowest_hashes():
    rows = [row(i, family="big") for i in range(10)] + [row(50, family="small")]
    kept = splits.cap_per_family(rows, 3)
    assert len([r for r in kept if r["family"] == "big"]) == 3 and any(r["family"] == "small" for r in kept)


def test_systematic_spreads_evenly():
    idx = splits.systematic(1000, 10, random.Random(0))
    assert len(idx) == 10 and all(80 <= b - a <= 120 for a, b in zip(idx, idx[1:]))


def meta(i, catalog, group=None, chars=100):
    return {"id": f"r{i}", "meta": {"catalog_id": catalog, "group_id": group or f"g{i}", "payload_chars": chars}}


def test_index_dev_keeps_linked_groups_whole():
    rows = [meta(i, 1, group=f"g{i // 2}") for i in range(200)]
    ids = set(splits.index_dev(rows, n_rows=20))
    for g in range(100):
        assert ({f"r{2 * g}", f"r{2 * g + 1}"} <= ids) or not ({f"r{2 * g}", f"r{2 * g + 1}"} & ids)


def test_latency_sample_skips_simplebench_and_is_disjoint():
    rows = [meta(i, 34 if i < 50 else 1 + i % 5, chars=i) for i in range(2000)]
    s = splits.latency_sample(rows)
    assert len(s["timed"]) == 750 and len(s["warmup"]) == 10
    assert not set(s["timed"]) & set(s["warmup"])
    assert all(int(i[1:]) >= 50 for i in s["timed"] + s["warmup"])
    assert splits.latency_sample(rows) == s
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_splits.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement** (`scripts/splits.py`)

```python
"""Which rows each phase-2 step uses, written once to data/splits/ and committed so every fit is reproducible.

usage: uv run python scripts/splits.py   (needs the Index export from scripts/index_suite.py export)
"""

import hashlib
import json
import random
from collections import defaultdict

from gateway.config import ROOT
from scripts.bench_data import JEVBENCH_SHA
from scripts.decision_rows import (
    DECISIONBENCH_SHA,
    decisionbench,
    index_meta,
    index_rows,
    jevbench,
    state_key,
)
from scripts.index_suite import EDITION, HARNESS_SHA

SPLITS = ROOT / "data" / "splits"
SEED = "phase2-v1"
CAP_PER_TASK = 300
LATENCY_SEED = 20260926  # latency-v1's published seed
SIMPLEBENCH = 34  # outside latency-v1's scope


def unit(key: str) -> float:
    return int(hashlib.sha256(f"{SEED}:{key}".encode()).hexdigest()[:12], 16) / 16**12


def cap_per_family(rows: list[dict], cap: int) -> list[dict]:
    by_family: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_family[r["family"]].append(r)
    return [r for members in by_family.values() for r in sorted(members, key=lambda r: unit(r["id"]))[:cap]]


def split_extras(rows: list[dict], index_keys: set[str]) -> dict[str, list[str]]:
    """Dedupe by state, then alternate calib/eval in hash order inside each (source, family, type) stratum."""
    unique: dict[str, dict] = {}
    for r in sorted(rows, key=lambda r: r["id"]):
        unique.setdefault(state_key(r["state"]), r)
    strata: dict[tuple, list[dict]] = defaultdict(list)
    for r in unique.values():
        strata[(r["source"], r["family"], next(iter(r["questions"].values()))["type"])].append(r)
    out: dict[str, list[str]] = {"calib": [], "eval": []}
    for key in sorted(strata):
        for i, r in enumerate(sorted(strata[key], key=lambda r: unit(r["id"]))):
            forced = r["meta"].get("reasoning") or state_key(r["state"]) in index_keys
            out["eval" if forced or i % 2 else "calib"].append(r["id"])
    return out


def systematic(n_items: int, n: int, rng: random.Random) -> list[int]:
    """n evenly spaced indices with a random start: proportional to every stretch of the sorted list."""
    step = n_items / n
    start = rng.random() * step
    return [int(start + i * step) for i in range(n)]


def index_dev(meta: list[dict], n_rows: int = 8000, seed: int = 0) -> list[str]:
    """Whole linked groups, systematic over (benchmark, payload length)."""
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for m in meta:
        groups[(m["meta"]["catalog_id"], m["meta"]["group_id"])].append(m)
    ordered = sorted(groups.values(), key=lambda g: (g[0]["meta"]["catalog_id"], g[0]["meta"]["payload_chars"], g[0]["id"]))
    n_groups = max(1, round(n_rows * len(ordered) / len(meta)))
    return [m["id"] for i in systematic(len(ordered), n_groups, random.Random(seed)) for m in ordered[i]]


def latency_sample(meta: list[dict], timed: int = 750, warmup: int = 10, seed: int = LATENCY_SEED) -> dict:
    """latency-v1's design on our rows: systematic over (benchmark, payload length), SimpleBench out."""
    scope = sorted(
        (m for m in meta if m["meta"]["catalog_id"] != SIMPLEBENCH),
        key=lambda m: (m["meta"]["catalog_id"], m["meta"]["payload_chars"], m["id"]),
    )
    chosen = set(systematic(len(scope), timed, random.Random(seed)))
    rest = [m for i, m in enumerate(scope) if i not in chosen]
    warm = systematic(len(rest), warmup, random.Random(seed + 1))
    return {"warmup": [rest[i]["id"] for i in warm], "timed": [scope[i]["id"] for i in sorted(chosen)]}


def write(name: str, data: dict) -> None:
    SPLITS.mkdir(parents=True, exist_ok=True)
    (SPLITS / f"{name}.json").write_text(json.dumps(data, indent=0) + "\n")


def load_split(name: str) -> dict:
    return json.loads((SPLITS / f"{name}.json").read_text())


def extras() -> list[dict]:
    return jevbench() + cap_per_family(decisionbench(), CAP_PER_TASK)


def rows_for(name: str) -> list[dict]:
    split = load_split(name)
    if name in ("calib", "eval"):
        wanted = set(split["ids"])
        return [r for r in extras() if r["id"] in wanted]
    ids = split["warmup"] + split["timed"] if name == "latency-v1" else split["ids"]
    by_id = {r["id"]: r for r in index_rows(set(ids))}
    return [by_id[i] for i in ids]


def main() -> None:
    meta = index_meta()
    sources = {"jevbench": JEVBENCH_SHA, "decisionbench": DECISIONBENCH_SHA, "harness": HARNESS_SHA, "edition": EDITION}
    parts = split_extras(extras(), {m["state_key"] for m in meta})
    for name in ("calib", "eval"):
        write(name, {"meta": sources | {"seed": SEED, "cap_per_task": CAP_PER_TASK}, "ids": parts[name]})
    write("index-dev", {"meta": sources | {"rows_target": 8000}, "ids": index_dev(meta)})
    write("latency-v1", {"meta": sources | {"seed": LATENCY_SEED, "design": "latency-v1, our rows"}, **latency_sample(meta)})
    print({name: len(v) for name, v in parts.items()})


if __name__ == "__main__":
    main()
```

The split names are `calib`, `eval`, `index-dev` and `latency-v1`. `rows_for("latency-v1")` returns warm-up rows, then timed rows.

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest tests/unit/test_splits.py -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/splits.py tests/unit/test_splits.py
git commit -F - <<'EOF'
feat(scripts): phase-2 split builder

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 8: collect raw letter logprobs

**Files:**
- Create: `scripts/collect.py`
- Test: `tests/unit/test_collect.py`

**Interfaces:**
- Consumes: `read_rows`, `build_batch` (Task 2); `gateway.app.load_engine`, `vllm_client`; `splits.rows_for`.
- Produces:
  - `COLLECT = ROOT / ".cache" / "collect"`, `ARMS = ("identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4")`;
  - `all_orders(n: int) -> list[list[int]]`;
  - `stamp(engine, layout: str) -> dict`;
  - `async collect_one(engine, row, layout) -> dict`;
  - `done_keys(path) -> set[tuple[str, str]]`, `records(path) -> Iterator[dict]`;
  - `async collect(engine, rows, layouts, path, concurrency=8) -> int` (records written).
  - **Collected record:** `{"id", "layout", "stamp", "status": "ok"|"unsupported"|"invalid", "error"?, "input_tokens"?, "questions"?: {qid: [{"perm": [...], "logprobs": [...]}]}}`.
  - Output path: `COLLECT / <profile> / <split>[-len<N>].jsonl.gz`.

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_collect.py`)

```python
import dataclasses

from gateway.orders import option_orders
from scripts import collect
from tests.helpers import QUICKSTART, STATE

ROW = {"id": "r1", "source": "jevbench", "family": "f", "state": STATE, "questions": QUICKSTART, "gold": {}, "meta": {}}


def test_all_orders_cover_every_arm_without_repeats():
    for n in range(2, 12):
        orders = collect.all_orders(n)
        assert len({tuple(p) for p in orders}) == len(orders) <= 7
        for arm in collect.ARMS:
            assert all(p in orders for p in option_orders(n, arm))
    assert collect.all_orders(3) == [[0, 1, 2], [2, 1, 0], [2, 0, 1], [1, 2, 0]]


async def test_collect_one_reads_every_order(engine):
    rec = await collect.collect_one(engine, ROW, "decider_chat")
    assert rec["status"] == "ok" and rec["layout"] == "decider_chat"
    assert [r["perm"] for r in rec["questions"]["department"]] == collect.all_orders(3)
    assert rec["questions"]["is_urgent"][0]["logprobs"] == [0.0, -1.0]
    assert rec["stamp"]["profile"] == "qwen3.6-27b" and rec["input_tokens"] > 0


async def test_refusals_are_recorded_not_raised(engine):
    small = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, systemone_max_len=10))
    rec = await collect.collect_one(small, ROW, "decider_chat")
    assert rec["status"] == "unsupported" and "maximum context length" in rec["error"]
    bad = ROW | {"questions": {"q": {"type": "choice", "instructions": "x", "criteria": {"only": None}}}}
    assert (await collect.collect_one(engine, bad, "decider_chat"))["status"] == "unsupported"
    broken = ROW | {"questions": {"q": {"type": "maybe"}}}
    assert (await collect.collect_one(engine, broken, "decider_chat"))["status"] == "invalid"


async def test_collect_resumes(engine, tmp_path):
    path = tmp_path / "out.jsonl.gz"
    assert await collect.collect(engine, [ROW], ["decider_chat", "header"], path) == 2
    assert await collect.collect(engine, [ROW], ["decider_chat", "header"], path) == 0
    assert collect.done_keys(path) == {("r1", "decider_chat"), ("r1", "header")}
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_collect.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement** (`scripts/collect.py`)

```python
"""Raw letter logprobs for every row, layout and option order, read from vLLM with the gateway's own code.

usage: uv run python scripts/collect.py --profile qwen3.6-27b --split calib [--layouts decider_chat,header]
       [--vllm http://127.0.0.1:8000] [--concurrency 8] [--limit N] [--max-len N]
Needs the stack up and idle (owner ok: this is a long run). Resumes where it stopped.
"""

import argparse
import asyncio
import dataclasses
import gzip
import json
import os
from collections.abc import Iterator

from pydantic import ValidationError

from gateway.app import load_engine, vllm_client
from gateway.config import ROOT, Settings
from gateway.decide import read_rows
from gateway.labels import tokenizer_sha256
from gateway.orders import option_orders
from gateway.schema import RequestError, SystemOneRequest
from scripts.splits import rows_for

COLLECT = ROOT / ".cache" / "collect"
ARMS = ("identity", "identity+reversed", "cyclic:2", "cyclic:3", "cyclic:4")


def all_orders(n: int) -> list[list[int]]:
    """Every order an experiment arm can use, once each, so one pass serves all arms."""
    out: list[list[int]] = []
    for arm in ARMS:
        out += [perm for perm in option_orders(n, arm) if perm not in out]
    return out


def stamp(engine, layout: str) -> dict:
    s = engine.settings
    return {
        "profile": s.profile,
        "hf_revision": s.hf_revision,
        "layout_sha256": engine.layouts[layout].sha256,
        "tokenizer_sha256": tokenizer_sha256(engine.tokenizer),
        "prefix_pad": s.prefix_pad,
        "prefix_block": s.prefix_block,
        "systemone_max_len": s.systemone_max_len,
    }


async def collect_one(engine, row: dict, layout: str) -> dict:
    rec = {"id": row["id"], "layout": layout, "stamp": stamp(engine, layout)}
    try:
        request = SystemOneRequest.model_validate({"state": row["state"], "questions": row["questions"], "layout": layout})
        r = await read_rows(engine, request, all_orders)
    except ValidationError as e:
        return rec | {"status": "invalid", "error": str(e).splitlines()[0]}
    except RequestError as e:
        return rec | {"status": "unsupported", "error": str(e)}
    questions = {qid: [{"perm": perm, "logprobs": lp} for lp, perm in reads] for qid, reads in r.reads.items()}
    return rec | {"status": "ok", "input_tokens": r.input_tokens, "questions": questions}


def records(path) -> Iterator[dict]:
    """Every complete record; a run killed mid-write leaves a truncated tail, which is skipped."""
    if not path.exists():
        return
    try:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for line in f:
                if line.endswith("\n"):
                    yield json.loads(line)
    except (EOFError, gzip.BadGzipFile):
        return


def done_keys(path) -> set[tuple[str, str]]:
    return {(r["id"], r["layout"]) for r in records(path)}


async def collect(engine, rows: list[dict], layouts: list[str], path, concurrency: int = 8) -> int:
    done = done_keys(path)
    todo = [(row, layout) for row in rows for layout in layouts if (row["id"], layout) not in done]
    path.parent.mkdir(parents=True, exist_ok=True)
    gate = asyncio.Semaphore(concurrency)

    async def one(row, layout):
        async with gate:
            return await collect_one(engine, row, layout)

    with gzip.open(path, "at", encoding="utf-8") as out:
        for start in range(0, len(todo), 500):  # write in chunks so a crash loses at most one chunk
            for rec in await asyncio.gather(*(one(r, lay) for r, lay in todo[start : start + 500])):
                out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{min(start + 500, len(todo))}/{len(todo)}", flush=True)
    return len(todo)


async def main(args) -> None:
    s = dataclasses.replace(
        Settings.from_profile(args.profile), vllm_url=args.vllm, vllm_api_key=os.environ.get("VLLM_API_KEY") or None
    )
    if args.max_len:
        s = dataclasses.replace(s, systemone_max_len=args.max_len)
    async with vllm_client(s, None) as client:
        served = [m["id"] for m in (await client.get("/v1/models")).json()["data"]]
        if s.served_model not in served:
            raise SystemExit(f"vLLM serves {served}, not {s.served_model}: start the {args.profile} profile first")
        engine = load_engine(s, client)
        rows = rows_for(args.split)[: args.limit]
        layouts = args.layouts.split(",") if args.layouts else sorted(engine.layouts)
        suffix = f"-len{args.max_len}" if args.max_len else ""
        path = COLLECT / args.profile / f"{args.split}{suffix}.jsonl.gz"
        print(f"wrote {await collect(engine, rows, layouts, path, args.concurrency)} records to {path}")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--split", required=True, choices=("calib", "eval", "index-dev", "latency-v1"))
    p.add_argument("--layouts")
    p.add_argument("--vllm", default=os.environ.get("VLLM_URL", "http://127.0.0.1:8000"))
    p.add_argument("--concurrency", type=int, default=8)
    p.add_argument("--limit", type=int)
    p.add_argument("--max-len", type=int, help="decision cap override (length study); must be <= MAX_MODEL_LEN")
    return p.parse_args(argv)


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
```


- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest tests/unit/test_collect.py -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/collect.py tests/unit/test_collect.py
git commit -F - <<'EOF'
feat(scripts): collect raw letter logprobs

One pass reads every layout and order an arm can use, via
gateway read_rows straight from vLLM. Resumable jsonl.gz.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 9: offline arms and metrics

**Files:**
- Create: `scripts/offline.py`
- Test: `tests/unit/test_offline.py`

**Interfaces:**
- Consumes: `blend` (Task 2), `metrics` (Task 3), `collect.records` (Task 8), `render_question`, `load_layouts`, `option_orders`.
- Produces:
  - `@dataclass(frozen=True) class Arm: layout: str = "decider_chat"; orders: str = "identity"; temperatures: dict[str, float]` (default all 1.0);
  - `gold_index(q: Rendered, gold) -> int | None`;
  - `scored(record, row, arm, layouts) -> list[Scored]`;
  - `evaluate(recs: Iterable[dict], rows_by_id: dict[str, dict], arm) -> dict` with keys `arm`, `overall`, `by_type`, `by_source`, `by_family`, `noul_bias`, `status`;
  - `markdown(report: dict) -> str`.

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_offline.py`)

```python
import pytest

from gateway.layouts import load_layouts
from scripts.offline import Arm, evaluate, markdown, scored

LAYOUTS = load_layouts()
ROW = {
    "id": "r1", "source": "jevbench", "family": "f", "state": "s",
    "questions": {
        "c": {"type": "choice", "instructions": "pick", "criteria": {"a": None, "b": None, "c": None}},
        "n": {"type": "noul", "instructions": "is it?"},
    },
    "gold": {"c": "b", "n": True},
}
# identity favours shown position 0 (=a); reversed shows c,b,a and favours position 1 (=b) more strongly
REC = {
    "id": "r1", "layout": "decider_chat", "status": "ok",
    "questions": {
        "c": [{"perm": [0, 1, 2], "logprobs": [0.0, -1.0, -5.0]}, {"perm": [2, 1, 0], "logprobs": [-5.0, 0.0, -2.0]}],
        "n": [{"perm": [0, 1], "logprobs": [-2.0, 0.0]}, {"perm": [1, 0], "logprobs": [0.0, -2.0]}],
    },
}


def test_identity_arm_uses_one_order():
    items = scored(REC, ROW, Arm(), LAYOUTS)
    choice = next(i for i in items if i.type == "choice")
    assert choice.gold == 1 and choice.pred == 0 and not choice.correct


def test_reversed_arm_averages_both_orders():
    items = scored(REC, ROW, Arm(orders="identity+reversed"), LAYOUTS)
    choice = next(i for i in items if i.type == "choice")
    assert choice.pred == 1 and choice.probs[1] > choice.probs[0] > choice.probs[2]
    assert sum(choice.probs) == pytest.approx(1.0)


def test_noul_gold_and_temperature():
    cold = next(i for i in scored(REC, ROW, Arm(), LAYOUTS) if i.type == "noul")
    warm = next(i for i in scored(REC, ROW, Arm(temperatures={"choice": 1, "score": 1, "noul": 4.0}), LAYOUTS)
                if i.type == "noul")
    assert cold.gold == 1 and cold.correct and warm.probs[1] < cold.probs[1]


def test_unsupported_and_other_layouts_are_not_scored():
    assert scored(REC | {"status": "unsupported"}, ROW, Arm(), LAYOUTS) == []
    assert scored(REC, ROW, Arm(layout="header"), LAYOUTS) == []


def test_evaluate_reports_status_counts_and_renders():
    report = evaluate([REC, {"id": "r2", "layout": "decider_chat", "status": "unsupported"}], {"r1": ROW}, Arm())
    assert report["status"] == {"ok": 1, "unsupported": 1}
    assert report["overall"]["n"] == 2 and set(report["by_type"]) == {"choice", "noul"}
    assert "| choice |" in markdown(report)
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_offline.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement** (`scripts/offline.py`)

```python
"""Experiment arms from collected logprobs: pick the orders, apply temperatures, average, score against gold."""

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

from gateway.decide import blend
from gateway.layouts import load_layouts
from gateway.orders import option_orders
from gateway.questions import Rendered, render_question
from gateway.schema import Question
from scripts import metrics
from scripts.metrics import Scored

UNCALIBRATED = {"choice": 1.0, "score": 1.0, "noul": 1.0}


@dataclass(frozen=True)
class Arm:
    layout: str = "decider_chat"
    orders: str = "identity"
    temperatures: dict[str, float] = field(default_factory=lambda: dict(UNCALIBRATED))


def gold_index(q: Rendered, gold) -> int | None:
    if gold is None:
        return None
    if q.type == "noul":
        return int(bool(gold))
    if q.type == "choice":
        return q.names.index(gold) if gold in q.names else None
    return int(gold) if 0 <= int(gold) < len(q.names) else None


def scored(record: dict, row: dict, arm: Arm, layouts: dict) -> list[Scored]:
    """One Scored per gold-labelled question, as the gateway would answer it under this arm."""
    if record["status"] != "ok" or record["layout"] != arm.layout:
        return []
    out = []
    for qid, reads in record["questions"].items():
        q = render_question(Question(**row["questions"][qid]), layouts[arm.layout])
        gold = gold_index(q, row["gold"].get(qid))
        if gold is None:
            continue
        wanted = option_orders(len(q.options), arm.orders)
        chosen = [(r["logprobs"], r["perm"]) for r in reads if r["perm"] in wanted]
        out.append(Scored(row["source"], row["family"], q.type, gold, blend(chosen, arm.temperatures[q.type])))
    return out


def grouped(items: list[Scored], key) -> dict[str, dict]:
    groups: dict[str, list[Scored]] = defaultdict(list)
    for i in items:
        groups[key(i)].append(i)
    return {k: metrics.summary(v) for k, v in sorted(groups.items())}


def evaluate(recs: Iterable[dict], rows_by_id: dict[str, dict], arm: Arm) -> dict:
    layouts, items, status = load_layouts(), [], Counter()
    for rec in recs:
        if rec["layout"] != arm.layout:
            continue
        status[rec["status"]] += 1
        items += scored(rec, rows_by_id[rec["id"]], arm, layouts) if rec["status"] == "ok" else []
    return {
        "arm": {"layout": arm.layout, "orders": arm.orders, "temperatures": arm.temperatures},
        "overall": metrics.summary(items),
        "by_type": grouped(items, lambda i: i.type),
        "by_source": grouped(items, lambda i: i.source),
        "by_family": grouped(items, lambda i: f"{i.source}/{i.family}"),
        "noul_bias": metrics.noul_bias(items),
        "status": dict(status),
    }


def fmt(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


def table(title: str, groups: dict[str, dict]) -> list[str]:
    lines = [f"| {title} | n | accuracy | ECE | NLL | Brier |", "|---|---|---|---|---|---|"]
    lines += [f"| {k} | {g['n']} | {fmt(g['accuracy'])} | {fmt(g['ece'])} | {fmt(g['nll'])} | {fmt(g['brier'])} |"
              for k, g in groups.items()]
    return lines


def markdown(report: dict) -> str:
    """Accuracy here is over answered, gold-labelled questions; refusals are counted separately under Status."""
    b = report["noul_bias"]
    lines = [
        f"Arm: {report['arm']}",
        "",
        "Status: " + ", ".join(f"{k} {v}" for k, v in sorted(report["status"].items())),
        "",
        *table("all", {"all": report["overall"]}),
        "",
        *table("type", report["by_type"]),
        "",
        *table("source", report["by_source"]),
        "",
        f"Noul: {b['rows']} rows, said yes {b['said_yes']}, gold yes {b['gold_yes']}, "
        f"false no {b['false_no']}, false yes {b['false_yes']}",
        "",
        *table("family", report["by_family"]),
    ]
    return "\n".join(lines) + "\n"
```


- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest tests/unit/test_offline.py -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/offline.py tests/unit/test_offline.py
git commit -F - <<'EOF'
feat(scripts): offline arms + metrics

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 10: sharded Index runs, board comparison, `evaluate.py`

**Files:**
- Create: `scripts/board.py`, `scripts/index_run.py`, `scripts/evaluate.py`
- Test: `tests/unit/test_index_run.py`, `tests/unit/test_board.py`

**Interfaces:**
- Consumes: `index_suite.PYTHON`, `SRC`, `SUITE`, `EXPORT`, `EDITION`; `decision_rows.index_rows`, `index_gold`; `offline` (Task 9); `collect.records`; `bench.git_revision`, `bench.chat_once`, `bench.CHAT_PROMPTS`; `bench_report.provenance`, `percentile`; `bench_vllm.Vllm`.
- Produces:
  - `board.BOARD: dict[str, dict]`, `board.MATCHES: dict[str, list[str]]`, `board.PARITY: dict[str, tuple[str, float]]`, `board.comparison(profile, ours: dict) -> list[str]` (markdown lines);
  - `index_run.write_shards(rows_path, n, out_dir, ids=None) -> list[Path]`;
  - `index_run.shard_command(shard: Path, out: Path, gateway: str) -> list[str]`;
  - `index_run.merge(shard_dirs: list[Path], out: Path) -> dict[str, int]`: last line per `run_id` wins (resume appends retries);
  - `index_run.replace(base: Path, override: Path, out: Path) -> int`;
  - `index_run.score_command(results: Path, out: Path) -> list[str]`;
  - `index_run.index_scored(results: Path, rows_by_id) -> list[Scored]`;
  - `evaluate.py` subcommands `offline`, `index` and `replace`. `lengths` comes in Task 12.

- [ ] **Step 1: Write the failing tests**

`tests/unit/test_board.py`:

```python
from scripts import board


def test_every_profile_has_a_matching_entry_and_qwen36_has_the_parity_gate():
    assert set(board.MATCHES) == {"qwen3.6-27b", "qwen3.8-27b", "gemma-4-31b"}
    assert all(e in board.BOARD for entries in board.MATCHES.values() for e in entries)
    assert board.PARITY["qwen3.6-27b"] == ("decider-chat-qwen3.6-27b", 1.5)


def test_comparison_flags_a_parity_miss():
    lines = board.comparison("qwen3.6-27b", {"index": 48.0, "ece": 0.03, "median_ms": 80.0, "coverage": 0.99})
    assert any("MISS" in line for line in lines)
    ok = board.comparison("qwen3.6-27b", {"index": 51.0, "ece": 0.03, "median_ms": 80.0, "coverage": 0.99})
    assert any("pass" in line for line in ok)
```

`tests/unit/test_index_run.py`:

```python
import gzip
import json

from scripts import index_run
from scripts.metrics import Scored


def write_rows(path, n):
    with gzip.open(path, "wt") as f:
        for i in range(n):
            f.write(json.dumps({"_evaluation": {"run_id": f"r{i}"}, "state": "", "questions": {}}) + "\n")


def run_ids(path):
    with gzip.open(path, "rt") as f:
        return [json.loads(line)["_evaluation"]["run_id"] for line in f]


def test_shards_partition_the_rows(tmp_path):
    write_rows(tmp_path / "rows.jsonl.gz", 10)
    shards = index_run.write_shards(tmp_path / "rows.jsonl.gz", 3, tmp_path / "s")
    ids = [i for s in shards for i in run_ids(s)]
    assert sorted(ids) == sorted(f"r{i}" for i in range(10)) and len(shards) == 3


def test_shards_can_be_limited_to_ids(tmp_path):
    write_rows(tmp_path / "rows.jsonl.gz", 10)
    shards = index_run.write_shards(tmp_path / "rows.jsonl.gz", 2, tmp_path / "s", ids={"r3", "r7"})
    assert sorted(i for s in shards for i in run_ids(s)) == ["r3", "r7"]


def test_merge_keeps_the_last_attempt(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(), b.mkdir()
    (a / "results.jsonl").write_text(
        json.dumps({"run_id": "r1", "status": "error"}) + "\n" + json.dumps({"run_id": "r1", "status": "ok"}) + "\n")
    (b / "results.jsonl").write_text(json.dumps({"run_id": "r2", "status": "unsupported"}) + "\n")
    counts = index_run.merge([a, b], tmp_path / "m")
    assert counts == {"ok": 1, "unsupported": 1}
    assert len((tmp_path / "m" / "results.jsonl").read_text().splitlines()) == 2


def test_replace_overrides_by_run_id(tmp_path):
    base, over = tmp_path / "base.jsonl", tmp_path / "over.jsonl"
    base.write_text("".join(json.dumps({"run_id": f"r{i}", "status": "unsupported"}) + "\n" for i in range(3)))
    over.write_text(json.dumps({"run_id": "r1", "status": "ok"}) + "\n")
    assert index_run.replace(base, over, tmp_path / "out") == 1
    statuses = [json.loads(x)["status"] for x in (tmp_path / "out" / "results.jsonl").read_text().splitlines()]
    assert statuses == ["unsupported", "ok", "unsupported"]


def test_shard_command_drives_the_http_engine(tmp_path):
    cmd = index_run.shard_command(tmp_path / "s.jsonl.gz", tmp_path / "out", "http://127.0.0.1:9000")
    assert cmd[1:5] == ["-m", "decision_index", "run", "--engine"] and "base_url=http://127.0.0.1:9000" in cmd
    assert "--compact" in cmd


def test_index_scored_reads_choice_and_noul_answers(tmp_path):
    rows = {"r1": {"source": "index", "family": "X", "gold": {"a": "k", "b": True},
                   "questions": {"a": {"type": "choice", "criteria": {"j": "", "k": ""}}, "b": {"type": "noul"}}}}
    result = {"run_id": "r1", "status": "ok", "response": {"answers": {
        "a": {"type": "choice", "choice": "k", "probabilities": {"j": 0.2, "k": 0.8}},
        "b": {"type": "noul", "noul": 0.3}}}}
    (tmp_path / "results.jsonl").write_text(json.dumps(result) + "\n")
    items = index_run.index_scored(tmp_path / "results.jsonl", rows)
    assert items == [Scored("index", "X", "choice", 1, [0.2, 0.8]), Scored("index", "X", "noul", 1, [0.7, 0.3])]
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_index_run.py tests/unit/test_board.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

`scripts/board.py`:

```python
"""Decision Index 0.2.1 board entries we compare against (snapshot 2026-09-27, docs/3-leaderboard.md)."""

BOARD = {
    "jev": {"name": "Jev (hosted API, latency over HTTPS)", "index": 57.9, "ece": 0.074, "median_ms": 524.1},
    "decider-chat-qwen3.6-27b": {"name": "Decider chat · Qwen3.6-27B", "index": 51.35, "ece": 0.0209, "median_ms": 83.6},
    "decider-chat-gemma4-31b": {"name": "Decider chat · Gemma-4-31B", "index": 57.33, "ece": 0.0471, "median_ms": 108.5},
    "simple-jev-qwen3.8-27b": {"name": "simple-jev · Qwen3.8-27B", "index": 55.7, "ece": 0.113, "median_ms": 373.0},
    "reflex-27b": {"name": "reflex 27B", "index": 52.2, "ece": 0.024, "median_ms": 108.0},
    "jevfire-uncapped": {"name": "Jevfire (Qwen3.8-27B-FP8)", "index": 49.4, "ece": 0.0521, "median_ms": 89.6},
}
MATCHES = {
    "qwen3.6-27b": ["decider-chat-qwen3.6-27b"],
    "gemma-4-31b": ["decider-chat-gemma4-31b"],
    "qwen3.8-27b": ["simple-jev-qwen3.8-27b", "reflex-27b", "jevfire-uncapped"],
}
PARITY = {"qwen3.6-27b": ("decider-chat-qwen3.6-27b", 1.5)}  # same prompt token for token as decider


def fmt(x, digits: int) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def comparison(profile: str, ours: dict) -> list[str]:
    """Ours next to the matching entries and Jev. ECE and latency are measured differently; see the notes."""
    lines = ["| entry | Index | ECE | median ms | coverage |", "|---|---|---|---|---|"]
    lines.append(f"| **ours: {profile}** | {fmt(ours['index'], 2)} | {fmt(ours['ece'], 3)} "
                 f"| {fmt(ours['median_ms'], 1)} | {fmt(ours['coverage'], 3)} |")
    for key in [*MATCHES[profile], "jev"]:
        e = BOARD[key]
        lines.append(f"| {e['name']} | {e['index']:.2f} | {e['ece']:.3f} | {e['median_ms']:.1f} | board |")
    if profile in PARITY:
        key, tolerance = PARITY[profile]
        gap = ours["index"] - BOARD[key]["index"]
        verdict = "pass" if abs(gap) <= tolerance else "MISS: file a ticket before M2"
        lines += ["", f"Parity gate vs {BOARD[key]['name']}: {gap:+.2f} (±{tolerance}) → {verdict}"]
    return lines
```

`scripts/index_run.py`:

```python
"""Full Decision Index runs: the pinned harness, unchanged, sharded across processes against the gateway."""

import asyncio
import gzip
import json
from collections import Counter
from pathlib import Path

from scripts.index_suite import EDITION, PYTHON, SRC, SUITE
from scripts.metrics import Scored


def write_shards(rows_path: Path, n: int, out_dir: Path, ids: set[str] | None = None) -> list[Path]:
    """Round-robin rows into n files; with ids, only those rows (the length study's long rows)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [out_dir / f"shard-{i}.jsonl.gz" for i in range(n)]
    files = [gzip.open(p, "wt", encoding="utf-8") for p in paths]
    with gzip.open(rows_path, "rt", encoding="utf-8") as rows:
        k = 0
        for line in rows:
            if ids is None or json.loads(line)["_evaluation"]["run_id"] in ids:
                files[k % n].write(line)
                k += 1
    for f in files:
        f.close()
    return paths


def shard_command(shard: Path, out: Path, gateway: str) -> list[str]:
    return [
        str(PYTHON), "-m", "decision_index", "run", "--engine", "http",
        "--option", f"base_url={gateway}", "--option", "model=jev-latest",
        "--rows", str(shard), "--out", str(out), "--compact",
    ]


async def run_all(commands: list[list[str]], env: dict) -> list[int]:
    procs = [await asyncio.create_subprocess_exec(*c, cwd=SRC, env=env) for c in commands]
    return [await p.wait() for p in procs]


def last_attempts(paths: list[Path]) -> dict[str, dict]:
    """The harness appends a retry after an error, so the last line per run_id is the answer."""
    latest: dict[str, dict] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                latest[r["run_id"]] = r
    return latest


def write_results(results: dict[str, dict], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.jsonl").write_text("".join(json.dumps(r) + "\n" for r in results.values()), encoding="utf-8")


def merge(shard_dirs: list[Path], out: Path) -> dict[str, int]:
    results = last_attempts([d / "results.jsonl" for d in shard_dirs if (d / "results.jsonl").exists()])
    write_results(results, out)
    return dict(Counter(r["status"] for r in results.values()))


def replace(base: Path, override: Path, out: Path) -> int:
    """Base results with override's rows swapped in by run_id (long rows rerun at a higher cap)."""
    results, new = last_attempts([base]), last_attempts([override])
    results.update({k: v for k, v in new.items() if k in results})
    write_results(results, out)
    return sum(k in results for k in new)


def score_command(results: Path, out: Path) -> list[str]:
    return [str(PYTHON), "-m", "decision_index", "score", "--edition", EDITION,
            "--results", str(results), "--suite-dir", str(SUITE), "--out", str(out)]


def index_scored(results: Path, rows_by_id: dict[str, dict]) -> list[Scored]:
    """Gold-labelled choice/noul answers from a results file, for our ECE (the harness reports none)."""
    items = []
    for r in last_attempts([results]).values():
        row = rows_by_id.get(r["run_id"])
        if r["status"] != "ok" or row is None:
            continue
        for qid, a in r["response"]["answers"].items():
            gold, q = row["gold"].get(qid), row["questions"][qid]
            if gold is None:
                continue
            if q["type"] == "noul":
                items.append(Scored("index", row["family"], "noul", int(gold), [1 - a["noul"], a["noul"]]))
            elif q["type"] == "choice":
                names = list(q["criteria"])
                items.append(Scored("index", row["family"], "choice", names.index(gold),
                                    [a["probabilities"][n] for n in names]))
    return items

```

`scripts/evaluate.py`:

```python
"""Phase-2 evaluation CLI.

usage:
  uv run python scripts/evaluate.py offline --profile P --split S [--layout L] [--orders O] [--uncalibrated]
  uv run python scripts/evaluate.py index --profile P [--gateway URL] [--shards 8] [--ids FILE] [--chat-probe]
  uv run python scripts/evaluate.py replace --profile P --base RUN_DIR --override RUN_DIR
Index runs and collect are long runs: get the owner's ok first.
"""

import argparse
import asyncio
import datetime
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path

import httpx

from gateway.calibration import load_temperatures
from gateway.config import ROOT, Settings
from scripts import board, index_run, metrics
from scripts.bench import CHAT_PROMPTS, chat_once, git_revision
from scripts.bench_report import percentile, provenance
from scripts.bench_vllm import Vllm
from scripts.collect import COLLECT, records
from scripts.decision_rows import index_rows
from scripts.index_suite import EXPORT, HARNESS_SHA, harness_env
from scripts.offline import Arm, evaluate, markdown
from scripts.splits import rows_for

RUNS = ROOT / ".cache" / "index-runs"


def now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")


def results_dir(profile: str, name: str) -> Path:
    out = ROOT / "docs" / "results" / profile / name
    out.mkdir(parents=True, exist_ok=True)
    return out


def cmd_offline(args) -> None:
    s = Settings.from_profile(args.profile)
    temps = {"choice": 1.0, "score": 1.0, "noul": 1.0} if args.uncalibrated else load_temperatures(
        s.data_dir(args.layout) / "calibration.json")
    arm = Arm(args.layout, args.orders, temps)
    rows = {r["id"]: r for r in rows_for(args.split)}
    report = evaluate(records(COLLECT / args.profile / f"{args.split}.jsonl.gz"), rows, arm)
    meta = {"timestamp": now(), "repo commit": git_revision(), "profile": args.profile, "split": args.split,
            "collected": str((COLLECT / args.profile / f"{args.split}.jsonl.gz").relative_to(ROOT))}
    name = f"{now()}-offline-{args.split}-{args.layout}-{args.orders.replace(':', '')}"
    out = results_dir(args.profile, name)
    (out / "summary.md").write_text(f"# {args.profile} offline: {args.split}\n\n{provenance(meta)}\n{markdown(report)}")
    print(out / "summary.md")


async def chat_probe(client: httpx.AsyncClient, served: str, stop: asyncio.Event, samples: list) -> None:
    """One short streaming chat at a time while the Index runs: what a chat user sees meanwhile."""
    while not stop.is_set():
        ttft, rate = await chat_once(client, served, CHAT_PROMPTS["short"])
        samples.append({"ttft_ms": ttft, "chunks_per_s": rate})
        await asyncio.sleep(2)


async def run_index(args, run: Path, health: dict) -> dict:
    ids = set(json.loads(Path(args.ids).read_text())["ids"]) if args.ids else None
    shards = sorted(run.glob("shard-*.jsonl.gz")) or index_run.write_shards(EXPORT, args.shards, run, ids)
    env = harness_env()
    if key := os.environ.get("GATEWAY_API_KEY"):
        env["DECISION_INDEX_API_KEY"] = key
    commands = [index_run.shard_command(s, run / s.name.removesuffix(".jsonl.gz"), args.gateway) for s in shards]
    vllm_records: list = []
    vllm = Vllm(args.vllm, vllm_records)
    stop, idle, busy = asyncio.Event(), [], []
    async with httpx.AsyncClient(base_url=args.gateway, timeout=600) as client:
        if args.chat_probe:
            for _ in range(3):
                idle.append(dict(zip(("ttft_ms", "chunks_per_s"), await chat_once(client, health["served_model"],
                                                                                    CHAT_PROMPTS["short"]))))
        probe = asyncio.create_task(chat_probe(client, health["served_model"], stop, busy)) if args.chat_probe else None
        started = time.perf_counter()
        async with vllm.watch("index"):
            codes = await index_run.run_all(commands, env)
        stop.set()
        if probe:
            await probe
    await vllm.aclose()
    return {"codes": codes, "seconds": time.perf_counter() - started, "vllm": vllm_records, "idle": idle, "busy": busy}


def score(run: Path, merged: Path) -> dict:
    subprocess.run(index_run.score_command(merged / "results.jsonl", merged), cwd=index_run.SRC, env=harness_env(),
                   check=True)
    return json.loads((merged / "scores.json").read_text())


def load(merged: Path) -> list[dict]:
    return [json.loads(x) for x in (merged / "results.jsonl").read_text().splitlines() if x.strip()]


def index_summary(profile: str, scores: dict, merged: Path, extra: list[str]) -> str:
    results = load(merged)
    counts = dict(Counter(r["status"] for r in results))
    rows = {r["id"]: r for r in index_rows({r["run_id"] for r in results})}
    items = index_run.index_scored(merged / "results.jsonl", rows)
    ms = [r["total_wall_ms"] for r in results if r["status"] == "ok"]
    total = len(results)
    ours = {"index": scores["decision_index"], "ece": metrics.ece(items) if items else None,
            "median_ms": percentile(ms, 0.5) if ms else None, "coverage": counts.get("ok", 0) / total if total else None}
    areas = ["| area | skill | raw | coverage | n |", "|---|---|---|---|---|"]
    areas += [f"| {a['id']} | {100 * a['skill']:.1f} | {100 * a['raw']:.1f} | {a['coverage']:.3f} | {a['n']} |"
              for a in scores["areas"]]
    notes = [
        "- ECE: ours over gold-labelled choice/noul answers (15 bins, probabilities as returned, 4 decimals);"
        " the board's ECE uses its own row set, so compare loosely.",
        "- median ms: the harness's per-request wall time with all shards running at once, not latency-v1;"
        " see the latency report for the comparable figure.",
    ]
    return "\n".join([*board.comparison(profile, ours), "", *areas, "", f"Status: {counts}", "", *notes, *extra]) + "\n"


async def cmd_index(args) -> None:
    async with httpx.AsyncClient(base_url=args.gateway, timeout=30) as client:
        health = (await client.get("/health")).json()
    if health["profile"] != args.profile:
        raise SystemExit(f"gateway serves {health['profile']!r}, not {args.profile!r}")
    run = Path(args.run_dir) if args.run_dir else RUNS / args.profile / now()
    run.mkdir(parents=True, exist_ok=True)
    outcome = await run_index(args, run, health)
    index_run.merge(sorted(p for p in run.glob("shard-*") if p.is_dir()), run / "merged")
    scores = score(run, run / "merged")
    extra = [f"- shard exit codes: {outcome['codes']}, wall {outcome['seconds'] / 60:.1f} min"]
    if outcome["vllm"]:
        v = outcome["vllm"][0]
        extra.append(f"- vLLM during the run: KV peak {100 * v['kv_peak']:.1f}%, mean {100 * v['kv_mean']:.1f}%,"
                     f" waiting peak {v['waiting_peak']:.0f}, preemptions {v['preemptions']}")
    for label, samples in (("idle", outcome["idle"]), ("during run", outcome["busy"])):
        if samples:
            ttft = percentile([s["ttft_ms"] for s in samples], 0.5)
            rate = percentile([s["chunks_per_s"] for s in samples], 0.5)
            extra.append(f"- chat {label}: median TTFT {ttft:.0f} ms, {rate:.1f} chunks/s ({len(samples)} samples)")
    keys = ("profile", "hf_model", "hf_revision", "prompt_layout", "option_orders", "systemone_max_len", "vllm_version")
    meta = {"timestamp": now(), "repo commit": git_revision(), "harness": HARNESS_SHA, "edition": "0.2.1",
            "run dir": str(run.relative_to(ROOT)), "shards": len(outcome["codes"]), "ids": args.ids or "full suite"}
    meta |= {k: health.get(k) for k in keys}
    out = results_dir(args.profile, f"{run.name}-index{'-subset' if args.ids else ''}")
    body = index_summary(args.profile, scores, run / "merged", extra)
    (out / "summary.md").write_text(f"# {args.profile} Decision Index 0.2.1\n\n{provenance(meta)}\n{body}")
    print(out / "summary.md")


def cmd_replace(args) -> None:
    base, override = Path(args.base), Path(args.override)
    out = base.parent / f"{base.name}+{override.name}"
    swapped = index_run.replace(base / "merged" / "results.jsonl", override / "merged" / "results.jsonl", out / "merged")
    scores = score(out, out / "merged")
    meta = {"timestamp": now(), "repo commit": git_revision(), "base": str(base.relative_to(ROOT)),
            "override": str(override.relative_to(ROOT)), "rows swapped": swapped}
    body = index_summary(args.profile, scores, out / "merged", [])
    target = results_dir(args.profile, f"{out.name}-index-replaced")
    (target / "summary.md").write_text(f"# {args.profile} Decision Index, long rows rerun\n\n{provenance(meta)}\n{body}")
    print(target / "summary.md")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    o = sub.add_parser("offline")
    o.add_argument("--profile", required=True)
    o.add_argument("--split", required=True, choices=("calib", "eval", "index-dev", "latency-v1"))
    o.add_argument("--layout", default="decider_chat")
    o.add_argument("--orders", default="identity")
    o.add_argument("--uncalibrated", action="store_true", help="T = 1 for every type instead of calibration.json")
    i = sub.add_parser("index")
    i.add_argument("--profile", required=True)
    i.add_argument("--gateway", default="http://127.0.0.1:9000")
    i.add_argument("--vllm", default=os.environ.get("VLLM_URL", "http://127.0.0.1:8000"))
    i.add_argument("--shards", type=int, default=8)
    i.add_argument("--ids", help="JSON file with an 'ids' list: run only those rows")
    i.add_argument("--run-dir", help="resume this run directory")
    i.add_argument("--chat-probe", action="store_true")
    r = sub.add_parser("replace")
    r.add_argument("--profile", required=True)
    r.add_argument("--base", required=True)
    r.add_argument("--override", required=True)
    return p.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    if args.command == "offline":
        cmd_offline(args)
    elif args.command == "index":
        asyncio.run(cmd_index(args))
    else:
        cmd_replace(args)


if __name__ == "__main__":
    main()
```

Add a CLI parse test to `tests/unit/test_index_run.py`:

```python
from scripts.evaluate import parse_args


def test_evaluate_cli_parses_each_command():
    assert parse_args(["offline", "--profile", "p", "--split", "eval"]).orders == "identity"
    assert parse_args(["index", "--profile", "p"]).shards == 8
    assert parse_args(["replace", "--profile", "p", "--base", "a", "--override", "b"]).command == "replace"
```

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/board.py scripts/index_run.py scripts/evaluate.py tests/unit/test_index_run.py tests/unit/test_board.py
git commit -F - <<'EOF'
feat(scripts): sharded Decision Index runs

Upstream harness unchanged, N shards vs gateway, merge keeps last
attempt, upstream score, our ECE, board comparison + parity gate.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 11: latency-v1-design runner

**Files:**
- Create: `scripts/latency.py`
- Test: `tests/unit/test_latency.py`

**Interfaces:**
- Consumes: `splits.rows_for("latency-v1")`, `load_split`; `bench_report.percentile`, `provenance`; `bench.git_revision`; `board`.
- Produces:
  - `time_rows(client: httpx.Client, rows, extra: dict) -> list[dict]`: one record per row with keys `id`, `catalog_id`, `status`, `ms`;
  - `summarize(records) -> dict` with keys `n`, `answered`, `median_ms`, `p95_ms`, `by_catalog` (`{catalog_id: median}` where ≥ 5 rows).

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_latency.py`)

```python
import httpx

from scripts.latency import summarize, time_rows


def test_time_rows_posts_one_request_at_a_time():
    seen = []

    def handler(request):
        seen.append(request.read())
        return httpx.Response(200, json={"answers": {}})

    client = httpx.Client(base_url="http://g", transport=httpx.MockTransport(handler))
    rows = [{"id": f"r{i}", "state": "s", "questions": {}, "meta": {"catalog_id": 1}} for i in range(3)]
    recs = time_rows(client, rows, {"layout": "header"})
    assert [r["status"] for r in recs] == [200] * 3 and all(r["ms"] >= 0 for r in recs)
    assert b'"layout": "header"' in seen[0] or b'"layout":"header"' in seen[0]


def test_summary_uses_answered_rows_and_per_catalog_medians():
    recs = [{"id": f"r{i}", "catalog_id": 1, "status": 200, "ms": float(i)} for i in range(10)]
    recs += [{"id": "x", "catalog_id": 2, "status": 422, "ms": 1.0}]
    s = summarize(recs)
    assert s["n"] == 11 and s["answered"] == 10 and s["median_ms"] == 5.0 and s["by_catalog"] == {1: 5.0}
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_latency.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement** (`scripts/latency.py`)

```python
"""latency-v1's design against the gateway: one sequential client, 10 warm-up rows, then 750 timed rows.

usage: uv run python scripts/latency.py --profile P [--gateway URL] [--layout L] [--option-orders O]
The board's own sample is private; ours follows its published design (data/splits/latency-v1.json).
"""

import argparse
import datetime
import json
import os
import time
from collections import defaultdict

import httpx

from gateway.config import ROOT
from scripts.bench import git_revision
from scripts.bench_report import percentile, provenance
from scripts.board import BOARD, MATCHES
from scripts.splits import load_split, rows_for


def time_rows(client: httpx.Client, rows: list[dict], extra: dict) -> list[dict]:
    out = []
    for row in rows:
        body = {"model": "jev-latest", "state": row["state"], "questions": row["questions"], **extra}
        start = time.perf_counter()
        r = client.post("/v1/systemone", json=body)
        ms = (time.perf_counter() - start) * 1000
        out.append({"id": row["id"], "catalog_id": row["meta"]["catalog_id"], "status": r.status_code, "ms": ms})
    return out


def summarize(records: list[dict]) -> dict:
    """Median and p95 over rows that returned an answer; per-benchmark medians only with >= 5 rows (as the board)."""
    ok = [r for r in records if r["status"] == 200]
    by: dict[int, list[float]] = defaultdict(list)
    for r in ok:
        by[r["catalog_id"]].append(r["ms"])
    return {
        "n": len(records),
        "answered": len(ok),
        "median_ms": percentile([r["ms"] for r in ok], 0.5) if ok else None,
        "p95_ms": percentile([r["ms"] for r in ok], 0.95) if ok else None,
        "by_catalog": {c: percentile(ms, 0.5) for c, ms in sorted(by.items()) if len(ms) >= 5},
    }


def main(args) -> None:
    split = load_split("latency-v1")
    rows = rows_for("latency-v1")
    warm, timed = rows[: len(split["warmup"])], rows[len(split["warmup"]) :]
    extra = {k: v for k, v in (("layout", args.layout), ("option_orders", args.option_orders)) if v}
    headers = {"Authorization": f"Bearer {k}"} if (k := os.environ.get("GATEWAY_API_KEY")) else {}
    with httpx.Client(base_url=args.gateway, headers=headers, timeout=600) as client:
        health = client.get("/health").json()
        if health["profile"] != args.profile:
            raise SystemExit(f"gateway serves {health['profile']!r}, not {args.profile!r}")
        time_rows(client, warm, extra)
        records = time_rows(client, timed, extra)
    s = summarize(records)
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")
    out = ROOT / "docs" / "results" / args.profile / f"{stamp}-latency{'-' + '-'.join(extra.values()) if extra else ''}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "raw.jsonl").write_text("".join(json.dumps(r) + "\n" for r in records))
    board = [f"| {BOARD[k]['name']} (board, its own sample) | {BOARD[k]['median_ms']:.1f} | n/a |"
             for k in [*MATCHES[args.profile], "jev"]]
    meta = {"timestamp": stamp, "repo commit": git_revision(), "design": split["meta"]["design"], **extra}
    meta |= {k: health.get(k) for k in ("profile", "hf_revision", "prompt_layout", "option_orders", "vllm_version")}
    table = ["| entry | median ms | p95 ms |", "|---|---|---|",
             f"| **ours** | {s['median_ms']:.1f} | {s['p95_ms']:.1f} |", *board]
    per = ["| catalog | median ms |", "|---|---|", *(f"| {c} | {m:.1f} |" for c, m in s["by_catalog"].items())]
    body = "\n".join([*table, "", f"Answered {s['answered']} of {s['n']} timed rows.", "", *per])
    (out / "summary.md").write_text(f"# {args.profile} latency (latency-v1 design)\n\n{provenance(meta)}\n{body}\n")
    print(out / "summary.md")


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", required=True)
    p.add_argument("--gateway", default="http://127.0.0.1:9000")
    p.add_argument("--layout")
    p.add_argument("--option-orders")
    return p.parse_args(argv)


if __name__ == "__main__":
    main(parse_args())
```


- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest tests/unit/test_latency.py -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/latency.py tests/unit/test_latency.py
git commit -F - <<'EOF'
feat(scripts): latency-v1 design runner

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 12: decision length-cap study (`evaluate.py lengths`)

**Files:**
- Modify: `scripts/evaluate.py` (new `lengths` subcommand)
- Create: `scripts/lengths.py`
- Test: `tests/unit/test_lengths.py`

**Interfaces:**
- Consumes: `build_batch` (Task 2), `decision_rows.index_meta`, `index_rows`, `gateway.app.load_engine`.
- Produces:
  - `BUCKETS = (8192, 16384, 32768, 65536, 131072, 262144)`;
  - `bucket(tokens: int | None) -> str`;
  - `bucket_counts(meta) -> dict[str, dict[int, int]]`: bucket → `{catalog_id: rows}`;
  - `async real_lengths(engine, rows) -> dict[str, int]`: id → the longest prompt row, using the profile's default layout;
  - writes `data/splits/long-rows-<profile>.json` = `{"meta": {...}, "ids": [...], "longest": {id: tokens}}` for rows at or over the current cap.

- [ ] **Step 1: Write the failing tests** (`tests/unit/test_lengths.py`)

```python
from scripts import lengths
from tests.helpers import QUICKSTART, STATE


def test_buckets():
    assert lengths.bucket(100) == "<8k"
    assert lengths.bucket(40000) == "32k-64k"
    assert lengths.bucket(300000) == ">=256k"
    assert lengths.bucket(None) == "unknown"


def test_bucket_counts_by_catalog():
    meta = [{"meta": {"catalog_id": 1, "proxy_tokens": 100}}, {"meta": {"catalog_id": 1, "proxy_tokens": 40000}},
            {"meta": {"catalog_id": 2, "proxy_tokens": 50}}]
    assert lengths.bucket_counts(meta) == {"<8k": {1: 1, 2: 1}, "32k-64k": {1: 1}}


async def test_real_lengths_measure_the_longest_row(engine):
    rows = [{"id": "r1", "state": STATE, "questions": QUICKSTART}]
    out = await lengths.real_lengths(engine, rows)
    assert out["r1"] > 20
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/unit/test_lengths.py -q`
Expected: FAIL with `ImportError`.

- [ ] **Step 3: Implement**

`scripts/lengths.py`:

```python
"""How many Index rows a decision cap refuses: proxy-token buckets for all rows, real token counts near the cap."""

from collections import defaultdict

from gateway.decide import build_batch
from gateway.schema import RequestError, SystemOneRequest

BUCKETS = (8192, 16384, 32768, 65536, 131072, 262144)
NAMES = ("<8k", "8k-16k", "16k-32k", "32k-64k", "64k-128k", "128k-256k", ">=256k")


def bucket(tokens: int | None) -> str:
    if tokens is None:
        return "unknown"
    return NAMES[sum(tokens >= b for b in BUCKETS)]


def bucket_counts(meta: list[dict]) -> dict[str, dict[int, int]]:
    counts: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for m in meta:
        counts[bucket(m["meta"]["proxy_tokens"])][m["meta"]["catalog_id"]] += 1
    return {k: dict(v) for k, v in counts.items()}


async def real_lengths(engine, rows: list[dict]) -> dict[str, int]:
    """Longest prompt per row in the profile's default layout; tokenizer only, no vLLM."""
    out = {}
    for row in rows:
        try:
            request = SystemOneRequest.model_validate({"state": row["state"], "questions": row["questions"]})
            _, _, batch = await build_batch(engine, request)
        except RequestError:
            continue  # refused for another reason (option count); not a length question
        out[row["id"]] = batch.longest
    return out
```

Add to `scripts/evaluate.py`:

```python
async def cmd_lengths(args) -> None:
    s = Settings.from_profile(args.profile)
    meta = index_meta()
    counts = bucket_counts(meta)
    near = {m["id"] for m in meta if (m["meta"]["proxy_tokens"] or 0) >= args.near * s.systemone_max_len}
    engine = load_engine(s, None)
    longest = await real_lengths(engine, index_rows(near))
    over = sorted(i for i, n in longest.items() if n >= s.systemone_max_len)
    split = {"meta": {"profile": args.profile, "cap": s.systemone_max_len, "max_model_len": s.max_model_len,
                      "near": args.near}, "ids": over, "longest": {i: longest[i] for i in over}}
    (ROOT / "data" / "splits" / f"long-rows-{args.profile}.json").write_text(json.dumps(split, indent=0) + "\n")
    lines = ["| proxy tokens | rows | benchmarks |", "|---|---|---|"]
    lines += [f"| {b} | {sum(c.values())} | {len(c)} |" for b, c in sorted(counts.items())]
    fits = sum(n < s.max_model_len for n in longest.values() if n >= s.systemone_max_len)
    lines += ["", f"At or over the decision cap ({s.systemone_max_len}): {len(over)} rows; "
                  f"{fits} of them fit under MAX_MODEL_LEN ({s.max_model_len})."]
    out = results_dir(args.profile, f"{now()}-lengths")
    meta_lines = {"timestamp": now(), "repo commit": git_revision(), "profile": args.profile}
    (out / "summary.md").write_text(f"# {args.profile} decision lengths\n\n{provenance(meta_lines)}\n" + "\n".join(lines) + "\n")
    print(out / "summary.md")
```

with these top-level imports added to `scripts/evaluate.py`:

```python
from gateway.app import load_engine
from scripts.decision_rows import index_meta, index_rows
from scripts.lengths import bucket_counts, real_lengths
```

and the CLI wiring:

```python
    n = sub.add_parser("lengths")
    n.add_argument("--profile", required=True)
    n.add_argument("--near", type=float, default=0.5, help="measure real tokens for rows with proxy >= near * cap")
```

```python
    elif args.command == "lengths":
        asyncio.run(cmd_lengths(args))
```

(`main` dispatches `offline`, `index`, `lengths`, then `replace` in its final `else`.)

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest -q && uv run ruff check .`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/lengths.py scripts/evaluate.py tests/unit/test_lengths.py
git commit -F - <<'EOF'
feat(scripts): decision length-cap study

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 13: live check that offline equals live

**Files:**
- Create: `tests/live/test_offline_matches_live.py`

**Interfaces:**
- Consumes: `collect.collect_one`, `offline.scored`-equivalent math via `answers_for`, `gateway.app.load_engine`, `splits.rows_for("eval")`, the `tests/live/api.py` helpers (gateway URL, key).

- [ ] **Step 1: Write the test**

```python
"""Offline answers (collected logprobs + gateway math) must match live /v1/systemone answers within bf16 noise."""

import dataclasses
import os

import httpx
import pytest

from gateway.app import load_engine, vllm_client
from gateway.config import Settings
from gateway.decide import answers_for, read_rows
from gateway.schema import SystemOneRequest
from scripts.splits import rows_for

pytestmark = pytest.mark.live
N = int(os.environ.get("SPOTCHECK_N", "20"))
GATEWAY = os.environ.get("GATEWAY_URL", "http://127.0.0.1:9000")
VLLM = os.environ.get("VLLM_URL", "http://127.0.0.1:8000")


def close(live: dict, offline: dict) -> bool:
    """Same rule as test_stability: probabilities within 0.05, top answer held when the top-two gap > 0.10."""
    if live["type"] == "noul":
        return abs(live["noul"] - offline["noul"]) <= 0.05
    a, b = live["probabilities"], offline["probabilities"]
    if any(abs(a[k] - b[k]) > 0.05 for k in a):
        return False
    top = sorted(b.values(), reverse=True)
    return top[0] - top[1] <= 0.10 or live.get("choice", live.get("score")) == offline.get("choice", offline.get("score"))


async def test_offline_answers_match_live():
    headers = {"Authorization": f"Bearer {k}"} if (k := os.environ.get("GATEWAY_API_KEY")) else {}
    async with httpx.AsyncClient(base_url=GATEWAY, headers=headers, timeout=600) as gw:
        health = (await gw.get("/health")).json()
        s = dataclasses.replace(Settings.from_profile(health["profile"]), vllm_url=VLLM,
                                vllm_api_key=os.environ.get("VLLM_API_KEY") or None)
        async with vllm_client(s, None) as client:
            engine = load_engine(s, client)
            misses = []
            for row in rows_for("eval")[:N]:
                body = {"model": "jev-latest", "state": row["state"], "questions": row["questions"]}
                live = (await gw.post("/v1/systemone", json=body)).json()["answers"]
                r = await read_rows(engine, SystemOneRequest.model_validate(body))
                offline = answers_for(r.questions, r.reads, engine.temperatures[r.layout])
                misses += [(row["id"], q) for q in live if not close(live[q], offline[q])]
    assert misses == []
```

- [ ] **Step 2: Check it is collected but skipped by default**

Run: `uv run pytest tests/live/test_offline_matches_live.py -q`
Expected: deselected (live marker), no failure. Lint: `uv run ruff check .`.

- [ ] **Step 3: Commit**

```bash
git add tests/live/test_offline_matches_live.py
git commit -F - <<'EOF'
test(live): offline matches live answers

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 14: README phase-2 section

**Files:**
- Modify: `README.md` (new section after "Benchmarks"; repository map rows)

- [ ] **Step 1: Add the section**

````markdown
## Phase 2: evaluation (DS-002)

Design: [docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md](docs/superpowers/specs/2026-09-30-phase2-calibrate-evaluate-design.md).
Long runs (suite rebuild, collect, full Index) take hours; plan them.

```bash
uv run python scripts/index_suite.py setup     # pinned harness clone + venv in .cache/
uv run python scripts/index_suite.py rebuild   # ~7 GB download, 17 GB scratch; HF token in secrets/.hf-token (HLE is gated)
uv run python scripts/index_suite.py export    # scoreable 0.2.1 rows → .cache/decision-index/rows-0.2.1.jsonl.gz
uv run python scripts/splits.py                # data/splits/*.json (committed)

uv run python scripts/collect.py --profile qwen3.6-27b --split eval       # raw letter logprobs, stack up
uv run python scripts/evaluate.py offline --profile qwen3.6-27b --split eval --orders identity+reversed
uv run python scripts/evaluate.py index --profile qwen3.6-27b             # full Index via the upstream harness, 8 shards
uv run python scripts/latency.py --profile qwen3.6-27b                    # latency-v1 design, one sequential client
uv run python scripts/evaluate.py lengths --profile qwen3.6-27b           # how many rows the decision cap refuses
```

- **Data:**
  - **Index rows are never used for fitting.**
  - Calibration and evaluation splits come from JevBench gold and filtered DecisionBench
    (public gold only), 50/50 by hash.
  - Jev's outputs are never read.
- **Offline vs live:** `collect.py` uses the gateway's own code, so offline answers equal
  live ones within bf16 noise (`tests/live/test_offline_matches_live.py`).
- **Results:** `docs/results/<profile>/<timestamp>-{index,offline-…,latency,lengths}/summary.md`.
  Large run data stays in `.cache/` (`collect/`, `index-runs/`).
````

Add repository-map rows for `scripts/` (append to the existing scripts cell: `collect.py`, `evaluate.py`, `latency.py`, `splits.py`, `index_suite.py` and helpers) and `data/splits/`.

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -F - <<'EOF'
docs: phase-2 evaluation commands

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
```

---

### Task 15: M1 runbook (owner-gated operations)

This task runs the pipeline. **Each step marked ⏸ needs the owner's explicit ok before it starts.** Post the estimate, then wait. Run long steps in the background and monitor them. After each step, record one terse line on DS-002 (`update_ticket_progress`) and commit results with explicit paths.

- [ ] **Step 1: Harness setup (≈2 min, network only).** `uv run python scripts/index_suite.py setup`.
- [ ] **Step 2: ⏸ Suite rebuild (≈1 h?, ~7 GB download, ~17 GB scratch, CPU).** `uv run python scripts/index_suite.py rebuild`. Expected: `suite import` prints matching hashes. On any hash mismatch, stop and report.
- [ ] **Step 3: Export (a few minutes, CPU).** `uv run python scripts/index_suite.py export`. Expected: `{"rows": ~150317, "match": true}`. Record the row count on DS-002.
- [ ] **Step 4: Splits (CPU).** `uv run python scripts/splits.py`.
  - Check the calib/eval sizes.
  - Check that `latency-v1.json` holds 750 + 10 ids.
  - Compare our per-catalog counts with the published latency-v1 `per_catalog` (`.firecrawl/space/data/methodology-v2.json`); they should be close.
  - Commit `data/splits/calib.json data/splits/eval.json data/splits/index-dev.json data/splits/latency-v1.json`, message `data: phase-2 split files`.
- [ ] **Step 5: ⏸ Bring up qwen3.6-27b (4–10 min GPU),** if it is not already running.
- [ ] **Step 6: Live checks (≈5 min).**
  - `uv run pytest -m live tests/live -v`;
  - then `SPOTCHECK_N=200 uv run pytest -m live tests/live/test_offline_matches_live.py -v`.

  Any mismatch: stop and use superpowers:systematic-debugging.
- [ ] **Step 7: Latency (≈5 min, sequential).** `uv run python scripts/latency.py --profile qwen3.6-27b`. Commit the latency results dir.
- [ ] **Step 8: ⏸ Baseline full Index, qwen3.6-27b (est. 1–2 h with 8 shards).** `uv run python scripts/evaluate.py index --profile qwen3.6-27b`.
  - Check the parity gate line, and that area skills look like the board's (Knowledge ≈ 37 for Decider chat · Qwen3.6). If the area scale is off by 100×, fix `index_summary`'s formatting.
  - **Parity MISS → file a DoStuff ticket, pull it into the sprint, and stop M1 for this profile until it's understood.**
  - Commit the `-index` results dir.
- [ ] **Step 9: ⏸ Collect qwen3.6-27b: calib, eval, index-dev (est. 2–4 h).** Three `collect.py` runs. Then run `evaluate.py offline` for `eval` and `index-dev` on `decider_chat`/`identity` (baseline arm), and commit those results dirs.
- [ ] **Step 10: Lengths (CPU, minutes).** `uv run python scripts/evaluate.py lengths --profile qwen3.6-27b`. Commit `data/splits/long-rows-qwen3.6-27b.json` and the results dir.
- [ ] **Step 11: ⏸ Repeat Steps 5–10 for qwen3.8-27b, then gemma-4-31b** (one ok per profile; each is ~4–7 h of GPU). Gemma has no parity gate; record how it compares to Decider chat · Gemma-4-31B.
- [ ] **Step 12: ⏸ Long-row study.** Needs DS-018 deployed, plus DS-016 (Qwen at 262,144) or DS-017 (Gemma at 131,072). For each profile:
  - start the stack with `SYSTEMONE_MAX_LEN` = that profile's `MAX_MODEL_LEN`;
  - `uv run python scripts/evaluate.py index --profile P --ids data/splits/long-rows-P.json --chat-probe`;
  - `uv run python scripts/evaluate.py replace --profile P --base <baseline run dir> --override <long run dir>`.

  Report the Index gain against long-row latency, KV peak and chat TTFT and chunks/s, then recommend a `SYSTEMONE_MAX_LEN` per profile. **The owner decides.**
- [ ] **Step 13: Close out M1.**
  - On DS-002, tick:
    - "Rebuild Decision Index corpus locally";
    - "evaluate.py via harness http engine";
    - "Extra datasets: DecisionBench, typed-decisions, JevBench" (note: typed-decisions dropped, teacher labels);
    - "latency-v1 protocol run".
  - Record the commit shas.
  - Post the M1 summary to the owner (per-profile Index vs board, ECE, latency, coverage, length study), then write the M2 plan.
