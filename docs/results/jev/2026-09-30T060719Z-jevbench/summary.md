# jev benchmark (full, JevBench only)

## Provenance

- timestamp: 2026-09-30T06:07:19.583674+00:00
- repo commit: 5bab2e8
- target: jev
- JevBench SHA: fcec62f13ce961115af0d16317f0ff15986a9a25
- gold rows available: 1682
- rows run: 1682
- base URL: https://api.typesafe.ai
- models returned: ['jev-1.13.0']

| rows | errors | overall % | choice % | noul % | score-QWK | score-MAE | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|
| 1682 | 0 | 91.2 | 92.0 | 95.7 | 0.944 | 0.179 | 152 | 204 |

| ECE (15 bins) | Brier | noul said-yes % | noul gold-yes % | noul false-no | noul false-yes |
|---|---|---|---|---|---|
| 0.028 | 0.142 | 44.5 | 42.7 | 8 | 19 |

Jev usage: 1071961 input tokens, about $0.05 at $0.042 per million.
