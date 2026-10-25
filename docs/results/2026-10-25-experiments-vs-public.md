# Prompt and readout experiments against the public Index (gemma-4-31b, 2026-10-22 to 25)

This report covers every prompt and readout arm run on gemma-4-31b from 2026-10-22 to 2026-10-25, set against our
public Decision Index scores. No arm had a full Index run. The public numbers are estimates built from index-dev-2k
deltas on top of the latest full run. CPU-only analysis, 2026-10-25. The scripts and their raw output are in
`.firecrawl/report-2026-10-25/` (git-ignored): `arms_report.py` → `arms_report.out` / `.json`, `sens.py`,
`h1q_cost.py`.

## Short answer

- **What shipped is worth about +1.5 public points.** The default today is `blurb_header_reread`: read the shared
  block twice on one-question requests, the new joiner, the cleanups, and the 0.32 refit. Its estimated public index
  is **64.52 [63.46, 65.55]**. The latest full run scored 62.98, our board entry 61.69, FlexDM 63.63 and Aleria 63.46.
  So the estimate sits above both peers on public, but the CIs overlap.
- **No 0.32 arm beats the default on the public estimate.** Each delta is vs `reread32`; the chained estimate is in
  brackets after the arrow:
  - H1 (full read-twice): +0.32 [−0.54, +1.18] → 64.84;
  - H1q (H1 on one-question requests only): +0.18 [−0.50, +0.83] → 64.70;
  - H2 (system turn): +0.05 [−0.64, +0.78] → 64.57;
  - D1: −0.85 [−1.65, −0.05] → 63.66.
- **H1 is the only arm with a clear off-suite gain.** On eval (JevBench), choice accuracy rises +0.81 points
  [+0.31, +1.37] (16 fixes, 3 breaks), and noul is 2 fixes to 0 breaks.
  - The catch: H1 makes 12 eval requests (entity-alignment, 255 options) longer than 65,536 tokens, so they come back
    unsupported. Counted as wrong, eval accuracy falls 0.8299 → 0.8218.
  - H1q (one-question gate) gets the same eval result, because every eval request has one question. It needs a
    length fallback before it can ship.
- **Cost.** All latencies below are estimates for the served `top_p` setting, as median / mean / p80:
  - H1 breaks the board's p80 gate: about 1,085 ms vs the default's 635 ms.
  - H1q stays under 1,000 ms at about 242 / 610 / 797 ms.
- **H1q measured (2026-10-25):** latency-v1 A/B at 510 W, identity + reversed: default 178.9 / 471.2 / 637.8 ms,
  H1q 255.5 / 610.6 / 813.6 ms (passes the gate). Fitted on calib, served `top_p` on eval: choice 0.847 → 0.854,
  score 0.675 → 0.686, noul 0.916 → 0.919; NLL lower on all three; noul ECE 0.019 → 0.027.
- **Pending:** the H1q length fallback, and refits of the other 8 profiles (only gemma-4-31b has a
  `blurb_header_reread` fit).

## 1. Public anchors

