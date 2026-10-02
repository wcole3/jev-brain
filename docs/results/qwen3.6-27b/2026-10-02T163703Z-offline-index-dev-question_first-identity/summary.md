# qwen3.6-27b offline: index-dev

## Provenance

- timestamp: 2026-10-02T163703Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: index-dev
- collected: .cache/collect/qwen3.6-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'question_first', 'orders': 'identity', 'calibration': {'T': {'choice': 1.4836733616074274, 'score': 8.054659971948029, 'noul': 1.1446681550320104}, 'b': 0.2527877422356274, 'source': 'qwen3.6-27b/question_first/calibration.json', 'orders': 'identity'}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.751

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.751 | 0.046 | 0.752 | 0.340 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.750 | 0.046 | 0.755 | 0.341 |
| noul | 143 | 0.860 | 0.070 | 0.379 | 0.208 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.751 | 0.046 | 0.752 | 0.340 |

Noul: 143 rows, said yes 65, gold yes 57, false no 6, false yes 14

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.937 | 0.025 | 0.155 | 0.089 |
| index/ANLI | 171 | 0.760 | 0.099 | 0.663 | 0.373 |
| index/API-Bank | 27 | 0.815 | 0.236 | 1.524 | 0.437 |
| index/ARC-Challenge | 62 | 0.968 | 0.055 | 0.109 | 0.056 |
| index/ARC-Easy | 126 | 0.976 | 0.029 | 0.050 | 0.023 |
| index/Amazon ESCI | 266 | 0.639 | 0.132 | 0.925 | 0.495 |
| index/BANKING77 | 164 | 0.695 | 0.118 | 1.508 | 0.428 |
| index/BBH fixed-option tasks | 293 | 0.734 | 0.079 | 0.683 | 0.362 |
| index/BFCL | 258 | 0.996 | 0.017 | 0.023 | 0.007 |
| index/BPoMP | 258 | 0.922 | 0.125 | 0.265 | 0.144 |
| index/BRIGHT | 20 | 0.550 | 0.323 | 0.769 | 0.512 |
| index/CLINC150+OOS | 293 | 0.836 | 0.054 | 0.674 | 0.230 |
| index/CLadder | 266 | 0.688 | 0.050 | 0.555 | 0.380 |
| index/CRUXEval | 30 | 0.367 | 0.285 | 1.069 | 0.657 |
| index/ChessBench | 266 | 0.132 | 0.260 | 3.754 | 1.039 |
| index/ContractNLI | 102 | 0.775 | 0.078 | 0.602 | 0.327 |
| index/FinEntity | 111 | 0.883 | 0.073 | 0.331 | 0.177 |
| index/ForecastBench | 539 | 0.712 | 0.091 | 0.527 | 0.351 |
| index/GPQA Diamond | 11 | 0.455 | 0.388 | 0.988 | 0.569 |
| index/GSM8K | 142 | 0.401 | 0.087 | 1.493 | 0.710 |
| index/HLE | 27 | 0.185 | 0.369 | 2.054 | 0.971 |
| index/Habermas Machine | 90 | 0.389 | 0.226 | 1.304 | 0.701 |
| index/HellaSwag | 534 | 0.951 | 0.033 | 0.139 | 0.068 |
| index/HoVer claim verification | 213 | 0.695 | 0.204 | 0.776 | 0.482 |
| index/Home appliance simulator | 90 | 0.933 | 0.092 | 0.283 | 0.115 |
| index/Humicroedit | 140 | 0.607 | 0.181 | 0.822 | 0.554 |
| index/MMLU | 747 | 0.858 | 0.040 | 0.394 | 0.205 |
| index/MMLU-Pro | 641 | 0.505 | 0.034 | 1.477 | 0.618 |
| index/MuSR | 40 | 0.525 | 0.261 | 0.955 | 0.593 |
| index/NLI4CT | 293 | 0.778 | 0.053 | 0.478 | 0.311 |
| index/New Yorker caption matching | 28 | 0.571 | 0.151 | 1.076 | 0.517 |
| index/POP909-CL | 106 | 0.226 | 0.099 | 3.730 | 0.909 |
| index/PhishNChips phishing decisions | 106 | 0.792 | 0.098 | 0.447 | 0.299 |
| index/RAGTruth response-level hallucination | 143 | 0.860 | 0.070 | 0.379 | 0.208 |
| index/RouterBench | 1062 | 0.137 | 0.483 | 3.280 | 1.223 |
| index/SATA-Bench | 823 | 0.827 | 0.059 | 0.406 | 0.255 |
| index/SGD/SGD-X | 133 | 0.150 | 0.668 | 1.955 | 1.231 |
| index/SimpleBench | 1 | 0.000 | 0.662 | 2.267 | 1.266 |
| index/ToolRet | 46 | 0.891 | 0.060 | 0.221 | 0.141 |
| index/VAST | 160 | 0.569 | 0.197 | 1.199 | 0.641 |
| index/When2Call MCQ | 195 | 0.738 | 0.072 | 0.699 | 0.372 |
| index/WinoGrande | 68 | 0.912 | 0.104 | 0.304 | 0.178 |
| index/cfcolor | 266 | 0.647 | 0.073 | 0.661 | 0.463 |
| index/iSarcasmEval | 620 | 0.797 | 0.055 | 0.422 | 0.278 |
