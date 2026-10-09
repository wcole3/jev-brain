"""Run with the harness venv: verify an edition's suite, then write its scoreable rows to one file.

usage: .cache/decision-index-venv/bin/python scripts/harness_export.py SUITE_DIR OUT.jsonl.gz EDITION
"""

import gzip
import json
import sys

from decision_index.suite.io import Suite

suite_dir, out, edition = sys.argv[1], sys.argv[2], sys.argv[3]
suite = Suite(suite_dir, edition)
report = suite.verify(strict=True)
n = 0
with gzip.open(out, "wt", encoding="utf-8") as f:
    for row in suite.rows(apply_exclusions=True):  # exclusions and the edition's subsets, as scoring sees them
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        n += 1
print(json.dumps({"rows": n, "suite_sha256": report["sha256"], "match": report["match"]}))
