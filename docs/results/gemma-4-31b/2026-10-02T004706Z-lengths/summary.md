# gemma-4-31b decision lengths

## Provenance

- timestamp: 2026-10-02T004706Z
- repo commit: 8df3768-dirty
- profile: gemma-4-31b

| proxy tokens | rows | benchmarks |
|---|---|---|
| <8k | 149807 | 44 |
| 8k-16k | 447 | 5 |
| 16k-32k | 62 | 2 |
| 32k-64k | 1 | 1 |

Real tokens measured for 63 rows with proxy tokens >= 0.5 x the cap.
At or over the decision cap (32768): 0 rows; 0 of them fit under MAX_MODEL_LEN (32768).
Row ids written to data/splits/long-rows-gemma-4-31b.json.
