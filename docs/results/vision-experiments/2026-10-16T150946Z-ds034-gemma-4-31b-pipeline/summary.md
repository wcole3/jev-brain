# Vision compare: ds034-gemma-4-31b-pipeline

Baseline `offline`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| offline | offline | 77.06 | baseline | 0.0808 | 0.6072 | 719 | 0 |
| live | live | 77.44 | +0.38 [+0.00, +0.86] | 0.0845 | 0.6063 | 719 | 0 |

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
| live | 0.9932 | 0.0041 | 1 | 5 | 0.2188 | +0.0038 | -0.0009 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | live |
|---|---|---|---|
| BLINK | 136 | 0.633 | +0.011 [+0.000, +0.035] |
| CV-Bench | 136 | 0.784 | +0.000 [+0.000, +0.000] |
| CharXiv | 136 | 0.922 | +0.000 [+0.000, +0.000] |
| InfographicVQA | 97 | 0.959 | +0.014 [+0.000, +0.041] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | +0.008 [+0.000, +0.026] |
| Mind2Web | 136 | 0.873 | +0.010 [+0.000, +0.029] |
| Moderation (Hateful Memes) | 136 | 0.574 | +0.000 [+0.000, +0.000] |
| R-Bench-M | 136 | 0.400 | +0.000 [-0.026, +0.026] |
| RealWorldQA | 136 | 0.713 | +0.000 [+0.000, +0.000] |
| Winoground | 136 | 0.838 | +0.000 [+0.000, +0.000] |
