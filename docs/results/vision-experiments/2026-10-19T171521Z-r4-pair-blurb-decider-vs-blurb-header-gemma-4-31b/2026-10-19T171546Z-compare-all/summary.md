# Vision compare: compare-all

Baseline `blurb-header`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| blurb-header | offline | 78.25 | baseline | 0.0855 | 0.6153 | 740 | 0 |
| blurb-decider | offline | 77.13 | -1.12 [-2.82, +0.48] | 0.0814 | 0.6169 | 693 | 0 |

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
| blurb-decider | 0.9302 | 0.0513 | 40 | 35 | 0.6445 | -0.0041 | +0.0016 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | blurb-decider |
|---|---|---|---|
| BLINK | 136 | 0.645 | +0.000 [-0.057, +0.057] |
| CV-Bench | 136 | 0.808 | -0.036 [-0.083, +0.000] |
| CharXiv | 136 | 0.922 | -0.010 [-0.049, +0.029] |
| InfographicVQA | 97 | 0.973 | +0.014 [+0.000, +0.041] |
| KIE (CORD+FUNSD) | 141 | 0.953 | -0.012 [-0.038, +0.000] |
| MMMU-Pro vision | 136 | 0.323 | +0.000 [-0.050, +0.044] |
| Mind2Web | 136 | 0.882 | +0.000 [-0.049, +0.049] |
| Moderation (Hateful Memes) | 136 | 0.603 | -0.015 [-0.088, +0.059] |
| R-Bench-M | 136 | 0.356 | +0.053 [-0.026, +0.132] |
| RealWorldQA | 136 | 0.749 | -0.048 [-0.131, +0.024] |
| Winoground | 136 | 0.838 | -0.029 [-0.088, +0.029] |
