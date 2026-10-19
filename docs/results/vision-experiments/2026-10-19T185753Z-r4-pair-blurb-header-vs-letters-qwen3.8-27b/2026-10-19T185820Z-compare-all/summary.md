# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.49 | baseline | 0.0399 | 0.5999 | 1117 | 0 |
| blurb-header | offline | 73.66 | +0.17 [-1.53, +1.89] | 0.0631 | 0.6059 | 1138 | 0 |

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
| blurb-header | 0.9357 | 0.0465 | 33 | 35 | 0.9036 | +0.0232 | +0.0059 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | blurb-header |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.046 [-0.141, +0.046] |
| CV-Bench | 136 | 0.748 | +0.000 [-0.048, +0.048] |
| CharXiv | 136 | 0.735 | +0.029 [-0.020, +0.078] |
| InfographicVQA | 97 | 0.904 | +0.014 [-0.027, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.929 | -0.012 [-0.037, +0.000] |
| MMMU-Pro vision | 136 | 0.272 | +0.000 [-0.042, +0.042] |
| Mind2Web | 136 | 0.882 | +0.000 [+0.000, +0.000] |
| Moderation (Hateful Memes) | 136 | 0.515 | +0.015 [-0.029, +0.059] |
| R-Bench-M | 136 | 0.250 | +0.009 [-0.053, +0.071] |
| RealWorldQA | 136 | 0.784 | +0.012 [-0.061, +0.095] |
| Winoground | 136 | 0.750 | +0.000 [-0.044, +0.044] |
