# Vision compare: r1-gemma-orders

Baseline `fitT_id`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| fitT_id | offline | 77.02 | baseline | 0.0407 | 0.5742 | 719 | 0 |
| pride_id | offline | 76.76 | -0.26 [-1.07, +0.54] | 0.0406 | 0.5740 | 719 | 0 |
| fitT_cyc | offline | 77.00 | -0.02 [-1.23, +1.21] | 0.0340 | 0.5783 | 966 | 0 |
| pride_cyc | offline | 76.93 | -0.09 [-1.30, +1.15] | 0.0362 | 0.5776 | 966 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| fitT_id | offline | 0 | 0 | 0 | — |
| pride_id | offline | 0 | 0 | 0 | — |
| fitT_cyc | offline | 0 | 0 | 0 | — |
| pride_cyc | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| pride_id | 0.9815 | 0.0116 | 9 | 8 | 1 | -0.0001 | -0.0003 |
| fitT_cyc | 0.9275 | 0.0424 | 29 | 33 | 0.7035 | -0.0067 | +0.0041 |
| pride_cyc | 0.9275 | 0.0424 | 29 | 33 | 0.7035 | -0.0045 | +0.0034 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | pride_id | fitT_cyc | pride_cyc |
|---|---|---|---|---|---|
| BLINK | 136 | 0.645 | -0.011 [-0.035, +0.000] | -0.011 [-0.056, +0.023] | -0.011 [-0.056, +0.023] |
| CV-Bench | 136 | 0.784 | +0.000 [+0.000, +0.000] | +0.000 [-0.036, +0.036] | +0.000 [-0.036, +0.036] |
| CharXiv | 136 | 0.922 | +0.000 [+0.000, +0.000] | -0.010 [-0.039, +0.020] | -0.010 [-0.039, +0.020] |
| InfographicVQA | 97 | 0.959 | +0.014 [+0.000, +0.041] | +0.027 [+0.000, +0.069] | +0.014 [-0.027, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.339 | -0.008 [-0.042, +0.017] | +0.000 [-0.068, +0.067] | +0.008 [-0.059, +0.075] |
| Mind2Web | 136 | 0.863 | +0.010 [-0.020, +0.039] | -0.010 [-0.039, +0.020] | +0.000 [-0.029, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.574 | -0.015 [-0.044, +0.000] | -0.015 [-0.044, +0.000] | -0.015 [-0.044, +0.000] |
| R-Bench-M | 136 | 0.400 | +0.018 [-0.018, +0.053] | +0.062 [-0.026, +0.150] | +0.053 [-0.035, +0.141] |
| RealWorldQA | 136 | 0.701 | +0.000 [-0.036, +0.036] | +0.000 [-0.048, +0.048] | +0.000 [-0.048, +0.048] |
| Winoground | 136 | 0.838 | -0.029 [-0.074, +0.000] | -0.015 [-0.074, +0.029] | -0.015 [-0.074, +0.029] |
