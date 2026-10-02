#!/usr/bin/env bash
# Box onstart entry, safe at every boot or rerun: bootstrap once, then reopen whichever `jev` tmux window is gone.
# Retry after a failed job: fix the cause, then `bash scripts/remote/start.sh` (the queue resumes at that job).
set -euo pipefail
cd "${JEV_REPO:-/workspace/jev-brain}" 2> /dev/null || exit 0
[[ -f .cache/remote/profile ]] || exit 0
profile=$(cat .cache/remote/profile)
mkdir -p .cache/remote/logs .cache/remote/state/"$profile"
exec >> .cache/remote/logs/start.log 2>&1
exec 9> .cache/remote/start.lock
flock 9
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) start.sh for $profile"

[[ -f .cache/remote/run_tag ]] || echo "$(date -u +%Y-%m-%dT%H%M%SZ)-vast" > .cache/remote/run_tag
windows=$(tmux list-windows -t jev -F '#{window_name}' 2> /dev/null || true)
has() { grep -qx "$1" <<< "$windows"; }
if has telemetry && has queue; then
  echo "tmux session jev already running both windows"
  exit 0
fi
bash scripts/remote/bootstrap.sh "$profile"

# open NAME COMMAND: a window in session jev, creating the session if it is gone.
# `9>&-` keeps the lock out of the tmux server, which would otherwise hold it forever.
open() {
  if tmux has-session -t jev 2> /dev/null; then
    tmux new-window -t jev -n "$1" -c "$PWD" "$2" 9>&-
  else
    tmux new-session -d -s jev -n "$1" -c "$PWD" "$2" 9>&-
  fi
  echo "opened window $1 (run tag $(cat .cache/remote/run_tag))"
}
has telemetry || open telemetry "uv run python scripts/gpu_telemetry.py sample --out .cache/remote/telemetry.csv --interval 5"
if ! has queue; then
  # The stack may be gone (a boot); stack.sh up is a no-op when it is healthy.
  rm -f .cache/remote/state/"$profile"/stack.done
  open queue "bash scripts/remote/queue.sh scripts/remote/jobs/$profile.txt"
fi
