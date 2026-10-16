# Vision Campaign Round 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the 3 × 2 × 2 image factorial, the image-temperature fit on a non-suite set, the cyclic-orders
check and the latency probes on gemma-4-31b and qwen3.8-27b, and hand the owner tables to pick from.

**Architecture:** Experiment layouts live in `prompts/experiments/` and reach vision_collect through
`--layout-file`. A new `image_label` layout key adds `Image N:` before images. `vision_factorial.py` turns 12
scored configs into factor effects with a shared paired bootstrap. A non-suite calibration set feeds a
`T_image` that the gateway applies to image rows. Probes measure latency causes. GPU runs come last, in
owner-approved chunks.

**Tech Stack:** Python 3.12, the gateway package, the DS-034 harness (`scripts/vision_*.py`), Pillow,
huggingface_hub for dataset downloads.

**Spec:** `docs/superpowers/specs/2026-10-16-vision-campaign-1-design.md`

## Global Constraints

- Factor levels:
  - gemma `max_soft_tokens` 280 / 560 / 1120;
  - qwen `max_pixels` 409600 / 819200 / 1638400;
  - placement {current, images before the question list};
  - wording {none, `Image {n}:` label + "Answer from the image(s)."}.
  - Base: 560 or 1638400, current placement, no wording.
- Every grid collect is on dev with `--orders identity+reversed`. ECE uses cross-fitted `fit-T`.
- Experiment layouts never go in `prompts/*.toml`. The gateway must start unchanged on every profile.
- Text requests must build byte-identical ids, and their probabilities must not change (golden tests stay green).
- Nothing is fitted on suite rows for shipping. `T_image` comes only from the non-suite calibration set, and
  rows whose image matches a suite image are dropped.
- Holdout: confirmation only, after the owner picks, logged.
- GPU over 10 min needs the owner's ok. Runs are local at 510 W. Check the power limit first.
- Repo rules:
  - comments ≤ 2 lines;
  - Conventional Commits, caveman style, subject ≤ 50 chars, explicit paths;
  - never `pkill -f`;
  - keys come from `.env` and are never printed.

## Review Focus

1. **Label letters in an experiment layout.** If a label letter isn't a single token in context (the
   `Image N:` text changes neighbours), collect refuses before any request and names the letter. Test: Task 2.
2. **Re-encoded suite images.** A calibration-set image identical in pixels to a suite image, but with
   different bytes, is still dropped (pixel fingerprint, not only the byte SHA-256). Test: Task 4.
3. **Stale `T_image`.** A calibration file whose image block was fitted under another layout, tokenizer or
   revision is refused at gateway startup, the way text calibration is. Test: Task 5.
4. **Text after `T_image`.** Text requests' probabilities are unchanged when a calibration file gains
   `T_image`. Test: Task 5.
5. **Incomplete factorial.** A factorial with a missing cell, or with cells on different ids, is refused and
   the gap is named. Test: Task 3.

---

### Task 1: `image_label` layout key and experiment layouts

**Files:**
- Modify: `gateway/layouts.py`, `gateway/prompts.py`
- Create: `prompts/experiments/header-imgfirst.toml`, `prompts/experiments/header-worded.toml`,
  `prompts/experiments/header-imgfirst-worded.toml`
- Test: `tests/unit/test_layouts.py`, `tests/unit/test_prompts.py`

**Interfaces:**
- Produces:
  - `Layout.image_label: str = ""` (optional TOML key; when set it must contain `{n}`);
  - `layouts.load_layout(path)` already loads any path.
- `image_context` writes `encode(layout.image_label.format(n=k))` before the k-th image (k from 1) when
  `image_label` is set.
- Layout files:
  - `header-imgfirst`: header with `order = ["context", "questions", "question", "options"]`;
  - `header-worded`: header plus `image_label = "Image {n}:\n"`, and question
    `"\n\nQuestion: {question}\nAnswer from the image(s).\nOptions:"`;
  - `header-imgfirst-worded`: both changes.
- `load_layouts()` stays non-recursive: `prompts/experiments/` is never loaded by the gateway.

