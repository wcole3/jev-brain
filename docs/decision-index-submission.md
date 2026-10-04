# Submitting to the Decision Index

Status **2026-10-04**: research done, nothing submitted. Revisit after the local JevBench and
bench sweep. Raw scrapes of the board and methodology pages are in `.firecrawl/decision-index-submit/`
(git-ignored).

## Short answer

- **Feasible.** Our three final 0.2.1 runs are complete:
  - all 150,317 rows;
  - stock runner at kit `87d4650`, which is still upstream HEAD;
  - suite hashes match;
  - one RTX PRO 6000, the board's card.
- **Not ready.** Nothing is packaged or published yet. The serving code is private and has no
  licence, and the disclosures are unwritten.
- **Timing.** Intake has been paused since 2026-09-28 for edition 0.3, which adds private held-out
  benchmarks. On 2026-10-03 the maintainer said 0.2.1 runs will be folded into 0.3. About 35
  submission PRs are waiting.
- **Start with qwen3.6.** Its layout choice is the cleanest (see [Selection risk](#selection-risk)).

| Profile | Run | Index | ECE | Single-client latency (median / p95) |
|---|---|---|---|---|
| qwen3.6-27b, header | [2026-10-03T140831Z-vast](results/qwen3.6-27b/2026-10-03T140831Z-vast-index/summary.md) | 55.92 | 0.042 | 95.7 / 583 ms |
| qwen3.8-27b, header | [2026-10-04T022907Z-vast](results/qwen3.8-27b/2026-10-04T022907Z-vast-index/summary.md) | 56.01 | 0.023 | 94.2 / 580 ms |
| gemma-4-31b, header | [2026-10-04T013002Z-vast](results/gemma-4-31b/2026-10-04T013002Z-vast-index/summary.md) | 60.61 | 0.122 | 105.7 / 615 ms |

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
   | <name> (`<hf repo>` @ `<rev8>`, bf16) | **NN.NN** | [full run and scores](<dataset URL pinned to a commit>/runs/<name>/scores.json) | kit `http` engine, kit `87d4650` (edition 0.2.1); server <repo> `<commit>` | 1 x NVIDIA RTX PRO 6000 Blackwell; N runner processes against one server | Context N tokens; up to 255 options. Nothing truncated, no options removed. X of 150,317 `ok`; Y `unsupported` (...). |
   ```

4. **The maintainer checks it:**
   - he re-scores our files;
   - he measures latency himself on one RTX PRO 6000, one request at a time; the median must be
     ≤ 1,000 ms;
   - he reruns a sample and compares answers.

   If it passes, he adds the entry to the board (the HF Space) and closes the PR. No PR has ever
   been merged.

**Files in `runs/<name>/`:**
- `results.jsonl.gz`
- `scores.json`, `index.json`, `benchmark-summary.json`
- each runner's `environment.json` and `status.json` (we ran 4 shards)

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

## What we have and what's missing

| Requirement | Status | Where / what to do |
|---|---|---|
| Complete, untouched run | have | `.cache/index-runs/<p>/<run>/merged/`. `runner_sha256` matches stock. Rows are a last-attempt merge of 4 shards by `run_id` (precedent #7; say so in the PR). |
| `results.jsonl.gz` | gzip only | `merged/results.jsonl` is compact (185 MB). |
| `scores.json`, `index.json`, `benchmark-summary.json` | have | `merged/` |
| `environment.json`, `status.json` | partial | Per shard only, in `shard-*/`. Upload all four. |
| HF dataset with a pinned link | missing | Token is in `secrets/.hf-token`. No dataset yet. |
| Public serving code, pinned commit, licence | missing | `wcole3/jev-brain` is private with no LICENSE. The maintainer must run it for latency, validation and 0.3. Without this, the entry can't be checked. |
| Exact serve commands for one RTX PRO 6000 | partial | Pieces are in the README, `compose.yaml` and `profiles/*.env`. Write one self-contained block. Keep vLLM port 8000 unpublished. |
| Latency ≤ 1,000 ms | have | latency-v1 replica, table above. Don't quote the 329–365 ms in `scores.json`: that ran with 4 shards concurrent. |
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
2. Gzip `merged/results.jsonl`.
3. Re-score the gz with the pinned harness (`score --edition 0.2.1`) and confirm `scores.json` is
   identical. CPU only.
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
10. Watch the PR and the Space. When 0.3 ships, check whether it needs a rerun or rescore.