| Entry | Setup | Full | Public | Same-skill | New-domain |
|---|---|---|---|---|---|
| jev-brain-gemma-4-31b (board, PR #193) | `header`, identity orders, vLLM 0.30 | 64.61 | 61.69 | 61.56 | 54.29 |
| our latest full run (2026-10-20T154258Z-vast) | `blurb_header`, `top_p:0.9+reversed`, 0.30 | — | 62.98 | — | — |
| FlexDM · Gemma-4-31B (board) | stock weights, read-twice ≤ 3,000 tokens | 67.56 | 63.63 | 62.98 | 58.52 |
| Aleria Judge 1.1.1 (board) | stock weights | 66.67 | 63.46 | 62.39 | 57.44 |
| **current default (estimate)** | `blurb_header_reread`, `top_p:0.9+reversed`, 0.32 | — | **64.52 [63.46, 65.55]** | — | — |

- **Sources:**
  - board rows: `.firecrawl/board-review-2026-10-22/index.json` (`v03` block);
  - latest run: `.cache/index-runs/gemma-4-31b/2026-10-20T154258Z-vast/merged/scores.json`;
  - other profiles' full runs: README "Scores".
- **Where the Full-score gap is:** 71% of the gap to FlexDM (2.09 of 2.95) and 75% of the gap to Aleria (1.55 of
  2.06) sit in new-domain, which no local data measures (`.firecrawl/gap-analysis/decompose.py`).

## 2. Method

- **Public estimate.** This is `.firecrawl/gap-analysis/reread_public.py`, generalized to every arm:
  - **Per-benchmark delta:** each arm's index-dev-2k accuracy delta against its same-engine control, under the
    served `top_p:0.9+reversed` policy.
  - **Shrinkage:** the delta is shrunk toward the pooled delta with k = 30, then turned into skill by dividing by
    (1 − chance).
  - **Weights:** public-index weights, skipping benchmarks clipped to 0 on the board.
  - **CI:** 1,000 request bootstraps within each benchmark.
  - **The top_p gate** softmaxes the identity read at the identity-fit T of the arm's layout. Fits used: blurb
    (2026-10-20), pre-cleanup reread (2026-10-23), the default's 0.32 refit (2026-10-24T195030Z) and H2's own fit.
    H1, H1q and D1 have no fit yet and borrow the default's.
- **Chaining.** A 0.32 arm's estimate is 62.98 + Δ(default vs `blurb_header`, on 0.30) + Δ(arm vs `reread32`, on
  0.32), with both terms bootstrapped jointly. This rests on `newjoiner-idrev` (0.30) and `reread32-idrev` (0.32)
  being token-identical (layout sha `fc835afa`). Between them they show an engine effect of +0.07 [−0.12, +0.27].
- **Paired accuracy.** Top answers from the identity and reversed reads averaged, which no T can change.
  - Brackets are 95% intervals that resample requests; fixes/breaks count questions.
  - The served `top_p` policy gives the same eval numbers in every comparison: no eval question changes answer
    between the two.
- **Sensitivity to k.** The small benchmarks swing the estimate: GPQA Diamond has 3 questions in index-dev-2k and
  BRIGHT has 2 to 4.

| k | default | H2 | H1 | H1q | D1 |
|---|---|---|---|---|---|
| 0 | 65.28 | +0.92 | +0.93 | −0.83 | −3.03 |
| 30 (used) | 64.52 | +0.05 | +0.32 | +0.18 | −0.85 |
| 100 | 64.07 | +0.05 | +0.44 | +0.22 | −0.52 |

## 3. Every arm: public estimate and verdict

| Arm | Engine | What changes | Δ public vs control [95% CI] | Est. public | Verdict |
|---|---|---|---|---|---|
| nolettername | 0.30 | "(A) A: text" → "(A) text" | +0.25 [−0.36, +0.97] vs blurb | 63.23 | shipped (owner; neutral) |
| B (`again-b`) | 0.30 | shared block twice, every request | +1.31 [+0.17, +2.51] vs blurb | 64.29 | shipped as the gated form |
| D, BD (`again-d`, `again-bd`) | 0.30 | per-row options twice (D), both (BD) | hle-focus only | — | rejected (D ≈ 0; BD = B) |
| reread (B, one-question gate, nolettername) | 0.30 | `blurb_header_reread` before cleanups | +1.20 [+0.19, +2.26] vs blurb | 64.18 | shipped |
| clean (dedupe names, drop "(A)" names) | 0.30 | Aleria cleanups 1–3 | +0.08 [−0.10, +0.30] vs reread | 64.26 | shipped |
| noindex | 0.30 | no `_index` on arrays ≥ 8 | +0.18 [−0.11, +0.44] vs reread | 64.35 | shipped |
| newjoiner (= current default) | 0.30 | cleanups + new joiner | +0.34 [−0.32, +0.94] vs reread; **+1.54 [+0.48, +2.57] vs blurb** | **64.52** | shipped |
| engine 0.30 → 0.32 | 0.32 | same tokens (`reread32`) | +0.07 [−0.12, +0.27] | 64.59 | shipped (v0.32.0) |
| H2 (`reread-system`) | 0.32 | Aleria's system turn | +0.05 [−0.64, +0.78] | 64.57 [63.43, 65.69] | rejected\* (eval −0.39, noul ECE worse) |
| H1 (`reread-h1`) | 0.32 | shared block + question + options twice, every request | +0.32 [−0.54, +1.18] | 64.84 [63.56, 66.09] | rejected\* (p80 > 1,000 ms; 2.2× tokens on multi) |
| H1q (`reread-h1q`, emulated) | 0.32 | H1 on one-question requests only | +0.18 [−0.50, +0.83] | 64.70 [63.58, 65.88] | **candidate** (fit and latency done; needs the length fallback) |
| D1 (`reread-d1`) | 0.32 | unlabelled options copy + joiner + labelled row | −0.85 [−1.65, −0.05] | 63.66 [62.47, 64.93] | rejected\* |

