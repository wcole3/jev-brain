# Vision compare: compare-pure

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.06 | baseline | 0.0861 | 0.6166 | 719 | 0 |
| labels-shuffled | offline | 74.49 | -2.57 [-4.17, -1.04] | 0.0931 | 0.6727 | 719 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-shuffled | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-shuffled | 0.9207 | 0.0499 | 52 | 21 | 0.0003713 | +0.0070 | +0.0561 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-shuffled |
|---|---|---|---|
| BLINK | 136 | 0.633 | -0.069 [-0.140, +0.000] |
| CV-Bench | 136 | 0.784 | +0.012 [-0.025, +0.050] |
| CharXiv | 136 | 0.922 | -0.010 [-0.039, +0.020] |
| InfographicVQA | 97 | 0.959 | -0.014 [-0.069, +0.041] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | -0.068 [-0.130, -0.008] |
| Mind2Web | 136 | 0.873 | -0.029 [-0.078, +0.010] |
| Moderation (Hateful Memes) | 136 | 0.574 | -0.015 [-0.044, +0.000] |
| R-Bench-M | 136 | 0.400 | -0.053 [-0.132, +0.026] |
| RealWorldQA | 136 | 0.713 | -0.024 [-0.084, +0.036] |
| Winoground | 136 | 0.838 | -0.059 [-0.132, +0.000] |
