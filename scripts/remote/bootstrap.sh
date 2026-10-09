#!/usr/bin/env bash
# One-time box setup: tools, venvs, suite check, weights, unit tests. A marker naming the profile makes reruns free.
# usage: bootstrap.sh PROFILE
set -euo pipefail
cd "$(dirname "$0")/../.."
profile=$1
marker=.cache/remote/state/bootstrap.done
harness=.cache/decision-index-venv/bin/python
if [[ -f $marker && $(cat "$marker") == "$profile" ]]; then
  echo "bootstrap already done for $profile"
  exit 0
fi

# retry CMD...: up to 3 tries 60 s apart, for transient HF errors (snapshot_download resumes).
retry() {
  local try
  for try in 1 2 3; do
    "$@" && return 0
    echo "try $try of 3 failed: $*" >&2
    (( try == 3 )) || sleep 60
  done
  return 1
}

if ! command -v rsync > /dev/null || ! command -v tmux > /dev/null || ! command -v git > /dev/null; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y rsync tmux git
fi
uv sync --frozen
# A setup cut off midway leaves a clone or venv that blocks the next one, so start it over.
if ! "$harness" -c 'import decision_index' 2> /dev/null; then
  rm -rf .cache/decision-index/src .cache/decision-index-venv
  uv run python scripts/index_suite.py setup
fi
# `suite verify` reports a mismatch without failing, so print its report and check the "match" field.
"$harness" -m decision_index suite verify --edition 0.3 --dir .cache/decision-index/suite-0.3 | python3 -c '
import json, sys
report = sys.stdin.read()
print(report)
sys.exit(0 if json.loads(report)["match"] else "suite hash mismatch")'
retry uv run python scripts/fetch_model.py --profile "$profile"
retry uv run pytest -q

mkdir -p "$(dirname "$marker")"
echo "$profile" > "$marker"
echo "bootstrap done for $profile"
