# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.09 | baseline | 0.0921 | 0.6260 | 719 | 0 |
| decider | offline | 77.96 | +0.87 [-0.77, +2.46] | 0.0770 | 0.6135 | 672 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| decider | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| decider | 0.9343 | 0.0472 | 32 | 37 | 0.6305 | -0.0150 | -0.0126 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | decider |
|---|---|---|---|
| BLINK | 136 | 0.645 | +0.011 [-0.047, +0.069] |
| CV-Bench | 136 | 0.784 | +0.000 [-0.048, +0.048] |
| CharXiv | 136 | 0.922 | -0.020 [-0.069, +0.029] |
| InfographicVQA | 97 | 0.959 | +0.027 [+0.000, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.323 | -0.025 [-0.078, +0.026] |
| Mind2Web | 136 | 0.873 | -0.010 [-0.059, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.574 | +0.029 [-0.044, +0.118] |
| R-Bench-M | 136 | 0.409 | +0.026 [-0.044, +0.097] |
| RealWorldQA | 136 | 0.713 | +0.024 [-0.037, +0.095] |
| Winoground | 136 | 0.824 | +0.015 [+0.000, +0.044] |
