# Vision compare: r1-calibration-qwen3.8-27b

Baseline `text`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| text | offline | 73.31 | baseline | 0.0424 | 0.6029 | 1117 | 0 |
| Tn_bucket | offline | 73.31 | +0.00 [+0.00, +0.00] | 0.0627 | 1.0545 | 1117 | 0 |
| Tn_log | offline | 73.31 | +0.00 [+0.00, +0.00] | 0.0598 | 0.6112 | 1117 | 0 |
| Tn_aleria | offline | 73.31 | +0.00 [+0.00, +0.00] | 0.3030 | 0.9064 | 1117 | 0 |
| ref_dev_fitT | offline | 73.31 | +0.00 [+0.00, +0.00] | 0.0255 | 0.5965 | 1117 | 0 |
| ref_dev_Tn_log | offline | 73.31 | +0.00 [+0.00, +0.00] | 0.0256 | 0.5966 | 1117 | 0 |

## Rows left out

Offline arms score only ok rows with a gold answer; errored live rows are counted, as wrong.

| config | kind | unsupported | invalid | no_gold | errored |
|---|---|---|---|---|---|
| text | offline | 0 | 0 | 0 | — |
| Tn_bucket | offline | 0 | 0 | 0 | — |
| Tn_log | offline | 0 | 0 | 0 | — |
| Tn_aleria | offline | 0 | 0 | 0 | — |
| ref_dev_fitT | offline | 0 | 0 | 0 | — |
| ref_dev_Tn_log | offline | 0 | 0 | 0 | — |

## Paired

McNemar p is row-level and unweighted (no groups, no benchmark weights): the Δ index CI is the headline.

| config | agreement | d | b (base only) | c (config only) | McNemar p (rows) | ΔECE | ΔNLL |
|---|---|---|---|---|---|---|---|
| Tn_bucket | 1.0000 | 0.0000 | 0 | 0 | 1 | +0.0203 | +0.4517 |
| Tn_log | 1.0000 | 0.0000 | 0 | 0 | 1 | +0.0174 | +0.0084 |
| Tn_aleria | 1.0000 | 0.0000 | 0 | 0 | 1 | +0.2606 | +0.3035 |
| ref_dev_fitT | 1.0000 | 0.0000 | 0 | 0 | 1 | -0.0169 | -0.0064 |
| ref_dev_Tn_log | 1.0000 | 0.0000 | 0 | 0 | 1 | -0.0168 | -0.0062 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | Tn_bucket | Tn_log | Tn_aleria | ref_dev_fitT | ref_dev_Tn_log |
|---|---|---|---|---|---|---|---|
| BLINK | 136 | 0.725 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| CV-Bench | 136 | 0.748 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| CharXiv | 136 | 0.725 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| InfographicVQA | 97 | 0.904 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| KIE (CORD+FUNSD) | 141 | 0.929 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.272 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| Mind2Web | 136 | 0.882 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| Moderation (Hateful Memes) | 136 | 0.515 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| R-Bench-M | 136 | 0.259 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| RealWorldQA | 136 | 0.772 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| Winoground | 136 | 0.750 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
