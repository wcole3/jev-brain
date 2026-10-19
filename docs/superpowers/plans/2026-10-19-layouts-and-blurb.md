# decider_chat orders and an intro blurb, round 4 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Score round 3's order rules on `decider_chat` (text and image), and screen a one-sentence intro blurb on
`header` and `decider_chat`, for gemma-4-31b and qwen3.8-27b.

**Architecture:** Two experiment layouts carry the blurb; no gateway change. `r3_orders.py` learns any layout and a
collect-file mode; a new `layout_screen.py` pairs any two collected arms by reusing `label_screen.py`'s report
functions with a configurable base. GPU collects reuse `collect.py` and `vision_collect.py` as they are.

**Tech Stack:** Python 3, uv, pytest, ruff; vLLM via `make up PROFILE=…`; DoStuff tickets.

**Spec:** `docs/superpowers/specs/2026-10-19-layouts-and-blurb-design.md`

## Global Constraints

- Never train, calibrate or tune on Jev API outputs. Dev splits only; never vision holdout rows.
- Served layouts (`prompts/*.toml`) and their label tables stay byte-identical; blurb layouts live in `prompts/experiments/`.
- GPU chunks over 10 minutes need the owner's ok: Tasks 6 and 7 each stop for it before any GPU work.
- Local runs at 510 W (owner sets it; check `nvidia-smi --query-gpu=power.limit`, never change it). Between collect sets: ≥ 10 min idle and GPU ≤ 50 °C, whichever is later.
- Kill background jobs by pgid, never `pkill -f`. Keys from `.env`, never printed.
- Comments ≤ 2 lines. Commits: Conventional, caveman, subject ≤ 50 chars, explicit paths (never `git add -A`), local only (the owner pushes). End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Checks before each commit: `uv run pytest -q` and `uv run ruff check .` pass.
- Blurb text, exact (two trailing newlines):
  `You will be asked questions about the following context. Answer each with the letter of the best option.\n\n`

## Ruling against the spec

The spec has `label_screen.py screen --arm/--control` with `--set S` as shorthand for `--arm S --control letters`.
That shorthand would be false: round 3's `screen` reads its letters control from the old full collects
(`calib`, `index-dev`, image `baseline`), while round 4's H arm is the fresh `letters` collects. So round 3's
`screen` stays as it is, and pairs get their own script, `scripts/layout_screen.py` (Task 3), sharing the report
code. Cost if wrong: a CLI rename.

## Review Focus

1. Blurb collects carry layout names `blurb-header` / `blurb-decider` (the toml stem), not `header`: the pair loader filters records by the arm's layout name (Task 3 test `test_pair_reads_each_arms_layout`).
2. The old full collects hold rows outside calib-600 / index-dev-2k: file mode skips them instead of raising KeyError (Task 2 test `test_files_mode_keeps_manifest_rows_only`).
3. A calib file and a dev file collected under different stamps: file mode refuses with SystemExit (Task 2 test `test_files_mode_refuses_mixed_stamps`).
4. Two arms collected with different profile, split or env: the pair refuses with SystemExit (Task 3 test `test_pair_refuses_mismatched_image_configs`).
5. The blurb on qwen's front-padded prefix: rows still share the reported prefix and the blurb lands inside it (Task 1 test `test_blurb_rows_share_the_prefix`).

---

### Task 1: Blurb layouts

**Files:**
- Create: `prompts/experiments/blurb-header.toml`, `prompts/experiments/blurb-decider.toml`
- Test: `tests/unit/test_blurb_layouts.py`

**Interfaces:**
- Produces: experiment layouts named `blurb-header` and `blurb-decider` (`load_layout(path).name` is the stem).

