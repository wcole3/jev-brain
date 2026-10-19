# gemma-4-31b R4 pair screen: decider vs letters, image dev

## Provenance

- timestamp: 2026-10-19T153546Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- title: R4 pair screen
- set: decider
- control: letters
- collect letters calib-600: .cache/collect/gemma-4-31b/calib-600-letters.jsonl.gz
- collect letters index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-letters.jsonl.gz
- collect decider calib-600: .cache/collect/gemma-4-31b/calib-600-decider.jsonl.gz
- collect decider index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-decider.jsonl.gz
- collect letters image dev: .cache/vision-collect/gemma-4-31b/labels-letters/dev.jsonl.gz
- collect decider image dev: .cache/vision-collect/gemma-4-31b/r4-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered

Reports only; the owner picks.

## T (choice, from each arm's text calib-600 fit)

- letters: 3.947
- decider: 3.875

## all (1462 rows)

vision_compare: `2026-10-19T153611Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| letters | 77.09 | baseline | 0.802 | 0.0921 |  | 0.6260 |  |  |
| decider | 77.96 | +0.87 [-0.77, +2.46] | 0.805 | 0.0770 | -0.0150 | 0.6135 | -0.0126 | 0.9343 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | letters | decider |
|---|---|---|---|
| overall | all | 0.127 | 0.134 |
| type | choice | 0.127 | 0.134 |
| options | 2 | 0.048 | 0.048 |
| options | 3-5 | 0.060 | 0.073 |
| options | 6-26 | 0.460 | 0.467 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| letters | 2 | chosen | 225 314 |
| letters | 2 | gold | 247 292 |
| letters | 3-5 | chosen | 186 157 170 146 3 |
| letters | 3-5 | gold | 187 155 175 143 2 |
| letters | 6-26 | chosen | 48 36 30 36 32 36 15 10 9 9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| letters | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| decider | 2 | chosen | 222 317 |
| decider | 2 | gold | 247 292 |
| decider | 3-5 | chosen | 186 153 169 151 3 |
| decider | 3-5 | gold | 187 155 175 143 2 |
| decider | 6-26 | chosen | 40 35 31 36 30 39 16 13 11 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| decider | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

