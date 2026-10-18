# gemma-4-31b R3 label pipeline check

## Provenance

- timestamp: 2026-10-18T154855Z
- repo commit: b784d38
- profile: gemma-4-31b
- rule: identity top answer on 200 rows (seed 0) both collects hold, any status, ≥ 0.98; a status mismatch or a question on one side only counts as disagreement
- collects calib-600: .cache/collect/gemma-4-31b/calib.jsonl.gz vs .cache/collect/gemma-4-31b/calib-600-letters.jsonl.gz
- collects index-dev-2k: .cache/collect/gemma-4-31b/index-dev.jsonl.gz vs .cache/collect/gemma-4-31b/index-dev-2k-letters.jsonl.gz
- collects image dev: .cache/vision-collect/gemma-4-31b/baseline/dev.jsonl.gz vs .cache/vision-collect/gemma-4-31b/labels-letters/dev.jsonl.gz

| split | rows | questions | agree | status mismatches | one-sided questions | agreement |
|---|---|---|---|---|---|---|
| calib-600 | 200 | 200 | 197 | 3 | 0 | 0.985 |
| index-dev-2k | 200 | 374 | 373 | 0 | 0 | 0.997 |
| image dev | 200 | 200 | 197 | 0 | 0 | 0.985 |

**passed**
