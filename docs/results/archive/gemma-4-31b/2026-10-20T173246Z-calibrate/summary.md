# gemma-4-31b calibration

## Provenance

- timestamp: 2026-10-20T173246Z
- repo commit: 326d316-dirty
- profile: gemma-4-31b
- orders: top_p:0.9+reversed
- calib split sha256: c8c8dba6f809a0e3da433fe50964205e061194af20463b1afa4ce3e7dadc09ed
- collect label: blurb
- collect: .cache/collect/gemma-4-31b/{calib,eval}-blurb.jsonl.gz

## blurb_header

| type | n calib/eval | T | T gate (eval ECE change vs T = 1) | b | NLL before → after (calib) | NLL before → after (eval) | ECE before → after (calib) | ECE before → after (eval) | eval acc |
|---|---|---|---|---|---|---|---|---|---|
| choice | 920/1619 | 3.978 | fitted -0.069 [-0.074, -0.057]; pooled -0.056 [-0.074, -0.035] → fitted |  | 1.708 → 0.556 | 2.088 → 0.623 | 0.116 → 0.030 | 0.149 → 0.080 | 0.842 |
| score | 259/554 | 5.211 (pooled; fitted 19.999 (edge)) | fitted -0.017 [-0.087, +0.057]; pooled -0.087 [-0.119, -0.038] → pooled |  | 9.840 → 2.024 | 5.052 → 1.220 | 0.532 → 0.422 | 0.287 → 0.201 | 0.690 |
| noul | 670/666 | 6.743 | fitted -0.048 [-0.060, -0.024]; pooled -0.031 [-0.042, -0.013] → fitted | +0.000 | 0.899 → 0.210 | 1.053 → 0.243 | 0.062 → 0.027 | 0.077 → 0.029 | 0.922 |

pooled T (one T for every type, b = 0; the gate's fallback): 5.211

noul offset: fitted b = +0.003; eval accuracy change -0.0015 [-0.0045, +0.0000], ECE change -0.0005 [-0.0037, +0.0030] → not shipped (b = 0)

