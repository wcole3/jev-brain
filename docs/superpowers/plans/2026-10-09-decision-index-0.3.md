# Decision Index 0.3: Harness Bump, Split Recut, Rescore

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (owner chose Native for DS-005). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** move our Decision Index tooling from edition 0.2.1 to 0.3, recut our splits on it, and rescore our latest full Index run per profile, so we see how far each one moves.

**Architecture:**
- The pinned harness becomes the 0.3 merge commit. Everything else follows from the existing pins: the suite folder, the row export, the split metadata and the score edition.
- The splits are recut on the 0.3 rows (owner, 2026-10-09). That is a **gate**: if the calib or eval ids change, every committed calibration is stale and we stop for the owner.
- The existing runs stay as they are. Each gets only the 2,638 rebuilt GSM8K rows, run under that run's own settings, then the run is rescored with `--edition 0.3`.

**Tech Stack:** `apolinario/decision-index` @ `9eb2dbe2a358004c8782c66e40a83ac07b953fec` (merge of PR #74, edition 0.3), `scripts/index_suite.py`, `scripts/evaluate.py index --ids`, `scripts/index_run.py`, `scripts/splits.py`, `scripts/board.py`, `scripts/phase2_report.py`.

**Spec:** the kit README at that commit (`.firecrawl/jdi/gh-readme.md`):
- 0.3 = the 0.2.1 rows + 2,638 rebuilt GSM8K rows, which replace the old ones at read time;
- ForecastBench is retired;
- WinoGrande moves to Knowledge & Reasoning;
- 37 public benchmarks;
- Full = 0.2 public + 0.5 same skills + 0.3 new domains (private parts are maintainer-only).

Ticket: "Decision Index 0.3: harness bump, split recut, rescore runs" (DoStuff).

## Global Constraints

- **Harness pin:** `HARNESS_SHA = "9eb2dbe2a358004c8782c66e40a83ac07b953fec"`, `EDITION = "0.3"`.
- **Suite import for 0.3:** `suite import` takes `--gsm8k-rows work/artifacts/benchmark-suite/release-v3-rebuilt/gsm8k-rows.jsonl.gz` in addition to `--rows` and `--added-rows`. The suite lands in `suite-0.3`.
- **Keep 0.2.1 readable:** keep `.cache/decision-index/rows-0.2.1.jsonl.gz` and `suite-0.2/` on disk. The old runs and archive reports read them.
- **GSM8K rows for an existing run:** use that run's settings exactly. That means its commit's profile, calibration files and prompts, with MTP off and 784-token blocks for Qwen. Runs: qwen3.6 `2026-10-03T140831Z-vast` (commit `3e58290`), qwen3.8 `2026-10-04T022907Z-vast` (`8a14b18`), gemma `2026-10-04T013002Z-vast` (`0aeee17`).
- **GPU:** this box, a few minutes per profile (owner ok, 2026-10-09).
- **Never train, calibrate or tune on Jev API outputs.**
- **Commits:** caveman Conventional Commits, subject ≤ 50 chars, explicit paths only. Comments at most two lines.

## Review Focus

- **Split recut changes calib/eval ids.** Every calibration becomes stale silently: the stamps don't hash the split. Task 2 diffs the ids and stops on any change.
- **Old suite paths deleted or renamed.** That breaks the 0.2.1 archive reports and the `--edition 0.2.1` rescore. Task 1 keeps both suites, and its test pins that the 0.3 paths differ from the 0.2.1 ones.
- **GSM8K rows run under today's profile** (MTP, 800 blocks, refit T). The rescored run then mixes two configurations. In Task 3, `/health` must show the run's own T values before any row is sent.
- **Old GSM8K rows counted twice.** If the merged results keep both the old and the new GSM8K run ids, scoring must drop the old ones. Task 3 checks that `score --edition 0.3` reports 2,638 GSM8K requests, not 5,276.
- **README table compares against 0.2.1 board numbers.** Task 4 switches `scripts/board.py` to the 0.3 entries and adds the Full score.

---

### Task 1: Pin the 0.3 harness and build its suite

**Files:**
- Modify: `scripts/index_suite.py` (`HARNESS_SHA`, `EDITION`, `SUITE`, `rebuild_commands`)
- Modify: `tests/unit/test_index_suite.py`
- Modify: `docs/remote-gpu.md:296` (the box copy line names the 0.3 export and suite)

**Interfaces:**
- Produces: `index_suite.EDITION == "0.3"`, `index_suite.SUITE == WORK / "suite-0.3"`, `index_suite.EXPORT == WORK / "rows-0.3.jsonl.gz"`, and `rebuild_commands()` with the 0.3 import. Tasks 2-4 use these.

- [ ] **Step 1: Write the failing tests** in `tests/unit/test_index_suite.py`:
  ```python
  def test_pins_edition_0_3_suite_and_export():
      assert index_suite.HARNESS_SHA == "9eb2dbe2a358004c8782c66e40a83ac07b953fec"
      assert index_suite.SUITE.name == "suite-0.3"
      assert index_suite.EXPORT.name == "rows-0.3.jsonl.gz"

  def test_import_passes_rebuilt_gsm8k_rows():
      imp = index_suite.rebuild_commands()[1]
      assert imp[imp.index("--edition") + 1] == "0.3"
      assert imp[imp.index("--gsm8k-rows") + 1].endswith("release-v3-rebuilt/gsm8k-rows.jsonl.gz")
  ```
- [ ] **Step 2: Run them and confirm they fail.**
  - Run: `uv run pytest tests/unit/test_index_suite.py -q`
  - Expected: FAIL on the old sha and the missing `--gsm8k-rows`.
- [ ] **Step 3: Make them pass.**
  - Set the pins.
  - Change `SUITE = WORK / "suite-0.3"`.
  - Add `REBUILT_V3 = WORK / "work" / "artifacts" / "benchmark-suite" / "release-v3-rebuilt"`, and `"--gsm8k-rows", str(REBUILT_V3 / "gsm8k-rows.jsonl.gz")` to the import.
- [ ] **Step 4: Build the suite (CPU).** Run, in order, `uv run python scripts/index_suite.py setup`, then `rebuild`, then `export`.
  - `setup` needs `SRC` re-pointed: if `.cache/decision-index/src` exists, run `git -C .cache/decision-index/src fetch && git -C … checkout 9eb2dbe…` instead of the clone, then reinstall the venv package.
  - Expected:
    - `suite-0.3/` exists;
    - `rows-0.3.jsonl.gz` is written;
    - `zcat rows-0.3.jsonl.gz | wc -l` is the 0.2.1 count with the GSM8K rows replaced;
    - `rows-0.2.1.jsonl.gz` and `suite-0.2/` are still there.
- [ ] **Step 5: Run the checks and commit.**
  - Run: `uv run pytest -q && uv run ruff check .`
  - Commit `scripts/index_suite.py tests/unit/test_index_suite.py docs/remote-gpu.md` with the message `feat(index): pin Decision Index 0.3 harness`.

### Task 2: Recut the splits on 0.3 (gate)

**Files:**
- Modify: `data/splits/{calib,eval,index-dev,latency-v1}.json` (written by `scripts/splits.py`)

**Interfaces:**
- Consumes: Task 1's pins (`splits.pins()` reads them).
- Produces: splits whose `meta.harness` and `meta.edition` match 0.3, so `rows_for()` works again for `collect.py` (DS-005 Stage 2) and `latency.py`.

- [ ] **Step 1: Save the old ids, then recut.**
  - Copy `data/splits/*.json` to `.superpowers/sdd/<plan>/splits-0.2.1/`.
  - Run: `uv run python scripts/splits.py`
- [ ] **Step 2: Diff the ids.** For each split, compare the old and new id lists (and `warmup` + `timed` for latency-v1).
  - Expected: **calib and eval ids identical**. index-dev and latency-v1 may change where they sampled GSM8K or ForecastBench rows. Record the counts.
  - **If calib or eval ids differ: stop.** Restore the old files (`git checkout data/splits`) and report the changed ids to the owner. Every committed calibration would need recollect + refit.
- [ ] **Step 3: Run the checks.**
  - Run: `uv run pytest -q`
  - Expected: PASS. If a test pins split counts or hashes, update it to the recut values and note it in the ledger.
- [ ] **Step 4: Commit** `data/splits/*.json` (plus any test updated in Step 3) with the message `chore(splits): recut on Decision Index 0.3`. The body gives the id diff counts per split.

### Task 3: Add the 0.3 GSM8K rows to each latest run

One profile at a time, on this box. Each takes about 10 min to boot plus a few minutes of rows.

**Files (throwaway, git-ignored or deleted):**
- `profiles/idx03-<p>.env`: `git show <commit>:profiles/<p>.env`, with `PROFILE` and `SERVED_MODEL` set to `idx03-<p>`.
- `data/idx03-<p>/<layout>/{labels.json,calibration.json}`: `git show <commit>:data/<p>/<layout>/…`.

**Interfaces:**
- Consumes: `EXPORT` (`rows-0.3`) from Task 1.
- Produces: `.cache/index-runs/<p>/<run>-gsm8k03/merged/results.jsonl`, and a rescored `.cache/index-runs/<p>/<run>-0.3/` (Task 4).

- [ ] **Step 1: List the rows.** Write the 0.3 GSM8K run ids to `.cache/decision-index/gsm8k-0.3-ids.txt`. These are the run ids in `rows-0.3` that are absent from `rows-0.2.1`. Expected: 2,638 ids.
- [ ] **Step 2: Boot the run's settings.**
  - Write the throwaway profile and data files.
  - Run `docker compose --env-file profiles/idx03-<p>.env up -d`. The prompts must match the run's commit; the gateway refuses a stale layout hash.
  - Check: `/health` shows `prefix_block` 784 for Qwen (0 for Gemma), no `--speculative-config` in the vLLM args, and `calibration` T values equal to that run's `summary.md`.
- [ ] **Step 3: Run the rows.**
  - Run: `uv run python scripts/evaluate.py index --profile idx03-<p> --shards 4 --ids .cache/decision-index/gsm8k-0.3-ids.txt --run-dir .cache/index-runs/<p>/<run>-gsm8k03 --strict`
  - Expected: 2,638 rows, all ok or unsupported. Record the run time.
- [ ] **Step 4: Combine and rescore.**
  - Write `.cache/index-runs/<p>/<run>-0.3/merged/results.jsonl` with `index_run.merge([<run>/merged, <run>-gsm8k03/merged], …)`.
  - Score it with `score --edition 0.3`.
  - Expected: `scores.json` is complete, with GSM8K counted on 2,638 requests and no ForecastBench in the index.
- [ ] **Step 5: Clean up.** Stop the stack and delete `profiles/idx03-<p>.env` and `data/idx03-<p>/`.

### Task 4: Report the move and switch the board to 0.3

**Files:**
- Modify: `scripts/board.py` (0.3 entries: Full, public, same skills, new domains, for the six comparison entries in the README table)
- Modify: `scripts/phase2_report.py` and its test (Full / public columns; edition label)
- Modify: `README.md` (phase-2 table, via `phase2_report.py --readme`)
- Create: `docs/results/index-0.3-rescore.md`
- Test: `tests/unit/test_phase2_report.py`

**Board values** (from `data/v03.json` of the Space, 2026-10-09):

| entry | full | public | same skills | new domains |
|---|---|---|---|---|
| Decider chat · Qwen3.6-27B | 51.25 | 51.57 | 52.15 | 43.57 |
| Decider chat · Gemma-4-31B | 57.62 | 57.79 | 56.88 | 50.35 |
| simple-jev · Qwen3.8-27B | 51.79 | 56.05 | 55.46 | 38.56 |
| reflex Qwen3.8-27B-FP8 | 51.40 | 52.27 | 53.25 | 42.22 |
| Jevfire Qwen3.8-27B | 45.55 | 49.80 | 46.86 | 36.98 |
| Jev | 60.11 | 57.96 | 58.04 | 54.98 |

- [ ] **Step 1: Write the failing test.** `test_phase2_table_shows_0_3_public_and_full`: given one fake run scored 0.3 and the board above, the rendered table row for Decider chat · Gemma-4-31B shows public `57.79` and Full `57.62`, and our row shows Full as `—` (private parts are maintainer-only).
- [ ] **Step 2: Run it and confirm it fails. Then update `board.py` and `phase2_report.py` until it passes.**
- [ ] **Step 3: Write the rescore report.** One row per profile in `docs/results/index-0.3-rescore.md`:
  - 0.2.1 index → 0.3 public index, and the delta;
  - the GSM8K score at 0.2.1 vs 0.3;
  - the effect of retiring ForecastBench and of moving WinoGrande, per area;
  - the GSM8K rows' run time.
  
  Add 2-3 lines comparing us with the board's public column, and note that the Full score needs the maintainers' private run.
- [ ] **Step 4: Regenerate the README table.** Run `uv run python scripts/phase2_report.py --readme` and update the README's "Decision Index 0.2.1" wording to 0.3.
- [ ] **Step 5: Run the checks and commit.** Run `uv run pytest -q && uv run ruff check .`, then commit the files above with the message `docs(index): rescore our runs on 0.3`. Tick the ticket.
