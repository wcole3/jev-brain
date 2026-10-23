# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-23T134208Z
- repo commit: 8eeab99-dirty
- profile: gemma-4-31b
- orders: identity
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: reread
- collect: .cache/collect/gemma-4-31b/{calib,eval}-reread.jsonl.gz

## blurb_header_reread

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 4.031 | fitted -0.078 [-0.082, -0.066]; pooled -0.071 [-0.093, -0.047] → fitted |  | 1.825 → 0.587 | 2.102 → 0.622 | 0.128 → 0.038 | 0.155 → 0.077 | 0.839 |
| score | 259/554 | 5.385 (pooled; fitted 19.999 (edge)) | fitted -0.103 [-0.173, -0.023]; pooled -0.147 [-0.169, -0.103] → pooled |  | 10.285 → 2.053 | 5.547 → 1.252 | 0.529 → 0.416 | 0.332 → 0.184 | 0.659 |
| noul | 670/666 | 7.429 | fitted -0.066 [-0.078, -0.037]; pooled -0.036 [-0.043, -0.024] → fitted | +0.000 | 1.137 → 0.238 | 1.347 → 0.274 | 0.086 → 0.033 | 0.101 → 0.035 | 0.895 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.385

noul offset: fitted b = -0.281; eval accuracy change +0.0030 [-0.0045, +0.0105], ECE change -0.0005 [-0.0150, +0.0159] → not shipped (b = 0)

