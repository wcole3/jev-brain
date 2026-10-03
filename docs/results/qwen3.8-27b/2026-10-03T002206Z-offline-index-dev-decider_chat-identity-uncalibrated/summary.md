# qwen3.8-27b offline: index-dev

## Provenance

- timestamp: 2026-10-03T002206Z
- repo commit: a4ad243
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- split: index-dev
- collected: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.769

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.769 | 0.060 | 0.837 | 0.330 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.769 | 0.060 | 0.839 | 0.330 |
| noul | 143 | 0.776 | 0.155 | 0.659 | 0.346 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.769 | 0.060 | 0.837 | 0.330 |

Noul: 143 rows, said yes 87, gold yes 57, false no 1, false yes 31

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.974 | 0.028 | 0.084 | 0.043 |
| index/ANLI | 171 | 0.749 | 0.074 | 0.643 | 0.368 |
| index/API-Bank | 27 | 0.889 | 0.104 | 1.025 | 0.194 |
| index/ARC-Challenge | 62 | 0.984 | 0.035 | 0.048 | 0.023 |
| index/ARC-Easy | 126 | 0.984 | 0.017 | 0.040 | 0.023 |
| index/Amazon ESCI | 266 | 0.617 | 0.158 | 1.001 | 0.535 |
| index/BANKING77 | 164 | 0.744 | 0.155 | 1.456 | 0.397 |
| index/BBH fixed-option tasks | 293 | 0.713 | 0.054 | 0.663 | 0.358 |
| index/BFCL | 258 | 0.996 | 0.021 | 0.024 | 0.008 |
| index/BPoMP | 258 | 0.926 | 0.080 | 0.205 | 0.115 |
| index/BRIGHT | 20 | 0.600 | 0.321 | 1.104 | 0.608 |
| index/CLINC150+OOS | 293 | 0.867 | 0.076 | 0.635 | 0.222 |
| index/CLadder | 266 | 0.602 | 0.097 | 0.612 | 0.431 |
| index/CRUXEval | 30 | 0.500 | 0.263 | 0.788 | 0.483 |
| index/ChessBench | 266 | 0.180 | 0.345 | 4.217 | 1.100 |
| index/ContractNLI | 102 | 0.873 | 0.108 | 0.503 | 0.252 |
| index/FinEntity | 111 | 0.856 | 0.072 | 0.394 | 0.216 |
| index/ForecastBench | 539 | 0.701 | 0.058 | 0.567 | 0.392 |
| index/GPQA Diamond | 11 | 0.455 | 0.232 | 0.979 | 0.540 |
| index/GSM8K | 142 | 0.641 | 0.094 | 0.932 | 0.481 |
| index/HLE | 27 | 0.074 | 0.461 | 2.529 | 1.106 |
| index/Habermas Machine | 90 | 0.389 | 0.291 | 1.684 | 0.816 |
| index/HellaSwag | 534 | 0.948 | 0.022 | 0.154 | 0.078 |
| index/HoVer claim verification | 213 | 0.723 | 0.073 | 0.520 | 0.353 |
| index/Home appliance simulator | 90 | 0.956 | 0.023 | 0.110 | 0.058 |
| index/Humicroedit | 140 | 0.579 | 0.218 | 0.853 | 0.572 |
| index/MMLU | 747 | 0.823 | 0.055 | 0.507 | 0.264 |
| index/MMLU-Pro | 641 | 0.583 | 0.077 | 1.276 | 0.534 |
| index/MuSR | 40 | 0.525 | 0.282 | 1.262 | 0.697 |
| index/NLI4CT | 293 | 0.785 | 0.063 | 0.427 | 0.270 |
| index/New Yorker caption matching | 28 | 0.714 | 0.156 | 0.680 | 0.347 |
| index/POP909-CL | 106 | 0.236 | 0.087 | 4.001 | 0.909 |
| index/PhishNChips phishing decisions | 106 | 0.764 | 0.086 | 0.480 | 0.322 |
| index/RAGTruth response-level hallucination | 143 | 0.776 | 0.155 | 0.659 | 0.346 |
| index/RouterBench | 1062 | 0.142 | 0.576 | 4.812 | 1.354 |
| index/SATA-Bench | 823 | 0.852 | 0.032 | 0.350 | 0.222 |
| index/SGD/SGD-X | 133 | 0.541 | 0.151 | 1.013 | 0.605 |
| index/SimpleBench | 1 | 0.000 | 0.374 | 1.110 | 0.655 |
| index/ToolRet | 46 | 0.891 | 0.094 | 0.311 | 0.184 |
| index/VAST | 160 | 0.544 | 0.204 | 1.207 | 0.663 |
| index/When2Call MCQ | 195 | 0.790 | 0.095 | 0.786 | 0.341 |
| index/WinoGrande | 68 | 0.824 | 0.098 | 0.350 | 0.227 |
| index/cfcolor | 266 | 0.613 | 0.062 | 0.668 | 0.472 |
| index/iSarcasmEval | 620 | 0.752 | 0.056 | 0.540 | 0.360 |
