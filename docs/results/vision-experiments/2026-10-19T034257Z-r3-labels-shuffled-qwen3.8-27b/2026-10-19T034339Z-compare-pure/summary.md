# Vision compare: compare-pure

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.31 | baseline | 0.0376 | 0.6008 | 1117 | 0 |
| labels-shuffled | offline | 71.88 | -1.42 [-3.63, +0.71] | 0.0508 | 0.6402 | 1117 | 0 |

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
| labels-shuffled | 0.8550 | 0.0951 | 81 | 58 | 0.06165 | +0.0132 | +0.0394 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-shuffled |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.126 [-0.233, -0.023] |
| CV-Bench | 136 | 0.748 | +0.000 [-0.048, +0.048] |
| CharXiv | 136 | 0.725 | +0.069 [-0.020, +0.157] |
| InfographicVQA | 97 | 0.904 | +0.000 [-0.069, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.929 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.272 | -0.085 [-0.172, +0.000] |
| Mind2Web | 136 | 0.882 | -0.010 [-0.059, +0.039] |
| Moderation (Hateful Memes) | 136 | 0.515 | -0.015 [-0.074, +0.029] |
| R-Bench-M | 136 | 0.259 | -0.053 [-0.150, +0.035] |
| RealWorldQA | 136 | 0.772 | -0.024 [-0.119, +0.072] |
| Winoground | 136 | 0.750 | +0.015 [-0.029, +0.059] |
