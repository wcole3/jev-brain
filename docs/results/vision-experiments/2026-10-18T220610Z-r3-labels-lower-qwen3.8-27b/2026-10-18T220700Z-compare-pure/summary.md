# Vision compare: compare-pure

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.31 | baseline | 0.0376 | 0.6008 | 1117 | 0 |
| labels-lower | offline | 73.16 | -0.15 [-1.52, +1.20] | 0.0402 | 0.6105 | 1117 | 0 |

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
| labels-lower | 0.9460 | 0.0315 | 26 | 20 | 0.4614 | +0.0026 | +0.0096 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-lower |
|---|---|---|---|
| BLINK | 136 | 0.725 | +0.011 [+0.000, +0.035] |
| CV-Bench | 136 | 0.748 | -0.036 [-0.083, +0.000] |
| CharXiv | 136 | 0.725 | +0.059 [+0.010, +0.118] |
| InfographicVQA | 97 | 0.904 | +0.041 [+0.000, +0.096] |
| KIE (CORD+FUNSD) | 141 | 0.929 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.272 | -0.042 [-0.101, +0.009] |
| Mind2Web | 136 | 0.882 | -0.010 [-0.029, +0.000] |
| Moderation (Hateful Memes) | 136 | 0.515 | -0.044 [-0.118, +0.015] |
| R-Bench-M | 136 | 0.259 | -0.026 [-0.071, +0.009] |
| RealWorldQA | 136 | 0.772 | -0.012 [-0.084, +0.060] |
| Winoground | 136 | 0.750 | +0.000 [+0.000, +0.000] |
