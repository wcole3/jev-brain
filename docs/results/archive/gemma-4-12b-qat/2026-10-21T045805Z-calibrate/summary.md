# gemma-4-12b-qat calibration

## Provenance

- timestamp: 2026-10-21T045805Z
- repo commit: 0e7b572-dirty
- profile: gemma-4-12b-qat
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/gemma-4-12b-qat/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 3.007 (pooled; fitted 2.317) | fitted -0.101 [-0.105, -0.087]; pooled -0.110 [-0.130, -0.075] → pooled |  | 0.928 → 0.615 | 0.994 → 0.622 | 0.096 → 0.093 | 0.150 → 0.040 | 0.788 |
| score | 259/554 | 12.942 | fitted -0.164 [-0.235, -0.088]; pooled -0.155 [-0.192, -0.094] → fitted |  | 5.735 → 1.284 | 3.443 → 1.286 | 0.505 → 0.079 | 0.371 → 0.207 | 0.518 |
| noul | 670/666 | 2.244 | fitted -0.057 [-0.070, -0.032]; pooled -0.042 [-0.067, -0.009] → fitted | +0.000 | 0.377 → 0.275 | 0.393 → 0.289 | 0.078 → 0.024 | 0.085 → 0.028 | 0.866 |

pooled T (one T for every type, b = 0; the gate's fallback): 3.007

noul offset: fitted b = +0.079; eval accuracy change +0.0030 [-0.0030, +0.0090], ECE change -0.0074 [-0.0163, +0.0077] → not shipped (b = 0)

