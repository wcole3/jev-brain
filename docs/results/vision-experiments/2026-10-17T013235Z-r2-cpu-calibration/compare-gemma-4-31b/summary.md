# Vision compare: r1-calibration-gemma-4-31b

Baseline `text`, 1462 rows of `vision-dev`, Δ = config − baseline. CIs are 95% paired bootstrap (10000 resamples, seed 0) over image groups within each benchmark.
Errored live rows count as wrong. This table reports; the owner picks.

## Frontier

| config | kind | index | Δ index [95% CI] | ECE | NLL | mean input tokens | errored |
|---|---|---|---|---|---|---|---|
| text | offline | 77.06 | baseline | 0.0808 | 0.6072 | 719 | 0 |
| Tn_bucket | offline | 77.06 | +0.00 [+0.00, +0.00] | 0.0670 | 0.5973 | 719 | 0 |
| Tn_log | offline | 77.06 | +0.00 [+0.00, +0.00] | 0.0420 | 0.5712 | 719 | 0 |
| Tn_aleria | offline | 77.06 | +0.00 [+0.00, +0.00] | 0.0478 | 0.5708 | 719 | 0 |
| ref_dev_fitT | offline | 77.06 | +0.00 [+0.00, +0.00] | 0.0426 | 0.5746 | 719 | 0 |
| ref_dev_Tn_log | offline | 77.06 | +0.00 [+0.00, +0.00] | 0.0512 | 0.5710 | 719 | 0 |

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
| Tn_bucket | 1.0000 | 0.0000 | 0 | 0 | 1 | -0.0138 | -0.0100 |
| Tn_log | 1.0000 | 0.0000 | 0 | 0 | 1 | -0.0388 | -0.0361 |
| Tn_aleria | 1.0000 | 0.0000 | 0 | 0 | 1 | -0.0330 | -0.0364 |
| ref_dev_fitT | 1.0000 | 0.0000 | 0 | 0 | 1 | -0.0382 | -0.0326 |
| ref_dev_Tn_log | 1.0000 | 0.0000 | 0 | 0 | 1 | -0.0296 | -0.0362 |

## Per-benchmark Δ skill

| benchmark | rows | baseline skill | Tn_bucket | Tn_log | Tn_aleria | ref_dev_fitT | ref_dev_Tn_log |
|---|---|---|---|---|---|---|---|
| BLINK | 136 | 0.633 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| CV-Bench | 136 | 0.784 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| CharXiv | 136 | 0.922 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| InfographicVQA | 97 | 0.959 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| KIE (CORD+FUNSD) | 141 | 0.941 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| MMMU-Pro vision | 136 | 0.314 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| Mind2Web | 136 | 0.873 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| Moderation (Hateful Memes) | 136 | 0.574 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| R-Bench-M | 136 | 0.400 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| RealWorldQA | 136 | 0.713 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| Winoground | 136 | 0.838 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
