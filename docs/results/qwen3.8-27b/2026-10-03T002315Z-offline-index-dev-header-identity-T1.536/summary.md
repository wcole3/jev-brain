# qwen3.8-27b offline: index-dev

## Provenance

- timestamp: 2026-10-03T002315Z
- repo commit: a4ad243
- host: RTX PRO 6000 Blackwell, 600/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.8-27b
- split: index-dev
- collected: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz
- coverage: 7990 of 7990 rows

Arm: {'layout': 'header', 'orders': 'identity', 'calibration': {'T': {'choice': 1.536, 'score': 1.536, 'noul': 1.536}, 'b': 0.0, 'source': 'override T=1.536', 'orders': None}}

Status: ok 7990

All rows (refused questions count as wrong): n 14684, refused 0, accuracy 0.779

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 14684 | 0.779 | 0.021 | 0.693 | 0.302 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 14541 | 0.778 | 0.022 | 0.695 | 0.302 |
| noul | 143 | 0.818 | 0.113 | 0.480 | 0.289 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index | 14684 | 0.779 | 0.021 | 0.693 | 0.302 |

Noul: 143 rows, said yes 77, gold yes 57, false no 3, false yes 23

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| index/ACOS | 4707 | 0.980 | 0.014 | 0.060 | 0.031 |
| index/ANLI | 171 | 0.772 | 0.082 | 0.600 | 0.333 |
| index/API-Bank | 27 | 0.889 | 0.095 | 0.775 | 0.194 |
| index/ARC-Challenge | 62 | 1.000 | 0.065 | 0.077 | 0.027 |
| index/ARC-Easy | 126 | 0.976 | 0.029 | 0.065 | 0.029 |
| index/Amazon ESCI | 266 | 0.605 | 0.087 | 0.940 | 0.508 |
| index/BANKING77 | 164 | 0.738 | 0.113 | 1.144 | 0.349 |
| index/BBH fixed-option tasks | 293 | 0.730 | 0.110 | 0.717 | 0.379 |
| index/BFCL | 258 | 0.992 | 0.042 | 0.061 | 0.020 |
| index/BPoMP | 258 | 0.930 | 0.124 | 0.266 | 0.148 |
| index/BRIGHT | 20 | 0.550 | 0.353 | 0.975 | 0.652 |
| index/CLINC150+OOS | 293 | 0.863 | 0.050 | 0.647 | 0.220 |
| index/CLadder | 266 | 0.632 | 0.081 | 0.572 | 0.396 |
| index/CRUXEval | 30 | 0.600 | 0.164 | 0.758 | 0.446 |
| index/ChessBench | 266 | 0.169 | 0.206 | 3.446 | 0.987 |
| index/ContractNLI | 102 | 0.873 | 0.125 | 0.474 | 0.238 |
| index/FinEntity | 111 | 0.874 | 0.100 | 0.427 | 0.239 |
| index/ForecastBench | 539 | 0.692 | 0.069 | 0.594 | 0.407 |
| index/GPQA Diamond | 11 | 0.455 | 0.276 | 0.988 | 0.529 |
| index/GSM8K | 142 | 0.662 | 0.200 | 1.037 | 0.519 |
| index/HLE | 27 | 0.148 | 0.392 | 2.183 | 1.016 |
| index/Habermas Machine | 90 | 0.356 | 0.228 | 1.423 | 0.754 |
| index/HellaSwag | 534 | 0.938 | 0.059 | 0.198 | 0.092 |
| index/HoVer claim verification | 213 | 0.718 | 0.052 | 0.513 | 0.344 |
| index/Home appliance simulator | 90 | 0.978 | 0.039 | 0.096 | 0.044 |
| index/Humicroedit | 140 | 0.564 | 0.133 | 0.746 | 0.533 |
| index/MMLU | 747 | 0.822 | 0.049 | 0.477 | 0.249 |
| index/MMLU-Pro | 641 | 0.580 | 0.050 | 1.237 | 0.530 |
| index/MuSR | 40 | 0.575 | 0.226 | 1.003 | 0.594 |
| index/NLI4CT | 293 | 0.819 | 0.092 | 0.424 | 0.269 |
| index/New Yorker caption matching | 28 | 0.714 | 0.182 | 0.665 | 0.330 |
| index/POP909-CL | 106 | 0.340 | 0.198 | 3.231 | 0.865 |
| index/PhishNChips phishing decisions | 106 | 0.953 | 0.139 | 0.250 | 0.130 |
| index/RAGTruth response-level hallucination | 143 | 0.818 | 0.113 | 0.480 | 0.289 |
| index/RouterBench | 1062 | 0.151 | 0.453 | 3.479 | 1.197 |
| index/SATA-Bench | 823 | 0.827 | 0.047 | 0.372 | 0.232 |
| index/SGD/SGD-X | 133 | 0.421 | 0.139 | 1.127 | 0.688 |
| index/SimpleBench | 1 | 0.000 | 0.363 | 1.501 | 0.850 |
| index/ToolRet | 46 | 0.913 | 0.054 | 0.196 | 0.116 |
| index/VAST | 160 | 0.662 | 0.124 | 0.840 | 0.484 |
| index/When2Call MCQ | 195 | 0.800 | 0.077 | 0.642 | 0.322 |
| index/WinoGrande | 68 | 0.926 | 0.168 | 0.320 | 0.185 |
| index/cfcolor | 266 | 0.583 | 0.063 | 0.657 | 0.465 |
| index/iSarcasmEval | 620 | 0.863 | 0.125 | 0.404 | 0.245 |
