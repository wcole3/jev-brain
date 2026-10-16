# Vision factorial: r1-gemma-factorial

12 cells on 1462 rows of `vision-dev`; effects are index points against the reference `budget=560 placement=current wording=none`. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark, one resample shared by every cell.
CIs are unadjusted for multiple comparisons (9 index effects, 44 per-benchmark); the minimum detectable Δ index on dev is ≈3.5 points (docs/background/vision-experiments.md).
This table reports; the owner picks.

## Main effects

Mean over the other factors' cells of index(level) − index(reference level).

| factor | level | Δ index [95% CI] |
|---|---|---|
| budget | 280 | -3.50 [-5.25, -1.81] |
| budget | 1120 | +1.01 [-0.53, +2.53] |
| placement | imgfirst | -0.06 [-1.03, +0.92] |
| wording | worded | +0.03 [-0.61, +0.66] |

## Two-way interactions

Mean over the other factor of [index(v, w) − index(v, ref)] − [index(ref, w) − index(ref, ref)].

| factors | levels | interaction [95% CI] |
|---|---|---|
| budget × placement | 280 × imgfirst | +0.17 [-1.66, +1.99] |
| budget × placement | 1120 × imgfirst | -0.78 [-2.64, +1.15] |
| budget × wording | 280 × worded | -0.24 [-1.69, +1.21] |
| budget × wording | 1120 × worded | +0.84 [-0.59, +2.29] |
| placement × wording | imgfirst × worded | +0.43 [-0.66, +1.59] |

## Per-benchmark main effects

Unclipped skill, Δ [95% CI].

| benchmark | rows | budget=280 | budget=1120 | placement=imgfirst | wording=worded |
|---|---|---|---|---|---|
| BLINK | 136 | +0.032 [-0.018, +0.080] | +0.011 [-0.039, +0.060] | -0.006 [-0.043, +0.030] | -0.010 [-0.034, +0.015] |
| CV-Bench | 136 | -0.012 [-0.063, +0.036] | +0.009 [-0.029, +0.051] | -0.010 [-0.043, +0.022] | +0.002 [-0.013, +0.018] |
| CharXiv | 136 | -0.088 [-0.142, -0.037] | -0.012 [-0.047, +0.022] | -0.010 [-0.036, +0.013] | +0.000 [-0.015, +0.016] |
| InfographicVQA | 97 | -0.062 [-0.131, -0.003] | +0.007 [-0.021, +0.038] | +0.000 [-0.018, +0.018] | -0.000 [-0.016, +0.016] |
| KIE (CORD+FUNSD) | 141 | -0.021 [-0.051, +0.000] | -0.006 [-0.014, +0.000] | -0.002 [-0.006, +0.000] | +0.002 [-0.000, +0.006] |
| MMMU-Pro vision | 136 | -0.032 [-0.090, +0.025] | +0.053 [-0.013, +0.119] | +0.003 [-0.021, +0.029] | +0.003 [-0.016, +0.021] |
| Mind2Web | 136 | -0.083 [-0.140, -0.029] | -0.025 [-0.076, +0.025] | +0.018 [-0.003, +0.039] | +0.011 [-0.005, +0.029] |
| Moderation (Hateful Memes) | 136 | +0.015 [-0.055, +0.081] | +0.015 [-0.070, +0.099] | +0.020 [-0.039, +0.076] | +0.010 [-0.015, +0.034] |
| R-Bench-M | 136 | +0.020 [-0.009, +0.053] | +0.022 [-0.015, +0.062] | -0.018 [-0.056, +0.019] | +0.003 [-0.025, +0.031] |
| RealWorldQA | 136 | -0.090 [-0.151, -0.036] | +0.075 [+0.018, +0.136] | +0.000 [-0.036, +0.036] | -0.008 [-0.030, +0.010] |
| Winoground | 136 | -0.033 [-0.096, +0.022] | +0.000 [-0.051, +0.048] | -0.007 [-0.032, +0.015] | -0.007 [-0.042, +0.022] |

## Cells

| budget | placement | wording | index | ECE | NLL | mean input tokens |
|---|---|---|---|---|---|---|
| 560 | current | none | 77.21 | 0.0462 | 0.5753 | 719 |
| 560 | imgfirst | none | 77.17 | 0.0378 | 0.5806 | 719 |
| 560 | current | worded | 76.85 | 0.0422 | 0.5682 | 733 |
| 560 | imgfirst | worded | 77.18 | 0.0370 | 0.5756 | 733 |
| 280 | current | none | 73.83 | 0.0361 | 0.6166 | 431 |
| 280 | imgfirst | none | 73.79 | 0.0341 | 0.6351 | 431 |
| 280 | current | worded | 73.06 | 0.0371 | 0.6194 | 444 |
| 280 | imgfirst | worded | 73.74 | 0.0423 | 0.6324 | 444 |
| 1120 | current | none | 78.15 | 0.0302 | 0.5368 | 1295 |
| 1120 | imgfirst | none | 77.41 | 0.0299 | 0.5508 | 1295 |
| 1120 | current | worded | 78.71 | 0.0416 | 0.5406 | 1308 |
| 1120 | imgfirst | worded | 78.18 | 0.0304 | 0.5439 | 1308 |

## Latency per budget level

Timed per budget level only, at power limit 510.0 W: placement and wording get Δ tokens, not latency.

| budget | p50 ms | p80 ms |
|---|---|---|
| 560 | 323 | 377 |
| 280 | 237 | 281 |
| 1120 | 712 | 766 |
