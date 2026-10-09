# DS-005 Stage 1 comparisons

Generated with `scripts/compare_runs.py <base> <arm>`; all arms at T = 1.

## A1a vs A0


- rows in common: 1682
- accuracy baseline: 88.1%, candidate: 88.0%, delta: -0.1 points
- answer flips: 12 (0.7%): wrong→right 4, right→wrong 6, wrong→wrong 2

- rows with probabilities in both: 1682
- max |Δp|: 0.9901, mean |Δp|: 0.0010
- ECE baseline: 0.1158, candidate: 0.1153

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:agent_trace_observability:378 | 1 | 0 | 1 | 0.000 |
| panoramic:avg_threshold:493 | no | yes | no | 0.462 |
| banking77:banking77:247 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.462 |
| banking77:banking77:276 | fiat_currency_support | receiving_money | exchange_via_app | 0.755 |
| banking77:banking77:273 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.848 |
| typed_decisions:security_incidents:1771 | contain | contain | investigate | 0.848 |
| banking77:banking77:37 | card_arrival | card_arrival | card_delivery_estimate | 0.880 |
| banking77:banking77:260 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.934 |
| banking77:banking77:236 | pending_cash_withdrawal | declined_cash_withdrawal | cash_withdrawal_not_recognised | 0.956 |
| banking77:banking77:15 | card_arrival | card_delivery_estimate | card_arrival | 0.959 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:invoice_reconcile:685 | no | no | yes | 1.000 |
| panoramic:invoice_reconcile:521 | no | yes | no | 0.981 |
| banking77:banking77:15 | card_arrival | card_delivery_estimate | card_arrival | 0.959 |
| banking77:banking77:236 | pending_cash_withdrawal | declined_cash_withdrawal | cash_withdrawal_not_recognised | 0.956 |
| banking77:banking77:260 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.934 |


## A1b vs A0


- rows in common: 1682
- accuracy baseline: 88.1%, candidate: 88.1%, delta: +0.0 points
- answer flips: 11 (0.7%): wrong→right 5, right→wrong 5, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.8379, mean |Δp|: 0.0007
- ECE baseline: 0.1158, candidate: 0.1151

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:agent_trace_observability:378 | 1 | 0 | 1 | 0.000 |
| typed_decisions:agent_trace_observability:8 | 1 | 0 | 1 | 0.000 |
| banking77:banking77:247 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.462 |
| banking77:banking77:276 | fiat_currency_support | receiving_money | exchange_via_app | 0.755 |
| banking77:banking77:273 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.848 |
| panoramic:avg_threshold:612 | no | yes | no | 0.848 |
| banking77:banking77:37 | card_arrival | card_arrival | card_delivery_estimate | 0.880 |
| banking77:banking77:260 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.934 |
| panoramic:invoice_reconcile:437 | no | yes | no | 0.968 |
| banking77:banking77:244 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.972 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:avg_threshold:387 | no | yes | no | 0.972 |
| banking77:banking77:244 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.972 |
| panoramic:invoice_reconcile:437 | no | yes | no | 0.968 |
| banking77:banking77:260 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.934 |
| banking77:banking77:37 | card_arrival | card_arrival | card_delivery_estimate | 0.880 |


## A2 vs A0


- rows in common: 1682
- accuracy baseline: 88.1%, candidate: 89.7%, delta: +1.6 points
- answer flips: 38 (2.3%): wrong→right 32, right→wrong 5, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.9560, mean |Δp|: 0.0021
- ECE baseline: 0.1158, candidate: 0.1038

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:agent_trace_observability:378 | 1 | 0 | 1 | 0.000 |
| typed_decisions:agent_trace_observability:8 | 1 | 0 | 1 | 0.000 |
| panoramic:avg_threshold:493 | no | yes | no | 0.462 |
| banking77:banking77:240 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.671 |
| banking77:banking77:34 | card_arrival | card_delivery_estimate | card_arrival | 0.704 |
| banking77:banking77:276 | fiat_currency_support | receiving_money | exchange_via_app | 0.755 |
| typed_decisions:agent_trace_observability:23 | 1 | 0 | 1 | 0.762 |
| banking77:banking77:265 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.787 |
| banking77:banking77:37 | card_arrival | card_arrival | card_delivery_estimate | 0.880 |
| panoramic:avg_threshold:803 | no | yes | no | 0.905 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:safety_severity:0 | 1 | 0 | 1 | 0.996 |
| panoramic:safety_severity:885 | 1 | 0 | 1 | 0.996 |
| panoramic:safety_severity:876 | 1 | 0 | 1 | 0.996 |
| panoramic:safety_severity:866 | 1 | 0 | 1 | 0.996 |
| panoramic:safety_severity:767 | 1 | 0 | 1 | 0.996 |


## A3 vs A0


- rows in common: 1682
- accuracy baseline: 88.1%, candidate: 89.4%, delta: +1.3 points
- answer flips: 43 (2.6%): wrong→right 32, right→wrong 10, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.9899, mean |Δp|: 0.0028
- ECE baseline: 0.1158, candidate: 0.1013

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:avg_threshold:493 | no | yes | no | 0.462 |
| banking77:banking77:240 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.671 |
| banking77:banking77:34 | card_arrival | card_delivery_estimate | card_arrival | 0.704 |
| typed_decisions:agent_trace_observability:373 | 1 | 0 | 1 | 0.734 |
| banking77:banking77:276 | fiat_currency_support | receiving_money | exchange_via_app | 0.755 |
| typed_decisions:agent_trace_observability:23 | 1 | 0 | 1 | 0.762 |
| banking77:banking77:265 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.787 |
| banking77:banking77:273 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.848 |
| typed_decisions:invoice_processing:1380 | 3 | 3 | 2 | 0.848 |
| banking77:banking77:37 | card_arrival | card_arrival | card_delivery_estimate | 0.880 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:security_incidents:1993 | no | no | yes | 0.999 |
| panoramic:avg_threshold:115 | yes | yes | no | 0.997 |
| panoramic:safety_severity:0 | 1 | 0 | 1 | 0.996 |
| panoramic:safety_severity:885 | 1 | 0 | 1 | 0.996 |
| panoramic:safety_severity:876 | 1 | 0 | 1 | 0.996 |


