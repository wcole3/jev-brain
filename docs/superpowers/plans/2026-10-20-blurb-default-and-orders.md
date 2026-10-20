# Blurb default, gated orders, Index reruns: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Serve `blurb_header` on all 7 gemma/qwen profiles, with `min_n:4+reversed` (qwen3.8), `top_p:0.9+reversed`
text / `identity` image (gemma) and `identity` (qwen3.6) under `mean-logprob`. Then get the box queues ready for
collect, calibrate, latency A/B and full Index reruns.

**Architecture:** `gateway/orders.py` learns two settings. `min_n` is fixed per option count. `top_p` is gated:
identity first, then a second pass for the questions under τ. `decide.py` gains the second pass, image/text order
routing and a `mean-logprob` combine. Calibration is loaded per order setting in use, and the identity fit gives
the gate T.

**Tech stack:** Python 3.12, FastAPI gateway, vLLM 0.30, pytest, uv, vast.ai box scripts.

**Spec:** [docs/superpowers/specs/2026-10-20-blurb-default-and-orders-design.md](../specs/2026-10-20-blurb-default-and-orders-design.md)

## Global Constraints

- Never train, calibrate or tune on Jev API outputs; fits use calib, eval judges.
- `prompts/header.toml`, `decider_chat.toml`, `question_first.toml` and their `labels.json` / calibration files stay byte-identical.
- Comments at most two lines; small focused functions; code reads like the surrounding code.
- Commits: caveman Conventional Commits, subject ≤ 50 chars, explicit `git add` paths, end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. No pushes.
- GPU jobs > 10 min and renting boxes need the owner's ok. Local smoke runs (< 10 min each) are fine.
- Setting strings, exactly: `min_n:4+reversed`, `top_p:0.9+reversed`, `identity`. File for a setting: `calibration-<setting with ':' and '+' → '-'>.json` (identity: `calibration-identity.json`).
- With one order, every answer must stay bit-identical to today (qwen3.6 and the identity experiments).

## Review Focus

- A `top_p` request where no question falls under τ sends no second vLLM call (Task 4 test).
- A gated override on a profile with no identity calibration file gates at the fallback file, or at T = 1 when there is none. No crash (Task 4 test).
- A noul question that is gated: reversed perm `[1, 0]`; b·T lands on "yes" in both orders (Task 2 test).
- Malformed settings (`min_n:x+reversed`, `top_p:1.5+reversed`, `min_n:4+half`, `top_p:0+reversed`) raise `ValueError`. An override becomes a 400; env settings fail at startup (Tasks 1, 3 tests).
- gemma image requests use `calibration-identity.json` and take no second pass, even though text is `top_p` (Task 4 test).

---

### Task 1: Order setting grammar

**Files:**
- Modify: `gateway/orders.py`
- Test: `tests/unit/test_orders.py`

**Interfaces:**
- Produces:
  - `option_orders(n: int, setting: str) -> list[list[int]]`: adds `min_n:<k>+reversed` (identity, plus `identity[::-1]` when `n >= k`) and `top_p:<τ>+reversed` (identity only).
  - `gate(setting: str) -> float | None`: τ for `top_p`, else `None`. Raises `ValueError` on a malformed setting.
  - `live_rows(option_counts: list[int], setting: str) -> int`: the sum of `len(option_orders(n, setting))`.
- Validation: k is an int ≥ 2; τ is a float with 0 < τ ≤ 1; the suffix must be `+reversed`. The error message lists every accepted form.

- [ ] **Step 1: Write failing tests**