- **\* Verdicts marked \*** are this report's reading of the numbers; the owner decides.
- **H1q is emulated** from the H1 and `reread32` collects. On one-question requests it is token-identical to H1;
  everywhere else it is the default.
- **Which benchmarks drive the 0.32 deltas** (public points, net questions / n):
  - H1q: Humicroedit +0.15 (+3/38), RAGTruth +0.09 (+1/38), CLadder −0.12 (−3/72), VAST −0.11 (−2/43);
  - H1, beyond H1q's list: BRIGHT +0.14 (+1/2), ContractNLI +0.13 (+2/34), PhishNChips −0.20 (−2/28);
  - D1: GSM8K −0.24 (−6/36).

## 4. index-dev-2k, paired accuracy (identity + reversed averaged)

| Arm vs control | All: Δ points [CI], fixes/breaks | One-question requests (1,720) | Multi-question (2,006–2,008) | Input tokens |
|---|---|---|---|---|
| nolettername vs blurb | 0.810 → 0.810, −0.03 [−0.36, +0.28], 18/19 | +0.00 [−0.70, +0.70] | −0.05 | — |
| B vs blurb | 0.811 → 0.815, +0.48 [−0.11, +1.04], 65/47 | +0.99 [−0.06, +2.03] | +0.05 | — |
| reread vs blurb | 0.810 → 0.814, +0.32 [−0.17, +0.82], 53/41 | +0.76 [−0.35, +1.80] | −0.05 | — |
| clean vs reread | +0.03 [−0.09, +0.15], 3/2 | +0.06 | 0.00 | ×0.999 |
| noindex vs reread | +0.08 [−0.13, +0.30], 10/7 | +0.35 [−0.06, +0.76] | −0.15 | ×0.973 |
| newjoiner vs blurb | 0.810 → 0.815, +0.48 [−0.05, +1.05], 62/44 | **+1.22 [+0.06, +2.38]** | −0.15 | — |
| reread32 (0.32) vs newjoiner (0.30) | +0.03 [−0.11, +0.17], 4/3 | +0.12 | −0.05 | ×1.000 |
| H2 vs reread32 | 0.815 → 0.816, +0.08 [−0.29, +0.48], 27/24 | +0.12 [−0.58, +0.76] | +0.05 | ×1.027 |
| H1 vs reread32 | 0.816 → 0.820, +0.40 [−0.05, +0.87], 45/30 | +0.35 [−0.47, +1.10] | +0.45 [−0.08, +1.02] | ×1.693 |
| H1q vs reread32 | 0.815 → 0.817, +0.16 [−0.19, +0.54], 27/21 | +0.35 [−0.47, +1.10] | 0 (same tokens) | ×1.331 |
| D1 vs reread32 | 0.815 → 0.814, −0.19 [−0.65, +0.27], 41/48 | −0.64 [−1.57, +0.29] | +0.20 | ×1.497 |

- **Input tokens** count the shared prefix once, from the collect records; "—" means the control collected all
  orders, so the counts don't compare.
