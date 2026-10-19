# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.49 | baseline | 0.0399 | 0.5999 | 1117 | 0 |
| decider | offline | 72.45 | -1.04 [-2.89, +0.80] | 0.1007 | 0.6577 | 1070 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| decider | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| decider | 0.9234 | 0.0561 | 45 | 37 | 0.4397 | +0.0608 | +0.0578 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | decider |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.046 [-0.093, -0.011] |
| CV-Bench | 136 | 0.748 | +0.012 [-0.048, +0.074] |
| CharXiv | 136 | 0.735 | +0.020 [-0.039, +0.078] |
| InfographicVQA | 97 | 0.904 | +0.014 [-0.041, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.929 | +0.036 [+0.000, +0.077] |
| MMMU-Pro vision | 136 | 0.272 | +0.034 [-0.017, +0.086] |
| Mind2Web | 136 | 0.882 | -0.088 [-0.147, -0.029] |
| Moderation (Hateful Memes) | 136 | 0.515 | +0.000 [-0.088, +0.088] |
| R-Bench-M | 136 | 0.250 | -0.018 [-0.079, +0.044] |
| RealWorldQA | 136 | 0.784 | -0.048 [-0.119, +0.012] |
| Winoground | 136 | 0.750 | +0.000 [-0.044, +0.044] |
