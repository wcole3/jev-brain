#!/usr/bin/env bash
# Put this commit and the pushed-not-rebuilt data on a rented box, set its profile, and start its queue.
# usage: push.sh SSH_URL PROFILE [--restore] [--vision] [--dry-run]   (SSH_URL as `vastai ssh-url ID` prints it: ssh://root@HOST:PORT)
set -euo pipefail
cd "$(dirname "$0")/../.."
box_repo=/workspace/jev-brain
usage() { echo "usage: push.sh ssh://root@HOST:PORT PROFILE [--restore] [--vision] [--dry-run]" >&2; exit 2; }

(( $# >= 2 )) || usage
url=$1 profile=$2 dry=0 restore=0 vision=0
shift 2
for arg; do
  case $arg in
    --dry-run) dry=1 ;;
    --restore) restore=1 ;;
    --vision) vision=1 ;;
    *) usage ;;
  esac
done
[[ $url =~ ^ssh://root@([^:/]+):([0-9]+)/?$ ]] || usage
box=root@${BASH_REMATCH[1]} port=${BASH_REMATCH[2]}
[[ -f scripts/remote/jobs/$profile.txt ]] || { echo "unknown profile $profile" >&2; usage; }
# vast reuses HOST:PORT across boxes, so each profile keeps its own known_hosts.
mirror=.cache/remote-boxes/$profile
mkdir -p "$mirror"
ssh=(ssh -p "$port" -o StrictHostKeyChecking=accept-new
  -o "UserKnownHostsFile=$PWD/$mirror/known_hosts" -o ServerAliveInterval=30)
# Vast key: JEV_SSH_KEY, else ~/.ssh/id_vast when it exists (ssh never offers that name by default).
key=${JEV_SSH_KEY:-$HOME/.ssh/id_vast}
[[ -f $key ]] && ssh+=(-i "$key" -o IdentitiesOnly=yes)
rsync=(rsync -az --no-owner --no-group -e "${ssh[*]}")
run() { if (( dry )); then printf '%q ' "$@"; echo; else "$@"; fi; }

if [[ -n $(git status --porcelain) ]]; then
  echo "refusing to push a dirty tree; commit or stash first:" >&2
  git status --short >&2
  exit 1
fi
if (( restore )) && [[ ! -f $mirror/run_tag ]]; then
  echo "--restore needs the old box's pulled state ($mirror/run_tag); pull it first" >&2
  exit 1
fi
echo "pushing $(git log -1 --format='%h %s') to $box port $port as $profile"

# The image has no rsync, tmux or git.
run "${ssh[@]}" "$box" "mkdir -p $box_repo && { command -v rsync && command -v tmux && command -v git; } > /dev/null \
|| { apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq rsync tmux git; }"
# secrets/ stays here except its tracked .gitkeep, so the box tree matches the commit.
run "${rsync[@]}" --include=/secrets/.gitkeep '--exclude=/secrets/*' \
  --exclude={.cache,.venv,.firecrawl,.superpowers,.env,.vscode,.pytest_cache,.ruff_cache,__pycache__} \
  ./ "$box:$box_repo/"
# Results are stamped "-dirty" when the box code differs from the commit (bench.git_revision's rule), so stop here.
check="git config --global --get-all safe.directory | grep -qxF $box_repo"
check+=" || git config --global --add safe.directory $box_repo;"
check+=" dirty=\$(git -C $box_repo status --porcelain -- . ':(exclude)docs/results') && [ -z \"\$dirty\" ]"
check+=" || { echo 'box tree differs from the pushed commit; not starting:' >&2; echo \"\$dirty\" >&2; exit 1; }"
run "${ssh[@]}" "$box" "$check"
run "${rsync[@]}" --relative .cache/decision-index/rows-0.3.jsonl.gz .cache/decision-index/suite-0.3 \
  .cache/jevbench "$box:$box_repo/"
# vision: the Decision Index kit source and its 4.3 GB Vision suite (DS-024), for vision_run.py and the stock baseline.
if (( vision )); then
  run "${rsync[@]}" --relative .cache/decision-index-vision/src .cache/decision-index-vision/work/vision \
    "$box:$box_repo/"
fi

# restore: a replacement box gets the pulled runs, run tag and index/collect markers before its queue starts.
# A finished index must stay done (a rerun would overwrite its summary); stack and host-compare rerun here.
restore() {
  local marker markers=()
  for marker in "$mirror/state/$profile"/{index,collect-*}.done; do
    [[ -f $marker ]] && markers+=("$marker")
  done
  run "${ssh[@]}" "$box" "mkdir -p $box_repo/.cache/remote/state/$profile"
  run "${rsync[@]}" --relative --ignore-missing-args .cache/index-runs/"$profile" .cache/collect/"$profile" \
    .cache/vision-runs/"$profile" "$box:$box_repo/"
  run "${rsync[@]}" "$mirror/run_tag" "$box:$box_repo/.cache/remote/run_tag"
  if (( ${#markers[@]} )); then
    run "${rsync[@]}" "${markers[@]}" "$box:$box_repo/.cache/remote/state/$profile/"
  fi
}
(( restore )) && restore

run "${ssh[@]}" "$box" "mkdir -p $box_repo/.cache/remote && echo $profile > $box_repo/.cache/remote/profile"
# Detached (setsid -f) so ssh returns: start.sh holds a lock and may bootstrap for a long time.
run "${ssh[@]}" "$box" "cd $box_repo && setsid -f bash scripts/remote/start.sh > /dev/null 2>&1 < /dev/null"
(( dry )) && exit 0

echo "started. follow: ${ssh[*]} $box tail -f $box_repo/.cache/remote/logs/start.log"
echo "attach: ${ssh[*]} -t $box tmux attach -t jev    pull: scripts/remote/pull.sh $url $profile --loop 1800"
