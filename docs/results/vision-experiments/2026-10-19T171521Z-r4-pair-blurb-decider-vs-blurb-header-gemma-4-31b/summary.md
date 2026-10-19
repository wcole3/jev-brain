# gemma-4-31b R4 pair screen: blurb-decider vs blurb-header, image dev

## Provenance

- timestamp: 2026-10-19T171521Z
- repo commit: b953b23
- host: RTX PRO 6000 Blackwell, 510/600 W, drv 597.16, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- title: R4 pair screen
- set: blurb-decider
- control: blurb-header
- collect blurb-header calib-600: .cache/collect/gemma-4-31b/calib-600-blurb-header.jsonl.gz
- collect blurb-header index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-blurb-header.jsonl.gz
- collect blurb-decider calib-600: .cache/collect/gemma-4-31b/calib-600-blurb-decider.jsonl.gz
- collect blurb-decider index-dev-2k: .cache/collect/gemma-4-31b/index-dev-2k-blurb-decider.jsonl.gz
- collect blurb-header image dev: .cache/vision-collect/gemma-4-31b/r4-blurb-header/dev.jsonl.gz
- collect blurb-decider image dev: .cache/vision-collect/gemma-4-31b/r4-blurb-decider/dev.jsonl.gz
- fits: T per type on each arm's calib-600 identity reads, mean-prob, b = 0 (ruling R2); image: choice T
- subsets: all = every question both arms answered

Reports only; the owner picks.

## T (choice, from each arm's text calib-600 fit)

- blurb-header: 3.783
- blurb-decider: 3.842

## all (1462 rows)

vision_compare: `2026-10-19T171546Z-compare-all/` (paired bootstrap over image groups).

| arm | index | Δ index [95% CI] | accuracy | ECE | Δ ECE | NLL | Δ NLL | agreement |
|---|---|---|---|---|---|---|---|---|
| blurb-header | 78.25 | baseline | 0.805 | 0.0855 |  | 0.6153 |  |  |
| blurb-decider | 77.13 | -1.12 [-2.82, +0.48] | 0.802 | 0.0814 | -0.0041 | 0.6169 | +0.0016 | 0.9302 |

### Flip rate: identity vs reversed top answer (noul left out)

| grouping | bucket | blurb-header | blurb-decider |
|---|---|---|---|
| overall | all | 0.120 | 0.117 |
| type | choice | 0.120 | 0.117 |
| options | 2 | 0.050 | 0.028 |
| options | 3-5 | 0.045 | 0.060 |
| options | 6-26 | 0.452 | 0.444 |

### Predicted vs gold shown position (identity read, noul left out)

| arm | options | series | count by caller position |
|---|---|---|---|
| blurb-header | 2 | chosen | 227 312 |
| blurb-header | 2 | gold | 247 292 |
| blurb-header | 3-5 | chosen | 184 160 172 143 3 |
| blurb-header | 3-5 | gold | 187 155 175 143 2 |
| blurb-header | 6-26 | chosen | 48 33 32 36 25 33 19 13 10 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-header | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-decider | 2 | chosen | 222 317 |
| blurb-decider | 2 | gold | 247 292 |
| blurb-decider | 3-5 | chosen | 185 154 172 148 3 |
| blurb-decider | 3-5 | gold | 187 155 175 143 2 |
| blurb-decider | 6-26 | chosen | 43 35 35 40 30 29 20 10 9 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |
| blurb-decider | 6-26 | gold | 36 33 32 38 45 31 13 10 7 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 |

