# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.31 | baseline | 0.0376 | 0.6008 | 1117 | 0 |
| labels-spaced | offline | 72.76 | -0.54 [-2.10, +1.05] | 0.0283 | 0.6158 | 1116 | 0 |

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
| labels-spaced | 0.9063 | 0.0561 | 44 | 38 | 0.5811 | -0.0092 | +0.0149 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-spaced |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.034 [-0.090, +0.012] |
| CV-Bench | 136 | 0.748 | -0.036 [-0.098, +0.024] |
| CharXiv | 136 | 0.725 | +0.010 [-0.039, +0.059] |
| InfographicVQA | 97 | 0.904 | +0.014 [-0.027, +0.055] |
| KIE (CORD+FUNSD) | 141 | 0.929 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.272 | +0.008 [-0.050, +0.067] |
| Mind2Web | 136 | 0.882 | -0.020 [-0.059, +0.020] |
| Moderation (Hateful Memes) | 136 | 0.515 | +0.015 [-0.029, +0.074] |
| R-Bench-M | 136 | 0.259 | -0.018 [-0.115, +0.079] |
| RealWorldQA | 136 | 0.772 | -0.024 [-0.094, +0.037] |
| Winoground | 136 | 0.750 | +0.029 [+0.000, +0.074] |
