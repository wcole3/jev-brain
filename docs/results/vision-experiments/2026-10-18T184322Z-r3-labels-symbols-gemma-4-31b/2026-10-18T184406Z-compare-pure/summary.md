# Vision compare: compare-pure

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.06 | baseline | 0.0861 | 0.6166 | 719 | 0 |
| labels-symbols | offline | 66.59 | -10.47 [-12.77, -7.86] | 0.0482 | 0.7006 | 711 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-symbols | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-symbols | 0.8345 | 0.1252 | 134 | 49 | 2.537e-10 | -0.0379 | +0.0840 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-symbols |
|---|---|---|---|
| BLINK | 136 | 0.633 | -0.069 [-0.157, +0.011] |
| CV-Bench | 136 | 0.784 | +0.036 [+0.000, +0.083] |
| CharXiv | 136 | 0.922 | -0.127 [-0.206, -0.059] |
| InfographicVQA | 97 | 0.959 | -0.014 [-0.082, +0.055] |
| KIE (CORD+FUNSD) | 141 | 0.941 | -0.012 [-0.037, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | -0.042 [-0.120, +0.034] |
| Mind2Web | 136 | 0.873 | -0.020 [-0.078, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.574 | +0.015 [-0.029, +0.059] |
| R-Bench-M | 136 | 0.400 | -0.062 [-0.176, +0.053] |
| RealWorldQA | 136 | 0.713 | -0.024 [-0.084, +0.036] |
| Winoground | 136 | 0.838 | -0.765 [-0.941, -0.588] |