- **The served `top_p` policy** moves each row by 0.05 points or less (`arms_report.out`).
- **H1's gain sits in multi-question requests** (+0.45, 18/9), which are the requests H1q leaves out. FlexDM also
  reads only short requests twice.

## 5. Off-suite eval (JevBench, 2,839 one-question requests)

| Arm vs control | All | Choice (1,607–1,619) | Score (554) | Noul (666) | Tokens |
|---|---|---|---|---|---|
| reread vs blurb (0.30) | +0.11 [−0.60, +0.85], 55/52 | +0.74 [−0.25, +1.79], 41/29 | −1.08 [−2.53, +0.36] | −0.45 [−1.80, +0.75] | ×1.312 |
| reread32 (0.32, cleanups + joiner) vs reread (0.30) | −0.25 [−0.63, +0.14], 13/20 | −0.25 | −0.36 | −0.15 | ×0.980 |
| H2 vs reread32 | −0.39 [−0.92, +0.11], 23/34 | +0.06 [−0.49, +0.68] | −1.26 [−2.89, +0.18] | −0.75 [−1.80, +0.30] | ×1.017 |
| **H1 = H1q vs reread32** | **+0.74 [+0.28, +1.20], 32/11** | **+0.81 [+0.31, +1.37], 16/3** | +1.08 [−0.54, +2.71], 14/8 | +0.30 [+0.00, +0.75], 2/0 | ×1.477 |
| D1 vs reread32 | −0.18 [−0.85, +0.46], 45/50 | −0.12 [−1.00, +0.62] | +0.36 [−1.99, +2.35] | −0.75 [−1.95, +0.30] | ×1.457 |
| gemma-4-12b reread vs blurb | +1.30 [+0.35, +2.22] | +1.17 [+0.06, +2.22] | +1.99 | +1.05 | — |
| qwen3.6-27b reread vs blurb | +0.78 [−0.04, +1.59] | +1.99 [+0.87, +3.11] | −1.26 | −0.45 | — |
| qwen3.8-27b reread vs blurb | +1.77 [+0.92, +2.65] | +2.24 [+1.12, +3.36] | +1.62 | +0.75 | — |

- **H1 and D1 leave out 12 requests.** Those are entity-alignment requests whose rows grow from about 39k to about
  78k tokens, past `systemone_max_len` (65,536), so they come back unsupported. The H1 and D1 rows above are paired
  on the remaining 2,827.
  - The control gets all 12 right, so counting them as wrong drops H1 from 0.8299 to 0.8218 (−0.81).
  - H1q inherits this.
  - On index-dev-2k (cut at 32,768 tokens), H1 lost 1 request (BRIGHT, 42,933 tokens).
- **Calibration fits on eval at top_p**, as accuracy / ECE after T:

| Fit | Choice | Score | Noul |
|---|---|---|---|
| reread (0.30) | 0.850 / 0.076 | 0.679 / — | 0.917 / 0.021 |
| reread32 (0.32) | 0.847 / 0.078 | 0.675 / 0.196 | 0.916 / 0.019 |
| H2 | 0.848 / 0.077 | 0.662 / 0.183 | 0.908 / 0.034 |

  - H2's noul T moves 7.15 → 7.90. Sources: `docs/results/archive/gemma-4-31b/2026-10-24T195122Z-calibrate/`,
    `.firecrawl/gpu-runs/h2-calibrate/2026-10-24T195348Z-calibrate/`.
  - H1/H1q has no fit yet.

## 6. HLE (hle-focus, vLLM 0.30, identity + reversed averaged)

| Arm vs control | HLE (501) | non-HLE (786) | All (1,287) |
|---|---|---|---|
| nolettername vs blurb | 0.140 → 0.144 (+0.40), 14/12 | −0.13 | +0.08 [−0.79, +0.96] |
| B vs blurb | 0.140 → 0.152 (+1.20 [−0.60, +2.99]), 14/8 | +0.89 | **+1.01 [+0.08, +2.09]** |
| D vs blurb | +0.40, 16/14 | +0.25 | +0.31 [−0.72, +1.31] |
| BD vs blurb | +1.40 [−1.00, +3.79], 21/14 | +0.76 | +1.01 [−0.19, +2.32] |
| reread vs blurb | 0.140 → 0.154 (+1.40), 21/14 | +0.00 | +0.54 [−0.47, +1.61] |
| clean / noindex / newjoiner vs reread | +0.20 / −0.40 / −0.20 | 0 / +0.13 / 0 | +0.08 / −0.08 / −0.08 |

