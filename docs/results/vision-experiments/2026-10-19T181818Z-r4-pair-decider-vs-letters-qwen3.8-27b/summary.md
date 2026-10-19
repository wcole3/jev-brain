# qwen3.8-27b R4 pair screen: decider vs letters, image dev

## Provenance

- timestamp: 2026-10-19T181818Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- title: R4 pair screen
- set: decider
- control: letters
- collect letters calib-600: .cache/collect/qwen3.8-27b/calib-600-letters.jsonl.gz
- collect letters index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-letters.jsonl.gz
- collect decider calib-600: .cache/collect/qwen3.8-27b/calib-600-decider.jsonl.gz
- collect decider index-dev-2k: .cache/collect/qwen3.8-27b/index-dev-2k-decider.jsonl.gz
- collect letters image dev: .cache/vision-collect/qwen3.8-27b/labels-letters/dev.jsonl.gz
- collect decider image dev: .cache/vision-collect/qwen3.8-27b/r4-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered

Reports only; the owner picks.

## T (choice, from each arm's text calib-600 fit)

- letters: 1.492
- decider: 1.471

## all (1462 rows)

vision_compare: `2026-10-19T181844Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 73.49 | baseline | 0.770 | 0.0399 |  | 0.5999 |  |  |
| decider | 72.45 | -1.04 [-2.89, +0.80] | 0.765 | 0.1007 | +0.0608 | 0.6577 | +0.0578 | 0.9234 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | decider |
|---|---|---|---|
| overall | all | 0.204 | 0.198 |
| type | choice | 0.204 | 0.198 |
| options | 2 | 0.102 | 0.111 |
| options | 3-5 | 0.171 | 0.160 |
| options | 6-26 | 0.498 | 0.475 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 227 312 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 180 139 198 142 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 82 42 38 28 19 15 13 5 7 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| decider | 2 | chosen | 232 307 |
| decider | 2 | gold | 247 292 |
| decider | 3-5 | chosen | 179 144 187 149 3 |
| decider | 3-5 | gold | 187 155 175 143 2 |
| decider | 6-26 | chosen | 91 38 41 30 19 11 8 6 6 11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| decider | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

