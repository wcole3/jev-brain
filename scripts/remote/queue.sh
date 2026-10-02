#!/usr/bin/env bash
# Run a job file's `name: command` lines in order from the repo root; done jobs are skipped, a failure stops the queue.
# usage: queue.sh JOBFILE  (markers and job logs per job-file name; env REMOTE_STATE: root, default .cache/remote)
set -euo pipefail
jobfile=$(realpath "$1")
cd "$(dirname "$0")/../.."
root=${REMOTE_STATE:-.cache/remote}
profile=$(basename "$jobfile" .txt)
state=$root/state/$profile
logs=$root/logs/$profile
mkdir -p "$state" "$logs"
rm -f "$state/QUEUE_DONE"  # a rerun (e.g. after a reboot) must not look finished to pull.sh --loop

note() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) == $*" | tee -a "$root/logs/queue.log"; }

while IFS= read -r line || [[ -n $line ]]; do
  [[ -z ${line// } || $line == \#* ]] && continue
  name=${line%%:*}
  command=${line#*:}
  [[ -f $state/$name.done ]] && continue
  rm -f "$state/$name.failed"
  note "$name start"
  code=0
  bash -c "$command" > "$logs/$name.log" 2>&1 < /dev/null || code=$?
  if (( code != 0 )); then
    echo "exit=$code at $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$state/$name.failed"
    note "$name FAILED (exit $code)"
    exit "$code"
  fi
  touch "$state/$name.done"
  note "$name done"
done < "$jobfile"
touch "$state/QUEUE_DONE"
note "$profile queue done"
