#!/usr/bin/env bash
# Put this commit and the pushed-not-rebuilt data on a rented box, set its profile, and start its queue.
# usage: push.sh SSH_URL PROFILE [--dry-run]   (SSH_URL as `vastai ssh-url ID` prints it: ssh://root@HOST:PORT)
set -euo pipefail
cd "$(dirname "$0")/../.."
box_repo=/workspace/jev-brain
usage() { echo "usage: push.sh ssh://root@HOST:PORT PROFILE [--dry-run]" >&2; exit 2; }

case $# in
  2) dry=0 ;;
  3) [[ $3 == --dry-run ]] || usage; dry=1 ;;
  *) usage ;;
esac
[[ $1 =~ ^ssh://root@([^:/]+):([0-9]+)/?$ ]] || usage
box=root@${BASH_REMATCH[1]} port=${BASH_REMATCH[2]} profile=$2
[[ -f scripts/remote/jobs/$profile.txt ]] || { echo "unknown profile $profile" >&2; usage; }
ssh=(ssh -p "$port" -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30)
rsync=(rsync -az --no-owner --no-group -e "${ssh[*]}")
run() { if (( dry )); then printf '%q ' "$@"; echo; else "$@"; fi; }

if [[ -n $(git status --porcelain) ]]; then
  echo "refusing to push a dirty tree; commit or stash first:" >&2
  git status --short >&2
  exit 1
fi
echo "pushing $(git log -1 --format='%h %s') to $box port $port as $profile"

# The image has no rsync, tmux or git.
run "${ssh[@]}" "$box" "mkdir -p $box_repo && { command -v rsync && command -v tmux && command -v git; } > /dev/null \
|| { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq rsync tmux git; }"
run "${rsync[@]}" --exclude={.cache,.venv,.firecrawl,secrets,.superpowers,.env,.vscode} \
  --exclude={.pytest_cache,.ruff_cache,__pycache__} ./ "$box:$box_repo/"
run "${rsync[@]}" --relative .cache/decision-index/rows-0.2.1.jsonl.gz .cache/decision-index/suite-0.2 \
  .cache/jevbench "$box:$box_repo/"
run "${ssh[@]}" "$box" "mkdir -p $box_repo/.cache/remote && echo $profile > $box_repo/.cache/remote/profile"
# Detached: start.sh holds a lock and may bootstrap for a long time.
run "${ssh[@]}" "$box" "cd $box_repo && setsid nohup bash scripts/remote/start.sh > /dev/null 2>&1 < /dev/null &"
(( dry )) && exit 0

echo "started. follow: ${ssh[*]} $box tail -f $box_repo/.cache/remote/logs/start.log"
echo "attach: ${ssh[*]} -t $box tmux attach -t jev    pull: scripts/remote/pull.sh $1 $profile --loop 1800"