- [ ] **Step 1: Write the failing tests** in `tests/unit/test_blurb_layouts.py`, with
  `BLURB = "You will be asked questions about the following context. Answer each with the letter of the best option.\n\n"`
  and `PAIRS = {"blurb-header": ("header", "questions"), "blurb-decider": ("decider_chat", "context")}`:
  - `test_blurb_layout_differs_only_by_the_prefix` (parametrized over PAIRS): `asdict` of both layouts, minus `name`
    and `sha256`, are equal except the first part's field, where `blurb[field] == BLURB + served[field]`; and
    `blurb.order[0] == field`.
  - `test_blurb_rows_match_served_after_the_blurb` (parametrized over PAIRS × `qwen_tok`, `gemma_tok`): build one
    batch for each layout the way `tests/unit/test_prompts.py`'s `batch_for` does (same state and questions); for
    every row, `tok.decode(blurb_row.ids) == tok.decode(served_row.ids).replace(first, BLURB + first, 1)` where
    `first` is the served first part's text before its first placeholder (`"Questions that will be asked"` /
    `"Context:"`).
  - `test_blurb_rows_share_the_prefix` (qwen_tok, front padding as `profiles/qwen3.8-27b.env` sets it): all rows
    share `ids[:shared_len]`, and the decoded shared prefix contains `BLURB.strip()`.
  - `test_blurb_decider_image_context` (gemma_tok): `image_context` on `blurb-decider` with one image item builds,
    and the decoded ids start with `BLURB.strip()` then `Context:`.

- [ ] **Step 2: Run** `uv run pytest tests/unit/test_blurb_layouts.py -v`. Expected: FAIL (files missing).

- [ ] **Step 3: Create the two tomls.** Copy `prompts/header.toml` / `prompts/decider_chat.toml` byte for byte
  except the first comment line (`# Experiment (never loaded by the gateway): <served> with an intro blurb.`) and the
  first part, which becomes the blurb plus the served text:
  `questions = "You will be asked … option.\n\nQuestions that will be asked about the context:\n{questions}\n\n"` and
  `context = "You will be asked … option.\n\nContext:\n{state}"`.

- [ ] **Step 4: Run** the test file, then `uv run pytest -q` (served goldens must not move). Expected: PASS.

- [ ] **Step 5: Commit** `prompts/experiments/blurb-header.toml prompts/experiments/blurb-decider.toml tests/unit/test_blurb_layouts.py`
  — `feat(prompts): blurb experiment layouts`.

### Task 2: Order grid on any layout and on collect files

**Files:**
- Modify: `scripts/r3_orders.py`, `scripts/vision_orders.py`
- Test: `tests/unit/test_r3_orders.py`, `tests/unit/test_vision_orders.py`

**Interfaces:**
- Consumes: `scripts.evaluate.collect_stamp(recs, layout) -> dict | None`; `scripts.splits.rows_for(name)`;
  `scripts.order_policies.IDENTITY`, `fit_types`.