```python
def test_min_n_adds_reversed_from_k_options():
    assert option_orders(3, "min_n:4+reversed") == [[0, 1, 2]]
    assert option_orders(4, "min_n:4+reversed") == [[0, 1, 2, 3], [3, 2, 1, 0]]

def test_top_p_reads_identity_first_and_names_its_threshold():
    assert option_orders(5, "top_p:0.9+reversed") == [[0, 1, 2, 3, 4]]
    assert gate("top_p:0.9+reversed") == 0.9
    assert gate("min_n:4+reversed") is None and gate("identity") is None

@pytest.mark.parametrize("bad", ["min_n:x+reversed", "min_n:1+reversed", "min_n:4+half",
                                 "top_p:0+reversed", "top_p:1.5+reversed", "top_p:0.9"])
def test_malformed_gated_settings_raise(bad):
    with pytest.raises(ValueError):
        option_orders(4, bad)

def test_live_rows_counts_what_the_first_pass_reads():
    assert live_rows([2, 4, 5], "min_n:4+reversed") == 5
    assert live_rows([2, 4, 5], "top_p:0.9+reversed") == 3

@pytest.mark.parametrize("n", [2, 3, 4, 5, 8])
def test_min_n_matches_round_3_policy(n):
    reads = {tuple(p): [0.0] * n for p in option_orders(n, "identity+reversed")}
    policy = Policy("x", "reversed", "min_n", 4, "mean-prob")
    assert option_orders(n, "min_n:4+reversed") == perms(reads, n, policy, 1.0)
    assert option_orders(n, "identity+reversed")[1] == second_perm(n, "reversed")
```

- [ ] **Step 2: Run** `uv run pytest tests/unit/test_orders.py -q`. Expected: FAIL (`gate`/`live_rows` missing, unknown setting).
- [ ] **Step 3: Implement** in `gateway/orders.py`. Parse with one helper, `_gated(setting) -> tuple[str, float] | None`, shared by `option_orders` and `gate`.
- [ ] **Step 4: Run** `uv run pytest tests/unit/test_orders.py tests/unit/test_order_policies.py -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(orders): min_n and top_p settings`.

### Task 2: `mean-logprob` combine

**Files:**
- Modify: `gateway/decide.py` (`probabilities`), `scripts/fit.py:32`
- Test: `tests/unit/test_decide.py`, `tests/unit/test_fit.py`

**Interfaces:**
- Produces: `combine(reads: list[tuple[list[float], list[int]]], temperature: float, yes_offset: float = 0.0) -> list[float]`, in `gateway/decide.py`.
  1. `average_back` the raw logprobs to caller order.
  2. Add `yes_offset * temperature` to caller option 1.
  3. Take one `softmax` at T.
- `probabilities` calls `combine`. `fit.py`'s NLL calls `combine`. `blend` stays unchanged for `order_policies`/`vision_offline`.

- [ ] **Step 1: Write failing tests**

```python
def test_combine_equals_blend_with_one_order():
    reads = [([-0.2, -1.9, -3.0], [0, 1, 2])]
    assert combine(reads, 1.7) == pytest.approx(blend(reads, 1.7))
    noul = [([-0.4, -1.2], [0, 1])]
    assert combine(noul, 0.9, 0.3) == pytest.approx(blend(noul, 0.9, 0.3))

def test_combine_averages_logprobs_then_softmaxes():
    reads = [([0.0, -2.0], [0, 1]), ([-1.0, 0.0], [1, 0])]  # caller logprobs: [0, -2] and [0, -1]
    assert combine(reads, 1.0) == pytest.approx(softmax([0.0, -1.5], 1.0))

def test_combine_puts_the_yes_offset_on_caller_yes_in_a_reversed_noul():
    reads = [([-0.5, -1.0], [0, 1]), ([-1.0, -0.5], [1, 0])]
    assert combine(reads, 2.0, 0.25) == pytest.approx(softmax([-0.5, -1.0 + 0.5], 2.0))
```

Update the multi-order expectations in `test_reversed_orders_average_back` and `test_decide_is_read_rows_then_answers_for` only if they fail, and recompute those values with `combine`.

- [ ] **Step 2: Run** `uv run pytest tests/unit/test_decide.py -q`. Expected: FAIL (`combine` missing).
- [ ] **Step 3: Implement** `combine`; switch `probabilities` and `scripts/fit.py` to it.
- [ ] **Step 4: Run** `uv run pytest -q`. Expected: PASS. A failure outside the multi-order tests means a one-order result moved, which is a bug.
- [ ] **Step 5: Commit** `feat(decide): mean-logprob combine`.

