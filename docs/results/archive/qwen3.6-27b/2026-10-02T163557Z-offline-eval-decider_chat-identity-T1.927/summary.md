# qwen3.6-27b offline: eval

## Provenance

- timestamp: 2026-10-02T163557Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: eval
- collected: .cache/collect/qwen3.6-27b/eval.jsonl.gz
- coverage: 2839 of 2839 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.927, 'score': 1.927, 'noul': 1.927}, 'b': 0.0, 'source': 'override T=1.927', 'orders': None}}

Status: ok 2827, unsupported 12

All rows (refused questions count as wrong): n 2839, refused 12, accuracy 0.785

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 2827 | 0.789 | 0.038 | 0.597 | 0.304 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 1607 | 0.811 | 0.061 | 0.523 | 0.261 |
| noul | 666 | 0.880 | 0.074 | 0.308 | 0.180 |
| score | 554 | 0.616 | 0.122 | 1.162 | 0.581 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| decisionbench | 2228 | 0.774 | 0.036 | 0.635 | 0.325 |
| jevbench | 599 | 0.845 | 0.079 | 0.457 | 0.229 |

Noul: 666 rows, said yes 199, gold yes 239, false no 60, false yes 20

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| decisionbench/finance/reasoning/ordinal_scoring/finqa-numerical-reasoning | 300 | 0.770 | 0.158 | 0.668 | 0.351 |
| decisionbench/legal/document_workflows/binary_classification/workflow_decision | 150 | 0.847 | 0.130 | 0.391 | 0.235 |
| decisionbench/legal/document_workflows/candidate_selection/workflow_decision | 40 | 0.675 | 0.144 | 0.732 | 0.351 |
| decisionbench/logic/reasoning/candidate_selection/folio-logical-inference | 200 | 0.685 | 0.115 | 0.749 | 0.429 |
| decisionbench/multi_hop_search/reasoning/binary_classification/musique-evidence-sufficiency | 300 | 0.683 | 0.039 | 0.592 | 0.406 |
| decisionbench/multi_hop_search/reasoning/candidate_selection/musique-multihop-answer | 200 | 0.835 | 0.121 | 0.482 | 0.230 |
| decisionbench/online_safety/guardrails_moderation/binary_classification/contains_threat | 150 | 0.993 | 0.092 | 0.108 | 0.031 |
| decisionbench/online_safety/guardrails_moderation/ordinal_scoring/toxicity_severity | 150 | 0.240 | 0.506 | 2.473 | 1.177 |
| decisionbench/privacy/bounded_extraction/candidate_selection/bounded_value | 150 | 0.967 | 0.043 | 0.177 | 0.055 |
| decisionbench/public_sector/entity_alignment/candidate_selection/canonical_entity | 138 | 1.000 | 0.140 | 0.158 | 0.034 |
| decisionbench/software_agents/function_agent_skill_routing/candidate_selection/tool_route | 150 | 0.993 | 0.087 | 0.106 | 0.022 |
| decisionbench/technical/document_record_classification/candidate_selection/patent_section | 150 | 0.553 | 0.091 | 1.372 | 0.600 |
| decisionbench/web/retrieval_verification/binary_classification/relevance | 150 | 0.867 | 0.059 | 0.305 | 0.184 |
| jevbench/agent_trace_observability | 45 | 0.689 | 0.091 | 0.713 | 0.430 |
| jevbench/banking | 150 | 0.833 | 0.150 | 0.682 | 0.265 |
| jevbench/commerce | 50 | 1.000 | 0.063 | 0.067 | 0.013 |
| jevbench/customer_service | 23 | 0.783 | 0.148 | 0.600 | 0.323 |
| jevbench/invoice_processing | 152 | 0.875 | 0.155 | 0.393 | 0.202 |
| jevbench/invoices | 50 | 0.580 | 0.190 | 0.720 | 0.522 |
| jevbench/logic | 2 | 1.000 | 0.144 | 0.155 | 0.041 |
| jevbench/moderation | 3 | 1.000 | 0.085 | 0.089 | 0.012 |
| jevbench/observability | 3 | 1.000 | 0.064 | 0.066 | 0.008 |
| jevbench/org | 48 | 1.000 | 0.057 | 0.058 | 0.006 |
| jevbench/quant | 50 | 0.880 | 0.109 | 0.304 | 0.176 |
| jevbench/reviews | 3 | 1.000 | 0.063 | 0.066 | 0.007 |
| jevbench/security_incidents | 17 | 0.824 | 0.206 | 0.442 | 0.238 |
| jevbench/support | 3 | 1.000 | 0.040 | 0.041 | 0.003 |
