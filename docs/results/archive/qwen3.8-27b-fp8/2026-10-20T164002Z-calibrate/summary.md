# qwen3.8-27b-fp8 calibration

## Provenance

- timestamp: 2026-10-20T164002Z
- repo commit: 0e16d32-dirty
- profile: qwen3.8-27b-fp8
- orders: min_n:4+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/qwen3.8-27b-fp8/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 898/1607 | 1.595 | fitted -0.028 [-0.045, -0.001]; pooled -0.003 [-0.030, +0.026] → fitted |  | 0.556 → 0.469 | 0.502 → 0.473 | 0.052 → 0.028 | 0.056 → 0.028 | 0.818 |
| score | 259/554 | 1.000 (none; fitted 5.479) | fitted +0.176 [+0.112, +0.213]; pooled +0.066 [+0.018, +0.090] → none |  | 2.534 → 2.534 | 1.483 → 1.483 | 0.365 → 0.365 | 0.142 → 0.142 | 0.666 |
| noul | 670/666 | 1.109 | fitted +0.007 [-0.009, +0.018]; b = 0 +0.007 [-0.006, +0.014]; pooled +0.047 [+0.025, +0.063] → fitted | +0.138 | 0.241 → 0.239 | 0.242 → 0.239 | 0.024 → 0.028 | 0.041 → 0.048 | 0.889 |

pooled T (one T for every type, b = 0; the gate's fallback): 1.880

noul offset: fitted b = +0.138; eval accuracy change +0.0090 [+0.0030, +0.0165], ECE change +0.0002 [-0.0108, +0.0143] → shipped

