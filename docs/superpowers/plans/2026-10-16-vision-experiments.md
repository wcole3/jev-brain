# Vision Experiments Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A dev/holdout split of the public vision suite plus tools to collect raw image-row logprobs,
re-score them offline, time configs, and compare configs with paired statistics.

**Architecture:** `vision_splits.py` cuts grouped, stratified manifests and guards the holdout.
`vision_collect.py` records raw letter logprobs per row through the gateway's own code, directly against
vLLM. `vision_offline.py` turns a collect file into scored rows per arm (orders + calibration, cross-fitted).
`vision_compare.py` reads scored rows or live kit runs and writes Δskill CIs, McNemar, per-benchmark and
frontier tables. `vision_run.py` gains `--ids` for the fixed latency set.

**Tech Stack:** Python 3.12, httpx, the gateway package, stdlib statistics; the Decision Index kit only for live
runs (unchanged).

**Spec:** `docs/superpowers/specs/2026-10-16-vision-experiments-design.md`

## Global Constraints

- Suite: `.cache/decision-index-vision/work/vision/vision-rows.jsonl` (12,210 rows; fields `id`, `benchmark`,
  `images`, `state`, `questions.answer{type,instructions,criteria}`, `expected.answer`).
- Dev = min(136, 40% of the benchmark), holdout = min(218, 40% of the benchmark), per benchmark; the rest is
  reserve and never read. Latency set: 320 rows from dev, the first 20 warm-up.
- Rows sharing any image file are one group; a group is in exactly one split.
- Holdout reads need `--holdout`; each use appends to `docs/results/vision-experiments/holdout-log.md`;
  warn from the 6th entry.
- Nothing is fitted on holdout rows. Fitted arms are 2-fold cross-fitted by group within the split.
- Skill and index match the kit (`decision_index/vision/score.py`): per benchmark
  skill = (acc − mean chance) / (1 − mean chance) with chance = 1/options per row; index =
  100 × Σ(w·clip(skill, 0, 1)) / Σw (all weights are 1.0 in edition 0.3).
- Bootstrap: 10,000 resamples, groups resampled within each benchmark, 95% percentile CI, seed 0.
- The harness never picks a winner; it reports.
- Repo rules: comments ≤ 2 lines; Conventional Commits caveman style, subject ≤ 50 chars, explicit paths;
  GPU jobs over 10 min need the owner's ok; never `pkill -f`; keys from `.env`, never printed.

## Review Focus

1. A row with an unreadable or missing image file: collect records it as `status: "unsupported"` with the
   error and keeps going, and compare excludes it from every config alike. Test: Task 2.
2. Two configs with different ids (a crashed collect, a stale split): compare refuses with the ids that differ
   instead of comparing unequal sets. Test: Task 4.
3. A benchmark where a fold has too few rows to fit (tiny folds): fitting falls back to the text calibration
   and says so in the arm's report. Test: Task 3.
4. A split manifest from another suite build (hash mismatch): every tool refuses it with both hashes. Test: Task 1.
5. A live kit run with errored rows: compare counts them as wrong and reports the count, not silently drops
   them. Test: Task 4.

---

### Task 1: Splits and the holdout guard

**Files:** Create `scripts/vision_splits.py`, `data/splits/vision-dev.json`, `data/splits/vision-holdout.json`,
`data/splits/vision-latency.json`; Test `tests/unit/test_vision_splits.py`.

**Interfaces:**
- Produces:
  - `SUITE = ROOT/".cache/decision-index-vision/work/vision/vision-rows.jsonl"`;
  - `groups(rows: list[dict]) -> dict[str, str]` (row id → group key; union over shared image paths;
    key = the smallest member id);
  - `cut(rows, seed: int = 20261016) -> dict[str, list[str]]` with keys `dev`, `holdout`, `latency`
    (`latency` is ordered; its first 20 ids are warm-up);
  - `load_split(name: str, *, holdout: bool = False, tool: str = "", label: str = "") -> list[dict]`
    returns suite rows for the manifest, refusing a stale suite hash and refusing `vision-holdout` unless
    `holdout=True` (then appending `| <UTC> | tool | label | commit |` to the holdout log and warning when
    the log has more than 5 entries).
  - Manifest JSON: `{"meta": {"suite_sha256", "seed", "rule", "counts": {benchmark: n}, "warmup": 20?}, "ids": [...]}`.