- [ ] **Step 1: Failing tests**
  - `test_image_label_needs_n` — a layout whose `image_label` lacks `{n}` raises naming the key.
  - `test_layouts_without_image_label_keep_their_hash_and_ids` — the existing golden prompt tests and the
    `image_context` goldens stay unchanged.
  - `test_image_label_precedes_each_image` — gemma tokenizer, items `[img, img]`, worded layout: ids contain
    `encode("Image 1:\n") + [258880]` and `encode("Image 2:\n") + [258880]`, in order.
  - `test_gateway_does_not_load_experiment_layouts` — `sorted(load_layouts())` is still
    `["decider_chat", "header", "question_first"]`.
  - `test_experiment_layouts_load_and_share_the_header_prefix_rule` — each of the three loads; `imgfirst`
    shared parts are `["context", "questions"]`.
- [ ] **Step 2:** The tests fail. **Step 3:** Implement. **Step 4:** Run `HF_HUB_OFFLINE=1 uv run pytest -q`
  and ruff; both green.
- [ ] **Step 5:** Commit: `feat(vision): image_label and experiment layouts`.

### Task 2: Collect experiment layouts and external rows

**Files:**
- Modify: `scripts/vision_collect.py`
- Test: `tests/unit/test_vision_collect.py`

**Interfaces:**
- Consumes: Task 1 layouts; `gateway.labels.label_table(tok, layout)` and the single-token check used by
  `scripts/build_labels.py`; `gateway.prompts.chat_frame`.
- Produces:
  - `--layout-file PATH`, mutually exclusive with `--layout`. It loads the layout, builds labels and the
    frame in memory, and registers them under the layout name in the engine's dicts.
  - The stamp carries `layout_sha256` and a `labels_sha256` of the in-memory table.
  - `config.json` records `layout_file` (repo-relative path).
  - `--rows FILE` (suite-format JSONL) replaces the split manifest. It takes a mandatory `--split NAME` used
    for the output file name. Image paths resolve against the rows file's directory, and groups come from
    `vision_splits.groups` on those rows.
  - `--rows` refuses `--holdout`.

- [ ] **Step 1: Failing tests**
  - `test_layout_file_is_collected_with_in_memory_labels` — a fake vLLM; the record stamp holds the
    experiment layout hash.
  - `test_layout_file_with_a_non_single_token_label_is_refused` (Review Focus 1) — a layout whose
    `option` text merges with the label refuses before any request and names the letter.
  - `test_rows_file_collects_with_its_own_image_dir`
  - `test_rows_and_holdout_are_refused_together`
  - `test_layout_and_layout_file_are_exclusive`
- [ ] **Step 2:** The tests fail. **Step 3:** Implement. **Step 4:** Full suite and ruff green.
- [ ] **Step 5:** Commit: `feat(vision): collect layout files and row files`.

### Task 3: Factorial analysis

**Files:**
- Create: `scripts/vision_factorial.py`
- Test: `tests/unit/test_vision_factorial.py`

**Interfaces:**
- Consumes:
  - `scripts/vision_compare.py`: its loaders for offline scored dirs, `index`, weights and group handling.
    Reuse them; don't copy them.
  - Task 2 collect configs.
- Produces:
  - CLI: `uv run python scripts/vision_factorial.py --grid GRID.json --out-label L [--latency LEVEL=DIR ...]`.
  - `GRID.json`: `{"factors": {"budget": [...], "placement": [...], "wording": [...]}, "reference":
    {...}, "cells": [{"dir": ..., "budget": ..., "placement": ..., "wording": ...}, ...]}`.
  - Output: `docs/results/vision-experiments/<UTC>-<L>/summary.md` + `summary.json`.
