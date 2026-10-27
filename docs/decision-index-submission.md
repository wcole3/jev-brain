# Submitting to the Decision Index

Status **2026-10-27**: the next candidate is gemma-4-31b-fp8 under the current default (`blurb_header_reread`,
`top_p:0.9+reversed`, choice T(n), vLLM 0.32, 65,536-token decision cap), run on one rented RTX PRO 6000:
- public text Index [63.64, ECE 0.079](results/gemma-4-31b-fp8/2026-10-26T153317Z-vast-index/summary.md), 140,178 of
  140,178 rows `ok` (none unsupported);
- public Vision Index [74.41](results/gemma-4-31b-fp8/2026-10-27T035039Z-vision/summary.md), 12,210 of 12,210 `ok`;
- latency-v1 on our workstation at 600 W
  [116.0 / 297.2 / 390.5 ms](results/archive/gemma-4-31b-fp8/2026-10-26T012140Z-latency/summary.md) (median / mean / p80).

`scripts/hub_export.py` builds the `runs/<name>/` folder for either board and runs the checks of
[Results file](#results-file-one-line-per-suite-row). The status below and the rest of the page are older.

Status **2026-10-20**: gemma-4-31b was submitted (PR #193, public 0.3 index 61.69) and is on the 0.4
board. The board's note says our results file had extra lines and duplicate questions; the next
submission ships a clean file (see [Results file](#results-file-one-line-per-suite-row)). The rest of
this page is the 2026-10-14 preparation, tracked in DS-030 (after DS-005 Stage 2 and DS-028). Raw scrapes
are in `.firecrawl/decision-index-submit/` (0.2.1), `.firecrawl/jdi/` (0.3) and
`.firecrawl/jdi-pr-recon/` (all PRs, board JSON, 2026-10-14), all git-ignored.

## Short answer

- **Feasible.** Our three final runs are complete on edition 0.3:
  - all 140,178 rows (the 0.2.1 runs plus the 2,638 rebuilt GSM8K rows, run under each run's
    own settings; [rescore](results/index-0.3-rescore.md));
  - stock runner at kit `9eb2dbe` (edition 0.3);
  - suite hashes match;
  - one RTX PRO 6000, the board's card.
- **Not ready.** Nothing is packaged or published yet. The serving code is private and has no
  licence, and the disclosures are unwritten.
- **Edition 0.3 is live (2026-10-06).** The Full score is 20% public, 50% private tests of the
  same skills, 30% private new-domain tasks. The maintainers run the private parts on submitted
  models, so they must be able to start our server. Stock-Qwen entries lose 8-17 points on the
  new-domain part, Gemma ones about 7 (DS-030).
- **Start with qwen3.6.** Its layout choice is the cleanest (see [Selection risk](#selection-risk)).

| Profile | Run | Index | ECE | Single-client latency (median / p95) |
|---|---|---|---|---|
| qwen3.6-27b, header | [2026-10-03T140831Z-vast, 0.3](results/qwen3.6-27b/2026-10-09T164331Z-rescore-0.3-index/summary.md) | 56.51 | 0.047 | 95.7 / 583 ms |
| qwen3.8-27b, header | [2026-10-04T022907Z-vast, 0.3](results/qwen3.8-27b/2026-10-09T164331Z-rescore-0.3-index/summary.md) | 56.60 | 0.024 | 94.2 / 580 ms |
| gemma-4-31b, header | [2026-10-04T013002Z-vast, 0.3](results/gemma-4-31b/2026-10-09T164331Z-rescore-0.3-index/summary.md) | 61.60 | 0.119 | 105.7 / 615 ms |

Index is the 0.3 public index (0.2.1: 55.92 / 56.01 / 60.61).

## How submission works

1. **Run the full suite** with the kit's stock runner. For a `/v1/systemone` server that is the
   `http` engine. `scores.json` must say `"complete": true`.
2. **Upload** the run as `runs/<name>/` to a Hugging Face dataset. It can be public if rows are
   compact (no payload text); otherwise make it gated.
3. **Open a PR** to `apolinario/decision-index` that adds one row to `submissions/README.md` and
   creates the file if missing. Use this template:

   ```
   | Model | Decision Index | Results | Engine and exact code | Hardware | Declared capacity limits |
   |---|---:|---|---|---|---|
   | <name> (`<hf repo>` @ `<rev8>`, bf16) | **NN.NN** | [full run and scores](<dataset URL pinned to a commit>/runs/<name>/scores.json) | kit `http` engine, kit `9eb2dbe` (edition 0.3); server <repo> `<commit>` | 1 x NVIDIA RTX PRO 6000 Blackwell; N runner processes against one server | Context N tokens; up to 255 options. Nothing truncated, no options removed. X of 140,178 `ok`; Y `unsupported` (...). |
   ```

4. **The maintainer checks it:**
   - he re-scores our files;
   - he measures latency himself on one RTX PRO 6000, one request at a time; the median, mean
     and 80th percentile must each be ≤ 1,000 ms;
   - he reruns a private held-out sample and compares answers;
   - he runs the two private parts of the Full score himself.

   If it passes, he adds the entry to the board (the HF Space) and closes the PR. No PR has ever
   been merged.

**Files in `runs/<name>/`:**
- `results.jsonl.gz`
- `scores.json`, `index.json`, `benchmark-summary.json`
- each runner's `environment.json` and `status.json` (we ran 4 shards)

### Results file: one line per suite row

Rule since 2026-10-20: `results.jsonl.gz` holds exactly one line per 0.3 suite row, 140,178 lines,
each the last attempt for its `run_id`. No retries, no rows outside the suite.

- **Why.** PR #193's file was the 0.2.1 run with later reruns appended: 152,966 lines, 12,777 of
  them retired rows (10,139 ForecastBench, 2,638 old GSM8K) and 11 `run_id`s twice (BRIGHT and
  ToolRet, `unsupported` at the 32k cap, then `ok` at 65k). The scorer keeps the last line per
  `run_id` and skips non-suite rows, so the score was right (rescore 61.69 = claim). But the board
  entry says "extra lines and duplicate questions with differing answers".
- **How.** Start from `merged/results.jsonl` (`evaluate.py index` writes it as a last-attempt merge
  of the shards, one line per `run_id`). Keep only `run_id`s in the suite export
  (`.cache/decision-index/rows-0.3.jsonl.gz`, field `_evaluation.run_id`), then gzip.
- **Tool.** `uv run python scripts/hub_export.py text RUN_DIR --name NAME --out OUT` (or `vision`) does the
  filtering and the checks below; any failed check writes no folder.
- **Check before upload.**
  - Lines = unique `run_id`s = 140,178.
  - Every `run_id` is in the suite export.
  - The pinned harness rescores the gz to the same `scores.json`.
- **Run card.** Describe a resume or rerun in prose and keep each runner's `environment.json` and
  `status.json`; the attempts themselves stay out of the results file.

**Rules that apply to us:**
- one fixed prompt rendering for every benchmark;
- no truncation (refuse with `Unsupported` instead);
- no option filtering;
- no labels in the adapter;
- no correctness-based retries;
- open weights only, no thinking or generation modes.

**Lessons from the example PRs:**
- **#5, Decider chat on the same Qwen3.6 and Gemma checkpoints.** This is our closest analogue.
  - It stated "No suite row was used for fitting or for choosing a configuration".
  - Its concurrent-runner latency in `scores.json` caused confusion.
  - The maintainer said he can't act on AI-written requests, so the PR text must be short and
    hand-written.
- **#7.** One model was held back because the answer-comparison check found disagreement.
- **#16.** It was rejected because the uploaded files didn't reproduce the claimed score.
- **#15 and the board's pplx-decider entry.** Both stay listed with declared use of suite rows for
  selection.
- **#21.** It led to the pause for 0.3. Selection on public rows is now read sceptically.

## What the PRs show (2026-10-14)

167 PRs to date (#2-#187). The README's submission steps are unchanged since 0.3. The only addition is a
Vision board: mark the PR **vision** for it. Our server takes no images, so we enter the text board
only. Kit HEAD is `f5a6e4f`; the commits after `9eb2dbe` touch vision and SGD (out of the index), and
`9eb2dbe` runs were still being accepted on 2026-10-14.

**How the maintainer works now:**
- He never merges submission PRs. He closes the PR once the entry is on the board.
- Since 0.3 he closes in silent batches (2026-10-07, 10-12, 10-13, 10-14). His last PR comment
  was on 2026-10-07.
- 48 accepted 0.3 PRs: median 3.4 days from open to close, max 7.2.
- Validation shows up on the board, not in the PR. Methodology notes list:
  - run-to-run agreement per entry;
  - "lifts", where he raises author-set caps and re-answers refused rows;
  - contamination checks that rebuild declared training data;
  - a shuffle test.

**Closed but never on the board (no reason posted):**

| PR | Entry | Visible difference |
|---|---|---|
| #118 | Bespoke-Nimble-27B-v3, 65.33 | Hosted API only, weights not released |
| #111 | BRREV-27B / 9B | Run on 2× H100, model parallel |
| #90, #92, #104 | KnowLine-4B Gen1-3, 60-63 | H20 only; a 4B scoring 60+; Gen4 and a 35B still open |
| #73, #79, #80, #132-#138 | Rev family | Resubmitted twice; open again as #173-#180 |
| #30 | Wald-4B v2.1, 60.05 | A 4B scoring 60; its 26B sibling (#129) was accepted |
| #101 | InferCrane Commerce-1, 61.69 | None visible |

Open since 2026-09-27: mogan-decision-31B (#21, #85). It trained on benchmark train splits and
drew public complaints.

**Closest analogues, both accepted.** Each is a stock model plus a published readout:

| Entry | PR | Public | Full | Rank | Body |
|---|---|---|---|---|---|
| MORJ 1.0.1 (stock Gemma 4 31B, own `/v1/systemone` server) | #143 | 60.24 | 60.96 | 8 | 910 chars |
| AnyJev L0 · Gemma-4-31B | #109 | 59.79 | 60.22 | 9 | 2,139 chars |
| Decider chat · Gemma-4-31B | #5 | 57.79 | 57.62 | 27 | – |
| Decider chat · Qwen3.6-27B | #5 | 51.57 | 51.25 | 47 | – |
| Jev | – | 57.96 | 60.11 | 12 | – |

Stock-Gemma entries hold their public score in the Full score. Stock-Qwen entries lose ground on new
domains (simple-jev: 56.05 public, 51.79 Full). This bears on owner decision 1.

**PR format that works (MORJ, #143):**
- **Body:** about 5 hand-written bullets:
  1. what it is (stock weights, no training, server repo @ commit);
  2. public score, `complete`, hardware, one request at a time;
  3. results link pinned to a dataset commit;
  4. how to run (`docker compose up -d` at the commit, kit commit, `http` engine, `--compact`);
  5. limits.
- **Row:** one row in a new `submissions/README.md`. Column headers vary between PRs (6 variants
  accepted), so ours is fine.
- **Long-form detail** (optional): a `submissions/<name>/README.md`, as AnyJev did.
- **Latency:** give single-process latency apart from the concurrent `scores.json` number. Say which
  card it was measured on.
- **Pins:** pin every link to a commit. A 2026-09-25 maintainer comment says he can't act on
  AI-written requests.

## What we have and what's missing

| Requirement | Status | Where / what to do |
|---|---|---|
| Complete, untouched run | have | `.cache/index-runs/<p>/<run>/merged/`. `runner_sha256` matches stock. Rows are a last-attempt merge of 4 shards by `run_id` (precedent #7; say so in the PR). |
| `results.jsonl.gz` | filter + gzip | `merged/results.jsonl` is compact (185 MB). Keep suite rows only, then gzip ([Results file](#results-file-one-line-per-suite-row)). |
| `scores.json`, `index.json`, `benchmark-summary.json` | have | `merged/` |
| `environment.json`, `status.json` | partial | Per shard only, in `shard-*/`. Upload all four. |
| HF dataset with a pinned link | missing | Token is in `secrets/.hf-token`. No dataset yet. |
| Public serving code, pinned commit, licence | missing | `wcole3/jev-brain` is private with no LICENSE. The maintainer must run it for latency, validation and 0.3. Without this, the entry can't be checked. |
| Exact serve commands for one RTX PRO 6000 | partial | Pieces are in the README, `compose.yaml` and `profiles/*.env`. Write one self-contained block. Keep vLLM port 8000 unpublished. |
| Latency ≤ 1,000 ms (median, mean, p80) | have | latency-v1 replica, table above; 2026-10-05 runs: mean 264-302 ms, p80 308-383 ms. Don't quote the 329–365 ms in `scores.json`: that ran with 4 shards concurrent. |
| Hardware | have | 1× RTX PRO 6000 Blackwell (vast), 600 W, bf16, vLLM 0.30.0, 4 kit runners against one gateway. |
| Capacity limits | have | 32,768-token decision cap, 255 labels. Unsupported rows: qwen3.6 7, qwen3.8 7, gemma 11, all ToolRet/BRIGHT over the cap. |
| Calibration disclosure | text to write | T fitted on our calib split only: JevBench gold `fcec62f` + DecisionBench `071b7b2`. Index states are kept out of calib. No training. No Jev outputs used. |
| Selection disclosure | text to write | See below. |
| Answer agreement with a single-process rerun | missing | Not measured. bf16 co-batching drift is about 0.03. Precedents report 97–100% agreement. GPU work. |
| PR row and body, entry name | missing | Owner. The name must not imply TypeSafe affiliation. |

## Selection risk

No upstream rule forbids choosing one global configuration with suite rows, and none requires
blind runs. Our layout is one fixed rendering, so the letter of the rules is met. But Decider chat
(#5) claims no suite use, so we must disclose ours, and 0.3's private benchmarks exist to catch
Index-specific gains.

- **All profiles:** layouts were compared on an 8,000-row Index sample (index-dev) plus our own
  non-Index eval split. Temperatures were fitted on non-Index data only.
- **qwen3.6, cleanest:** header passed our pre-set rule on both splits (+0.020 index-dev, +0.017
  eval accuracy) and was adopted before its final Index run.
- **qwen3.8 and gemma, weaker:** our rule said to keep decider_chat. Header won on index-dev only.
  We adopted it after comparing two full Index runs (qwen3.8 51.47 → 56.01, gemma 57.16 → 60.61),
  which is selection on the test set. The gain didn't show on our non-Index split. gemma at 60.61
  would also sit above Jev (57.89), which invites scrutiny.
- **JevBench confirms header outside the Index (2026-10-04).** We compared all 1,682 JevBench
  gold rows, paired by row, header now against the 2026-09-30 decider_chat runs, with a 95%
  bootstrap interval:

  | Profile | All rows | Choice + noul only |
  |---|---|---|
  | qwen3.6 | +4.82 pts [+3.69, +5.89] | +3.85 [+2.69, +5.02] |
  | qwen3.8 | +3.27 [+2.26, +4.34] | +3.27 [+2.11, +4.44] |
  | gemma | +1.25 [+0.36, +2.20] | +1.89 [+0.95, +2.91] |

  - **Choice + noul only** removes temperature effects, because the top answer doesn't depend on
    T at one option order with b = 0.
  - **Runs:** [qwen3.6](results/qwen3.6-27b/2026-10-04T130116Z/summary.md),
    [qwen3.8](results/qwen3.8-27b/2026-10-04T133322Z/summary.md),
    [gemma](results/gemma-4-31b/2026-10-04T140204Z/summary.md).
  - **Disclosure:** JevBench was measured after the layout was chosen, so it is a confirmation, not
    the selection rule. Also say that our DecisionBench rows (the rest of eval) did not show the
    gain for qwen3.8 and gemma.
- **Option:** submit qwen3.8 and gemma on decider_chat instead, using the earlier final runs:
  [qwen3.8 51.47](results/qwen3.8-27b/2026-10-03T133219Z-vast-index/summary.md),
  [gemma 57.16](results/gemma-4-31b/2026-10-03T133229Z-vast-index/summary.md).

Background: [M3 recommendations and Index confirmation](results/archive/m3-recommendations.md).

## Owner decisions

1. Which profile to submit first. Recommendation: qwen3.6 on header.
2. The entry name.
3. Whether to make `jev-brain` public or publish a snapshot, and under which licence.
4. The selection disclosure wording, and whether qwen3.8 and gemma go in on header or decider_chat.
5. Whether to submit now (queued, folded into 0.3) or wait for 0.3.

## To-do for one profile (qwen3.6), smallest first

1. The owner decides the items above.
2. Filter `merged/results.jsonl` to the suite rows and gzip it
   ([Results file](#results-file-one-line-per-suite-row)).
3. Run the checks there: 140,178 lines, all in the suite, and the pinned harness
   (`score --edition 0.3`) rescores the gz to an identical `scores.json`. CPU only.
4. Assemble `runs/<name>/`:
   - the result files;
   - the 4 shards' `environment.json` and `status.json`;
   - a short card: model @ revision, layout `header` + its hash, T values, vLLM 0.30.0, 4 runners,
     single-client latency.
5. Write the disclosures, about 6 hand-written sentences: calibration data, no training or Jev
   outputs, selection, capacity limits, the 4-runner merge.
6. Publish the serving code at a pinned commit with a LICENSE, plus one exact serve block. The
   kit options are `base_url` (the gateway) and `model=jev-latest`.
7. Run the agreement check: single-process rerun of the 750 latency rows or about 3,000 Index rows,
   compared row by row. Report choice agreement and max |dp|. This is GPU work and needs the
   owner's OK if it runs over 10 min.
8. Create the HF dataset, upload, and note the commit for the pinned link.
9. Fork, add the `submissions/README.md` row, and open the PR. This posts to GitHub, so it is the
   owner's action.
10. Watch the PR and the Space.
