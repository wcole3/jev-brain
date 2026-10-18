# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.06 | baseline | 0.0861 | 0.6166 | 719 | 0 |
| labels-digits | offline | 75.26 | -1.80 [-3.16, -0.47] | 0.0882 | 0.6246 | 719 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-digits | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-digits | 0.9562 | 0.0321 | 32 | 15 | 0.01862 | +0.0021 | +0.0080 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-digits |
|---|---|---|---|
| BLINK | 136 | 0.633 | -0.046 [-0.103, +0.000] |
| CV-Bench | 136 | 0.784 | +0.012 [-0.025, +0.050] |
| CharXiv | 136 | 0.922 | -0.049 [-0.108, +0.000] |
| InfographicVQA | 97 | 0.959 | +0.014 [-0.027, +0.055] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | +0.017 [-0.025, +0.059] |
| Mind2Web | 136 | 0.873 | -0.039 [-0.078, -0.010] |
| Moderation (Hateful Memes) | 136 | 0.574 | -0.015 [-0.044, +0.000] |
| R-Bench-M | 136 | 0.400 | -0.035 [-0.088, +0.018] |
| RealWorldQA | 136 | 0.713 | -0.024 [-0.072, +0.024] |
| Winoground | 136 | 0.838 | -0.015 [-0.059, +0.029] |