- Effects, computed on one shared bootstrap resample per iteration (10,000 resamples, groups within each
  benchmark, seed 0) so all cells are paired:
  - **Main effect** of level `v` of factor F: the mean over all cells of the other factors of
    index(F = v) − index(F = reference).
  - **Two-way interaction** of F = v and G = w: the mean over the third factor of
    [index(v, w) − index(v, ref_G)] − [index(ref_F, w) − index(ref_F, ref_G)].
  - Each is reported with a 95% percentile CI, plus per-benchmark main effects (unclipped skill).
  - Per cell: index, ECE, mean input tokens. Latency is attached per budget level from `--latency` dirs
    (compare's power-limit rules apply).
- Refuse: a missing or duplicate cell, cells on different ids, and an unknown factor level (Review Focus 5).

- [ ] **Step 1: Failing tests**
  - `test_main_effect_recovers_a_planted_effect` — synthetic cells where budget=high flips 5% of rows to
    correct in every benchmark; the main effect equals the mean of index(high cell) − index(reference cell)
    computed directly with `vision_compare.index`, and its CI excludes 0.
  - `test_null_factor_has_zero_effect_and_ci_covering_zero`
  - `test_interaction_is_zero_for_additive_effects_and_nonzero_when_planted`
  - `test_missing_or_duplicate_cell_is_refused_naming_it`
  - `test_cells_on_different_ids_are_refused`
- [ ] **Step 2:** The tests fail. **Step 3:** Implement. **Step 4:** Full suite and ruff green.
- [ ] **Step 5:** Commit: `feat(vision): factorial effects with paired bootstrap`.

### Task 4: Non-suite image calibration set

**Files:**
- Create: `scripts/vision_calib_set.py`, `data/splits/vision-calib.json` (source manifest: datasets,
  revisions, row ids, image SHA-256s, drop counts)
- Modify: `pyproject.toml` (dev group only: whatever reader the parquet files need, e.g. `pyarrow`)
- Test: `tests/unit/test_vision_calib_set.py`

**Interfaces:**
- Produces:
  - `uv run python scripts/vision_calib_set.py build` writes `.cache/vision-calib/rows.jsonl` and
    `.cache/vision-calib/img/...` (rows in the suite format: `id`, `benchmark` = source name, `images`,
    `state: {}`, `questions.answer {type: "choice", instructions, criteria}`, `expected.answer`), plus the
    committed manifest.
  - `fingerprint(image_bytes) -> str`: SHA-256 of the image converted to 16×16 grayscale, so re-encoded
    copies match.
- Sources: train splits of ScienceQA (image questions only), AI2D and A-OKVQA (multiple-choice), about 600
  each, seeded sample (seed 20261016).
  - Pin each dataset's revision.
  - If a source is unavailable, take its share from the others and record that.
  - Option letters `A`, `B`, ... in the source's order; at most 10 options.
- Drop any row whose image byte SHA-256 or fingerprint matches any suite image (compute suite fingerprints
  once from `vision_splits.SUITE`'s images). Report the counts per source.
- Downloads are CPU/network work (no GPU). No secrets are needed: the datasets are public; refuse a gated one.

- [ ] **Step 1: Failing tests** (no network: build from tiny fake sources through a source adapter interface)
  - `test_rows_are_in_suite_format_and_load_in_collect` — a row passes `vision_collect`'s row parsing.
  - `test_byte_identical_suite_image_is_dropped`
  - `test_reencoded_suite_image_is_dropped_by_fingerprint` (Review Focus 2) — a suite PNG saved as JPEG q90
    is dropped.
  - `test_unavailable_source_shifts_its_share_and_is_recorded`
  - `test_more_than_10_options_are_skipped`
- [ ] **Step 2:** The tests fail. **Step 3:** Implement.
- [ ] **Step 4:** Tests and ruff green. Run `build` for real (network). Report per-source counts, drops and
  the total, then commit the manifest.
- [ ] **Step 5:** Commit: `feat(vision): non-suite image calibration set`.

### Task 5: `T_image` in calibration and the gateway

**Files:**
- Create: `scripts/fit_image_t.py`
- Modify: `gateway/calibration.py`, `gateway/decide.py`, `gateway/app.py` (`/health`)
- Test: `tests/unit/test_calibration.py`, `tests/unit/test_decide.py`, `tests/unit/test_fit_image_t.py`

**Interfaces:**
- Produces:
  - `Calibration.T_image: float | None = None` and `as_dict` including it.
  - The calibration file's optional `"image": {"T": float, "stamp": {...}, "fit": {"source":
    "vision-calib", "rows": n, "orders": ...}}`.
  - `load_calibration` refuses a stale image stamp with the same STAMP_KEYS check as the text stamp
    (Review Focus 3).
  - `decide.answers_for(questions, reads, cal, image: bool = False)` uses `cal.T_image` for choice questions
    when `image` and `T_image` is set. Image requests pass `image=True`.
  - `/health` shows the calibration dict, including `T_image`.
  - `scripts/fit_image_t.py --collect FILE --profile P [--write]`: fits one T on all scorable rows of a
    collect made with `--rows` (refusing suite collects by checking `config.json` has `rows`, not a split
    manifest), prints T and the NLL before and after, and with `--write` adds the image block plus a
    `comments` entry to `data/<profile>/header/calibration.json`.

- [ ] **Step 1: Failing tests**
  - `test_image_block_is_optional_and_loaded`
  - `test_stale_image_stamp_is_refused`
  - `test_image_rows_use_T_image_and_text_rows_do_not` (Review Focus 4) — the same reads give different
    probabilities with `image=True` and identical ones with `image=False`.
  - `test_fit_image_t_refuses_a_suite_collect`
  - `test_fit_image_t_writes_block_and_comment` — tmp data root.
- [ ] **Step 2:** The tests fail. **Step 3:** Implement. **Step 4:** Full suite (goldens included) and ruff
  green.
- [ ] **Step 5:** Commit: `feat(vision): image temperature (T_image)`.

### Task 6: Latency probes (E6)

**Files:**
- Modify: `scripts/image_share_probe.py`
- Create: `scripts/image_resend_probe.py`
- Test: `tests/unit/test_image_share_probe.py`, `tests/unit/test_image_resend_probe.py`

**Interfaces:**
- `image_share_probe.py` gets `ARMS = ("all", "prefix", "row")`. `row` sends row 1 alone, then the rest
  together, as `WARM_UP=row` does.
- `image_resend_probe.py --profile P [--vllm URL] [--rows 300]` reads dev rows (`load_split("vision-dev")`) and
  reports per request:
  - (a) gateway time to build parts and JSON per row, measured in process by timing `json.dumps` of the
    generate payloads;
  - (b) vLLM time for a request with the image vs the same token ids with `uuid` only and no `url`, once the
    image is cached. A rejection of the uuid-only part is recorded, not raised.
- Output: `docs/results/archive/<profile>/<UTC>-image-resend/` (`results.json` + `summary.md`).

- [ ] **Step 1: Failing tests** — `test_row_arm_sends_row_one_first`;
  `test_resend_summary_reports_json_ms_and_uuid_outcome` (fake vLLM accepting and rejecting uuid-only).
- [ ] **Step 2–4:** The tests fail, implement, then the tests and ruff are green.
- [ ] **Step 5:** Commit: `feat(vision): latency probes for image rows`.

### Task 7: GPU runs, gemma-4-31b (owner ok first)

- [ ] **Step 1:** Ask for the owner's ok with an estimate: about 2.6 h for 3 restarts, 12 grid collects, the
  cyclic collect, the calibration-set collect, 3 latency runs and the probes. Check the power limit (510 W).
- [ ] **Step 2:** For each budget in (560, 280, 1120):
  - restart the stack with `MM_PROCESSOR_KWARGS={"max_soft_tokens":B}` (profile env override via
    `docker compose` with a run-local env file, never editing the profile);
  - collect the four layouts (`header` plus the three experiment files) with label `r1-b{B}-<layout>`;
  - run one latency set (`vision_run.py --ids vision-latency --workers 1`).
- [ ] **Step 3:** At budget 560:
  - cyclic collect (`--orders cyclic:4`, label `r1-cyclic`);
  - calibration-set collect (`--rows .cache/vision-calib/rows.jsonl --split calib`, label `r1-calib`);
  - both probes.
- [ ] **Step 4:** Run the offline arms (`fit-T` identity, and `fit-T`/`pride` for cyclic). Write `GRID.json`,
  then run `vision_factorial.py` and `fit_image_t.py` (no `--write` yet). Run compare for E5.
- [ ] **Step 5:** Commit the result folders: `docs(results): vision round 1, gemma`.

### Task 8: GPU runs, qwen3.8-27b (owner ok first)

- [ ] **Steps:** The same as Task 7, with `MM_PROCESSOR_KWARGS={"max_pixels":P}` for P in
  (1638400, 409600, 819200). Commit: `docs(results): vision round 1, qwen3.8`.

### Task 9: Results doc and tickets

- [ ] **Step 1:** Add a "Round 1 results" section to `docs/background/vision-experiments.md`, per model:
  - factorial main effects and interactions with CIs;
  - per-benchmark effects;
  - ECE text vs `T_image` on dev;
  - E5 and E6 findings;
  - latency per budget.

  Report only; no recommendation is written as decided.
- [ ] **Step 2:** Add DS-035, DS-036 and DS-037 progress notes with the commit. Commit:
  `docs: vision round 1 results`.
- [ ] **Step 3:** Stop. The owner picks per model. Holdout confirmation, `T_image --write` and any shipping
  follow as a separate, owner-approved step.
