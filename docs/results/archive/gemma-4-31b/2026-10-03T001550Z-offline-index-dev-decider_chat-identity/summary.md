# gemma-4-31b offline: index-dev

## Provenance

- timestamp: 2026-10-03T001550Z
- repo commit: ae318d3
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: gemma-4-31b
- split: index-dev
- collected: .cache/collect/gemma-4-31b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 4.122840843073183, 'score': 5.3780273588596375, 'noul': 7.527710804948447}, 'b': -0.6359937209430613, 'source': 'gemma-4-31b/decider_chat/calibration.json', 'orders': 'identity'}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.749

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.749 | 0.155 | 0.970 | 0.409 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.748 | 0.156 | 0.976 | 0.411 |
| noul | 143 | 0.853 | 0.081 | 0.394 | 0.236 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.749 | 0.155 | 0.970 | 0.409 |

Noul: 143 rows, said yes 68, gold yes 57, false no 5, false yes 16

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.871 | 0.102 | 0.492 | 0.230 |
| index/ANLI | 171 | 0.737 | 0.189 | 0.882 | 0.436 |
| index/API-Bank | 27 | 0.889 | 0.116 | 0.678 | 0.192 |
| index/ARC-Challenge | 62 | 1.000 | 0.040 | 0.043 | 0.008 |
| index/ARC-Easy | 126 | 0.984 | 0.020 | 0.068 | 0.024 |
| index/Amazon ESCI | 266 | 0.620 | 0.297 | 1.549 | 0.657 |
| index/BANKING77 | 164 | 0.744 | 0.090 | 1.395 | 0.379 |
| index/BBH fixed-option tasks | 293 | 0.737 | 0.152 | 0.852 | 0.410 |
| index/BFCL | 258 | 1.000 | 0.004 | 0.004 | 0.000 |
| index/BPoMP | 258 | 0.884 | 0.105 | 0.412 | 0.211 |
| index/BRIGHT | 20 | 0.600 | 0.393 | 1.789 | 0.775 |
| index/CLINC150+OOS | 293 | 0.891 | 0.155 | 0.716 | 0.197 |
| index/CLadder | 266 | 0.729 | 0.218 | 0.863 | 0.470 |
| index/CRUXEval | 30 | 0.700 | 0.208 | 0.879 | 0.489 |
| index/ChessBench | 266 | 0.203 | 0.226 | 3.202 | 0.962 |
| index/ContractNLI | 102 | 0.725 | 0.237 | 0.971 | 0.484 |
| index/FinEntity | 111 | 0.901 | 0.064 | 0.295 | 0.162 |
| index/ForecastBench | 539 | 0.751 | 0.171 | 0.828 | 0.425 |
| index/GPQA Diamond | 11 | 0.455 | 0.325 | 1.286 | 0.693 |
| index/GSM8K | 142 | 0.873 | 0.123 | 0.470 | 0.206 |
| index/HLE | 27 | 0.148 | 0.548 | 2.719 | 1.213 |
| index/Habermas Machine | 90 | 0.389 | 0.440 | 1.936 | 0.936 |
| index/HellaSwag | 534 | 0.918 | 0.049 | 0.252 | 0.123 |
| index/HoVer claim verification | 213 | 0.798 | 0.178 | 0.827 | 0.373 |
| index/Home appliance simulator | 90 | 0.967 | 0.036 | 0.102 | 0.054 |
| index/Humicroedit | 140 | 0.621 | 0.321 | 1.246 | 0.639 |
| index/MMLU | 747 | 0.851 | 0.070 | 0.464 | 0.232 |
| index/MMLU-Pro | 641 | 0.672 | 0.079 | 1.099 | 0.462 |
| index/MuSR | 40 | 0.600 | 0.310 | 1.302 | 0.648 |
| index/NLI4CT | 293 | 0.829 | 0.147 | 0.625 | 0.298 |
| index/New Yorker caption matching | 28 | 0.857 | 0.146 | 0.472 | 0.219 |
| index/POP909-CL | 106 | 0.340 | 0.178 | 3.541 | 0.867 |
| index/PhishNChips phishing decisions | 106 | 0.877 | 0.103 | 0.378 | 0.211 |
| index/RAGTruth response-level hallucination | 143 | 0.853 | 0.081 | 0.394 | 0.236 |
| index/RouterBench | 1062 | 0.157 | 0.601 | 3.759 | 1.340 |
| index/SATA-Bench | 823 | 0.844 | 0.107 | 0.526 | 0.264 |
| index/SGD/SGD-X | 133 | 0.075 | 0.842 | 3.397 | 1.625 |
| index/SimpleBench | 1 | 1.000 | 0.063 | 0.065 | 0.005 |
| index/ToolRet | 46 | 0.913 | 0.090 | 0.366 | 0.170 |
| index/VAST | 160 | 0.681 | 0.252 | 1.246 | 0.560 |
| index/When2Call MCQ | 195 | 0.810 | 0.121 | 0.695 | 0.317 |
| index/WinoGrande | 68 | 0.882 | 0.095 | 0.445 | 0.210 |
| index/cfcolor | 266 | 0.620 | 0.321 | 1.322 | 0.673 |
| index/iSarcasmEval | 620 | 0.697 | 0.255 | 0.990 | 0.516 |
