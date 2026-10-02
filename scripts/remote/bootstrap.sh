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

if ! command -v rsync > /dev/null || ! command -v tmux > /dev/null || ! command -v git > /dev/null; then
  apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y rsync tmux git
fi
uv sync --frozen
[[ -x $harness ]] || uv run python scripts/index_suite.py setup
# `suite verify` reports a mismatch without failing, so check its "match" field.
"$harness" -m decision_index suite verify --edition 0.2.1 --dir .cache/decision-index/suite-0.2 \
  | tee /dev/stderr | python3 -c 'import json, sys; sys.exit(0 if json.load(sys.stdin)["match"] else "suite hash mismatch")'
uv run python scripts/fetch_model.py --profile "$profile"
uv run pytest -q

mkdir -p "$(dirname "$marker")"
echo "$profile" > "$marker"
echo "bootstrap done for $profile"
