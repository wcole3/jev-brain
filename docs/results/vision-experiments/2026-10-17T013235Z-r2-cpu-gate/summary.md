# R2 CPU R3: gate sizing for gated thinking (vision dev, both models)

Created 2026-10-17T013235Z, commit a306b77 (clean tree). Reports; the owner picks. Nothing here runs thinking: the index columns are what-ifs under assumed fix and break rates.

## Method

- First read = identity read at the shipped text choice T. Gates: top probability < τ; identity/reversed top-answer disagreement (each order softmaxed at T alone, mapped back); top-two probability margin < m; disagreement or top-p < τ.
- What-if index: per benchmark, a gated error turns right with probability X and a gated correct row turns wrong with probability Y; the expected hits go through the kit's skill and weights (`vision_compare.skill`, `combine`). X = 100%, Y = 0% is the oracle ceiling.
- Latency: the 300 timed dev rows of `ds034-latency-baseline` (warm-up 20 dropped; ids are dev rows, so each row's gate is known), rank-mapped onto the 600 W vast sample (300 rows) so median/mean/p80 equal it; the raw ds034 run (510 W) is the alternative. A gated row adds 57 ms for the second letter read (cached shared-image read, `docs/background/images.md` §5) plus N/rate for N thought tokens (gemma 24.3 tok/s, qwen 46.7 tok/s). Gates that use disagreement make every row pay the reversed read: 0.33 ms/token x its suffix (~94 tokens, ≈31 ms; the ds034 wall-ms vs input-token slope), or a flat 57 ms per row as a variant (not always larger: long-option rows have suffixes of 150+ tokens).
- Budget = largest N (same N on every gated row) that keeps median, mean and p80 (`bench_report.percentile`, as `vision_summary`) <= 1,000 ms, and <= 900 ms for a 10% margin. `binding` names the statistic that breaks first.

## Data

- `.cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz` (sha256 `a4b9fcaf89675bd5…`)
- `.cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz` (sha256 `86af73abf00b2369…`)
- `data/gemma-4-31b/header/calibration.json` (sha256 `907179a67fdea7df…`)
- `data/qwen3.8-27b/header/calibration.json` (sha256 `58c75d522e2385bb…`)
- `.cache/vision-runs/gemma-4-31b/ds034-latency-baseline/results.jsonl` (sha256 `f51c9b96229faea2…`)
- `.cache/vision-runs/qwen3.8-27b/ds034-latency-baseline/results.jsonl` (sha256 `0964760aa2f58bcd…`)
- `.cache/vision-runs/gemma-4-31b/latency-2026-10-16T000616Z-vast/results.jsonl` (sha256 `b5f7347c7332feee…`)
- `.cache/vision-runs/qwen3.8-27b/latency-2026-10-16T000604Z-vast/results.jsonl` (sha256 `beb32be4e3c9e7e4…`)
- `data/splits/vision-dev.json` (sha256 `ec05c385e0c0eca7…`)
- `data/splits/vision-latency.json` (sha256 `2b0e00e972a1a957…`)

## gemma-4-31b

Identity read at text T: accuracy 0.800 (292 errors of 1462), index 77.06. Latency base: 600 W sample median 334 / mean 384 / p80 445 ms; ds034 measured median 328 / mean 368 / p80 389 ms. Decode 24.3 tok/s.

### Gates

| gate | gated share (dev) | share on latency set | errors inside | accuracy inside | accuracy outside |
|---|---|---|---|---|---|
| top-p < 0.5 | 0.066 (96) | 0.053 | 0.226 (66) | 0.312 | 0.835 |
| top-p < 0.6 | 0.114 (166) | 0.120 | 0.353 (103) | 0.380 | 0.854 |
| top-p < 0.7 | 0.161 (235) | 0.157 | 0.476 (139) | 0.409 | 0.875 |
| top-p < 0.8 | 0.222 (325) | 0.210 | 0.634 (185) | 0.431 | 0.906 |
| top-p < 0.9 | 0.305 (446) | 0.317 | 0.784 (229) | 0.487 | 0.938 |
| disagree | 0.124 (181) | 0.123 | 0.380 (111) | 0.387 | 0.859 |
| margin < 0.1 | 0.028 (41) | 0.033 | 0.099 (29) | 0.293 | 0.815 |
| margin < 0.3 | 0.073 (106) | 0.060 | 0.233 (68) | 0.358 | 0.835 |
| margin < 0.5 | 0.144 (211) | 0.157 | 0.414 (121) | 0.427 | 0.863 |
| disagree or top-p < 0.5 | 0.151 (221) | 0.153 | 0.469 (137) | 0.380 | 0.875 |
| disagree or top-p < 0.6 | 0.172 (252) | 0.180 | 0.510 (149) | 0.409 | 0.882 |
| disagree or top-p < 0.7 | 0.205 (299) | 0.203 | 0.586 (171) | 0.428 | 0.896 |
| disagree or top-p < 0.8 | 0.242 (354) | 0.220 | 0.685 (200) | 0.435 | 0.917 |
| disagree or top-p < 0.9 | 0.311 (455) | 0.317 | 0.798 (233) | 0.488 | 0.941 |

Gated share per benchmark:

| gate | BLINK | CV-Bench | CharXiv | InfographicVQA | KIE | MMMU-Pro | Mind2Web | Hateful Memes | R-Bench-M | RealWorldQA | Winoground |
|---|---|---|---|---|---|---|---|---|---|---|---|
| top-p < 0.5 | 0.00 | 0.01 | 0.01 | 0.00 | 0.00 | 0.35 | 0.04 | 0.00 | 0.29 | 0.01 | 0.00 |
| top-p < 0.6 | 0.01 | 0.02 | 0.03 | 0.02 | 0.00 | 0.48 | 0.10 | 0.01 | 0.51 | 0.04 | 0.01 |
| top-p < 0.7 | 0.04 | 0.06 | 0.10 | 0.03 | 0.01 | 0.62 | 0.10 | 0.01 | 0.69 | 0.07 | 0.02 |
| top-p < 0.8 | 0.15 | 0.08 | 0.18 | 0.06 | 0.01 | 0.74 | 0.11 | 0.03 | 0.88 | 0.11 | 0.04 |
| top-p < 0.9 | 0.30 | 0.14 | 0.29 | 0.13 | 0.01 | 0.86 | 0.18 | 0.07 | 0.97 | 0.26 | 0.10 |
| disagree | 0.07 | 0.04 | 0.07 | 0.05 | 0.00 | 0.35 | 0.06 | 0.01 | 0.57 | 0.05 | 0.07 |
| margin < 0.1 | 0.01 | 0.01 | 0.00 | 0.00 | 0.00 | 0.12 | 0.03 | 0.00 | 0.11 | 0.01 | 0.01 |
| margin < 0.3 | 0.01 | 0.01 | 0.01 | 0.01 | 0.00 | 0.32 | 0.07 | 0.01 | 0.29 | 0.03 | 0.01 |
| margin < 0.5 | 0.04 | 0.06 | 0.08 | 0.03 | 0.01 | 0.51 | 0.10 | 0.01 | 0.60 | 0.08 | 0.04 |
| disagree or top-p < 0.5 | 0.07 | 0.05 | 0.07 | 0.05 | 0.00 | 0.51 | 0.07 | 0.01 | 0.67 | 0.06 | 0.07 |
| disagree or top-p < 0.6 | 0.08 | 0.06 | 0.10 | 0.05 | 0.00 | 0.56 | 0.10 | 0.02 | 0.75 | 0.08 | 0.07 |
| disagree or top-p < 0.7 | 0.10 | 0.08 | 0.14 | 0.06 | 0.01 | 0.66 | 0.10 | 0.02 | 0.85 | 0.11 | 0.07 |
| disagree or top-p < 0.8 | 0.18 | 0.10 | 0.20 | 0.09 | 0.01 | 0.76 | 0.11 | 0.03 | 0.92 | 0.13 | 0.09 |
| disagree or top-p < 0.9 | 0.31 | 0.15 | 0.29 | 0.13 | 0.01 | 0.88 | 0.18 | 0.07 | 0.98 | 0.26 | 0.13 |

### What-if Δ index (X = share of gated errors fixed, Y = share of gated correct rows broken)

| gate | X 25 Y 0 | X 25 Y 5 | X 25 Y 10 | X 50 Y 0 | X 50 Y 5 | X 50 Y 10 | X 75 Y 0 | X 75 Y 5 | X 75 Y 10 | X 100 Y 0 | X 100 Y 5 | X 100 Y 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top-p < 0.5 | +0.61 | +0.54 | +0.47 | +1.22 | +1.15 | +1.08 | +1.83 | +1.76 | +1.69 | +2.44 | +2.37 | +2.30 |
| top-p < 0.6 | +1.12 | +0.94 | +0.75 | +2.25 | +2.06 | +1.87 | +3.37 | +3.18 | +3.00 | +4.49 | +4.31 | +4.12 |
| top-p < 0.7 | +1.61 | +1.30 | +0.99 | +3.22 | +2.91 | +2.60 | +4.83 | +4.52 | +4.21 | +6.44 | +6.13 | +5.82 |
| top-p < 0.8 | +2.50 | +2.01 | +1.52 | +5.01 | +4.52 | +4.02 | +7.51 | +7.02 | +6.53 | +10.02 | +9.52 | +9.03 |
| top-p < 0.9 | +3.70 | +2.84 | +1.98 | +7.40 | +6.54 | +5.68 | +11.10 | +10.24 | +9.38 | +14.80 | +13.94 | +13.08 |
| disagree | +1.57 | +1.32 | +1.06 | +3.14 | +2.89 | +2.63 | +4.71 | +4.46 | +4.20 | +6.28 | +6.03 | +5.77 |
| margin < 0.1 | +0.31 | +0.27 | +0.22 | +0.62 | +0.58 | +0.53 | +0.93 | +0.89 | +0.85 | +1.24 | +1.20 | +1.16 |
| margin < 0.3 | +0.72 | +0.60 | +0.47 | +1.44 | +1.32 | +1.19 | +2.16 | +2.03 | +1.91 | +2.87 | +2.75 | +2.63 |
| margin < 0.5 | +1.49 | +1.16 | +0.84 | +2.97 | +2.65 | +2.33 | +4.46 | +4.13 | +3.81 | +5.94 | +5.62 | +5.30 |
| disagree or top-p < 0.5 | +1.81 | +1.53 | +1.24 | +3.62 | +3.34 | +3.06 | +5.43 | +5.15 | +4.87 | +7.25 | +6.96 | +6.68 |
| disagree or top-p < 0.6 | +1.99 | +1.64 | +1.28 | +3.99 | +3.63 | +3.27 | +5.98 | +5.63 | +5.27 | +7.98 | +7.62 | +7.26 |
| disagree or top-p < 0.7 | +2.31 | +1.86 | +1.41 | +4.63 | +4.18 | +3.73 | +6.94 | +6.49 | +6.04 | +9.26 | +8.81 | +8.35 |
| disagree or top-p < 0.8 | +2.94 | +2.39 | +1.83 | +5.89 | +5.33 | +4.77 | +8.83 | +8.27 | +7.72 | +11.78 | +11.22 | +10.66 |
| disagree or top-p < 0.9 | +3.82 | +2.94 | +2.06 | +7.65 | +6.77 | +5.89 | +11.47 | +10.59 | +9.71 | +15.29 | +14.41 | +13.53 |

### Latency budget: max thought tokens per gated row

| gate | ≤1000 ms (600 W) | binding | ≤900 ms (600 W) | ≤1000 ms (ds034 510 W) | ≤900 ms (ds034) | ≤1000 / ≤900, reversed read flat 57 ms (600 W) |
|---|---|---|---|---|---|---|
| top-p < 0.5 | 279 | mean | 233 | 286 | 240 | — |
| top-p < 0.6 | 123 | mean | 103 | 126 | 106 | — |
| top-p < 0.7 | 94 | mean | 78 | 96 | 81 | — |
| top-p < 0.8 | 16 | p80 | 13 | 15 | 12 | — |
| top-p < 0.9 | 14 | p80 | 11 | 14 | 12 | — |
| disagree | 113 | mean | 94 | 116 | 97 | 108 / 89 |
| margin < 0.1 | 447 | mean | 375 | 459 | 386 | — |
| margin < 0.3 | 248 | mean | 207 | 254 | 214 | — |
| margin < 0.5 | 94 | mean | 78 | 96 | 81 | — |
| disagree or top-p < 0.5 | 91 | mean | 75 | 93 | 77 | 87 / 71 |
| disagree or top-p < 0.6 | 16 | p80 | 13 | 79 | 66 | 15 / 12 |
| disagree or top-p < 0.7 | 14 | p80 | 12 | 14 | 12 | 14 / 11 |
| disagree or top-p < 0.8 | 14 | p80 | 11 | 14 | 11 | 14 / 11 |
| disagree or top-p < 0.9 | 13 | p80 | 10 | 13 | 11 | 12 / 10 |

## qwen3.8-27b

Identity read at text T: accuracy 0.769 (337 errors of 1462), index 73.31. Latency base: 600 W sample median 237 / mean 300 / p80 466 ms; ds034 measured median 389 / mean 423 / p80 606 ms. Decode 46.7 tok/s.

### Gates

| gate | gated share (dev) | share on latency set | errors inside | accuracy inside | accuracy outside |
|---|---|---|---|---|---|
| top-p < 0.5 | 0.202 (296) | 0.200 | 0.570 (192) | 0.351 | 0.876 |
| top-p < 0.6 | 0.298 (436) | 0.283 | 0.751 (253) | 0.420 | 0.918 |
| top-p < 0.7 | 0.374 (547) | 0.343 | 0.846 (285) | 0.479 | 0.943 |
| top-p < 0.8 | 0.479 (700) | 0.470 | 0.926 (312) | 0.554 | 0.967 |
| top-p < 0.9 | 0.611 (894) | 0.573 | 0.950 (320) | 0.642 | 0.970 |
| disagree | 0.202 (296) | 0.237 | 0.522 (176) | 0.405 | 0.862 |
| margin < 0.1 | 0.152 (222) | 0.133 | 0.436 (147) | 0.338 | 0.847 |
| margin < 0.3 | 0.294 (430) | 0.280 | 0.736 (248) | 0.423 | 0.914 |
| margin < 0.5 | 0.391 (571) | 0.360 | 0.866 (292) | 0.489 | 0.949 |
| disagree or top-p < 0.5 | 0.293 (428) | 0.293 | 0.739 (249) | 0.418 | 0.915 |
| disagree or top-p < 0.6 | 0.343 (502) | 0.330 | 0.828 (279) | 0.444 | 0.940 |
| disagree or top-p < 0.7 | 0.397 (581) | 0.373 | 0.872 (294) | 0.494 | 0.951 |
| disagree or top-p < 0.8 | 0.486 (711) | 0.480 | 0.926 (312) | 0.561 | 0.967 |
| disagree or top-p < 0.9 | 0.614 (897) | 0.577 | 0.950 (320) | 0.643 | 0.970 |

Gated share per benchmark:

| gate | BLINK | CV-Bench | CharXiv | InfographicVQA | KIE | MMMU-Pro | Mind2Web | Hateful Memes | R-Bench-M | RealWorldQA | Winoground |
|---|---|---|---|---|---|---|---|---|---|---|---|
| top-p < 0.5 | 0.12 | 0.10 | 0.15 | 0.06 | 0.00 | 0.65 | 0.12 | 0.00 | 0.90 | 0.10 | 0.00 |
| top-p < 0.6 | 0.29 | 0.19 | 0.27 | 0.13 | 0.00 | 0.76 | 0.21 | 0.09 | 0.97 | 0.27 | 0.06 |
| top-p < 0.7 | 0.40 | 0.25 | 0.37 | 0.18 | 0.02 | 0.84 | 0.29 | 0.14 | 0.99 | 0.38 | 0.21 |
| top-p < 0.8 | 0.58 | 0.35 | 0.51 | 0.20 | 0.04 | 0.90 | 0.46 | 0.32 | 1.00 | 0.51 | 0.34 |
| top-p < 0.9 | 0.79 | 0.50 | 0.72 | 0.31 | 0.09 | 0.96 | 0.71 | 0.47 | 1.00 | 0.71 | 0.40 |
| disagree | 0.26 | 0.10 | 0.24 | 0.12 | 0.04 | 0.46 | 0.10 | 0.04 | 0.56 | 0.19 | 0.10 |
| margin < 0.1 | 0.16 | 0.12 | 0.10 | 0.05 | 0.00 | 0.41 | 0.07 | 0.04 | 0.56 | 0.10 | 0.04 |
| margin < 0.3 | 0.35 | 0.18 | 0.28 | 0.13 | 0.01 | 0.67 | 0.15 | 0.12 | 0.90 | 0.28 | 0.12 |
| margin < 0.5 | 0.42 | 0.26 | 0.36 | 0.18 | 0.03 | 0.80 | 0.30 | 0.23 | 0.98 | 0.40 | 0.30 |
| disagree or top-p < 0.5 | 0.34 | 0.15 | 0.30 | 0.16 | 0.04 | 0.71 | 0.19 | 0.04 | 0.93 | 0.23 | 0.10 |
| disagree or top-p < 0.6 | 0.37 | 0.22 | 0.35 | 0.20 | 0.04 | 0.80 | 0.26 | 0.10 | 0.98 | 0.31 | 0.14 |
| disagree or top-p < 0.7 | 0.44 | 0.26 | 0.41 | 0.23 | 0.04 | 0.85 | 0.33 | 0.15 | 0.99 | 0.40 | 0.24 |
| disagree or top-p < 0.8 | 0.60 | 0.35 | 0.53 | 0.24 | 0.05 | 0.90 | 0.46 | 0.32 | 1.00 | 0.51 | 0.35 |
| disagree or top-p < 0.9 | 0.79 | 0.50 | 0.73 | 0.31 | 0.10 | 0.96 | 0.71 | 0.47 | 1.00 | 0.71 | 0.40 |

### What-if Δ index (X = share of gated errors fixed, Y = share of gated correct rows broken)

| gate | X 25 Y 0 | X 25 Y 5 | X 25 Y 10 | X 50 Y 0 | X 50 Y 5 | X 50 Y 10 | X 75 Y 0 | X 75 Y 5 | X 75 Y 10 | X 100 Y 0 | X 100 Y 5 | X 100 Y 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top-p < 0.5 | +2.54 | +2.20 | +1.85 | +5.09 | +4.74 | +4.39 | +7.63 | +7.28 | +6.94 | +10.17 | +9.83 | +9.48 |
| top-p < 0.6 | +4.18 | +3.41 | +2.65 | +8.35 | +7.59 | +6.83 | +12.53 | +11.77 | +11.01 | +16.71 | +15.95 | +15.18 |
| top-p < 0.7 | +5.07 | +3.86 | +2.65 | +10.15 | +8.94 | +7.73 | +15.22 | +14.01 | +12.80 | +20.30 | +19.08 | +17.87 |
| top-p < 0.8 | +5.86 | +3.91 | +1.95 | +11.73 | +9.77 | +7.81 | +17.59 | +15.63 | +13.67 | +23.45 | +21.49 | +19.54 |
| top-p < 0.9 | +6.05 | +3.02 | -0.02 | +12.11 | +9.07 | +6.03 | +18.16 | +15.12 | +12.08 | +24.22 | +21.18 | +18.14 |
| disagree | +3.07 | +2.50 | +1.93 | +6.13 | +5.56 | +4.99 | +9.20 | +8.63 | +8.06 | +12.26 | +11.69 | +11.13 |
| margin < 0.1 | +2.28 | +1.97 | +1.65 | +4.57 | +4.25 | +3.93 | +6.85 | +6.53 | +6.22 | +9.13 | +8.82 | +8.50 |
| margin < 0.3 | +4.31 | +3.49 | +2.66 | +8.63 | +7.80 | +6.97 | +12.94 | +12.11 | +11.29 | +17.26 | +16.43 | +15.60 |
| margin < 0.5 | +5.39 | +4.03 | +2.67 | +10.79 | +9.43 | +8.06 | +16.18 | +14.82 | +13.46 | +21.58 | +20.21 | +18.85 |
| disagree or top-p < 0.5 | +4.11 | +3.33 | +2.55 | +8.22 | +7.44 | +6.66 | +12.33 | +11.55 | +10.77 | +16.44 | +15.66 | +14.88 |
| disagree or top-p < 0.6 | +4.92 | +3.93 | +2.94 | +9.84 | +8.85 | +7.87 | +14.77 | +13.78 | +12.79 | +19.69 | +18.70 | +17.71 |
| disagree or top-p < 0.7 | +5.35 | +3.99 | +2.63 | +10.70 | +9.34 | +7.99 | +16.05 | +14.69 | +13.34 | +21.40 | +20.04 | +18.69 |
| disagree or top-p < 0.8 | +5.86 | +3.84 | +1.81 | +11.73 | +9.70 | +7.67 | +17.59 | +15.56 | +13.54 | +23.45 | +21.43 | +19.40 |
| disagree or top-p < 0.9 | +6.05 | +3.00 | -0.06 | +12.11 | +9.05 | +6.00 | +18.16 | +15.11 | +12.05 | +24.22 | +21.16 | +18.11 |

### Latency budget: max thought tokens per gated row

| gate | ≤1000 ms (600 W) | binding | ≤900 ms (600 W) | ≤1000 ms (ds034 510 W) | ≤900 ms (ds034) | ≤1000 / ≤900, reversed read flat 57 ms (600 W) |
|---|---|---|---|---|---|---|
| top-p < 0.5 | 40 | p80 | 36 | 36 | 31 | — |
| top-p < 0.6 | 37 | p80 | 33 | 33 | 28 | — |
| top-p < 0.7 | 33 | p80 | 28 | 27 | 22 | — |
| top-p < 0.8 | 28 | p80 | 23 | 21 | 17 | — |
| top-p < 0.9 | 24 | p80 | 20 | 20 | 15 | — |
| disagree | 36 | p80 | 32 | 32 | 26 | 37 / 32 |
| margin < 0.1 | 242 | mean | 207 | 199 | 164 | — |
| margin < 0.3 | 37 | p80 | 33 | 33 | 28 | — |
| margin < 0.5 | 33 | p80 | 28 | 26 | 21 | — |
| disagree or top-p < 0.5 | 33 | p80 | 28 | 27 | 21 | 34 / 29 |
| disagree or top-p < 0.6 | 31 | p80 | 26 | 25 | 20 | 30 / 26 |
| disagree or top-p < 0.7 | 28 | p80 | 23 | 22 | 17 | 30 / 24 |
| disagree or top-p < 0.8 | 26 | p80 | 21 | 20 | 15 | 25 / 20 |
| disagree or top-p < 0.9 | 24 | p80 | 18 | 18 | 13 | 22 / 17 |

## Notes

- p80 is a cliff: once the gate covers about 20% of the latency rows, the p80 row is a gated row and must fit base + 57 ms + N/rate under the limit itself, so the budget drops from hundreds to ~15 tokens (gemma). Below that share the mean binds: budget ≈ (1000 − mean − share x 57) x rate / (share x 1000).
- The gate's share on the 300 latency rows differs a little from dev (columns 2-3); the budget uses the latency rows' own gate membership, so it can be lumpy near the p80 cliff.
- The what-if Δ index assumes the fix/break rates are the same in every benchmark; thinking is likelier to help reasoning rows (MMMU-Pro, R-Bench-M) than perception errors, and the research notes found 59% of gemma's errors confident (margin ≥ 0.5), which no gate on the first read can reach.
- The second-read cost (57 ms) is one gemma measurement on a cached shared image; qwen uses the same figure. A thinking pass may also need its own request round trip before decoding starts, not counted here.
- τ and m act on probabilities at the text T. gemma's text T (4.26) is sharper than its dev-fitted image T (~5.9), so the same τ gates fewer gemma rows than it would after an image recalibration (see R1).
- Thinking rows would need their own calibration; ECE is not modelled here.
