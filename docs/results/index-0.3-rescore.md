# Our Index runs rescored on Decision Index 0.3

How far do our latest full Index runs move when the board changes from edition 0.2.1 to
0.3? Measured 2026-10-09 with harness `9eb2dbe` (DS-031). Each run kept all its answers and
only added the 2,638 rebuilt GSM8K rows. Those rows were run on this machine under the run's
own settings: that commit's profile, calibration and prompts, MTP off, the `header` layout.
They took 3-5 minutes per profile. Both editions are scored with the same harness.

## Short answer

| profile (run) | 0.2.1 index | 0.3 public index | move | board neighbour 0.2.1 → 0.3 |
|---|---|---|---|---|
| qwen3.6-27b (`2026-10-03T140831Z-vast`) | 55.92 | **56.51** | +0.59 | Decider chat · Qwen3.6-27B 51.35 → 51.57 (+0.22) |
| qwen3.8-27b (`2026-10-04T022907Z-vast`) | 56.01 | **56.60** | +0.59 | simple-jev · Qwen3.8-27B 55.70 → 56.05 (+0.35) |
| gemma-4-31b (`2026-10-04T013002Z-vast`) | 60.61 | **61.60** | +0.99 | Decider chat · Gemma-4-31B 57.33 → 57.79 (+0.46) |

- **Same harness, both editions:** rescoring the same runs with `--edition 0.2.1` reproduces
  our committed 0.2.1 numbers exactly (55.92 / 56.01 / 60.61).
- **We move up a bit more than our board neighbours.** The reason is ForecastBench: it was
  one of our weakest benchmarks (skill 0.18 / 0.20 / 0.00), and its retirement lifts Arts &
  Human Taste by 3.7-7.6 points.
- **The rebuilt GSM8K is harder for everyone.** Our skill falls 51.8 → 32.2 (Qwen3.6),
  51.9 → 27.8 (Qwen3.8) and 79.1 → 68.1 (Gemma). The board's Decider chat entries fall the
  same way (Qwen3.6 49.3 → 29.8, Gemma 78.8 → 65.4).
- **The public index is only 20% of the 0.3 Full score.** The other 80% are private tests
  that only the maintainers run on submitted models, so these numbers can't place us on the
  Full-score board. Stock-model entries lose 8-17 points on the private new-domain tasks
  (Qwen-based) or about 7 (Gemma-based); see DS-030.

## Per area (skill, 0.2.1 → 0.3)

| profile | Knowledge & Reasoning | Language Understanding | Retrieval & Classification | Tools & Automation | Arts & Human Taste |
|---|---|---|---|---|---|
| qwen3.6-27b | 38.0 → 39.8 | 64.6 → 63.6 | 60.7 → 60.7 | 74.5 → 74.5 | 36.5 → 40.2 |
| qwen3.8-27b | 34.2 → 35.7 | 64.3 → 63.6 | 63.7 → 63.7 | 76.3 → 76.3 | 38.5 → 42.2 |
| gemma-4-31b | 46.7 → 48.6 | 66.8 → 65.8 | 67.2 → 67.2 | 76.6 → 76.6 | 38.1 → 45.7 |

- **Knowledge & Reasoning** gains WinoGrande, which moved in (skill 0.72 / 0.70 / 0.75). The
  harder GSM8K offsets part of that gain.
- **Language Understanding** loses WinoGrande.
- **Arts & Human Taste** loses ForecastBench.

## Caveats

- **GSM8K rows on a different machine:** the new rows ran on this box, while the rest of each
  run ran on a rented box. bf16 noise of about 0.03 per question applies.
- **Gateway code is newer than the runs:** governor, priority and per-block calibration files
  came later. None of these changes the decision math.
- **The summaries' Status line counts 152,9xx rows:** the merged results still hold the
  retired ForecastBench rows and the old GSM8K rows. The harness scores only the 140,178
  rows of 0.3 (`complete: true`).
- **The splits were recut on 0.3 in the same ticket.** calib and eval ids are unchanged, but
  index-dev and latency-v1 were resampled. Earlier index-dev and latency runs are not
  row-for-row comparable with new ones.

Summaries: `docs/results/<profile>/2026-10-09T164331Z-rescore-0.3-index/summary.md`. Run
data: `.cache/index-runs/<profile>/<run>-0.3/`.
