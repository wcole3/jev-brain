# qwen3.6-27b offline: index-dev

## Provenance

- timestamp: 2026-10-03T004723Z
- repo commit: 49152c6
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: index-dev
- collected: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'header', 'orders': 'identity', 'calibration': {'T': {'choice': 1.626739845878971, 'score': 1.9577583066935726, 'noul': 1.2842455905297372}, 'b': 0.0, 'source': 'qwen3.6-27b/header/calibration.json', 'orders': 'identity'}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.780

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.780 | 0.045 | 0.672 | 0.299 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.780 | 0.046 | 0.674 | 0.300 |
| noul | 143 | 0.832 | 0.110 | 0.423 | 0.230 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.780 | 0.045 | 0.672 | 0.299 |

Noul: 143 rows, said yes 69, gold yes 57, false no 6, false yes 18

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.975 | 0.017 | 0.069 | 0.036 |
| index/ANLI | 171 | 0.807 | 0.097 | 0.578 | 0.319 |
| index/API-Bank | 27 | 0.852 | 0.102 | 0.965 | 0.246 |
| index/ARC-Challenge | 62 | 0.968 | 0.062 | 0.114 | 0.050 |
| index/ARC-Easy | 126 | 0.984 | 0.038 | 0.058 | 0.019 |
| index/Amazon ESCI | 266 | 0.571 | 0.208 | 1.056 | 0.584 |
| index/BANKING77 | 164 | 0.713 | 0.086 | 1.445 | 0.417 |
| index/BBH fixed-option tasks | 293 | 0.734 | 0.059 | 0.654 | 0.347 |
| index/BFCL | 258 | 0.992 | 0.025 | 0.033 | 0.011 |
| index/BPoMP | 258 | 0.837 | 0.110 | 0.369 | 0.221 |
| index/BRIGHT | 20 | 0.600 | 0.307 | 0.870 | 0.535 |
| index/CLINC150+OOS | 293 | 0.846 | 0.092 | 0.676 | 0.226 |
| index/CLadder | 266 | 0.741 | 0.086 | 0.539 | 0.367 |
| index/CRUXEval | 30 | 0.467 | 0.215 | 0.915 | 0.548 |
| index/ChessBench | 266 | 0.150 | 0.206 | 3.485 | 0.985 |
| index/ContractNLI | 102 | 0.853 | 0.107 | 0.518 | 0.267 |
| index/FinEntity | 111 | 0.856 | 0.102 | 0.410 | 0.215 |
| index/ForecastBench | 539 | 0.686 | 0.085 | 0.597 | 0.410 |
| index/GPQA Diamond | 11 | 0.455 | 0.211 | 1.038 | 0.595 |
| index/GSM8K | 142 | 0.634 | 0.119 | 0.975 | 0.474 |
| index/HLE | 27 | 0.185 | 0.343 | 2.013 | 0.955 |
| index/Habermas Machine | 90 | 0.422 | 0.243 | 1.476 | 0.781 |
| index/HellaSwag | 534 | 0.951 | 0.058 | 0.168 | 0.074 |
| index/HoVer claim verification | 213 | 0.704 | 0.143 | 0.640 | 0.428 |
| index/Home appliance simulator | 90 | 0.956 | 0.086 | 0.181 | 0.072 |
| index/Humicroedit | 140 | 0.593 | 0.172 | 0.766 | 0.538 |
| index/MMLU | 747 | 0.857 | 0.038 | 0.402 | 0.203 |
| index/MMLU-Pro | 641 | 0.629 | 0.041 | 1.139 | 0.491 |
| index/MuSR | 40 | 0.575 | 0.266 | 0.902 | 0.535 |
| index/NLI4CT | 293 | 0.836 | 0.059 | 0.408 | 0.257 |
| index/New Yorker caption matching | 28 | 0.750 | 0.102 | 0.592 | 0.306 |
| index/POP909-CL | 106 | 0.330 | 0.167 | 3.532 | 0.867 |
| index/PhishNChips phishing decisions | 106 | 0.934 | 0.106 | 0.201 | 0.107 |
| index/RAGTruth response-level hallucination | 143 | 0.832 | 0.110 | 0.423 | 0.230 |
| index/RouterBench | 1062 | 0.161 | 0.443 | 3.146 | 1.160 |
| index/SATA-Bench | 823 | 0.849 | 0.055 | 0.339 | 0.212 |
| index/SGD/SGD-X | 133 | 0.195 | 0.446 | 1.431 | 0.922 |
| index/SimpleBench | 1 | 0.000 | 0.605 | 2.039 | 1.154 |
| index/ToolRet | 46 | 0.935 | 0.063 | 0.111 | 0.071 |
| index/VAST | 160 | 0.637 | 0.144 | 0.893 | 0.509 |
| index/When2Call MCQ | 195 | 0.831 | 0.039 | 0.499 | 0.262 |
| index/WinoGrande | 68 | 0.897 | 0.089 | 0.296 | 0.173 |
| index/cfcolor | 266 | 0.658 | 0.053 | 0.638 | 0.444 |
| index/iSarcasmEval | 620 | 0.829 | 0.054 | 0.426 | 0.266 |
