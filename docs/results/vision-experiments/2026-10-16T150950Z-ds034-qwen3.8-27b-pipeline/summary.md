# Vision compare: ds034-qwen3.8-27b-pipeline

Baseline `offline`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| offline | offline | 73.31 | baseline | 0.0424 | 0.6029 | 1117 | 0 |
| live | live | 73.00 | -0.31 [-0.97, +0.35] | 0.0427 | 0.6020 | 1117 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| offline | offline | 0 | 0 | 0 | — |
| live | live | — | — | — | 0 |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| live | 0.9897 | 0.0055 | 6 | 2 | 0.2891 | +0.0004 | -0.0009 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | live |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.011 [-0.035, +0.000] |
| CV-Bench | 136 | 0.748 | +0.000 [+0.000, +0.000] |
| CharXiv | 136 | 0.725 | -0.010 [-0.029, +0.000] |
| InfographicVQA | 97 | 0.904 | +0.000 [+0.000, +0.000] |
| KIE (CORD+FUNSD) | 141 | 0.929 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.272 | +0.000 [+0.000, +0.000] |
| Mind2Web | 136 | 0.882 | -0.020 [-0.049, +0.000] |
| Moderation (Hateful Memes) | 136 | 0.515 | +0.015 [-0.029, +0.074] |
| R-Bench-M | 136 | 0.259 | -0.009 [-0.026, +0.000] |
| RealWorldQA | 136 | 0.772 | +0.000 [+0.000, +0.000] |
| Winoground | 136 | 0.750 | +0.000 [+0.000, +0.000] |
