# gemma-4-31b offline: index-dev

## Provenance

- timestamp: 2026-10-03T001647Z
- repo commit: ae318d3
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- split: index-dev
- collected: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'question_first', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.749

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.749 | 0.241 | 3.340 | 0.488 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.748 | 0.242 | 3.348 | 0.489 |
| noul | 143 | 0.846 | 0.154 | 2.574 | 0.307 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.749 | 0.241 | 3.340 | 0.488 |

Noul: 143 rows, said yes 69, gold yes 57, false no 5, false yes 17

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.900 | 0.098 | 1.323 | 0.196 |
| index/ANLI | 171 | 0.754 | 0.238 | 3.138 | 0.477 |
| index/API-Bank | 27 | 0.889 | 0.105 | 1.622 | 0.205 |
| index/ARC-Challenge | 62 | 1.000 | 0.001 | 0.001 | 0.000 |
| index/ARC-Easy | 126 | 0.984 | 0.016 | 0.175 | 0.032 |
| index/Amazon ESCI | 266 | 0.650 | 0.345 | 5.259 | 0.690 |
| index/BANKING77 | 164 | 0.744 | 0.250 | 4.691 | 0.506 |
| index/BBH fixed-option tasks | 293 | 0.744 | 0.253 | 3.011 | 0.499 |
| index/BFCL | 258 | 0.992 | 0.007 | 0.025 | 0.014 |
| index/BPoMP | 258 | 0.872 | 0.124 | 1.599 | 0.245 |
| index/BRIGHT | 20 | 0.650 | 0.350 | 6.309 | 0.700 |
| index/CLINC150+OOS | 293 | 0.894 | 0.105 | 1.806 | 0.211 |
| index/CLadder | 266 | 0.733 | 0.257 | 3.207 | 0.516 |
| index/CRUXEval | 30 | 0.433 | 0.542 | 4.429 | 1.073 |
| index/ChessBench | 266 | 0.158 | 0.766 | 10.282 | 1.571 |
| index/ContractNLI | 102 | 0.804 | 0.196 | 2.690 | 0.392 |
| index/FinEntity | 111 | 0.928 | 0.073 | 0.563 | 0.139 |
| index/ForecastBench | 539 | 0.755 | 0.241 | 3.056 | 0.482 |
| index/GPQA Diamond | 11 | 0.455 | 0.505 | 3.707 | 1.022 |
| index/GSM8K | 142 | 0.577 | 0.379 | 2.738 | 0.780 |
| index/HLE | 27 | 0.185 | 0.774 | 10.067 | 1.564 |
| index/Habermas Machine | 90 | 0.400 | 0.560 | 5.067 | 1.098 |
| index/HellaSwag | 534 | 0.923 | 0.071 | 0.672 | 0.145 |
| index/HoVer claim verification | 213 | 0.765 | 0.235 | 4.125 | 0.469 |
| index/Home appliance simulator | 90 | 0.967 | 0.036 | 0.488 | 0.068 |
| index/Humicroedit | 140 | 0.636 | 0.367 | 5.243 | 0.729 |
| index/MMLU | 747 | 0.847 | 0.146 | 1.518 | 0.293 |
| index/MMLU-Pro | 641 | 0.535 | 0.422 | 4.054 | 0.868 |
| index/MuSR | 40 | 0.600 | 0.392 | 4.950 | 0.774 |
| index/NLI4CT | 293 | 0.826 | 0.173 | 2.539 | 0.340 |
| index/New Yorker caption matching | 28 | 0.679 | 0.314 | 2.703 | 0.629 |
| index/POP909-CL | 106 | 0.406 | 0.450 | 6.177 | 1.018 |
| index/PhishNChips phishing decisions | 106 | 0.896 | 0.104 | 1.536 | 0.208 |
| index/RAGTruth response-level hallucination | 143 | 0.846 | 0.154 | 2.574 | 0.307 |
| index/RouterBench | 1062 | 0.153 | 0.831 | 13.993 | 1.674 |
| index/SATA-Bench | 823 | 0.852 | 0.147 | 2.082 | 0.291 |
| index/SGD/SGD-X | 133 | 0.090 | 0.908 | 14.139 | 1.813 |
| index/SimpleBench | 1 | 1.000 | 0.000 | 0.000 | 0.000 |
| index/ToolRet | 46 | 0.978 | 0.022 | 0.379 | 0.043 |
| index/VAST | 160 | 0.637 | 0.351 | 5.121 | 0.708 |
| index/When2Call MCQ | 195 | 0.667 | 0.331 | 4.055 | 0.652 |
| index/WinoGrande | 68 | 0.882 | 0.119 | 1.465 | 0.232 |
| index/cfcolor | 266 | 0.624 | 0.370 | 4.896 | 0.731 |
| index/iSarcasmEval | 620 | 0.723 | 0.270 | 2.899 | 0.538 |
