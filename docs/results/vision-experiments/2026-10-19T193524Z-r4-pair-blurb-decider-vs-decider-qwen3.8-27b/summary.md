# qwen3.8-27b R4 pair screen: blurb-decider vs decider, image dev

## Provenance

- timestamp: 2026-10-19T193524Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- title: R4 pair screen
- set: blurb-decider
- control: decider
- collect decider calib-600: .cache/collect/qwen3.8-27b/calib-600-decider.jsonl.gz
- collect decider index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-decider.jsonl.gz
- collect blurb-decider calib-600: .cache/collect/qwen3.8-27b/calib-600-blurb-decider.jsonl.gz
- collect blurb-decider index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-blurb-decider.jsonl.gz
- collect decider image dev: .cache/vision-collect/qwen3.8-27b/r4-decider/dev.jsonl.gz
- collect blurb-decider image dev: .cache/vision-collect/qwen3.8-27b/r4-blurb-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered

Reports only; the owner picks.

## T (choice, from each arm's text calib-600 fit)

- decider: 1.471
- blurb-decider: 1.546

## all (1462 rows)

vision_compare: `2026-10-19T193552Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| decider | 72.45 | baseline | 0.765 | 0.1007 |  | 0.6577 |  |  |
| blurb-decider | 72.96 | +0.51 [-1.46, +2.48] | 0.767 | 0.0893 | -0.0113 | 0.6333 | -0.0244 | 0.9172 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | decider | blurb-decider |
|---|---|---|---|
| overall | all | 0.198 | 0.174 |
| type | choice | 0.198 | 0.174 |
| options | 2 | 0.111 | 0.078 |
| options | 3-5 | 0.160 | 0.139 |
| options | 6-26 | 0.475 | 0.464 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| decider | 2 | chosen | 232 307 |
| decider | 2 | gold | 247 292 |
| decider | 3-5 | chosen | 179 144 187 149 3 |
| decider | 3-5 | gold | 187 155 175 143 2 |
| decider | 6-26 | chosen | 91 38 41 30 19 11 8 6 6 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| decider | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-decider | 2 | chosen | 257 282 |
| blurb-decider | 2 | gold | 247 292 |
| blurb-decider | 3-5 | chosen | 185 146 187 142 2 |
| blurb-decider | 3-5 | gold | 187 155 175 143 2 |
| blurb-decider | 6-26 | chosen | 70 40 53 31 19 16 12 6 5 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-decider | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

