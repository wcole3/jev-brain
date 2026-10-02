# qwen3.6-27b offline: eval

## Provenance

- timestamp: 2026-10-02T163601Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: eval
- collected: .cache/collect/qwen3.6-27b/eval.jsonl.gz
- coverage: 2839 of 2839 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.943, 'score': 1.943, 'noul': 1.943}, 'b': 0.0, 'source': 'override T=1.943', 'orders': None}}

Status: ok 2827, unsupported 12

All rows (refused questions count as wrong): n 2839, refused 12, accuracy 0.785

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 2827 | 0.789 | 0.041 | 0.598 | 0.305 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 1607 | 0.811 | 0.065 | 0.524 | 0.261 |
| noul | 666 | 0.880 | 0.075 | 0.309 | 0.180 |
| score | 554 | 0.616 | 0.122 | 1.160 | 0.581 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| decisionbench | 2228 | 0.774 | 0.037 | 0.635 | 0.325 |
| jevbench | 599 | 0.845 | 0.077 | 0.459 | 0.230 |

Noul: 666 rows, said yes 199, gold yes 239, false no 60, false yes 20

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| decisionbench/finance/reasoning/ordinal_scoring/finqa-numerical-reasoning | 300 | 0.770 | 0.160 | 0.670 | 0.352 |
| decisionbench/legal/document_workflows/binary_classification/workflow_decision | 150 | 0.847 | 0.131 | 0.392 | 0.235 |
| decisionbench/legal/document_workflows/candidate_selection/workflow_decision | 40 | 0.675 | 0.145 | 0.733 | 0.351 |
| decisionbench/logic/reasoning/candidate_selection/folio-logical-inference | 200 | 0.685 | 0.116 | 0.751 | 0.430 |
| decisionbench/multi_hop_search/reasoning/binary_classification/musique-evidence-sufficiency | 300 | 0.683 | 0.039 | 0.592 | 0.406 |
| decisionbench/multi_hop_search/reasoning/candidate_selection/musique-multihop-answer | 200 | 0.835 | 0.123 | 0.484 | 0.230 |
| decisionbench/online_safety/guardrails_moderation/binary_classification/contains_threat | 150 | 0.993 | 0.093 | 0.110 | 0.032 |
| decisionbench/online_safety/guardrails_moderation/ordinal_scoring/toxicity_severity | 150 | 0.240 | 0.504 | 2.458 | 1.174 |
| decisionbench/privacy/bounded_extraction/candidate_selection/bounded_value | 150 | 0.967 | 0.045 | 0.178 | 0.056 |
| decisionbench/public_sector/entity_alignment/candidate_selection/canonical_entity | 138 | 1.000 | 0.144 | 0.163 | 0.036 |
| decisionbench/software_agents/function_agent_skill_routing/candidate_selection/tool_route | 150 | 0.993 | 0.090 | 0.110 | 0.023 |
| decisionbench/technical/document_record_classification/candidate_selection/patent_section | 150 | 0.553 | 0.090 | 1.370 | 0.600 |
| decisionbench/web/retrieval_verification/binary_classification/relevance | 150 | 0.867 | 0.060 | 0.305 | 0.184 |
| jevbench/agent_trace_observability | 45 | 0.689 | 0.092 | 0.715 | 0.430 |
| jevbench/banking | 150 | 0.833 | 0.137 | 0.687 | 0.266 |
| jevbench/commerce | 50 | 1.000 | 0.064 | 0.069 | 0.013 |
| jevbench/customer_service | 23 | 0.783 | 0.141 | 0.599 | 0.323 |
| jevbench/invoice_processing | 152 | 0.875 | 0.148 | 0.395 | 0.203 |
| jevbench/invoices | 50 | 0.580 | 0.212 | 0.719 | 0.521 |
| jevbench/logic | 2 | 1.000 | 0.146 | 0.157 | 0.042 |
| jevbench/moderation | 3 | 1.000 | 0.087 | 0.091 | 0.013 |
| jevbench/observability | 3 | 1.000 | 0.065 | 0.067 | 0.009 |
| jevbench/org | 48 | 1.000 | 0.058 | 0.060 | 0.006 |
| jevbench/quant | 50 | 0.880 | 0.110 | 0.305 | 0.177 |
| jevbench/reviews | 3 | 1.000 | 0.065 | 0.068 | 0.007 |
| jevbench/security_incidents | 17 | 0.824 | 0.208 | 0.445 | 0.239 |
| jevbench/support | 3 | 1.000 | 0.041 | 0.042 | 0.003 |
