# gemma-4-12b-qat calibration

## Provenance

- timestamp: 2026-10-21T045855Z
- repo commit: 0e7b572-dirty
- profile: gemma-4-12b-qat
- orders: top_p:0.9+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/gemma-4-12b-qat/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 2.934 (pooled; fitted 2.297) | fitted -0.090 [-0.094, -0.075]; pooled -0.097 [-0.117, -0.064] → pooled |  | 0.837 → 0.545 | 0.921 → 0.575 | 0.099 → 0.073 | 0.137 → 0.040 | 0.807 |
| score | 259/554 | 2.934 (pooled; fitted 11.939) | fitted -0.040 [-0.110, +0.029]; pooled -0.053 [-0.108, +0.001] → pooled |  | 5.396 → 2.029 | 3.150 → 1.487 | 0.468 → 0.363 | 0.304 → 0.251 | 0.560 |
| noul | 670/666 | 2.206 | fitted -0.057 [-0.068, -0.028]; pooled -0.044 [-0.064, -0.008] → fitted | +0.000 | 0.354 → 0.256 | 0.394 → 0.281 | 0.066 → 0.021 | 0.088 → 0.031 | 0.871 |

pooled T (one T for every type, b = 0; the gate's fallback): 2.934

noul offset: fitted b = -0.020; eval accuracy change +0.0000 [+0.0000, +0.0000], ECE change +0.0006 [-0.0095, +0.0098] → not shipped (b = 0)

