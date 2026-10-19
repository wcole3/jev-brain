# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.06 | baseline | 0.0861 | 0.6166 | 719 | 0 |
| labels-shuffled-q | offline | 74.85 | -2.21 [-3.87, -0.59] | 0.0898 | 0.6496 | 719 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-shuffled-q | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-shuffled-q | 0.9152 | 0.0581 | 52 | 33 | 0.05025 | +0.0037 | +0.0331 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-shuffled-q |
|---|---|---|---|
| BLINK | 136 | 0.633 | -0.069 [-0.153, +0.012] |
| CV-Bench | 136 | 0.784 | -0.012 [-0.050, +0.024] |
| CharXiv | 136 | 0.922 | -0.029 [-0.078, +0.020] |
| InfographicVQA | 97 | 0.959 | -0.055 [-0.124, +0.000] |
| KIE (CORD+FUNSD) | 141 | 0.941 | -0.012 [-0.037, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | +0.000 [-0.084, +0.084] |
| Mind2Web | 136 | 0.873 | -0.010 [-0.049, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.574 | -0.015 [-0.044, +0.000] |
| R-Bench-M | 136 | 0.400 | -0.018 [-0.088, +0.053] |
| RealWorldQA | 136 | 0.713 | +0.024 [-0.024, +0.073] |
| Winoground | 136 | 0.838 | -0.029 [-0.088, +0.029] |