- CLI: `uv run python scripts/vision_splits.py write` writes the three manifests.

- [ ] **Step 1: Failing tests** (hand-made rows, no suite needed):
  - `test_rows_sharing_an_image_are_one_group`
  - `test_groups_never_straddle_splits`
  - `test_counts_follow_min_136_and_40_percent` — a 244-row benchmark gets ≤ 98 dev, a 2,465-row one 136 dev / 218 holdout
  - `test_same_seed_same_cut` and `test_other_seed_other_cut`
  - `test_latency_set_is_320_dev_rows_stratified`
  - `test_holdout_refused_without_flag` and `test_holdout_use_is_logged_and_warns_after_five` (tmp log path)
  - `test_stale_suite_hash_refused_naming_both_hashes`
- [ ] **Step 2:** `uv run pytest tests/unit/test_vision_splits.py -q` fails.
- [ ] **Step 3:** Implement. Assignment: sort each benchmark's groups by `sha256(seed:group_key)`, fill dev
  then holdout by whole groups until each target is met (a group may overshoot by its size). Latency: 320
  dev rows, stratified by benchmark (largest-remainder quotas), ordered by the same hash.
- [ ] **Step 4:** Tests pass; run `write` on the local suite; check the counts printed (dev ≈1,500,
  holdout ≈2,400).
- [ ] **Step 5:** Commit the script, test and three manifests: `feat(vision): dev/holdout splits (DS-034)`.

### Task 2: Collect

**Files:** Create `scripts/vision_collect.py`; Test `tests/unit/test_vision_collect.py`.

**Interfaces:**
- Consumes: `load_split` (Task 1); `gateway.app.load_engine`, `gateway.decide.read_rows`,
  `gateway.vision.load_vision`, `gateway.images.decode_image`; `scripts/collect.py`'s `records` and
  `stamp` patterns.
- Produces: `.cache/vision-collect/<profile>/<label>/<split>.jsonl.gz`, one record per row:
  `{"id", "benchmark", "group", "status": "ok"|"unsupported"|"invalid", "error"?, "names": [...],
  "gold": int|None, "input_tokens", "reads": [{"perm": [...], "logprobs": [...]}], "stamp": {...}}`
  plus a `config.json` beside it (`profile`, `label`, `layout`, `orders`, `env`, `split`, `commit`).
- CLI: `uv run python scripts/vision_collect.py --profile P --label L [--split dev] [--layout header]
  [--orders identity+reversed] [--env KEY=VALUE ...] [--vllm URL] [--concurrency 8] [--holdout]`.

Rules:
- Settings: `Settings.from_profile(P)` with `--env` overrides applied (`dataclasses.replace` through
  `Settings.from_env` on the merged env) and `systemone_images` forced on; the layout from `--layout`.
- Request per row: `SystemOneRequest(state=row["state"], questions=row["questions"], images=[data URL of each
  file under the suite dir], layout=..., option_orders=...)`; the gateway's own decode/downscale applies.
- Reads come from `read_rows(engine, request)`; record every (perm, logprobs) of question `answer`.
- Self-check at start: send one generated 1280×1092 PNG through `/inference/v1/generate` with
  `return_token_ids` (as in `tests/live/test_image_decisions.py`) and exit with both numbers unless the
  prompt length equals `len(ids) + vision.added(image)`.
- A layout whose `data/<profile>/<layout>/labels.json` is missing is refused before any request.
- Resume: skip ids already in the file; skip a truncated tail; retry `httpx.HTTPError` like `collect.py`.

- [ ] **Step 1: Failing tests** with an httpx MockTransport standing in for vLLM and a 4-row fake suite:
  - `test_record_shape_and_config_json`
  - `test_resume_skips_done_ids_and_a_truncated_tail`
  - `test_stamp_has_layout_labels_model_mm_kwargs_commit`
  - `test_self_check_refuses_a_count_mismatch`
  - `test_missing_label_table_is_refused`
  - `test_unreadable_image_is_recorded_unsupported_and_run_continues` (Review Focus 1)
  - `test_holdout_needs_the_flag`
