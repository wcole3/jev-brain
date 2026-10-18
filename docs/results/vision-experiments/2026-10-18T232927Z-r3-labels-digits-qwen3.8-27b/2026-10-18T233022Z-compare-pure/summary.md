# Vision compare: compare-pure

Baseline `letters`, 1367 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| letters | offline | 73.29 | baseline | 0.0408 | 0.5153 | 1090 | 0 |
| labels-digits | offline | 72.91 | -0.38 [-2.02, +1.32] | 0.0572 | 0.5484 | 1094 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| letters | offline | 0 | 0 | 0 | — |
| labels-digits | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| labels-digits | 0.9217 | 0.0534 | 40 | 33 | 0.4828 | +0.0164 | +0.0331 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | labels-digits |
|---|---|---|---|
| BLINK | 136 | 0.725 | -0.011 [-0.058, +0.035] |
| CV-Bench | 136 | 0.748 | +0.000 [-0.048, +0.048] |
| CharXiv | 136 | 0.725 | +0.069 [+0.010, +0.127] |
| InfographicVQA | 97 | 0.904 | +0.014 [-0.041, +0.069] |
| KIE (CORD+FUNSD) | 141 | 0.929 | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 41 | 0.263 | -0.123 [-0.291, +0.031] |
| Mind2Web | 136 | 0.882 | -0.010 [-0.059, +0.039] |
| Moderation (Hateful Memes) | 136 | 0.515 | +0.015 [+0.000, +0.044] |
| R-Bench-M | 136 | 0.259 | -0.044 [-0.115, +0.026] |
| RealWorldQA | 136 | 0.772 | -0.060 [-0.154, +0.036] |
| Winoground | 136 | 0.750 | +0.000 [+0.000, +0.000] |
