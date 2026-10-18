# Vision compare: compare-all

Baseline `letters`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 77.06 | baseline | 0.0861 | 0.6166 | 719 | 0 |
| labels-unused | offline | 51.40 | -25.66 [-28.89, -22.38] | 0.1442 | 1.0769 | 711 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-unused | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-unused | 0.6949 | 0.2401 | 309 | 42 | 2.227e-51 | +0.0581 | +0.4603 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-unused |
|---|---|---|---|
| BLINK | 136 | 0.633 | -0.229 [-0.368, -0.091] |
| CV-Bench | 136 | 0.784 | -0.132 [-0.215, -0.059] |
| CharXiv | 136 | 0.922 | -0.569 [-0.686, -0.461] |
| InfographicVQA | 97 | 0.959 | -0.495 [-0.632, -0.357] |
| KIE (CORD+FUNSD) | 141 | 0.941 | -0.189 [-0.249, -0.122] |
| MMMU-Pro vision | 136 | 0.314 | -0.220 [-0.334, -0.104] |
| Mind2Web | 136 | 0.873 | -0.333 [-0.451, -0.216] |
| Moderation (Hateful Memes) | 136 | 0.574 | -0.029 [-0.074, +0.000] |
| R-Bench-M | 136 | 0.400 | -0.353 [-0.450, -0.247] |
| RealWorldQA | 136 | 0.713 | -0.263 [-0.391, -0.135] |
| Winoground | 136 | 0.838 | -0.029 [-0.103, +0.044] |