- Produces:
  - `r3_orders.items(recs, rows, layout: Layout) -> dict[tuple[str, str], Item]` — skips records whose id is not in `rows`.
  - `r3_orders.identity_T(calib_items: dict) -> dict[str, float]` — the identity policy's mean-prob fit per type.
  - `r3_orders.report(calib, splits, gate_T: dict[str, float] | None, policies=POLICIES, pmap=map, layout: Layout | None = None) -> dict`
    — `layout` defaults to served `header`; `gate_T=None` gates at `identity_T` of calib; the report's `gate_T` holds what was used.
  - `r3_orders.run(profile, layout="header", pmap=map)` (stage 1: shipped calibration of that layout, splits index-dev and eval).
  - `r3_orders.run_files(profile, layout: Layout, calib: Path, dev: Path, pmap=map)` (rows of `calib-600` and
    `index-dev-2k`; one scored split named `index-dev-2k`; gates at the arm's own identity T).
  - CLI: `--layout NAME` (served, default `header`) or `--layout-file PATH`; `--calib PATH --dev PATH` (together;
    `--layout-file` needs them). Output dir: unchanged name with no new flag; `<UTC>-r4-orders-text-<layout>-<profile>`
    with `--layout` only; `<UTC>-r4-orders-text-<layout>-2k-<profile>` in file mode.
  - `vision_orders.py --out-label LABEL` (default `r3-orders-<profile>`, today's name).

- [ ] **Step 1: Write the failing tests** in `tests/unit/test_r3_orders.py`. Update the `run` fixture to call
  `report(calib, splits, SHIPPED.T, policies)`; existing tests must still pass unchanged otherwise. Add:
  - `test_report_on_another_layout`: a fixture collect whose `decider_chat` records hold the reads (the `header`
    records a different, fixed answer); `report(..., layout=load_layouts()["decider_chat"])` identity accuracy
    equals `evaluate(recs, rows, Arm("decider_chat", "identity", Calibration(T)))["overall"]["accuracy"]`.
  - `test_own_gate_is_the_identity_fit`: `report(calib, splits, None, policies)["gate_T"] == identity_T(items(*calib, header))`.
  - `test_files_mode_keeps_manifest_rows_only`: `items(recs, rows, header)` with 30 records and `rows` holding 10 of
    their ids returns questions of those 10 ids only (no KeyError).
  - `test_files_mode_refuses_mixed_stamps`: `run_files` with a calib file stamped `{"model": "a"}` and a dev file
    stamped `{"model": "b"}` raises SystemExit (monkeypatch `rows_for` to the fixture rows).
  - `test_out_names`: `main(["--profile", "p", "--layout", "decider_chat"])` with `run` monkeypatched writes under a
    dir ending `-r4-orders-text-decider_chat-p`; with `--calib/--dev/--layout-file …blurb-header.toml` ending
    `-r4-orders-text-blurb-header-2k-p`; with no flag ending `-r3-orders-text-p` (monkeypatch `ROOT`).
  In `tests/unit/test_vision_orders.py`, add `test_out_label`: `--out-label r4-orders-decider_chat-p` makes the
  results dir end with that label.

- [ ] **Step 2: Run** `uv run pytest tests/unit/test_r3_orders.py tests/unit/test_vision_orders.py -v`. Expected: the new tests FAIL.

- [ ] **Step 3: Implement** the Produces list. `LAYOUT` stays as the default name. `run_files` checks
  `collect_stamp(calib_recs, layout.name) == collect_stamp(dev_recs, layout.name)` (SystemExit naming both paths
  otherwise) and records both paths, the row manifests and `gates: own identity T on calib-600` in meta. Update the
  module docstring's usage lines.

- [ ] **Step 4: Run** the two test files, `uv run pytest -q`, `uv run ruff check .`. Expected: PASS.

- [ ] **Step 5: Commit** `scripts/r3_orders.py scripts/vision_orders.py tests/unit/test_r3_orders.py tests/unit/test_vision_orders.py`
  — `feat(orders): grid on any layout and collect files`.

### Task 3: Pair screen for any two arms

**Files:**
- Modify: `scripts/label_screen.py`, `scripts/label_screen_report.py`
- Create: `scripts/layout_screen.py`
- Test: `tests/unit/test_label_screen.py`, `tests/unit/test_layout_screen.py`

**Interfaces:**
- Produces in `label_screen.py` (defaults keep round 3's behaviour):
  - `subsets(base, other, pure: bool = True)` — `pure=False` returns `{"all": keys}` only.
  - `text_report(calib, dev, pmap=map, base: str = BASE, pure: bool = True)` and
    `image_report(fits, dev, out, base: str = BASE, pure: bool = True)`; `compare(dirs, label, out, base: str = BASE)`.
    The paired key in both reports is renamed `vs_letters` → `vs_base`; `fallback_share` is left out when `pure=False`.
  - `label_screen_report.head` titles `"# {profile} {meta.get('title', 'R3 label screen')}: {set} vs {control}, {what}"`
    (`control` defaults to `letters`), and prints the subsets note and the fallback table only when the report has
    a `pure` subset.
- Produces in `scripts/layout_screen.py`:
  - `Arm(text: str, image: str, layout: str)` (frozen dataclass): text label (`<split>-<text>.jsonl.gz`), image label
    (`VISION/<profile>/<image>/dev.jsonl.gz`), and the layout name the records carry.
  - `ARMS = {"letters": Arm("letters", "labels-letters", "labels-letters"), "decider": Arm("decider", "r4-decider", "decider_chat"),
    "blurb-header": Arm("blurb-header", "r4-blurb-header", "blurb-header"), "blurb-decider": Arm("blurb-decider", "r4-blurb-decider", "blurb-decider")}`
  - `layout_of(name: str) -> Layout` — served layout if `name` is one, else `prompts/experiments/<name>.toml`.
  - `pair(profile: str, arm: str, control: str, pmap=map) -> tuple[Path, Path]` — text and image results dirs,
    both named `<UTC>-r4-pair-<arm>-vs-<control>-<profile>` (under `label_screen.ARCHIVE` and `IMAGE_OUT`).
  - CLI: `uv run python scripts/layout_screen.py --profile P --arm A --control C` (choices: `ARMS`).

- [ ] **Step 1: Write the failing tests.** In `tests/unit/test_label_screen.py`, update assertions on `vs_letters`
  to `vs_base` (no other change). New `tests/unit/test_layout_screen.py`, reusing that file's `write`, `text_rec`,
  `image_rec` helpers (import them from `tests.unit.test_label_screen`) and monkeypatching `TEXT`, `VISION`,
  `ARCHIVE`, `IMAGE_OUT` and `rows_for`:
  - `test_pair_reads_each_arms_layout`: collect files for `blurb-header` and `letters` that also hold records of
    other layouts with a different answer; the report's per-arm accuracy matches only the arm's own layout records.
  - `test_pair_has_no_pure_subset`: `report["subsets"].keys() == {"all"}` in text and image reports, and no `fallback_share`.
  - `test_pair_pairs_shared_rows_only`: the arm misses 3 of the control's index-dev-2k rows; `subsets.all.n` is the shared count.
  - `test_pair_refuses_mismatched_image_configs`: image configs differing in `env` raise SystemExit; differing in
    `label`, `layout`, `layout_file` or `commit` do not.
  - `test_pair_names_dirs`: both dirs end `-r4-pair-blurb-header-vs-letters-p`, and `summary.md` starts with
    `# p R4 pair screen: blurb-header vs letters, ` (meta `title` is `R4 pair screen`).

- [ ] **Step 2: Run** `uv run pytest tests/unit/test_label_screen.py tests/unit/test_layout_screen.py -v`. Expected: new tests FAIL.

- [ ] **Step 3: Implement.** In `pair`: per arm, load both text splits with `label_screen.load(path, ARMS[a].layout)`,
  `same_stamp` across the two splits, `text_items` with `layout_of(...)` and `rows_for(split)`; image collects via
  `split_config` (dev only) and `load`; refuse unless both image configs agree on `profile`, `split`, `env`. Key all
  dicts by arm name, control first. Meta: `set` = arm, `control`, collect paths, fits note as round 3's. Write
  `summary.{json,md}` to both dirs like `label_screen.screen` does.

- [ ] **Step 4: Run** both test files, `uv run pytest -q`, `uv run ruff check .`. Expected: PASS.

- [ ] **Step 5: Commit** `scripts/label_screen.py scripts/label_screen_report.py scripts/layout_screen.py tests/unit/test_label_screen.py tests/unit/test_layout_screen.py`
  — `feat(screen): pair any two collected arms`.

### Task 4: Stage 1 — decider_chat text grid (CPU)

**Files:**
- Create: `docs/results/archive/<UTC>-r4-orders-text-decider_chat-{gemma-4-31b,qwen3.8-27b}/summary.{md,json}`

- [ ] **Step 1: Ticket.** Create one DoStuff ticket (type `Spike`, title `Round 4: decider_chat orders, intro blurb`,
  description from the spec's Goal) and move it to `Working`.

- [ ] **Step 2: Run** for each profile: `uv run python scripts/r3_orders.py --profile P --layout decider_chat`.
  Expected: a results dir per profile; meta names `data/P/decider_chat/calibration.json` as the gate source. A stale
  stamp refusal stops the task: report it, don't refit.

- [ ] **Step 3: Check** each summary has every policy of round 3's header summary
  (`docs/results/archive/*-r3-orders-text-P/summary.json`) and, per split, a question count within 1% of that
  summary's (same rows, other layout; a few rows can be unsupported on one layout only).

- [ ] **Step 4: Commit** both results dirs — `docs(results): r4 decider_chat text orders`. Ticket progress note with the sha.

### Task 5: Stage 2 runner (no GPU yet)

**Files:**
- Create: `<scratchpad>/r4-stage2.sh` (not committed; modeled on round 3's `r3-gpu.sh`)

- [ ] **Step 1: Write the runner.** Per profile (gemma-4-31b, then qwen3.8-27b): log the power limit, `make up PROFILE=P`, then:
  1. D text: `collect.py --profile P --split {calib-600,index-dev-2k} --layouts decider_chat --orders identity+reversed --label decider`;
  2. D image: `vision_collect.py --profile P --layout decider_chat --label r4-decider`, then `--orders cyclic:4 --label r4-decider-cyclic4`;
  3. cool; HB: text both splits with `--layout-file prompts/experiments/blurb-header.toml --orders identity+reversed --label blurb-header`, image `--layout-file … --label r4-blurb-header`;
  4. cool; DB: the same with `blurb-decider` / `r4-blurb-decider`;
  5. `make down`; cool before the next profile.
  `set -uo pipefail`, `.env` sourced, log `== <step> <date -Is>` lines to `.cache/r4/stage2.log`, stop the profile
  on a failed collect. Run it with `setsid` so it can be killed by pgid.

- [ ] **Step 2: Dry check.** `bash -n` the runner; confirm the H collects exist for both profiles:
  `.cache/collect/P/{calib-600,index-dev-2k}-letters.jsonl.gz` and `.cache/vision-collect/P/labels-letters/dev.jsonl.gz`.

### Task 6: Stage 2 — run and screen (GPU, ~5 h)

- [ ] **Step 1: STOP for the owner's ok** to start the ~5 h stage 2 GPU run. State the runner path and the power limit.
- [ ] **Step 2: Run** the runner in the background; check the log at each phase change; never `pkill -f`.
- [ ] **Step 3: Pairs (CPU)**, per profile: `layout_screen.py --profile P` with `--arm blurb-header --control letters`,
  `--arm blurb-decider --control decider`, `--arm decider --control letters`, `--arm blurb-decider --control blurb-header`.
- [ ] **Step 4: Image grid on D**, per profile: `vision_orders.py --profile P --collect .cache/vision-collect/P/r4-decider/dev.jsonl.gz --collect .cache/vision-collect/P/r4-decider-cyclic4/dev.jsonl.gz --text-fit <Task 4 summary.json> --out .cache/r4/arms/orders-decider_chat-P --out-label r4-orders-decider_chat-P`.
- [ ] **Step 5: Commit** the 8 pair dirs (text and image) and 2 image grid dirs — `docs(results): r4 screens, decider image orders`. Ticket progress note.
- [ ] **Step 6: Survivors.** For HB (vs letters) and DB (vs decider), per profile: drop the arm if text index-dev-2k
  Δ accuracy or image Δ index has a 95% CI entirely below 0. Write the table of survivors.

### Task 7: Stage 3 — order grid on survivors (GPU, up to ~5.5 h)

- [ ] **Step 1: STOP for the owner's ok**, showing the survivors table and the GPU estimate (~80 min per arm per
  profile plus cool-downs). The owner may add or drop arms.
- [ ] **Step 2: Runner** `<scratchpad>/r4-stage3.sh`, same shape as Task 5, per surviving arm A and profile:
  `collect.py --split {calib-600,index-dev-2k} --layout-file prompts/experiments/A.toml --orders all --label A-all`;
  `vision_collect.py --layout-file … --orders cyclic:4 --label r4-A-cyclic4`. Cool between arms. Run it, as Task 6 step 2.
- [ ] **Step 3: Text grids (CPU)**, per profile with a survivor:
  - the arm: `r3_orders.py --profile P --layout-file prompts/experiments/A.toml --calib .cache/collect/P/calib-600-A-all.jsonl.gz --dev .cache/collect/P/index-dev-2k-A-all.jsonl.gz`;
  - the like-for-like controls: `--layout header` and `--layout decider_chat`, each with `--calib .cache/collect/P/calib.jsonl.gz --dev .cache/collect/P/index-dev.jsonl.gz`.
- [ ] **Step 4: Image grid**, per arm: `vision_orders.py` with `r4-A` and `r4-A-cyclic4` collects, `--text-fit` the arm's step 3 summary, `--out-label r4-orders-A-P`.
- [ ] **Step 5: Commit** the results dirs — `docs(results): r4 blurb order grids`. Ticket progress note.

### Task 8: Docs

**Files:**
- Modify: `docs/background/prompt-layouts.md`, `docs/background/option-ordering.md`, `docs/development.md`

- [ ] **Step 1: `prompt-layouts.md`:** a "Blurb (round 4)" section: wording, placement, prefix cost, the four pair
  tables (text Δ accuracy, ΔECE; image Δ index) per profile, linking the results dirs; the `decider_chat` image
  numbers beside `header`'s. Replace the stale "Only qwen3.6 is calibrated" bullet with which layouts have
  calibration files for each profile (`data/<profile>/<layout>/`).
- [ ] **Step 2: `option-ordering.md`:** a round 4 section: the `decider_chat` text grid beside round 3's `header`
  headline rows, the `decider_chat` image grid, and (if run) each blurb grid against its like-for-like control.
  Carry the uncorrected-intervals caveat with arm counts.
- [ ] **Step 3: `development.md`:** one line each for `layout_screen.py` and the new `r3_orders.py` flags.
- [ ] **Step 4: Commit** the three docs — `docs: round 4 layouts, blurb, orders`. Ticket to `Verification`, then
  `request_ticket_complete`.
