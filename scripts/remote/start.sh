#!/usr/bin/env bash
# Box onstart entry, safe at every boot: bootstrap once, then tmux session `jev` runs telemetry and the job queue.
# usage: start.sh  (vast.ai --onstart-cmd; push.sh also runs it once)
set -euo pipefail
cd /workspace/jev-brain 2> /dev/null || exit 0
[[ -f .cache/remote/profile ]] || exit 0
profile=$(cat .cache/remote/profile)
mkdir -p .cache/remote/logs .cache/remote/state
exec >> .cache/remote/logs/start.log 2>&1
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) start.sh for $profile"

[[ -f .cache/remote/run_tag ]] || echo "$(date -u +%Y-%m-%dT%H%M%SZ)-vast" > .cache/remote/run_tag
if tmux has-session -t jev 2> /dev/null; then
  echo "tmux session jev already running"
  exit 0
fi
bash scripts/remote/bootstrap.sh "$profile"
# No session means the stack is gone too (a boot), so the queue must bring it up again.
rm -f .cache/remote/state/stack.done
tmux new-session -d -s jev -n telemetry -c "$PWD" \
  "uv run python scripts/gpu_telemetry.py sample --out .cache/remote/telemetry.csv --interval 5"
tmux new-window -t jev -n queue -c "$PWD" "bash scripts/remote/queue.sh scripts/remote/jobs/$profile.txt"
echo "tmux session jev started (run tag $(cat .cache/remote/run_tag))"
