# qwen3.6-27b offline: index-dev

## Provenance

- timestamp: 2026-10-02T163722Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: index-dev
- collected: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'header', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.780

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.780 | 0.105 | 0.829 | 0.327 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.780 | 0.105 | 0.832 | 0.328 |
| noul | 143 | 0.832 | 0.106 | 0.458 | 0.229 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.780 | 0.105 | 0.829 | 0.327 |

Noul: 143 rows, said yes 69, gold yes 57, false no 6, false yes 18

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.975 | 0.012 | 0.066 | 0.038 |
| index/ANLI | 171 | 0.807 | 0.136 | 0.714 | 0.340 |
| index/API-Bank | 27 | 0.852 | 0.137 | 1.381 | 0.246 |
| index/ARC-Challenge | 62 | 0.968 | 0.033 | 0.094 | 0.047 |
| index/ARC-Easy | 126 | 0.984 | 0.011 | 0.027 | 0.016 |
| index/Amazon ESCI | 266 | 0.571 | 0.298 | 1.410 | 0.669 |
| index/BANKING77 | 164 | 0.713 | 0.180 | 1.842 | 0.465 |
| index/BBH fixed-option tasks | 293 | 0.734 | 0.067 | 0.654 | 0.354 |
| index/BFCL | 258 | 0.992 | 0.009 | 0.016 | 0.009 |
| index/BPoMP | 258 | 0.837 | 0.066 | 0.313 | 0.200 |
| index/BRIGHT | 20 | 0.600 | 0.343 | 1.263 | 0.610 |
| index/CLINC150+OOS | 293 | 0.846 | 0.088 | 0.714 | 0.234 |
| index/CLadder | 266 | 0.741 | 0.117 | 0.575 | 0.388 |
| index/CRUXEval | 30 | 0.467 | 0.306 | 1.051 | 0.610 |
| index/ChessBench | 266 | 0.150 | 0.386 | 4.540 | 1.129 |
| index/ContractNLI | 102 | 0.853 | 0.079 | 0.512 | 0.252 |
| index/FinEntity | 111 | 0.856 | 0.115 | 0.491 | 0.221 |
| index/ForecastBench | 539 | 0.686 | 0.037 | 0.571 | 0.392 |
| index/GPQA Diamond | 11 | 0.455 | 0.213 | 1.109 | 0.658 |
| index/GSM8K | 142 | 0.634 | 0.082 | 0.937 | 0.465 |
| index/HLE | 27 | 0.185 | 0.518 | 2.533 | 1.095 |
| index/Habermas Machine | 90 | 0.422 | 0.344 | 1.943 | 0.877 |
| index/HellaSwag | 534 | 0.951 | 0.008 | 0.135 | 0.070 |
| index/HoVer claim verification | 213 | 0.704 | 0.210 | 0.851 | 0.483 |
| index/Home appliance simulator | 90 | 0.956 | 0.024 | 0.175 | 0.075 |
| index/Humicroedit | 140 | 0.593 | 0.252 | 0.964 | 0.610 |
| index/MMLU | 747 | 0.857 | 0.060 | 0.430 | 0.211 |
| index/MMLU-Pro | 641 | 0.629 | 0.108 | 1.230 | 0.509 |
| index/MuSR | 40 | 0.575 | 0.299 | 1.146 | 0.614 |
| index/NLI4CT | 293 | 0.836 | 0.095 | 0.456 | 0.268 |
| index/New Yorker caption matching | 28 | 0.750 | 0.142 | 0.586 | 0.332 |
| index/POP909-CL | 106 | 0.330 | 0.119 | 3.733 | 0.851 |
| index/PhishNChips phishing decisions | 106 | 0.934 | 0.071 | 0.149 | 0.090 |
| index/RAGTruth response-level hallucination | 143 | 0.832 | 0.106 | 0.458 | 0.229 |
| index/RouterBench | 1062 | 0.161 | 0.617 | 4.491 | 1.368 |
| index/SATA-Bench | 823 | 0.849 | 0.088 | 0.403 | 0.231 |
| index/SGD/SGD-X | 133 | 0.195 | 0.566 | 1.849 | 1.132 |
| index/SimpleBench | 1 | 0.000 | 0.812 | 2.708 | 1.540 |
| index/ToolRet | 46 | 0.935 | 0.052 | 0.135 | 0.075 |
| index/VAST | 160 | 0.637 | 0.226 | 1.115 | 0.564 |
| index/When2Call MCQ | 195 | 0.831 | 0.103 | 0.593 | 0.274 |
| index/WinoGrande | 68 | 0.897 | 0.064 | 0.265 | 0.164 |
| index/cfcolor | 266 | 0.658 | 0.130 | 0.691 | 0.470 |
| index/iSarcasmEval | 620 | 0.829 | 0.055 | 0.430 | 0.261 |
