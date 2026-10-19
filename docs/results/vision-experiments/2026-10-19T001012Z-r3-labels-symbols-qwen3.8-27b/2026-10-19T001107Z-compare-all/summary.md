# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.31 | baseline | 0.0376 | 0.6008 | 1117 | 0 |
| labels-symbols | offline | 33.75 | -39.56 [-44.04, -34.95] | 0.2313 | 1.4962 | 1112 | 0 |

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
| labels-symbols | 0.5342 | 0.3584 | 442 | 82 | 1.124e-60 | +0.1937 | +0.8953 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-symbols |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.562 [-0.728, -0.392] |
| CV-Bench | 136 | 0.748 | -0.204 [-0.316, -0.095] |
| CharXiv | 136 | 0.725 | -0.343 [-0.471, -0.216] |
| InfographicVQA | 97 | 0.904 | -0.330 [-0.454, -0.206] |
| KIE (CORD+FUNSD) | 141 | 0.929 | -0.414 [-0.591, -0.254] |
| MMMU-Pro vision | 136 | 0.272 | -0.161 [-0.263, -0.059] |
| Mind2Web | 136 | 0.882 | -0.667 [-0.784, -0.549] |
| Moderation (Hateful Memes) | 136 | 0.515 | -0.397 [-0.588, -0.206] |
| R-Bench-M | 136 | 0.259 | -0.203 [-0.335, -0.079] |
| RealWorldQA | 136 | 0.772 | -0.563 [-0.710, -0.410] |
| Winoground | 136 | 0.750 | -0.235 [-0.397, -0.088] |
