# DS-004 run comparisons, qwen3.6-27b

Each section is `scripts/compare_runs.py <baseline> <candidate>`, named candidate-vs-baseline. Runs are in `runs/`.

## A2-vs-A

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.0 points
- answer flips: 3 (0.2%): wrong→right 1, right→wrong 1, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0787, mean |Δp|: 0.0005
- ECE baseline: 0.0401, candidate: 0.0350

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |
| banking77:banking77:295 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.000 |
| typed_decisions:invoice_processing:1140 | 3 | 3 | 0 | 0.025 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:invoice_processing:1140 | 3 | 3 | 0 | 0.025 |
| banking77:banking77:295 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.000 |
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |

## Aprime-vs-A

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.0 points
- answer flips: 2 (0.1%): wrong→right 1, right→wrong 1, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0273, mean |Δp|: 0.0001
- ECE baseline: 0.0401, candidate: 0.0401

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:295 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.000 |
| typed_decisions:invoice_processing:1140 | 3 | 3 | 0 | 0.025 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:invoice_processing:1140 | 3 | 3 | 0 | 0.025 |
| banking77:banking77:295 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.000 |

## P-vs-A

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.0 points
- answer flips: 3 (0.2%): wrong→right 1, right→wrong 1, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0769, mean |Δp|: 0.0005
- ECE baseline: 0.0401, candidate: 0.0347

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |
| banking77:banking77:295 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.000 |
| typed_decisions:invoice_processing:1140 | 3 | 3 | 0 | 0.025 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:invoice_processing:1140 | 3 | 3 | 0 | 0.025 |
| banking77:banking77:295 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.000 |
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |

## P2-vs-A

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.0 points
- answer flips: 0 (0.0%): wrong→right 0, right→wrong 0, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0533, mean |Δp|: 0.0005
- ECE baseline: 0.0401, candidate: 0.0359

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|

## Pnd-vs-A

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.1%, delta: -0.1 points
- answer flips: 2 (0.1%): wrong→right 0, right→wrong 1, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0536, mean |Δp|: 0.0002
- ECE baseline: 0.0401, candidate: 0.0370

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |
| banking77:banking77:222 | pending_cash_withdrawal | pending_cash_withdrawal | cash_withdrawal_not_recognised | 0.064 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:222 | pending_cash_withdrawal | pending_cash_withdrawal | cash_withdrawal_not_recognised | 0.064 |
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |

## Pndprime-vs-Aprime

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.1%, delta: -0.1 points
- answer flips: 2 (0.1%): wrong→right 0, right→wrong 2, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0439, mean |Δp|: 0.0003
- ECE baseline: 0.0401, candidate: 0.0400

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:222 | pending_cash_withdrawal | pending_cash_withdrawal | cash_withdrawal_not_recognised | 0.032 |
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.033 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.033 |
| banking77:banking77:222 | pending_cash_withdrawal | pending_cash_withdrawal | cash_withdrawal_not_recognised | 0.032 |

## Pndprime-vs-Pnd

- rows in common: 1682
- accuracy baseline: 89.1%, candidate: 89.1%, delta: -0.1 points
- answer flips: 2 (0.1%): wrong→right 0, right→wrong 1, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0395, mean |Δp|: 0.0003
- ECE baseline: 0.0370, candidate: 0.0400

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_via_app | exchange_rate | 0.018 |
| typed_decisions:invoice_processing:1140 | 3 | 3 | 0 | 0.025 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:invoice_processing:1140 | 3 | 3 | 0 | 0.025 |
| banking77:banking77:261 | fiat_currency_support | exchange_via_app | exchange_rate | 0.018 |

## Pprime-vs-A

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.1%, delta: -0.1 points
- answer flips: 2 (0.1%): wrong→right 0, right→wrong 1, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0782, mean |Δp|: 0.0006
- ECE baseline: 0.0401, candidate: 0.0356

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.063 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.063 |
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |

## Pprime-vs-Aprime

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.1%, delta: -0.1 points
- answer flips: 4 (0.2%): wrong→right 1, right→wrong 2, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0782, mean |Δp|: 0.0006
- ECE baseline: 0.0401, candidate: 0.0356

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |
| typed_decisions:invoice_processing:1140 | 3 | 0 | 3 | 0.000 |
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.033 |
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.063 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.063 |
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.033 |
| typed_decisions:invoice_processing:1140 | 3 | 0 | 3 | 0.000 |
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |

## Pprime-vs-P

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.1%, delta: -0.1 points
- answer flips: 3 (0.2%): wrong→right 1, right→wrong 2, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0659, mean |Δp|: 0.0003
- ECE baseline: 0.0347, candidate: 0.0356

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| typed_decisions:invoice_processing:1140 | 3 | 0 | 3 | 0.025 |
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.031 |
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.034 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.034 |
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.031 |
| typed_decisions:invoice_processing:1140 | 3 | 0 | 3 | 0.025 |

## R-vs-A

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.0 points
- answer flips: 2 (0.1%): wrong→right 1, right→wrong 1, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0735, mean |Δp|: 0.0006
- ECE baseline: 0.0401, candidate: 0.0344

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:295 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.000 |
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.063 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.063 |
| banking77:banking77:295 | card_delivery_estimate | card_arrival | card_delivery_estimate | 0.000 |

