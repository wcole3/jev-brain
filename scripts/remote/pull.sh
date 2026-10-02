#!/usr/bin/env bash
# Copy a box's results, collect and index runs, and remote logs/state here; never deletes local files.
# usage: pull.sh SSH_URL PROFILE [--loop SECONDS]   (--loop: repeat until the queue is done, then pull once more)
# Each pass prints a status line; one pass exits 3 when bootstrap or a job failed, --loop keeps going.
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
state=$mirror/state
queue_done=$state/$profile/QUEUE_DONE
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
  # Markers only: the box removes these when it retries, so a stale copy must not keep the alarm up.
  rm -f "$queue_done" "$state/$profile"/*.failed "$state"/bootstrap.{done,failed}
  fetch "$box:$box_repo/.cache/remote/"{logs,state,telemetry.csv,run_tag} "$mirror/" || return
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) pulled $profile; queue.log ends:"
  tail -n 3 "$mirror/logs/queue.log" 2> /dev/null || true
}

# report: one status line from the mirror (and start.log's tail if bootstrap failed); fails on any failure.
report() {
  local boot=running job marker failed=()
  [[ -f $state/bootstrap.done ]] && boot=done
  [[ -f $state/bootstrap.failed ]] && boot=FAILED
  for marker in "$state/$profile"/*.failed; do
    [[ -f $marker ]] && failed+=("$(basename "$marker" .failed)")
  done
  # The current job is the last one started with no done or FAILED line after it.
  job=$(awk '$4 == "start" {job = $3} ($4 == "done" || $4 == "FAILED") && $3 == job {job = ""} END {print job}' \
    "$mirror/logs/queue.log" 2> /dev/null || true)
  echo "bootstrap: $boot; job: ${job:-none}; failed: ${failed[*]:-none}"
  if [[ $boot == FAILED ]]; then tail -n 5 "$mirror/logs/start.log" 2> /dev/null || true; fi
  [[ $boot != FAILED && ${#failed[@]} == 0 ]]
}

if [[ -z $loop ]]; then
  pull_once
  report || exit 3
  exit 0
fi
final=0
while true; do
  if pull_once; then
    report || true
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
