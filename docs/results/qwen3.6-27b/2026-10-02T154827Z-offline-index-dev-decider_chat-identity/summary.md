# qwen3.6-27b offline: index-dev

## Provenance

- timestamp: 2026-10-02T154827Z
- repo commit: 72ef31e-dirty
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: index-dev
- collected: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.6479149611375679, 'score': 6.323441128895665, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json'}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.761

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.761 | 0.040 | 0.723 | 0.322 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.760 | 0.041 | 0.725 | 0.323 |
| noul | 143 | 0.846 | 0.097 | 0.506 | 0.270 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.761 | 0.040 | 0.723 | 0.322 |

Noul: 143 rows, said yes 71, gold yes 57, false no 4, false yes 18

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.935 | 0.027 | 0.148 | 0.086 |
| index/ANLI | 171 | 0.760 | 0.047 | 0.630 | 0.358 |
| index/API-Bank | 27 | 0.852 | 0.143 | 0.940 | 0.250 |
| index/ARC-Challenge | 62 | 0.968 | 0.064 | 0.127 | 0.058 |
| index/ARC-Easy | 126 | 0.968 | 0.040 | 0.060 | 0.025 |
| index/Amazon ESCI | 266 | 0.609 | 0.188 | 0.949 | 0.534 |
| index/BANKING77 | 164 | 0.695 | 0.099 | 1.424 | 0.420 |
| index/BBH fixed-option tasks | 293 | 0.734 | 0.062 | 0.655 | 0.344 |
| index/BFCL | 258 | 0.996 | 0.024 | 0.032 | 0.009 |
| index/BPoMP | 258 | 0.868 | 0.139 | 0.360 | 0.209 |
| index/BRIGHT | 20 | 0.650 | 0.280 | 0.879 | 0.514 |
| index/CLINC150+OOS | 293 | 0.860 | 0.109 | 0.669 | 0.229 |
| index/CLadder | 266 | 0.692 | 0.044 | 0.561 | 0.381 |
| index/CRUXEval | 30 | 0.567 | 0.290 | 0.869 | 0.491 |
| index/ChessBench | 266 | 0.150 | 0.192 | 3.547 | 0.977 |
| index/ContractNLI | 102 | 0.775 | 0.094 | 0.621 | 0.337 |
| index/FinEntity | 111 | 0.856 | 0.054 | 0.431 | 0.231 |
| index/ForecastBench | 539 | 0.711 | 0.071 | 0.545 | 0.366 |
| index/GPQA Diamond | 11 | 0.364 | 0.356 | 0.989 | 0.564 |
| index/GSM8K | 142 | 0.641 | 0.147 | 1.017 | 0.491 |
| index/HLE | 27 | 0.222 | 0.339 | 1.985 | 0.947 |
| index/Habermas Machine | 90 | 0.344 | 0.274 | 1.483 | 0.802 |
| index/HellaSwag | 534 | 0.953 | 0.067 | 0.177 | 0.074 |
| index/HoVer claim verification | 213 | 0.690 | 0.154 | 0.650 | 0.438 |
| index/Home appliance simulator | 90 | 0.944 | 0.069 | 0.215 | 0.091 |
| index/Humicroedit | 140 | 0.571 | 0.191 | 0.788 | 0.550 |
| index/MMLU | 747 | 0.851 | 0.043 | 0.417 | 0.214 |
| index/MMLU-Pro | 641 | 0.637 | 0.043 | 1.121 | 0.485 |
| index/MuSR | 40 | 0.500 | 0.235 | 0.945 | 0.583 |
| index/NLI4CT | 293 | 0.843 | 0.044 | 0.408 | 0.253 |
| index/New Yorker caption matching | 28 | 0.750 | 0.262 | 0.659 | 0.338 |
| index/POP909-CL | 106 | 0.198 | 0.101 | 4.343 | 0.941 |
| index/PhishNChips phishing decisions | 106 | 0.736 | 0.113 | 0.528 | 0.355 |
| index/RAGTruth response-level hallucination | 143 | 0.846 | 0.097 | 0.506 | 0.270 |
| index/RouterBench | 1062 | 0.148 | 0.419 | 3.300 | 1.174 |
| index/SATA-Bench | 823 | 0.866 | 0.022 | 0.305 | 0.188 |
| index/SGD/SGD-X | 133 | 0.165 | 0.463 | 1.454 | 0.945 |
| index/SimpleBench | 1 | 0.000 | 0.654 | 2.245 | 1.250 |
| index/ToolRet | 46 | 0.891 | 0.109 | 0.201 | 0.142 |
| index/VAST | 160 | 0.594 | 0.151 | 1.051 | 0.586 |
| index/When2Call MCQ | 195 | 0.815 | 0.064 | 0.532 | 0.281 |
| index/WinoGrande | 68 | 0.897 | 0.139 | 0.325 | 0.184 |
| index/cfcolor | 266 | 0.609 | 0.065 | 0.676 | 0.478 |
| index/iSarcasmEval | 620 | 0.776 | 0.040 | 0.509 | 0.333 |