## R800-vs-Rfull

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.1%, delta: -0.1 points
- answer flips: 2 (0.1%): wrong→right 0, right→wrong 1, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0555, mean |Δp|: 0.0005
- ECE baseline: 0.0353, candidate: 0.0342

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:10 | card_arrival | card_arrival | lost_or_stolen_card | 0.000 |
| banking77:banking77:261 | fiat_currency_support | exchange_via_app | exchange_rate | 0.019 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_via_app | exchange_rate | 0.019 |
| banking77:banking77:10 | card_arrival | card_arrival | lost_or_stolen_card | 0.000 |

## R800-vs-S

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.1%, delta: -0.1 points
- answer flips: 3 (0.2%): wrong→right 1, right→wrong 2, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0799, mean |Δp|: 0.0005
- ECE baseline: 0.0344, candidate: 0.0342

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:invoice_reconcile:742 | yes | yes | no | 0.000 |
| banking77:banking77:10 | card_arrival | card_arrival | lost_or_stolen_card | 0.023 |
| banking77:banking77:166 | extra_charge_on_statement | card_payment_not_recognised | extra_charge_on_statement | 0.031 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:166 | extra_charge_on_statement | card_payment_not_recognised | extra_charge_on_statement | 0.031 |
| banking77:banking77:10 | card_arrival | card_arrival | lost_or_stolen_card | 0.023 |
| panoramic:invoice_reconcile:742 | yes | yes | no | 0.000 |

## Rfull-vs-S

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.0 points
- answer flips: 3 (0.2%): wrong→right 1, right→wrong 1, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.0807, mean |Δp|: 0.0005
- ECE baseline: 0.0344, candidate: 0.0353

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:invoice_reconcile:742 | yes | yes | no | 0.000 |
| banking77:banking77:166 | extra_charge_on_statement | card_payment_not_recognised | extra_charge_on_statement | 0.031 |
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.036 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.036 |
| banking77:banking77:166 | extra_charge_on_statement | card_payment_not_recognised | extra_charge_on_statement | 0.031 |
| panoramic:invoice_reconcile:742 | yes | yes | no | 0.000 |

## Rprime-vs-Aprime

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.1 points
- answer flips: 6 (0.4%): wrong→right 3, right→wrong 2, wrong→wrong 1

- rows with probabilities in both: 1682
- max |Δp|: 0.1048, mean |Δp|: 0.0005
- ECE baseline: 0.0401, candidate: 0.0351

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:261 | fiat_currency_support | exchange_rate | exchange_via_app | 0.000 |
| panoramic:invoice_reconcile:742 | yes | yes | no | 0.000 |
| typed_decisions:invoice_processing:1140 | 3 | 0 | 3 | 0.000 |
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.033 |
| banking77:banking77:10 | card_arrival | lost_or_stolen_card | card_arrival | 0.046 |
| panoramic:avg_threshold:815 | yes | no | yes | 0.049 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:avg_threshold:815 | yes | no | yes | 0.049 |
| banking77:banking77:10 | card_arrival | lost_or_stolen_card | card_arrival | 0.046 |
| banking77:banking77:295 | card_delivery_estimate | card_delivery_estimate | card_arrival | 0.033 |
| typed_decisions:invoice_processing:1140 | 3 | 0 | 3 | 0.000 |
| panoramic:invoice_reconcile:742 | yes | yes | no | 0.000 |

## Rprime-vs-Pprime

- rows in common: 1682
- accuracy baseline: 89.1%, candidate: 89.2%, delta: +0.1 points
- answer flips: 4 (0.2%): wrong→right 3, right→wrong 1, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.1396, mean |Δp|: 0.0005
- ECE baseline: 0.0356, candidate: 0.0351

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:166 | extra_charge_on_statement | card_payment_not_recognised | extra_charge_on_statement | 0.000 |
| panoramic:invoice_reconcile:742 | yes | yes | no | 0.000 |
| banking77:banking77:10 | card_arrival | lost_or_stolen_card | card_arrival | 0.046 |
| panoramic:avg_threshold:815 | yes | no | yes | 0.049 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:avg_threshold:815 | yes | no | yes | 0.049 |
| banking77:banking77:10 | card_arrival | lost_or_stolen_card | card_arrival | 0.046 |
| panoramic:invoice_reconcile:742 | yes | yes | no | 0.000 |
| banking77:banking77:166 | extra_charge_on_statement | card_payment_not_recognised | extra_charge_on_statement | 0.000 |

## Rprime-vs-Rfull

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.1 points
- answer flips: 1 (0.1%): wrong→right 1, right→wrong 0, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0447, mean |Δp|: 0.0002
- ECE baseline: 0.0353, candidate: 0.0351

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:avg_threshold:815 | yes | no | yes | 0.049 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| panoramic:avg_threshold:815 | yes | no | yes | 0.049 |

## S-vs-A

- rows in common: 1682
- accuracy baseline: 89.2%, candidate: 89.2%, delta: +0.0 points
- answer flips: 2 (0.1%): wrong→right 1, right→wrong 1, wrong→wrong 0

- rows with probabilities in both: 1682
- max |Δp|: 0.0586, mean |Δp|: 0.0005
- ECE baseline: 0.0401, candidate: 0.0344

#### Flips with the smallest baseline top-two gap

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:10 | card_arrival | lost_or_stolen_card | card_arrival | 0.046 |
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.063 |

#### Flips with the largest baseline top-two gap (large gap = bug signal)

| id | gold | baseline | candidate | baseline gap |
|---|---|---|---|---|
| banking77:banking77:166 | extra_charge_on_statement | extra_charge_on_statement | card_payment_not_recognised | 0.063 |
| banking77:banking77:10 | card_arrival | lost_or_stolen_card | card_arrival | 0.046 |
