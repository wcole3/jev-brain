# Vision compare: compare-pure

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.31 | baseline | 0.0376 | 0.6008 | 1117 | 0 |
| labels-content | offline | 72.63 | -0.68 [-2.51, +1.15] | 0.0256 | 0.6262 | 1112 | 0 |

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
| labels-content | 0.8906 | 0.0684 | 52 | 48 | 0.7644 | -0.0120 | +0.0254 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-content |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.011 [-0.059, +0.035] |
| CV-Bench | 136 | 0.748 | -0.084 [-0.157, -0.024] |
| CharXiv | 136 | 0.725 | +0.020 [-0.039, +0.078] |
| InfographicVQA | 97 | 0.904 | +0.027 [+0.000, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.929 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.272 | +0.008 [-0.050, +0.067] |
| Mind2Web | 136 | 0.882 | -0.010 [-0.049, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.515 | +0.015 [-0.044, +0.088] |
| R-Bench-M | 136 | 0.259 | +0.018 [-0.088, +0.124] |
| RealWorldQA | 136 | 0.772 | -0.048 [-0.131, +0.035] |
| Winoground | 136 | 0.750 | +0.015 [-0.044, +0.074] |
