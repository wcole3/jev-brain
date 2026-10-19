# Vision compare: compare-all

Baseline `decider`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| decider | offline | 77.96 | baseline | 0.0770 | 0.6135 | 672 | 0 |
| blurb-decider | offline | 77.13 | -0.83 [-2.18, +0.50] | 0.0814 | 0.6169 | 693 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| decider | offline | 0 | 0 | 0 | — |
| blurb-decider | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| blurb-decider | 0.9501 | 0.0335 | 27 | 22 | 0.5682 | +0.0044 | +0.0034 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | blurb-decider |
|---|---|---|---|
| BLINK | 136 | 0.656 | -0.011 [-0.056, +0.023] |
| CV-Bench | 136 | 0.784 | -0.012 [-0.050, +0.025] |
| CharXiv | 136 | 0.902 | +0.010 [+0.000, +0.029] |
| InfographicVQA | 97 | 0.986 | +0.000 [+0.000, +0.000] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.297 | +0.025 [-0.026, +0.083] |
| Mind2Web | 136 | 0.863 | +0.020 [-0.020, +0.059] |
| Moderation (Hateful Memes) | 136 | 0.603 | -0.015 [-0.088, +0.059] |
| R-Bench-M | 136 | 0.435 | -0.026 [-0.088, +0.035] |
| RealWorldQA | 136 | 0.737 | -0.036 [-0.095, +0.012] |
| Winoground | 136 | 0.838 | -0.029 [-0.074, +0.000] |
