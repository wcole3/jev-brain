# qwen3.6-27b offline: eval

## Provenance

- timestamp: 2026-10-02T160224Z
- repo commit: 7506b87-dirty
- host: RTX PRO 6000 Blackwell, 540/600 W, drv 610.62, PCIe 4x16, AMD Ryzen 7 3800X 8-Core Processor (16 thr), 94 GB, WSL
- profile: qwen3.6-27b
- split: eval
- collected: .cache/collect/qwen3.6-27b/eval.jsonl.gz
- coverage: 2839 of 2839 rows

Arm: {'layout': 'decider_chat', 'orders': 'identity', 'calibration': {'T': {'choice': 1.6479149611375679, 'score': 6.323441128895665, 'noul': 1.38614000084428}, 'b': 0.0, 'source': 'qwen3.6-27b/decider_chat/calibration.json'}}

Status: ok 2827, unsupported 12

All rows (refused questions count as wrong): n 2839, refused 12, accuracy 0.785

| all | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| all | 2827 | 0.789 | 0.067 | 0.583 | 0.310 |

| type | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| choice | 1607 | 0.811 | 0.041 | 0.501 | 0.255 |
| noul | 666 | 0.880 | 0.038 | 0.286 | 0.173 |
| score | 554 | 0.616 | 0.236 | 1.179 | 0.636 |

| source | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| decisionbench | 2228 | 0.774 | 0.075 | 0.609 | 0.326 |
| jevbench | 599 | 0.845 | 0.087 | 0.487 | 0.252 |

Noul: 666 rows, said yes 199, gold yes 239, false no 60, false yes 20

| family | n | accuracy | ECE | NLL | Brier |
|---|---|---|---|---|---|
| decisionbench/finance/reasoning/ordinal_scoring/finqa-numerical-reasoning | 300 | 0.770 | 0.404 | 1.059 | 0.570 |
| decisionbench/legal/document_workflows/binary_classification/workflow_decision | 150 | 0.847 | 0.102 | 0.352 | 0.216 |
| decisionbench/legal/document_workflows/candidate_selection/workflow_decision | 40 | 0.675 | 0.188 | 0.717 | 0.357 |
| decisionbench/logic/reasoning/candidate_selection/folio-logical-inference | 200 | 0.685 | 0.113 | 0.727 | 0.417 |
| decisionbench/multi_hop_search/reasoning/binary_classification/musique-evidence-sufficiency | 300 | 0.683 | 0.096 | 0.591 | 0.405 |
| decisionbench/multi_hop_search/reasoning/candidate_selection/musique-multihop-answer | 200 | 0.835 | 0.093 | 0.453 | 0.219 |
| decisionbench/online_safety/guardrails_moderation/binary_classification/contains_threat | 150 | 0.993 | 0.052 | 0.058 | 0.017 |
| decisionbench/online_safety/guardrails_moderation/ordinal_scoring/toxicity_severity | 150 | 0.240 | 0.186 | 1.519 | 0.824 |
| decisionbench/privacy/bounded_extraction/candidate_selection/bounded_value | 150 | 0.967 | 0.030 | 0.163 | 0.054 |
| decisionbench/public_sector/entity_alignment/candidate_selection/canonical_entity | 138 | 1.000 | 0.082 | 0.089 | 0.015 |
| decisionbench/software_agents/function_agent_skill_routing/candidate_selection/tool_route | 150 | 0.993 | 0.045 | 0.056 | 0.012 |
| decisionbench/technical/document_record_classification/candidate_selection/patent_section | 150 | 0.553 | 0.152 | 1.426 | 0.617 |
| decisionbench/web/retrieval_verification/binary_classification/relevance | 150 | 0.867 | 0.074 | 0.323 | 0.193 |
| jevbench/agent_trace_observability | 45 | 0.689 | 0.250 | 0.954 | 0.521 |
| jevbench/banking | 150 | 0.833 | 0.087 | 0.616 | 0.251 |
| jevbench/commerce | 50 | 1.000 | 0.040 | 0.043 | 0.008 |
| jevbench/customer_service | 23 | 0.783 | 0.118 | 0.464 | 0.254 |
| jevbench/invoice_processing | 152 | 0.875 | 0.208 | 0.495 | 0.260 |
| jevbench/invoices | 50 | 0.580 | 0.265 | 0.804 | 0.576 |
| jevbench/logic | 2 | 1.000 | 0.077 | 0.081 | 0.012 |
| jevbench/moderation | 3 | 1.000 | 0.434 | 0.570 | 0.284 |
| jevbench/observability | 3 | 1.000 | 0.024 | 0.024 | 0.001 |
| jevbench/org | 48 | 1.000 | 0.033 | 0.034 | 0.002 |
| jevbench/quant | 50 | 0.880 | 0.075 | 0.275 | 0.167 |
| jevbench/reviews | 3 | 1.000 | 0.038 | 0.038 | 0.002 |
| jevbench/security_incidents | 17 | 0.824 | 0.337 | 0.639 | 0.363 |
| jevbench/support | 3 | 1.000 | 0.022 | 0.022 | 0.001 |
