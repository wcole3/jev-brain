# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.09 | baseline | 0.0921 | 0.6260 | 719 | 0 |
| blurb-header | offline | 78.25 | +1.16 [-0.28, +2.63] | 0.0855 | 0.6153 | 740 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| blurb-header | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| blurb-header | 0.9446 | 0.0390 | 26 | 31 | 0.5966 | -0.0066 | -0.0108 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | blurb-header |
|---|---|---|---|
| BLINK | 136 | 0.645 | +0.000 [-0.046, +0.046] |
| CV-Bench | 136 | 0.784 | +0.024 [+0.000, +0.061] |
| CharXiv | 136 | 0.922 | +0.000 [-0.029, +0.029] |
| InfographicVQA | 97 | 0.959 | +0.014 [-0.027, +0.055] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.012 [+0.000, +0.038] |
| MMMU-Pro vision | 136 | 0.323 | +0.000 [-0.059, +0.059] |
| Mind2Web | 136 | 0.873 | +0.010 [-0.020, +0.039] |
| Moderation (Hateful Memes) | 136 | 0.574 | +0.029 [-0.044, +0.103] |
| R-Bench-M | 136 | 0.409 | -0.053 [-0.115, +0.009] |
| RealWorldQA | 136 | 0.713 | +0.036 [-0.024, +0.097] |
| Winoground | 136 | 0.824 | +0.015 [-0.029, +0.059] |