- **HLE scores below chance (0.165) in every arm.**
- **The 0.32 arms have no HLE measurement:** index-dev-2k holds 7 HLE questions.
- **The pointwise readouts carry no usable signal.** These score each option alone, P(yes) to "is this answer
  correct", on the 501 HLE rows (`.firecrawl/hle-research/gpu-session/pw_{pt,p0,pmi}.jsonl`). Against the served
  letter readout's 15.0%:
  - P-T reaches 18.4% (+3.4 [+0.0, +6.8]).
  - P-0, with the question withheld, reaches 18.2%, and option length alone reaches 22.0%.
  - P-T's partial coefficient given letters and length is +0.041/SD, z = 0.87, permutation P = 0.21.

## 7. Engine agreement (0.30 vs 0.32)

| Comparison (hle-focus, identity reads, 1,287 questions) | Top-answer agreement | Accuracy |
|---|---|---|
| 0.30 repeat (`v030-id` vs `v030-id-b`) | 1,286 (99.92%) | 0.610 → 0.610 |
| 0.30 → 0.32 (`v030-id` vs `v032-id`) | 1,278 (99.30%) | +0.16, 2/0 |
| 0.32 vs 0.32 with the prefill cap (`v032-capped-id`) | 1,280 (99.46%) | +0.08, 1/0 |
| index-dev-2k, identity + reversed, `newjoiner` vs `reread32` | 3,719 / 3,728 (99.76%) | +0.03 [−0.11, +0.17] |

The 99.63% agreement quoted from the GPU session uses a different count from this per-question top answer. Either
way, the engine change is well inside the arm effects above.

## 8. Cost

| Layout (latency-v1, gemma-4-31b) | Orders | Median / mean / p80 ms | Source |
|---|---|---|---|
| `blurb_header` | identity + reversed | 151.5 / 416.6 / 537.5 | measured, `archive/gemma-4-31b/2026-10-23T051704Z-latency-blurb_header-identity+reversed` |
| `blurb_header_reread` (old joiner) | identity + reversed | 185.5 / 506.5 / 675.9 | measured, `…/2026-10-23T052356Z-latency-blurb_header_reread-identity+reversed` |
| default (CONTROL) | `top_p:0.9+reversed` | 189 / 465 / 635 | estimate |
| H1 | `top_p:0.9+reversed` | 252 / 813 / **1,085** | estimate (identity + reversed: 288 / 948 / 1,117) |
| H1q | `top_p:0.9+reversed` | 242 / 610 / 797 | estimate (identity + reversed: 276 / 659 / 842) |
| D1 | `top_p:0.9+reversed` | 230 / 616 / 827 | estimate |
| default, vLLM 0.32, 510 W | identity + reversed | 178.9 / 471.2 / 637.8 (p95 1,232.5) | measured, `…/2026-10-25T022949Z-latency-blurb_header_reread-identity+reversed` |
| H1q, vLLM 0.32, 510 W | identity + reversed | 255.5 / 610.6 / 813.6 (p95 1,779.0) | measured, `…/2026-10-25T023853Z-latency-blurb_header_reread_h1q-identity+reversed` |

- **How the estimates were made:** a quadratic fit of the measured reread run against computed tokens (R² 0.985),
  then the ratio method (`.firecrawl/h1-cost/report.md`). H1q was added by `h1q_cost.py`.
- **Computed tokens per request under `top_p`, index-dev-2k:** H1 ×1.67 (multi-question ×2.05), H1q ×1.34 (×1.49
  on one-question, ×1.00 on multi), D1 ×1.29. On eval, H1 = H1q at ×1.51.
