# JevBench: our models vs Jev (2026-09-29)

**Short answer:** yes, the results are consistent.

- Our benchmark reproduces the upstream JevBench harness exactly.
- Jev's score on it matches the recorded board, within the board's own margin.
- Our three stock models trail Jev by 4–7 points. Almost all of the gap is in `noul` and
  `score`. On `choice` they are level with Jev.

## What was run

- **Data:** JevBench at upstream commit `fcec62f`, all **1682 gold rows**. The upstream
  board used a 232-row gold sample whose row ids are not published.
- **Jev:** `jev-1.13.0` via `api.typesafe.ai`, run twice:
  - upstream's `bench_eval.py --backend jev`;
  - our `bench.py --target jev`.
- **Our models:** `bench.py --profile <p> --jevbench-only`.
  - bf16, `decider_chat` layout, identity option order, vLLM 0.30.0.
  - Repo commit `4de0f45`.
  - Per-run provenance is in each `summary.md`.

## Results

Overall, choice and noul are exact-match accuracy in %. QWK and MAE cover the 207
ordinal `score` rows. A failed request counts as wrong. These are the upstream board's
rules.

| Run | Rows | Overall | Choice | Noul | Score QWK | Score MAE | p50 ms |
|---|---|---|---|---|---|---|---|
| Jev, upstream board (recorded) | 232 | 88.8 | 94 | 92 | 0.92 | 0.20 | – |
| Jev, upstream harness | 1682 | 91.1 | 91.9 | 96.0 | 0.940 | 0.19 | – |
| Jev, our bench | 1682 | 91.3 | 92.0 | 95.7 | 0.946 | 0.169 | 194* |
| gemma-4-31b | 1682 | 87.1 | 92.1 | 87.5 | 0.936 | 0.203 | 62 |
| qwen3.8-27b | 1682 | 86.3 | 90.3 | 86.2 | 0.878 | 0.213 | 88 |
| qwen3.6-27b | 1682 | 84.4 | 91.9 | 83.7 | 0.818 | 0.377 | 89 |

\* Jev latency includes the HTTPS round trip; ours is on the local GPU.

## Why we trust the comparison

1. **Same harness.** Against our gateway, upstream's `bench_eval.py` and our `bench.py`
   gave **1682/1682 identical predictions** and identical metrics (qwen3.6-27b). They also
   build the same request body for every row.
2. **Jev is slightly non-deterministic.** Our two Jev passes differ on 18 rows:
   - 17 are near-ties where Jev gives different answers to identical requests (checked
     by re-asking each 3 times);
   - 1 was a single HTTP error.

   This is about ±0.2 points of noise.
3. **The recorded board.**
   - Jev scores 91.1–91.3 on all 1682 rows vs 88.8 on the board's 232. That is inside the
     board's stated ±~4-point margin, with the same per-type pattern.
   - An exact match needs the board's row ids.
4. **Our earlier reports.**
   - 2026-09-28: 84.2 / 86.4 / 87.2 (qwen3.6 / qwen3.8 / gemma).
   - Today: 84.4 / 86.3 / 87.1.
   - The gap is a handful of near-tie rows (bf16 noise).

## Where the gap is

Accuracy % by source and type:

| Source | Type | Rows | Jev | qwen3.6 | qwen3.8 | gemma |
|---|---|---|---|---|---|---|
| banking77 | choice | 300 | 82.3 | 81.7 | 84.0 | 80.7 |
| panoramic | choice | 400 | 100.0 | 99.8 | 94.8 | 100.0 |
| panoramic | noul | 400 | 95.8 | 81.0 | 80.5 | 83.2 |
| panoramic | score | 100 | 76.0 | 61.0 | 61.0 | 61.0 |
| typed_decisions | choice | 50 | 86.0 | 90.0 | 92.0 | 98.0 |
| typed_decisions | noul | 225 | 95.6 | 88.4 | 96.4 | 95.1 |
| typed_decisions | score | 207 | 82.6 | 71.0 | 84.5 | 80.2 |

- **Choice:** level with Jev or better.
- **Noul:** the biggest gap, mostly on panoramic's computed yes/no questions. The misses
  lean one way, and the direction depends on the model:

  | Model | Gold "yes" answered "no" | Gold "no" answered "yes" |
  |---|---|---|
  | Jev | 8 / 267 | 19 / 358 |
  | qwen3.6-27b | 74 / 267 | 28 / 358 |
  | qwen3.8-27b | 54 / 267 | 32 / 358 |
  | gemma-4-31b | 6 / 267 | 72 / 358 |

  Temperature can't fix this: it never moves which side of 0.5 a noul lands on. Fixes to
  try in phase 2 (DS-002):
  - a per-profile noul bias fitted on a labelled calibration split;
  - option-order averaging, since `no` is always shown first as `(A)`;
  - the noul prompt wording.
- **Score:** panoramic score is 61 for all three models vs Jev's 76. On typed_decisions,
  qwen3.8 and gemma are at or above Jev.

## Notes

- None of these models has our own fitted temperature yet (qwen3.6 uses decider's published
  T = 1.943; the others T = 1.0). Accuracy doesn't depend on the temperature, so the
  comparison is fair. Calibration error (ECE) is not measured here.
- TypeSafe's terms forbid using Jev outputs to train or calibrate a similar model.
  - Jev's per-row answers stay in `.cache/jev-results/`; only the summary is committed.
  - Phase-2 calibration uses JevBench's gold labels, never Jev's answers.

## Reproduce

```bash
uv run python scripts/bench.py --target jev                            # Jev (key: TYPESAFE_API_KEY or secrets/.jev-key)
uv run python scripts/bench.py --profile qwen3.6-27b --jevbench-only   # each profile, stack running
```
