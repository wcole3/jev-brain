#!/usr/bin/env bash
# Copy a box's results, collect and index runs, and remote logs/state here; never deletes local files.
# usage: pull.sh SSH_URL PROFILE [--loop SECONDS]   (--loop: repeat until the queue is done, then pull once more)
set -euo pipefail
cd "$(dirname "$0")/../.."
box_repo=/workspace/jev-brain
usage() { echo "usage: pull.sh ssh://root@HOST:PORT PROFILE [--loop SECONDS]" >&2; exit 2; }

case $# in
  2) loop= ;;
  4) [[ $3 == --loop && $4 =~ ^[0-9]+$ ]] || usage; loop=$4 ;;
  *) usage ;;
esac
[[ $1 =~ ^ssh://root@([^:/]+):([0-9]+)/?$ ]] || usage
box=root@${BASH_REMATCH[1]} port=${BASH_REMATCH[2]} profile=$2
[[ -f scripts/remote/jobs/$profile.txt ]] || { echo "unknown profile $profile" >&2; usage; }
mirror=.cache/remote-boxes/$profile
queue_done=$mirror/state/$profile/QUEUE_DONE
ssh=(ssh -p "$port" -o StrictHostKeyChecking=accept-new -o "UserKnownHostsFile=$PWD/$mirror/known_hosts"
  -o ServerAliveInterval=30)

# fetch RSYNC_ARGS...: exit 24 (files vanished mid-copy while jobs write) is fine; the next pass gets them.
fetch() { rsync -az --ignore-missing-args -e "${ssh[*]}" "$@" || (( $? == 24 )); }

# Box state comes last, so the pass after the one that brings QUEUE_DONE has every result.
pull_once() {
  local dir
  mkdir -p {docs/results,.cache/collect,.cache/index-runs}/"$profile" "$mirror"
  # --update: a local file newer than the box's copy (an edit here) is kept.
  for dir in docs/results .cache/collect .cache/index-runs; do
    fetch --update "$box:$box_repo/$dir/$profile" "$dir/" || return
  done
  rm -f "$queue_done"  # the box removes it when its queue restarts
  fetch "$box:$box_repo/.cache/remote/"{logs,state,telemetry.csv,run_tag} "$mirror/" || return
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) pulled $profile; queue.log ends:"
  tail -n 3 "$mirror/logs/queue.log" 2> /dev/null || true
}

if [[ -z $loop ]]; then
  pull_once
  exit
fi
final=0
while true; do
  if pull_once; then
    (( final )) && exit 0
    if [[ -f $queue_done ]]; then
      echo "queue done; one final pass"
      final=1
      continue
    fi
  else
    echo "warning: pull failed (box down or rebooting?); retrying in $loop s" >&2
  fi
  sleep "$loop"
done