### Task 3: Image order setting and calibration per setting

**Files:**
- Modify: `gateway/config.py`, `gateway/calibration.py`, `gateway/app.py` (`load_calibrations`, `load_engine`, `/health` settings output at line ~178), `gateway/decide.py` (`Engine`)
- Test: `tests/unit/test_config.py`, `tests/unit/test_calibration.py`, `tests/unit/test_app.py`

**Interfaces:**
- Consumes: `gate` (Task 1).
- Produces:
  - `Settings.option_orders_images: str = ""` from env `OPTION_ORDERS_IMAGES`.
  - `Settings.image_orders -> str`: the image setting, falling back to `option_orders`.
  - `Settings.orders_in_use() -> list[str]`: the text setting; plus the image setting when `systemone_images`; plus `"identity"` when any of those is gated. Deduplicated, text first.
  - `Settings.calibration_path(layout: str, orders: str | None = None) -> Path`:
    - `None` or the text setting: today's rule.
    - Any other setting: `calibration-<slug>.json` if it exists, else today's rule (fallback).
  - `Engine.other_calibrations: dict[str, dict[str, Calibration]] = field(default_factory=dict)`: orders → layout, for every setting in `orders_in_use()` except the text one.
  - `calibration_for(engine: Engine, layout: str, orders: str) -> Calibration` in `gateway/decide.py`:
    - the text setting: `engine.calibration[layout]`;
    - another setting: `other_calibrations[orders].get(layout, UNCALIBRATED)`;
    - an unknown setting (request override): `engine.calibration[layout]`, as today.
- Startup: for `s.prompt_layout`, a loaded file whose `fit.orders` is not `None` and differs from its setting raises `RuntimeError` naming the file, the file's orders and the setting. Other layouts keep `orders_warning`. `load_engine` calls `option_orders(2, x)` on each setting in use, so a malformed env setting fails at startup.

- [ ] **Step 1: Write failing tests**
  - `test_orders_in_use_adds_identity_for_a_gate_and_the_image_setting`:
    - gemma-like settings (`top_p:0.9+reversed`, images `identity`, `systemone_images=True`) give `["top_p:0.9+reversed", "identity"]`;
    - qwen-like (`min_n:4+reversed`, images empty) gives `["min_n:4+reversed"]`;
    - `identity` gives `["identity"]`.
  - `test_calibration_path_per_setting_falls_back_to_the_default_file` (tmp `data_root`): no `calibration-identity.json` → `calibration.json`; with it → it.
  - `test_served_layout_with_wrong_fit_orders_refuses_startup` (tmp files): `blurb_header/calibration.json` with `fit.orders = "identity"` under `OPTION_ORDERS=min_n:4+reversed` → `RuntimeError`; the same file under `header` (not served) only logs a warning.
  - `test_malformed_env_orders_fail_at_startup`: `OPTION_ORDERS=min_n:4+half` → `ValueError` from `load_engine`.
- [ ] **Step 2: Run** `uv run pytest tests/unit/test_config.py tests/unit/test_calibration.py tests/unit/test_app.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement.** `/health` also reports `option_orders_images`.
- [ ] **Step 4: Run** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(gateway): calibration per order setting`.

### Task 4: Two-pass gated read and order routing

