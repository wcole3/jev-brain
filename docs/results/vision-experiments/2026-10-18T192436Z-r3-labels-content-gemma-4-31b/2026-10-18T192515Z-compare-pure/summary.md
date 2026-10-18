# Vision compare: compare-pure

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.06 | baseline | 0.0861 | 0.6166 | 719 | 0 |
| labels-content | offline | 76.54 | -0.52 [-1.72, +0.63] | 0.0723 | 0.6287 | 711 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-content | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-content | 0.9514 | 0.0315 | 25 | 21 | 0.6587 | -0.0138 | +0.0121 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-content |
|---|---|---|---|
| BLINK | 136 | 0.633 | +0.000 [-0.034, +0.034] |
| CV-Bench | 136 | 0.784 | +0.000 [+0.000, +0.000] |
| CharXiv | 136 | 0.922 | -0.029 [-0.069, +0.000] |
| InfographicVQA | 97 | 0.959 | +0.027 [-0.027, +0.082] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | +0.025 [-0.017, +0.068] |
| Mind2Web | 136 | 0.873 | -0.020 [-0.069, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.574 | +0.000 [-0.044, +0.044] |
| R-Bench-M | 136 | 0.400 | -0.018 [-0.088, +0.053] |
| RealWorldQA | 136 | 0.713 | -0.012 [-0.059, +0.024] |
| Winoground | 136 | 0.838 | -0.015 [-0.044, +0.000] |
