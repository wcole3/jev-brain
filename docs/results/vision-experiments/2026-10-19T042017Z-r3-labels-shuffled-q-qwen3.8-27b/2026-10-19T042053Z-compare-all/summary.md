# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.31 | baseline | 0.0376 | 0.6008 | 1117 | 0 |
| labels-shuffled-q | offline | 71.62 | -1.69 [-3.82, +0.40] | 0.0388 | 0.6479 | 1117 | 0 |

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
| labels-shuffled-q | 0.8659 | 0.0889 | 74 | 56 | 0.1357 | +0.0012 | +0.0470 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-shuffled-q |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.149 [-0.251, -0.047] |
| CV-Bench | 136 | 0.748 | +0.000 [-0.048, +0.048] |
| CharXiv | 136 | 0.725 | +0.088 [+0.020, +0.157] |
| InfographicVQA | 97 | 0.904 | +0.014 [-0.041, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.929 | -0.012 [-0.052, +0.026] |
| MMMU-Pro vision | 136 | 0.272 | -0.034 [-0.111, +0.043] |
| Mind2Web | 136 | 0.882 | -0.010 [-0.059, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.515 | -0.015 [-0.074, +0.029] |
| R-Bench-M | 136 | 0.259 | -0.026 [-0.124, +0.071] |
| RealWorldQA | 136 | 0.772 | -0.060 [-0.153, +0.024] |
| Winoground | 136 | 0.750 | +0.000 [-0.074, +0.074] |