**Files:**
- Modify: `gateway/decide.py` (`build_batch`, `read_batch`, `read_rows`, `Reads`, `decide`)
- Modify: `docs/background/option-ordering.md` §1 table (two rows for the new settings; the short answer's first bullet → "profiles read …" per the spec table)
- Test: `tests/unit/test_decide.py`

**Interfaces:**
- Consumes: `option_orders`, `gate` (Task 1); `combine` (Task 2); `calibration_for`, `Settings.image_orders` (Task 3).
- Produces:
  - `setting_for(engine: Engine, request: SystemOneRequest) -> str`: `request.option_orders`, else `image_orders` when `has_images(request)`, else `option_orders`.
  - `build_batch(engine, request, orders: OrderFn | None = None, pad_rows: int | None = None, perms: dict[str, list[list[int]]] | None = None)`: `perms` overrides `orders`. A question with `[]` gets no rows. All questions still render into the shared prefix.
  - `read_batch(readout, batch: Batch, warm: bool = True)`: `warm=False` passes `shared_len=0` (text) or `shared_tokens=0` (image), so the cached prefix is not warmed twice.
  - `Reads.orders: str`: the setting used.
  - `read_rows`: a gated pass runs only when the caller passed no `orders`/`perms` and `gate(setting)` is not `None`:
    1. The first pass reads identity rows.
    2. Gate each question: `max(softmax(lp, calibration_for(engine, layout, "identity").T[q.type])) < τ`.
    3. If any question is kept, build a second batch with `perms={qid: [reversed] if kept else []}` and `pad_rows=len(request.questions)` (same pad decision as pass 1), and read it with `warm=False`.
    4. Append each second-pass read after its question's identity read.
  - `Reads.input_tokens` is the sum of both passes. The `systemone_max_len` check applies to each batch. `Reads.batch`, `shared_len` and `padded` come from pass 1.
  - `decide` answers with `calibration_for(engine, r.layout, r.orders)`.

- [ ] **Step 1: Write failing tests** (fake readouts in `tests/helpers.py` if needed; the `engine` fixture is qwen3.6 on `decider_chat`):

```python
async def test_top_p_reads_reversed_only_for_questions_under_tau(engine):
    # FavourFirstLabel gives a confident identity read; a readout that flattens one question puts it under τ
    ...
    assert [len(r.reads[q]) for q in ("sure", "unsure")] == [1, 2]
    assert r.reads["unsure"][1][1] == list(range(n))[::-1]
    assert r.input_tokens == first_pass_tokens + second_pass_tokens

async def test_top_p_with_every_question_confident_sends_one_call(engine): ...   # readout call count == 1
async def test_gated_override_without_identity_file_gates_at_T_1(engine): ...    # no crash; UNCALIBRATED gate
async def test_image_request_uses_image_orders_and_their_calibration(seeing): ...# gemma-like: images identity, one pass, identity cal
async def test_orders_fn_from_collect_disables_the_gate(engine): ...             # orders=identity+reversed → one pass, 2 reads each
async def test_bad_gated_override_is_a_400(engine): ...                           # "top_p:1.5+reversed" → RequestError
async def test_second_pass_skips_warm_up(engine): ...                             # second read_batch sees shared_len 0
```

- [ ] **Step 2: Run** `uv run pytest tests/unit/test_decide.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement.** Keep `read_rows` short: put the gate step in its own function, `gated_questions(reads, questions, cal, tau) -> set[str]`.
- [ ] **Step 4: Run** `uv run pytest -q && uv run pytest tests/parity -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(decide): two-pass top_p gate`, plus the doc edit.

### Task 5: Collect pads for the live setting; offline and calibrate learn the gates

**Files:**
- Modify: `scripts/collect.py` (`collect`, `collect_one`), `scripts/offline.py` (`chosen_reads`, `questions`), `scripts/calibrate.py` (`--orders`, `--collect-label`, output path), `scripts/evaluate.py` (`cmd_offline` passes the gate calibration)
- Modify: `docs/development.md` (calibrate line: `--orders`, `--collect-label`, gemma two-step)
- Test: `tests/unit/test_collect.py`, `tests/unit/test_offline.py`, `tests/unit/test_calibrate.py`

**Interfaces:**
- Consumes: `option_orders`, `gate`, `live_rows` (Task 1); `combine` via `probabilities` (Task 2); `Settings.calibration_path(layout, orders)` (Task 3).
- Produces:
  - `collect`: drop the identity-only `SystemExit`. `collect_one` uses `pad_rows=live_rows([len(q["options"]) …], engine.settings.option_orders)`. Use the rendered option counts, as `read_rows` does. The `pad_rows` passed for an `identity` profile is unchanged (`len(questions)`).
  - `chosen_reads(q, reads, orders, gate_T: float | None = None)`: for a gated setting, return identity, plus the reversed read when `max(softmax(identity_lp, gate_T)) < τ`. Raise `ValueError` when `gate_T` is missing for a gated setting.
  - `questions(record, row, layout, orders, layouts, gate: Calibration | None = None)`: passes `gate.T[q.type]` when `gate` is given.
  - `calibrate.py`:
    - `--collect-label L` reads `COLLECT/<profile>/<split>-L.jsonl.gz`.
    - A gated `--orders` loads the gate with `load_calibration(s.calibration_path(layout, "identity"), stamp)` and refuses when that file is missing or `fit.orders != "identity"`.
    - The file is written to `s.calibration_path(layout, args.orders)`. When the slug file does not exist yet and `args.orders` is not the profile's text setting, the target is the `calibration-<slug>.json` path (not the fallback).

- [ ] **Step 1: Write failing tests**
  - `test_collect_pads_like_the_live_min_n_request`: qwen profile with `min_n:4+reversed`. A row with 2 and 5 options gets `pad_rows == 3`. An identity profile still gets `len(questions)`.
  - `test_chosen_reads_top_p_adds_reversed_under_tau` and `test_chosen_reads_gated_without_gate_T_raises`.
  - `test_calibrate_reads_the_labelled_collect_and_writes_the_setting_file`: tmp collect `calib-blurb.jsonl.gz` / `eval-blurb.jsonl.gz`. `--orders identity` writes `calibration-identity.json` on a `top_p` profile; then `--orders top_p:0.9+reversed` writes `calibration.json` with `fit.orders == "top_p:0.9+reversed"`.
  - `test_calibrate_gated_refuses_without_identity_fit`.
- [ ] **Step 2: Run** `uv run pytest tests/unit/test_collect.py tests/unit/test_offline.py tests/unit/test_calibrate.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(calibrate): gated orders, collect label`.

### Task 6: `blurb_header` layout, profiles, label tables

**Files:**
- Create: `prompts/blurb_header.toml` (from `prompts/experiments/blurb-header.toml`; first line becomes `# Default layout: header with an intro blurb (round 4, DS-043). Each part is tokenized on its own.`)
- Create: `data/<profile>/blurb_header/labels.json` ×7 (via `scripts/build_labels.py`)
- Modify: `profiles/*.env` ×7
- Modify: `README.md` (profile defaults: layout, orders), `docs/background/prompt-layouts.md` (served layouts list), `CLAUDE.md` only if it names a default layout (it doesn't today; leave it)
- Test: `tests/unit/test_profile_env.py`, `tests/unit/test_layouts.py`, `tests/unit/test_blurb_layouts.py`

**Profile values:**

| Profile | `PROMPT_LAYOUT` | `OPTION_ORDERS` | `OPTION_ORDERS_IMAGES` | Vision added |
|---|---|---|---|---|
| gemma-4-31b | blurb_header | top_p:0.9+reversed | identity | (has it) |
| gemma-4-31b-fp8 | blurb_header | top_p:0.9+reversed | identity | `SYSTEMONE_IMAGES=1`, `MM_PROCESSOR_KWARGS={"max_soft_tokens":560}`, `--limit-mm-per-prompt {"video":0,"image":4}`, `--max-logprobs 128` |
| qwen3.8-27b | blurb_header | min_n:4+reversed | (empty) | (has it) |
| qwen3.8-27b-fp8, -nvfp4 | blurb_header | min_n:4+reversed | (empty) | `LANGUAGE_MODEL_ONLY=0`, `SYSTEMONE_IMAGES=1`, `MM_PROCESSOR_KWARGS={"max_pixels":1638400}`, `--limit-mm-per-prompt {"video":0,"image":4}`, `--max-logprobs 128` |
| qwen3.6-27b, -fp8 | blurb_header | identity | (empty) | none |

Copy the bf16 profiles' vision comment lines into the quant profiles; drop gemma fp8's "images (<=280)" note.

- [ ] **Step 1: Write failing tests**
  - `test_blurb_header_is_the_experiment_layout_token_for_token`: `load_layouts()["blurb_header"]` equals the experiment file's parts (every template field).
  - `test_profiles_serve_the_round_4_defaults`: parametrized over the table above, using `Settings.from_profile`.
  - `test_vision_profiles_raise_max_logprobs`: every profile with `SYSTEMONE_IMAGES=1` has `--max-logprobs 128` and `"image":4` in `EXTRA_ARGS`.
- [ ] **Step 2: Run** `uv run pytest tests/unit/test_profile_env.py tests/unit/test_layouts.py tests/unit/test_blurb_layouts.py -q`. Expected: FAIL.
- [ ] **Step 3: Create the layout, edit the profiles, then run** `for p in gemma-4-31b gemma-4-31b-fp8 qwen3.8-27b qwen3.8-27b-fp8 qwen3.8-27b-nvfp4 qwen3.6-27b qwen3.6-27b-fp8; do uv run python scripts/build_labels.py --profile $p; done`. Expected: `git status` shows only the new `blurb_header/labels.json` files under `data/`. Existing tables are unchanged; revert and investigate if any moved.
- [ ] **Step 4: Run** `uv run pytest -q && uv run pytest tests/parity -q && uv run ruff check .`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(profiles): blurb_header and round 4 orders`, staging the layout, the 7 profiles, the 7 label files, the docs and the tests.

### Task 7: Stage 1 box queues and runbook

**Files:**
- Modify: `scripts/remote/jobs/*.txt` (the 7 profiles)
- Modify: `docs/remote-gpu.md` (new section "Two-stage campaign: collect, calibrate, latency + Index")
- Test: `tests/unit/test_remote_scripts.py`

**Stage 1 job files** (P = profile; `live-images` only on the 5 vision profiles):

```
stack: bash scripts/remote/stack.sh up P
live-images: bash scripts/remote/stack.sh up P && uv run pytest -m live tests/live/test_image_decisions.py -v
collect-calib: bash scripts/remote/stack.sh up P && uv run python scripts/collect.py --profile P --split calib --layouts blurb_header --orders identity+reversed --label blurb
collect-eval: bash scripts/remote/stack.sh up P && uv run python scripts/collect.py --profile P --split eval --layouts blurb_header --orders identity+reversed --label blurb
```

- [ ] **Step 1: Update tests.** `test_collect_jobs_run_their_split_for_their_profile` accepts the `--layouts … --label …` tail. The latency assert accepts trailing override args. Add `test_vision_profiles_check_images_before_collecting` (`live-images` comes before `collect-calib` exactly when the profile sets `SYSTEMONE_IMAGES=1`).
- [ ] **Step 2: Run** `uv run pytest tests/unit/test_remote_scripts.py -q`. Expected: FAIL.
- [ ] **Step 3: Write the 7 job files and the runbook section.** The runbook covers:
  - push with `--vision` for the 5 vision profiles;
  - the pull loop;
  - local calibrate (gemma: identity then top_p; qwen3.8: min_n; qwen3.6: identity, all with `--layouts blurb_header --collect-label blurb`);
  - the owner commits;
  - appending the stage 2 lines (Task 9) and re-pushing to the same box.
- [ ] **Step 4: Run** `uv run pytest -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(remote): stage 1 blurb collect queues`.

### Task 8: Local smoke test, then stop for the owner

GPU, < 10 min per profile. The owner sets the power limit; check it first and pause between profiles (memory: gpu-power-limit-runs).

- [ ] **Step 1:** `docker compose --env-file profiles/gemma-4-31b-fp8.env up -d`, wait for healthy, then `uv run pytest -m live tests/live -v`.
  - Expected: all pass, including `test_image_decisions.py`. `blurb_header` runs uncalibrated (T = 1, warning in the log).
  - Send one `top_p` request with a low-confidence question and check that the gateway log shows two vLLM completions calls.
  - `docker compose down`.
- [ ] **Step 2:** The same for `profiles/qwen3.8-27b-nvfp4.env`. Expected: all pass. A request with a 4-option question reads 2 rows for it.
- [ ] **Step 3:** If vLLM refuses a quant profile with vision (KV, OOM), stop and report the log line to the owner. Don't tune silently.
- [ ] **Step 4: STOP.** Report to the owner and ask for the ok to rent 7 boxes (spec §6).

### Task 9: After stage 1, calibrate and write the stage 2 queues (owner-gated)

Runs after the owner rents the boxes and stage 1 pulls are complete.

**Files:**
- Create: `data/<profile>/blurb_header/calibration.json` ×7 and `calibration-identity.json` ×2 (gemma)
- Modify: `scripts/remote/jobs/*.txt` (append stage 2), `tests/unit/test_remote_scripts.py`

**Stage 2 lines, appended** (`vision-*` only on the 5 vision profiles):

```
restack: bash scripts/remote/stack.sh down; bash scripts/remote/stack.sh up P
latency-before: bash scripts/remote/stack.sh up P && uv run python scripts/latency.py --profile P --layout header --option-orders identity
latency-after: bash scripts/remote/stack.sh up P && uv run python scripts/latency.py --profile P
vision-setup: python3 -m pip install -q --no-deps -e .cache/decision-index-vision/src
vision-latency: bash scripts/remote/stack.sh up P && uv run python scripts/vision_run.py --profile P --gateway http://127.0.0.1:9000 --sample 300 --workers 1 --run-dir .cache/vision-runs/P/latency-$(cat .cache/remote/run_tag)
index: bash scripts/remote/stack.sh up P && uv run python scripts/evaluate.py index --profile P --shards 4 --run-dir .cache/index-runs/P/$(cat .cache/remote/run_tag) --strict
vision-full: bash scripts/remote/stack.sh up P && uv run python scripts/vision_run.py --profile P --gateway http://127.0.0.1:9000 --run-dir .cache/vision-runs/P/full-$(cat .cache/remote/run_tag)
```

- [ ] **Step 1: Calibrate each profile.**
  - gemma ×2: `uv run python scripts/calibrate.py --profile P --layouts blurb_header --collect-label blurb --orders identity`, then the same command with `--orders top_p:0.9+reversed`.
  - qwen3.8 ×3: `--orders min_n:4+reversed`.
  - qwen3.6 ×2: `--orders identity`.
  - Expected: each prints a `docs/results/archive/<profile>/<UTC>-calibrate/summary.md`, and each file's `fit.orders` matches.
- [ ] **Step 2:** `uv run pytest -q`. Show the owner the calibration summaries and let the owner commit the files. The owner commits label tables and calibrations deliberately.
- [ ] **Step 3:** Append the stage 2 lines, update the remote tests, run `uv run pytest tests/unit/test_remote_scripts.py -q` (PASS), and commit `feat(remote): stage 2 latency and Index queues`.
- [ ] **Step 4:** Re-push each box (`scripts/remote/push.sh … P [--vision]`), then `pull.sh … --loop 1800` until `QUEUE_DONE`.

### Task 10: Results

- [ ] **Step 1:** Commit each profile's complete result dirs: `docs/results/<profile>/…` and `docs/results/archive/<profile>/…`, explicit paths.
- [ ] **Step 2:** Write a short report with these tables:
  - latency A/B per profile: median/p95 before → after;
  - image latency against the 2026-10-16 bf16 runs;
  - Index text and image scores against each profile's last run.
  Then ask the owner to judge the latency change. Box destroy needs the owner's ok (memory: vast-box-replace-rule).