- **The board gate** is median, mean and p80 each ≤ 1,000 ms. H1 fails it on p80 in both estimates; H1q and D1
  pass.

## 9. Other studies

- **Temperature ensembles** (`.firecrawl/temperature-ensemble/out/*.json`): none adopted.
  - ETS and Mix improve calibration over the shipped per-type T on gemma-4-31b `top_p` choice: on eval NLL −0.048
    [−0.061, −0.036] and ECE −0.017; on index-dev-2k NLL −0.054.
  - They change no answers, and on score they make ECE and MAE worse.
  - MPMix flips answers and loses: −0.12 points on eval, −0.08 on index-dev-2k.
  - Gating the second read at T = 1 instead of the fitted T costs −0.74 [−1.36, −0.12] choice points. That is why
    profiles without a fit matter (§10).
- **Gap analysis** (`.firecrawl/gap-analysis/`):
  - The private same-skill gap to FlexDM is spread thin, +0.86 over 34 benchmarks; the largest is Humicroedit
    +0.119.
  - New-domain tracks BBH, GPQA and MuSR: partial r 0.67–0.78 within the stock-weights entries. Our new-domain
    score is about 2.0 points below what those predict.

## 10. What shipped, what is pending

- **Shipped (default on all 9 profiles):** `blurb_header_reread`: B gated to one-question requests, letter names
  dropped, the new joiner, `same_name_once`, `drop_label_names`, no `_index`. vLLM v0.32.0 underneath.
  - Estimated public **64.52 [63.46, 65.55]**, +1.54 over the latest full run, +2.83 over the board entry, +0.89
    over FlexDM's public.
  - Only gemma-4-31b has been refit (on 0.32).
- **Pending:**
  1. **H1q calibration: done.** T choice 4.222, score 5.583, noul 7.216, b = 0 (fit in
     `.firecrawl/gpu-runs/h1-calibrate/`); served eval gains on all three types (§0).
  2. **H1q latency A/B: done**, p80 813.6 ms at 510 W (§8).
  3. **H1q length fallback.** Read once when the H1 row would pass `systemone_max_len`; without it, 12 of 2,839 eval
     requests fail.
  4. **Refits for the other 8 profiles.** These run `blurb_header_reread` at T = 1. That changes answers only under
     a `top_p` gate (`gemma-4-31b-fp8`); everywhere else it moves only scores and confidences.
     - The 4 quantized profiles need a re-borrow after the bf16 refits.
  5. **A full Index run under the default**, to replace these estimates.

## Caveats

- **index-dev-2k is suite data**, and the one-question gate (B, H1q) was chosen on it. The off-suite eval has no
  multi-question requests, so it can't test that gate.
- **The public numbers are estimates.** They carry shrinkage (k = 30, and the sign of H1q flips at k = 0), use T
  borrowed for H1/H1q/D1, and are chained across engines.
- **New-domain and same-skill can't be measured** from local data. They make up the whole board Full score (the
  `v03` parts weight them 60/40), and most of the gap to the peers sits in new-domain.
- **Single collects per arm.** A same-engine repeat agrees on 99.92% of top answers; bf16 noise is about 0.25% of
  questions.
- **H1's eval gain is the best off-suite evidence** for any 0.32 arm, but its index-dev-2k one-question gain alone
  (+0.35 [−0.47, +1.10]) is not significant.

## Files

- Collects: `.cache/collect/gemma-4-31b/{index-dev-2k-len32768-*,eval-*,calib-*,hle-focus-*}.jsonl.gz`. GPU scripts
  and logs: `.firecrawl/gpu-runs/{h1,h1q,d1}.{sh,log}`.
- Layouts: `prompts/blurb_header_reread.toml`, `prompts/experiments/reread-{system,h1,h1q,d1,clean,noindex}.toml`,
  `prompts/experiments/blurb-header-{nolettername,again-b,again-d,again-bd}.toml`.
- Background: [read-twice.md](../background/read-twice.md) (DS-045).
