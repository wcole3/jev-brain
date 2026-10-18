# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.06 | baseline | 0.0861 | 0.6166 | 719 | 0 |
| labels-lower | offline | 76.47 | -0.59 [-1.44, +0.19] | 0.0858 | 0.6120 | 719 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-lower | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-lower | 0.9767 | 0.0123 | 10 | 8 | 0.8145 | -0.0003 | -0.0046 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-lower |
|---|---|---|---|
| BLINK | 136 | 0.633 | +0.000 [+0.000, +0.000] |
| CV-Bench | 136 | 0.784 | +0.012 [+0.000, +0.037] |
| CharXiv | 136 | 0.922 | +0.000 [+0.000, +0.000] |
| InfographicVQA | 97 | 0.959 | +0.000 [+0.000, +0.000] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | +0.008 [-0.017, +0.042] |
| Mind2Web | 136 | 0.873 | -0.020 [-0.049, +0.000] |
| Moderation (Hateful Memes) | 136 | 0.574 | -0.015 [-0.044, +0.000] |
| R-Bench-M | 136 | 0.400 | +0.026 [-0.009, +0.062] |
| RealWorldQA | 136 | 0.713 | -0.036 [-0.083, +0.000] |
| Winoground | 136 | 0.838 | -0.015 [-0.059, +0.029] |
