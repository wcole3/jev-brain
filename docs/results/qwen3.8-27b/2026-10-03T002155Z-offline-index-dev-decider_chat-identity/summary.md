# qwen3.8-27b offline: index-dev

## Provenance

- timestamp: 2026-10-03T002155Z
- repo commit: a4ad243
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- split: index-dev
- collected: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.4958925733915396, 'score': 1.0, 'noul': 0.9701214258536706}, 'b': 0.0, 'source': 'qwen3.8-27b/decider_chat/calibration.json', 'orders': 'identity'}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.769

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.769 | 0.021 | 0.734 | 0.320 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.769 | 0.021 | 0.735 | 0.320 |
| noul | 143 | 0.776 | 0.145 | 0.669 | 0.347 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.769 | 0.021 | 0.734 | 0.320 |

Noul: 143 rows, said yes 87, gold yes 57, false no 1, false yes 31

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.974 | 0.068 | 0.120 | 0.054 |
| index/ANLI | 171 | 0.749 | 0.119 | 0.664 | 0.380 |
| index/API-Bank | 27 | 0.889 | 0.089 | 0.747 | 0.190 |
| index/ARC-Challenge | 62 | 0.984 | 0.067 | 0.085 | 0.032 |
| index/ARC-Easy | 126 | 0.984 | 0.031 | 0.059 | 0.025 |
| index/Amazon ESCI | 266 | 0.617 | 0.071 | 0.912 | 0.501 |
| index/BANKING77 | 164 | 0.744 | 0.098 | 1.183 | 0.367 |
| index/BBH fixed-option tasks | 293 | 0.713 | 0.092 | 0.702 | 0.372 |
| index/BFCL | 258 | 0.996 | 0.043 | 0.051 | 0.015 |
| index/BPoMP | 258 | 0.926 | 0.130 | 0.267 | 0.143 |
| index/BRIGHT | 20 | 0.600 | 0.255 | 0.845 | 0.556 |
| index/CLINC150+OOS | 293 | 0.867 | 0.053 | 0.587 | 0.211 |
| index/CLadder | 266 | 0.602 | 0.089 | 0.616 | 0.431 |
| index/CRUXEval | 30 | 0.500 | 0.218 | 0.790 | 0.470 |
| index/ChessBench | 266 | 0.180 | 0.183 | 3.428 | 0.983 |
| index/ContractNLI | 102 | 0.873 | 0.160 | 0.536 | 0.278 |
| index/FinEntity | 111 | 0.856 | 0.084 | 0.413 | 0.221 |
| index/ForecastBench | 539 | 0.701 | 0.071 | 0.582 | 0.400 |
| index/GPQA Diamond | 11 | 0.455 | 0.247 | 0.979 | 0.530 |
| index/GSM8K | 142 | 0.641 | 0.169 | 1.029 | 0.515 |
| index/HLE | 27 | 0.074 | 0.355 | 2.135 | 0.989 |
| index/Habermas Machine | 90 | 0.389 | 0.202 | 1.418 | 0.746 |
| index/HellaSwag | 534 | 0.948 | 0.068 | 0.195 | 0.089 |
| index/HoVer claim verification | 213 | 0.723 | 0.043 | 0.514 | 0.346 |
| index/Home appliance simulator | 90 | 0.956 | 0.045 | 0.123 | 0.056 |
| index/Humicroedit | 140 | 0.579 | 0.155 | 0.743 | 0.526 |
| index/MMLU | 747 | 0.823 | 0.046 | 0.497 | 0.262 |
| index/MMLU-Pro | 641 | 0.583 | 0.053 | 1.244 | 0.532 |
| index/MuSR | 40 | 0.525 | 0.229 | 1.049 | 0.638 |
| index/NLI4CT | 293 | 0.785 | 0.088 | 0.438 | 0.280 |
| index/New Yorker caption matching | 28 | 0.714 | 0.159 | 0.708 | 0.347 |
| index/POP909-CL | 106 | 0.236 | 0.105 | 3.832 | 0.923 |
| index/PhishNChips phishing decisions | 106 | 0.764 | 0.115 | 0.503 | 0.334 |
| index/RAGTruth response-level hallucination | 143 | 0.776 | 0.145 | 0.669 | 0.347 |
| index/RouterBench | 1062 | 0.142 | 0.456 | 3.561 | 1.213 |
| index/SATA-Bench | 823 | 0.852 | 0.060 | 0.364 | 0.227 |
| index/SGD/SGD-X | 133 | 0.541 | 0.086 | 0.951 | 0.572 |
| index/SimpleBench | 1 | 0.000 | 0.332 | 1.187 | 0.664 |
| index/ToolRet | 46 | 0.891 | 0.076 | 0.270 | 0.166 |
| index/VAST | 160 | 0.544 | 0.128 | 1.067 | 0.626 |
| index/When2Call MCQ | 195 | 0.790 | 0.096 | 0.688 | 0.339 |
| index/WinoGrande | 68 | 0.824 | 0.100 | 0.383 | 0.241 |
| index/cfcolor | 266 | 0.613 | 0.034 | 0.654 | 0.463 |
| index/iSarcasmEval | 620 | 0.752 | 0.047 | 0.533 | 0.357 |
