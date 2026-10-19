# Vision compare: compare-all

Baseline `decider`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| decider | offline | 72.45 | baseline | 0.1007 | 0.6577 | 1070 | 0 |
| blurb-decider | offline | 72.96 | +0.51 [-1.46, +2.48] | 0.0893 | 0.6333 | 1091 | 0 |

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
| blurb-decider | 0.9172 | 0.0629 | 44 | 48 | 0.7547 | -0.0113 | -0.0244 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | blurb-decider |
|---|---|---|---|
| BLINK | 136 | 0.679 | -0.046 [-0.154, +0.058] |
| CV-Bench | 136 | 0.760 | -0.012 [-0.073, +0.049] |
| CharXiv | 136 | 0.755 | +0.020 [-0.029, +0.078] |
| InfographicVQA | 97 | 0.918 | +0.027 [-0.027, +0.082] |
| KIE (CORD+FUNSD) | 141 | 0.964 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.306 | -0.042 [-0.101, +0.008] |
| Mind2Web | 136 | 0.794 | -0.010 [-0.069, +0.049] |
| Moderation (Hateful Memes) | 136 | 0.515 | -0.015 [-0.059, +0.029] |
| R-Bench-M | 136 | 0.232 | +0.053 [+0.000, +0.106] |
| RealWorldQA | 136 | 0.737 | +0.084 [+0.000, +0.170] |
| Winoground | 136 | 0.750 | -0.015 [-0.074, +0.029] |
