# Vision compare: compare-all

Baseline `blurb-header`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| blurb-header | offline | 73.66 | baseline | 0.0631 | 0.6059 | 1138 | 0 |
| blurb-decider | offline | 72.96 | -0.70 [-2.58, +1.17] | 0.0893 | 0.6333 | 1091 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| blurb-header | offline | 0 | 0 | 0 | — |
| blurb-decider | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| blurb-decider | 0.9248 | 0.0575 | 45 | 39 | 0.5856 | +0.0262 | +0.0275 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | blurb-decider |
|---|---|---|---|
| BLINK | 136 | 0.679 | -0.046 [-0.128, +0.035] |
| CV-Bench | 136 | 0.748 | +0.000 [-0.048, +0.048] |
| CharXiv | 136 | 0.765 | +0.010 [-0.029, +0.049] |
| InfographicVQA | 97 | 0.918 | +0.027 [-0.027, +0.082] |
| KIE (CORD+FUNSD) | 141 | 0.917 | +0.047 [+0.011, +0.092] |
| MMMU-Pro vision | 136 | 0.272 | -0.008 [-0.068, +0.051] |
| Mind2Web | 136 | 0.882 | -0.098 [-0.157, -0.049] |
| Moderation (Hateful Memes) | 136 | 0.529 | -0.029 [-0.118, +0.059] |
| R-Bench-M | 136 | 0.259 | +0.026 [-0.035, +0.088] |
| RealWorldQA | 136 | 0.796 | +0.024 [-0.035, +0.084] |
| Winoground | 136 | 0.750 | -0.015 [-0.044, +0.000] |