- [ ] **Step 2:** Tests fail. **Step 3:** Implement. **Step 4:** `uv run pytest -q`, ruff clean.
- [ ] **Step 5:** Commit: `feat(vision): collect raw image-row logprobs`.

### Task 3: Offline arms

**Files:** Create `scripts/vision_offline.py`; Test `tests/unit/test_vision_offline.py`.

**Interfaces:**
- Consumes: Task 2 records; `gateway.decide.blend`; `scripts.fit.fit_temperature`;
  `gateway.calibration.load_calibration` for the `text` arm (the profile's header calibration).
- Produces: `score(records, arm: str, orders: str, text_cal) -> tuple[list[dict], dict]` returning scored
  rows `{"id", "benchmark", "group", "gold", "probs", "chance"}` and an arm report (fitted values per fold,
  fallbacks). Arms: `text`, `fit-T`, `fit-T-bench`, `pride`. CLI:
  `uv run python scripts/vision_offline.py --collect FILE --arm A [--orders identity] --out DIR` writes
  `scored.jsonl.gz` and `arm.json`.
- Folds: group keys sorted by `sha256("fold:" + group)`, alternate 0/1. Rows in fold k are scored with
  parameters fitted on fold 1−k.
- `pride`: on the fitting fold, for each option count k, the letter prior is the mean over reads of the
  read's logprobs centred to mean zero, by position; scoring subtracts the prior for that k from each read's
  logprobs, then applies the fold's fitted T. A k never seen in the fitting fold uses no prior.
- Fallback: a fit with fewer than 30 questions (fold, or fold × benchmark for `fit-T-bench`) uses the text T
  and records `"fallback": true` in the report (Review Focus 3).

- [ ] **Step 1: Failing tests:**
  - `test_text_arm_reproduces_gateway_probabilities` — same logprobs through `gateway.decide.probabilities`
  - `test_cross_fit_never_scores_a_row_with_its_own_fold` — a row's prediction is unchanged when its own fold's data changes
  - `test_fit_T_recovers_a_planted_temperature` — logprobs generated at T=2 fit to 2 ± 0.1
  - `test_pride_removes_a_planted_letter_bias` — a +1.0 bias on position 0 is removed to within 0.1
  - `test_tiny_fold_falls_back_to_text_T_and_says_so`
  - `test_orders_subset_uses_only_collected_perms` — asking for an uncollected order raises naming the row
- [ ] **Step 2:** Tests fail. **Step 3:** Implement. **Step 4:** Tests pass, ruff clean.
- [ ] **Step 5:** Commit: `feat(vision): offline arms with cross-fit`.

### Task 4: Compare

**Files:** Create `scripts/vision_compare.py`; Test `tests/unit/test_vision_compare.py`.

**Interfaces:**
- Consumes: Task 3 `scored.jsonl.gz`; live kit run folders (`results.jsonl.gz` from
  `scripts/vision_summary.py`) joined with suite rows for gold, chance, benchmark and group (Task 1 `groups`);
  latency `summary.json` from Task 5.
- Produces:
  - `index(rows) -> tuple[float, dict[str, float]]` (kit formula);
  - `paired(a_rows, b_rows, resamples=10000, seed=0) -> dict` with `delta_index`, `ci`, per-benchmark
    `delta_skill` with CIs, `mcnemar_p` (exact two-sided binomial on discordant counts), `discordant_share`,
    `delta_ece`, `delta_nll`;
  - CLI: `uv run python scripts/vision_compare.py --baseline NAME=PATH CFG=PATH ... [--latency NAME=DIR ...]
    --out-label L` writing `docs/results/vision-experiments/<UTC>-<L>/summary.md` and `summary.json`
    (frontier table: config, index, Δ with CI, ECE, NLL, mean input tokens, latency p50/p80 when given;
    a per-benchmark Δ table; d and McNemar per config).
- Live errored rows count as wrong and are reported per config (Review Focus 5).
- Refuse: id sets that differ (print up to 10 ids each way; Review Focus 2); latency summaries with
  different power limits.

- [ ] **Step 1: Failing tests:**
  - `test_index_matches_the_kit_on_stored_results` — on `docs/results/gemma-4-31b/2026-10-16T023752Z-vision`
    gives 73.70 ± 0.005 and the stored per-benchmark skills (skip if the suite is absent)
  - `test_mcnemar_exact_on_known_counts` — b=10, c=2 gives p ≈ 0.0386
  - `test_bootstrap_ci_resamples_groups_within_benchmarks` — duplicated rows in one group do not narrow the CI
  - `test_identical_configs_give_zero_delta_and_p_one`
  - `test_different_ids_are_refused_with_examples`
  - `test_errored_live_rows_count_as_wrong_and_are_reported`
  - `test_mixed_power_limits_are_refused`
- [ ] **Step 2:** Tests fail. **Step 3:** Implement. **Step 4:** Tests pass, ruff clean.
- [ ] **Step 5:** Commit: `feat(vision): paired compare and frontier`.

### Task 5: Latency set runs

**Files:** Modify `scripts/vision_run.py`, `scripts/vision_summary.py`; Test `tests/unit/test_vision_run.py`.

**Interfaces:**
- `vision_run.py --ids FILE` (a manifest from Task 1, refusing `vision-holdout` unless `--holdout`): writes
  the sample-suite dir from those ids in manifest order (existing `write_sample_dir`) and passes the
  manifest's warm-up ids to the summary.
- `vision_summary.latency(rows, skip: set[str] = frozenset())` drops warm-up ids before percentiles.
- `summary.json` gains `power_limit_w` (from `nvidia-smi --query-gpu=power.limit`, start and end of the
  run) and `telemetry` (the `scripts/gpu_telemetry.py summarize` dict for the run window); `vision_run.py`
  runs `gpu_telemetry.py sample` as a child for the run and stops it by its own pid.

- [ ] **Step 1: Failing tests:** `test_ids_manifest_orders_the_sample_suite`,
  `test_warmup_ids_are_dropped_from_latency`, `test_power_limit_is_recorded` (fake `nvidia-smi` on PATH),
  `test_holdout_manifest_needs_the_flag`.
- [ ] **Step 2–4:** fail, implement, pass, ruff clean.
- [ ] **Step 5:** Commit: `feat(vision): latency set runs`.

### Task 6: Docs

**Files:** Create `docs/background/vision-experiments.md`; Modify `docs/development.md`,
`docs/background/README.md`.

- [ ] **Step 1:** `vision-experiments.md`: why the split (public suite = half the board), the split rule and
  counts from the manifests, holdout rules and log, the arms and cross-fit, how to read the compare table
  (Δ CI, McNemar, d, per-benchmark), latency procedure (320-row set, warm-up dropped, A–B–A when a config
  needs a vLLM restart, power limit recorded), cost per run, and the research table from the spec. Same voice as
  `docs/background/prompt-sharing.md`.
- [ ] **Step 2:** `docs/development.md`: a short "Run a vision experiment" section with the five commands
  (splits are committed; collect; offline; latency; compare). Link from `docs/background/README.md`.
- [ ] **Step 3:** Commit: `docs: vision experiments method (DS-034)`.

### Task 7: Baselines (GPU; owner ok first)

- [ ] **Step 1:** Estimate and ask: per model, one dev collect (≈1,500 rows × 2 orders, about 12 min on a
  600 W box, longer locally) and one latency run (320 rows, one client, a few minutes), plus stack start.
- [ ] **Step 2:** For gemma-4-31b then qwen3.8-27b at today's profile: stack up; `vision_collect.py --label
  baseline`; `vision_offline.py` for arms `text`, `fit-T`, `fit-T-bench`, `pride` (orders `identity` and
  `identity+reversed`); `vision_run.py --ids data/splits/vision-latency.json --workers 1`.
- [ ] **Step 3: Pipeline check.** Compare the `text`/`identity` arm with the stored full-suite live run
  restricted to dev ids (`docs/results/<profile>/2026-10-16T02*-vision`): top-answer agreement ≥ 98% and
  index within 1 point; anything worse stops here and is reported.
- [ ] **Step 4:** `vision_compare.py --baseline text=... fit-T=... fit-T-bench=... pride=...
  text+reversed=... --latency text=...` per model; commit the result folders and collect `config.json`
  copies: `docs(results): vision dev baselines (DS-034)`.
- [ ] **Step 5:** DS-034 progress note with the frontier tables; move the ticket to Verification.
