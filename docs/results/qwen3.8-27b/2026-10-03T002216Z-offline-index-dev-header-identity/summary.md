# qwen3.8-27b offline: index-dev

## Provenance

- timestamp: 2026-10-03T002216Z
- repo commit: a4ad243
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- split: index-dev
- collected: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'header', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 0.9629807468103339}, 'b': 0.0, 'source': 'qwen3.8-27b/header/calibration.json', 'orders': 'identity'}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.779

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.779 | 0.074 | 0.812 | 0.316 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.778 | 0.075 | 0.815 | 0.317 |
| noul | 143 | 0.818 | 0.079 | 0.534 | 0.281 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.779 | 0.074 | 0.812 | 0.316 |

Noul: 143 rows, said yes 77, gold yes 57, false no 3, false yes 23

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.980 | 0.005 | 0.053 | 0.030 |
| index/ANLI | 171 | 0.772 | 0.055 | 0.591 | 0.324 |
| index/API-Bank | 27 | 0.889 | 0.092 | 1.110 | 0.204 |
| index/ARC-Challenge | 62 | 1.000 | 0.030 | 0.037 | 0.016 |
| index/ARC-Easy | 126 | 0.976 | 0.024 | 0.053 | 0.031 |
| index/Amazon ESCI | 266 | 0.605 | 0.184 | 1.076 | 0.548 |
| index/BANKING77 | 164 | 0.738 | 0.162 | 1.419 | 0.387 |
| index/BBH fixed-option tasks | 293 | 0.730 | 0.035 | 0.678 | 0.363 |
| index/BFCL | 258 | 0.992 | 0.012 | 0.032 | 0.015 |
| index/BPoMP | 258 | 0.930 | 0.065 | 0.211 | 0.124 |
| index/BRIGHT | 20 | 0.550 | 0.399 | 1.386 | 0.751 |
| index/CLINC150+OOS | 293 | 0.863 | 0.087 | 0.727 | 0.229 |
| index/CLadder | 266 | 0.632 | 0.100 | 0.574 | 0.402 |
| index/CRUXEval | 30 | 0.600 | 0.193 | 0.736 | 0.447 |
| index/ChessBench | 266 | 0.169 | 0.382 | 4.338 | 1.117 |
| index/ContractNLI | 102 | 0.873 | 0.087 | 0.458 | 0.216 |
| index/FinEntity | 111 | 0.874 | 0.103 | 0.449 | 0.234 |
| index/ForecastBench | 539 | 0.692 | 0.051 | 0.582 | 0.400 |
| index/GPQA Diamond | 11 | 0.455 | 0.214 | 0.988 | 0.534 |
| index/GSM8K | 142 | 0.662 | 0.160 | 0.924 | 0.480 |
| index/HLE | 27 | 0.148 | 0.444 | 2.649 | 1.142 |
| index/Habermas Machine | 90 | 0.356 | 0.327 | 1.721 | 0.834 |
| index/HellaSwag | 534 | 0.938 | 0.019 | 0.157 | 0.082 |
| index/HoVer claim verification | 213 | 0.718 | 0.059 | 0.514 | 0.348 |
| index/Home appliance simulator | 90 | 0.978 | 0.029 | 0.094 | 0.045 |
| index/Humicroedit | 140 | 0.564 | 0.201 | 0.862 | 0.581 |
| index/MMLU | 747 | 0.822 | 0.043 | 0.489 | 0.250 |
| index/MMLU-Pro | 641 | 0.580 | 0.074 | 1.258 | 0.529 |
| index/MuSR | 40 | 0.575 | 0.297 | 1.244 | 0.662 |
| index/NLI4CT | 293 | 0.819 | 0.057 | 0.404 | 0.255 |
| index/New Yorker caption matching | 28 | 0.714 | 0.139 | 0.619 | 0.322 |
| index/POP909-CL | 106 | 0.340 | 0.174 | 3.160 | 0.814 |
| index/PhishNChips phishing decisions | 106 | 0.953 | 0.078 | 0.187 | 0.101 |
| index/RAGTruth response-level hallucination | 143 | 0.818 | 0.079 | 0.534 | 0.281 |
| index/RouterBench | 1062 | 0.151 | 0.595 | 4.794 | 1.359 |
| index/SATA-Bench | 823 | 0.827 | 0.056 | 0.380 | 0.237 |
| index/SGD/SGD-X | 133 | 0.421 | 0.222 | 1.279 | 0.753 |
| index/SimpleBench | 1 | 0.000 | 0.415 | 1.629 | 0.953 |
| index/ToolRet | 46 | 0.913 | 0.072 | 0.238 | 0.130 |
| index/VAST | 160 | 0.662 | 0.152 | 0.915 | 0.504 |
| index/When2Call MCQ | 195 | 0.800 | 0.088 | 0.728 | 0.324 |
| index/WinoGrande | 68 | 0.926 | 0.110 | 0.258 | 0.152 |
| index/cfcolor | 266 | 0.583 | 0.115 | 0.684 | 0.481 |
| index/iSarcasmEval | 620 | 0.863 | 0.063 | 0.360 | 0.221 |
