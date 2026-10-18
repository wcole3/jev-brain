# qwen3.8-27b R3 label pipeline check

## Provenance

- timestamp: 2026-10-18T212640Z
- repo commit: e4d2608-dirty
- profile: qwen3.8-27b
- rule: identity top answer on 200 rows (seed 0) both collects hold, any status, ≥ 0.98; a status mismatch or a question on one side only counts as disagreement
- collects calib-600: .cache/collect/qwen3.8-27b/calib.jsonl.gz vs .cache/collect/qwen3.8-27b/calib-600-letters.jsonl.gz
- collects index-dev-2k: .cache/collect/qwen3.8-27b/index-dev.jsonl.gz vs .cache/collect/qwen3.8-27b/index-dev-2k-letters.jsonl.gz
- collects image dev: .cache/vision-collect/qwen3.8-27b/baseline/dev.jsonl.gz vs .cache/vision-collect/qwen3.8-27b/labels-letters/dev.jsonl.gz

| split | rows | questions | agree | status mismatches | one-sided questions | agreement |
|---|---|---|---|---|---|---|
| calib-600 | 200 | 197 | 197 | 0 | 0 | 1.000 |
| index-dev-2k | 200 | 374 | 373 | 0 | 0 | 0.997 |
| image dev | 200 | 200 | 199 | 0 | 0 | 0.995 |

**passed**
