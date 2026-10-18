# Vision compare: compare-pure

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.06 | baseline | 0.0861 | 0.6166 | 719 | 0 |
| labels-spaced | offline | 76.13 | -0.93 [-2.10, +0.19] | 0.0677 | 0.6097 | 714 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-spaced | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-spaced | 0.9542 | 0.0280 | 23 | 18 | 0.5327 | -0.0184 | -0.0069 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-spaced |
|---|---|---|---|
| BLINK | 136 | 0.633 | +0.011 [+0.000, +0.035] |
| CV-Bench | 136 | 0.784 | +0.000 [+0.000, +0.000] |
| CharXiv | 136 | 0.922 | -0.029 [-0.069, +0.000] |
| InfographicVQA | 97 | 0.959 | +0.014 [-0.027, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | +0.025 [-0.017, +0.068] |
| Mind2Web | 136 | 0.873 | -0.010 [-0.049, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.574 | -0.029 [-0.074, +0.000] |
| R-Bench-M | 136 | 0.400 | +0.000 [-0.062, +0.062] |
| RealWorldQA | 136 | 0.713 | -0.024 [-0.072, +0.024] |
| Winoground | 136 | 0.838 | -0.029 [-0.074, +0.000] |
