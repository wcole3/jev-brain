# qwen3.6-27b offline: eval

## Provenance

- timestamp: 2026-10-02T163545Z
- repo commit: e93c263
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: eval
- collected: .cache/collect/qwen3.6-27b/eval.jsonl.gz
- coverage: 2839 of 2839 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.0, 'score': 1.0, 'noul': 1.0}, 'b': 0.0, 'source': 'uncalibrated', 'orders': None}}

Status: ok 2827, unsupported 12

All rows (refused questions count as wrong): n 2839, refused 12, accuracy 0.785

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 2827 | 0.789 | 0.085 | 0.694 | 0.312 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 1607 | 0.811 | 0.067 | 0.545 | 0.264 |
| noul | 666 | 0.880 | 0.045 | 0.296 | 0.179 |
| score | 554 | 0.616 | 0.197 | 1.602 | 0.609 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| decisionbench | 2228 | 0.774 | 0.091 | 0.758 | 0.333 |
| jevbench | 599 | 0.845 | 0.065 | 0.453 | 0.233 |

Noul: 666 rows, said yes 199, gold yes 239, false no 60, false yes 20

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| decisionbench/finance/reasoning/ordinal_scoring/finqa-numerical-reasoning | 300 | 0.770 | 0.031 | 0.557 | 0.308 |
| decisionbench/legal/document_workflows/binary_classification/workflow_decision | 150 | 0.847 | 0.066 | 0.335 | 0.215 |
| decisionbench/legal/document_workflows/candidate_selection/workflow_decision | 40 | 0.675 | 0.160 | 0.767 | 0.394 |
| decisionbench/logic/reasoning/candidate_selection/folio-logical-inference | 200 | 0.685 | 0.093 | 0.706 | 0.406 |
| decisionbench/multi_hop_search/reasoning/binary_classification/musique-evidence-sufficiency | 300 | 0.683 | 0.101 | 0.622 | 0.423 |
| decisionbench/multi_hop_search/reasoning/candidate_selection/musique-multihop-answer | 200 | 0.835 | 0.059 | 0.460 | 0.220 |
| decisionbench/online_safety/guardrails_moderation/binary_classification/contains_threat | 150 | 0.993 | 0.026 | 0.030 | 0.011 |
| decisionbench/online_safety/guardrails_moderation/ordinal_scoring/toxicity_severity | 150 | 0.240 | 0.626 | 4.281 | 1.346 |
| decisionbench/privacy/bounded_extraction/candidate_selection/bounded_value | 150 | 0.967 | 0.029 | 0.207 | 0.058 |
| decisionbench/public_sector/entity_alignment/candidate_selection/canonical_entity | 138 | 1.000 | 0.011 | 0.012 | 0.001 |
| decisionbench/software_agents/function_agent_skill_routing/candidate_selection/tool_route | 150 | 0.993 | 0.010 | 0.014 | 0.007 |
| decisionbench/technical/document_record_classification/candidate_selection/patent_section | 150 | 0.553 | 0.280 | 1.884 | 0.698 |
| decisionbench/web/retrieval_verification/binary_classification/relevance | 150 | 0.867 | 0.097 | 0.384 | 0.208 |
| jevbench/agent_trace_observability | 45 | 0.689 | 0.190 | 0.744 | 0.467 |
| jevbench/banking | 150 | 0.833 | 0.100 | 0.683 | 0.258 |
| jevbench/commerce | 50 | 1.000 | 0.010 | 0.011 | 0.004 |
| jevbench/customer_service | 23 | 0.783 | 0.171 | 0.875 | 0.376 |
| jevbench/invoice_processing | 152 | 0.875 | 0.088 | 0.315 | 0.177 |
| jevbench/invoices | 50 | 0.580 | 0.315 | 0.959 | 0.648 |
| jevbench/logic | 2 | 1.000 | 0.031 | 0.032 | 0.002 |
| jevbench/moderation | 3 | 1.000 | 0.006 | 0.006 | 0.000 |
| jevbench/observability | 3 | 1.000 | 0.006 | 0.006 | 0.000 |
| jevbench/org | 48 | 1.000 | 0.003 | 0.003 | 0.000 |
| jevbench/quant | 50 | 0.880 | 0.063 | 0.275 | 0.168 |
| jevbench/reviews | 3 | 1.000 | 0.003 | 0.003 | 0.000 |
| jevbench/security_incidents | 17 | 0.824 | 0.153 | 0.289 | 0.180 |
| jevbench/support | 3 | 1.000 | 0.001 | 0.001 | 0.000 |
