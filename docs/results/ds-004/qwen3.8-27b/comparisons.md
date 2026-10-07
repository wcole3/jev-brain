# DS-004 run comparisons, qwen3.8-27b

Each section is `scripts/compare_runs.py <baseline> <candidate>`, named candidate-vs-baseline. Runs are in `runs/`.

## A8prime-vs-S8

- rows in common: 1682
- accuracy baseline: 89.7%, candidate: 89.6%, delta: -0.1 points
- answer flips: 2 (0.1%): wrong→right 0, right→wrong 2, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0324, mean |Δp|: 0.0001
- ECE baseline: 0.0629, candidate: 0.0627

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:invoice_processing:1415 | 3 | 3 | 2 | 0.032 |
| panoramic:invoice_reconcile:225 | no | no | yes | 0.065 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:invoice_reconcile:225 | no | no | yes | 0.065 |
| typed_decisions:invoice_processing:1415 | 3 | 3 | 2 | 0.032 |

## R8-vs-S8

- rows in common: 1682
- accuracy baseline: 89.7%, candidate: 89.7%, delta: +0.0 points
- answer flips: 7 (0.4%): wrong→right 3, right→wrong 3, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0586, mean |Δp|: 0.0005
- ECE baseline: 0.0629, candidate: 0.0564

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:285 | card_delivery_estimate | card_arrival | get_physical_card | 0.000 |
| typed_decisions:agent_trace_observability:168 | 3 | 2 | 3 | 0.000 |
| typed_decisions:invoice_processing:1165 | 3 | 3 | 2 | 0.030 |
| typed_decisions:invoice_processing:1085 | 2 | 3 | 2 | 0.031 |
| typed_decisions:invoice_processing:1415 | 3 | 3 | 2 | 0.032 |
| banking77:banking77:125 | card_payment_wrong_exchange_rate | exchange_rate | card_payment_wrong_exchange_rate | 0.035 |
| banking77:banking77:278 | fiat_currency_support | fiat_currency_support | exchange_rate | 0.057 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:278 | fiat_currency_support | fiat_currency_support | exchange_rate | 0.057 |
| banking77:banking77:125 | card_payment_wrong_exchange_rate | exchange_rate | card_payment_wrong_exchange_rate | 0.035 |
| typed_decisions:invoice_processing:1415 | 3 | 3 | 2 | 0.032 |
| typed_decisions:invoice_processing:1085 | 2 | 3 | 2 | 0.031 |
| typed_decisions:invoice_processing:1165 | 3 | 3 | 2 | 0.030 |

## R8prime-vs-A8prime

- rows in common: 1682
- accuracy baseline: 89.6%, candidate: 89.7%, delta: +0.1 points
- answer flips: 6 (0.4%): wrong→right 3, right→wrong 2, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0586, mean |Δp|: 0.0006
- ECE baseline: 0.0627, candidate: 0.0573

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:285 | card_delivery_estimate | card_arrival | get_physical_card | 0.000 |
| panoramic:invoice_reconcile:225 | no | yes | no | 0.000 |
| typed_decisions:invoice_processing:1085 | 2 | 3 | 2 | 0.031 |
| banking77:banking77:125 | card_payment_wrong_exchange_rate | exchange_rate | card_payment_wrong_exchange_rate | 0.035 |
| banking77:banking77:278 | fiat_currency_support | fiat_currency_support | exchange_rate | 0.057 |
| panoramic:avg_threshold:309 | no | no | yes | 0.065 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:avg_threshold:309 | no | no | yes | 0.065 |
| banking77:banking77:278 | fiat_currency_support | fiat_currency_support | exchange_rate | 0.057 |
| banking77:banking77:125 | card_payment_wrong_exchange_rate | exchange_rate | card_payment_wrong_exchange_rate | 0.035 |
| typed_decisions:invoice_processing:1085 | 2 | 3 | 2 | 0.031 |
| panoramic:invoice_reconcile:225 | no | yes | no | 0.000 |

## R8prime-vs-R8

- rows in common: 1682
- accuracy baseline: 89.7%, candidate: 89.7%, delta: -0.1 points
- answer flips: 3 (0.2%): wrong→right 1, right→wrong 2, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0333, mean |Δp|: 0.0002
- ECE baseline: 0.0564, candidate: 0.0573

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:invoice_processing:1165 | 3 | 2 | 3 | 0.000 |
| typed_decisions:agent_trace_observability:168 | 3 | 3 | 2 | 0.033 |
| panoramic:avg_threshold:309 | no | no | yes | 0.065 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:avg_threshold:309 | no | no | yes | 0.065 |
| typed_decisions:agent_trace_observability:168 | 3 | 3 | 2 | 0.033 |
| typed_decisions:invoice_processing:1165 | 3 | 2 | 3 | 0.000 |