## B1 vs B0


- rows in common: 1682
- accuracy baseline: 89.7%, candidate: 89.4%, delta: -0.4 points
- answer flips: 12 (0.7%): wrong→right 3, right→wrong 9, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.1289, mean |Δp|: 0.0011
- ECE baseline: 0.0333, candidate: 0.0270

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:125 | card_payment_wrong_exchange_rate | card_payment_wrong_exchange_rate | exchange_rate | 0.000 |
| banking77:banking77:265 | fiat_currency_support | fiat_currency_support | supported_cards_and_currencies | 0.000 |
| panoramic:invoice_reconcile:552 | yes | yes | no | 0.000 |
| typed_decisions:invoice_processing:1085 | 2 | 2 | 3 | 0.000 |
| typed_decisions:invoice_processing:1415 | 3 | 2 | 3 | 0.000 |
| typed_decisions:invoice_processing:1040 | 3 | 3 | 2 | 0.047 |
| typed_decisions:invoice_processing:1425 | 3 | 3 | 2 | 0.056 |
| panoramic:avg_threshold:309 | no | no | yes | 0.062 |
| panoramic:invoice_reconcile:481 | yes | no | yes | 0.062 |
| typed_decisions:agent_trace_observability:388 | 3 | 3 | 2 | 0.123 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:284 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.124 |
| banking77:banking77:292 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.124 |
| typed_decisions:agent_trace_observability:388 | 3 | 3 | 2 | 0.123 |
| panoramic:invoice_reconcile:481 | yes | no | yes | 0.062 |
| panoramic:avg_threshold:309 | no | no | yes | 0.062 |


## B2 vs B0


- rows in common: 1682
- accuracy baseline: 89.7%, candidate: 90.2%, delta: +0.5 points
- answer flips: 43 (2.6%): wrong→right 25, right→wrong 16, wrong→wrong 2

- rows with probabilities in both: 1682
- max |Δp|: 0.3913, mean |Δp|: 0.0039
- ECE baseline: 0.0333, candidate: 0.0362

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:125 | card_payment_wrong_exchange_rate | card_payment_wrong_exchange_rate | exchange_rate | 0.000 |
| banking77:banking77:239 | pending_cash_withdrawal | declined_cash_withdrawal | pending_cash_withdrawal | 0.000 |
| banking77:banking77:265 | fiat_currency_support | fiat_currency_support | exchange_rate | 0.000 |
| typed_decisions:agent_trace_observability:168 | 3 | 2 | 3 | 0.000 |
| typed_decisions:invoice_processing:1165 | 3 | 2 | 3 | 0.000 |
| typed_decisions:invoice_processing:1415 | 3 | 2 | 3 | 0.000 |
| typed_decisions:invoice_processing:1090 | 3 | 3 | 0 | 0.044 |
| banking77:banking77:57 | card_linking | card_linking | card_arrival | 0.051 |
| typed_decisions:invoice_processing:1425 | 3 | 3 | 2 | 0.056 |
| typed_decisions:invoice_processing:1300 | 3 | 3 | 2 | 0.060 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:invoice_reconcile:32 | yes | no | yes | 0.412 |
| panoramic:invoice_reconcile:173 | yes | no | yes | 0.412 |
| banking77:banking77:250 | fiat_currency_support | exchange_via_app | exchange_rate | 0.399 |
| panoramic:invoice_reconcile:460 | yes | no | yes | 0.358 |
| panoramic:avg_threshold:196 | yes | no | yes | 0.358 |


## C1 vs C0


- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.1 points
- answer flips: 10 (0.6%): wrong→right 4, right→wrong 3, wrong→wrong 3

- rows with probabilities in both: 1682
- max |Δp|: 0.2494, mean |Δp|: 0.0014
- ECE baseline: 0.0396, candidate: 0.0405

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:invoice_processing:1415 | 3 | 2 | 3 | 0.000 |
| banking77:banking77:261 | fiat_currency_support | exchange_via_app | exchange_rate | 0.037 |
| banking77:banking77:285 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.050 |
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.062 |
| panoramic:invoice_reconcile:823 | yes | no | yes | 0.062 |
| banking77:banking77:276 | fiat_currency_support | card_acceptance | exchange_rate | 0.120 |
| typed_decisions:invoice_processing:1085 | 2 | 3 | 2 | 0.120 |
| typed_decisions:agent_trace_observability:273 | 1 | 1 | 0 | 0.121 |
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.123 |
| banking77:banking77:236 | pending_cash_withdrawal | declined_cash_withdrawal | cash_withdrawal_charge | 0.181 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:236 | pending_cash_withdrawal | declined_cash_withdrawal | cash_withdrawal_charge | 0.181 |
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.123 |
| typed_decisions:agent_trace_observability:273 | 1 | 1 | 0 | 0.121 |
| typed_decisions:invoice_processing:1085 | 2 | 3 | 2 | 0.120 |
| banking77:banking77:276 | fiat_currency_support | card_acceptance | exchange_rate | 0.120 |

