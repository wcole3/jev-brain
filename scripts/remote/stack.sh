#!/usr/bin/env bash
# Box stack: the image's own vLLM, then the gateway, both on 127.0.0.1 (reach them with ssh -L).
# usage: stack.sh up PROFILE [K=V ...] | down | status | patch-vllm
set -euo pipefail
cd "$(dirname "$0")/../.."
remote=.cache/remote
logs=$remote/logs
vllm=http://127.0.0.1:8000
gateway=http://127.0.0.1:9000
mkdir -p "$logs"

# The gateway's profile when it is healthy, else nothing.
gateway_profile() {
  curl -sf -m 10 "$gateway/health" 2>/dev/null \
    | python3 -c 'import json, sys; b = json.load(sys.stdin); print(b["profile"] if b["status"] == "ok" else "")' \
    2>/dev/null || true
}

# start NAME CMD...: run CMD in its own session (so stop can signal the whole group), log and pid under .cache/remote.
# An earlier log is kept under the time it was last written, so a crash's log survives the restart.
start() {
  local name=$1 log=$logs/$1.log
  shift
  if [[ -f $log ]]; then mv "$log" "$logs/$name.$(date -u -r "$log" +%Y%m%dT%H%M%SZ).log"; fi
  setsid nohup "$@" > "$logs/$name.log" 2>&1 < /dev/null &
  echo $! > "$remote/$name.pid"
}

# stop NAME PATTERN: TERM the group, KILL after 60 s; PATTERN must match the pid's command line (pids survive reboots).
stop() {
  local file=$remote/$1.pid pid
  [[ -f $file ]] || return 0
  pid=$(cat "$file")
  rm -f "$file"
  grep -qa -- "$2" "/proc/$pid/cmdline" 2>/dev/null || return 0
  kill -TERM -- "-$pid" 2>/dev/null || true
  for _ in $(seq 60); do
    kill -0 -- "-$pid" 2>/dev/null || return 0
    sleep 1
  done
  kill -KILL -- "-$pid" 2>/dev/null || true
}

# wait_for NAME SECONDS CHECK...: poll CHECK every 5 s; fail with the log tail if NAME's process dies or time runs out.
wait_for() {
  local name=$1 limit=$2 pid
  shift 2
  pid=$(cat "$remote/$name.pid")
  local deadline=$((SECONDS + limit))
  until "$@"; do
    if ! kill -0 "$pid" 2>/dev/null || (( SECONDS > deadline )); then
      echo "$name did not become healthy within $limit s (or died); last log lines:" >&2
      tail -n 40 "$logs/$name.log" >&2
      exit 1
    fi
    sleep 5
  done
  echo "$name healthy"
}

vllm_ok() { curl -sf -m 10 "$vllm/health" > /dev/null 2>&1; }
gateway_ok() { [[ -n $(gateway_profile) ]]; }

# Compose mounts our fixed rejection sampler (DS-004) and scheduler (#60476) over the image's;
# boxes run the image's vLLM, so copy them in.
patch_vllm() {
  local dir
  dir=$(python3 -c 'import os, vllm; print(os.path.dirname(vllm.__file__))')
  cp docker/vllm/rejection_sampler.py "$dir/v1/worker/gpu/spec_decode/rejection_sampler.py"
  cp docker/vllm/scheduler.py "$dir/v1/core/sched/scheduler.py"
}

up() {
  local profile=$1 envs
  shift
  if [[ $(gateway_profile) == "$profile" ]]; then
    echo "stack already up for $profile"
    return 0
  fi
  down
  envs=$(uv run python scripts/profile_env.py "$profile" \
    VLLM_HOST=127.0.0.1 VLLM_URL=http://127.0.0.1:8000 HF_HUB_OFFLINE=1 "$@")
  eval "$envs"
  patch_vllm
  start vllm bash docker/vllm-entrypoint.sh
  wait_for vllm 1800 vllm_ok
  start gateway uv run --frozen uvicorn gateway.app:app --host 127.0.0.1 --port 9000
  wait_for gateway 120 gateway_ok
}

down() {
  stop gateway uvicorn
  stop vllm vllm
}

status() {
  if vllm_ok; then echo "vllm: ok"; else echo "vllm: down"; fi
  echo "gateway: $(curl -sf -m 10 "$gateway/health" 2>/dev/null || echo down)"
}

case ${1:-} in
  up) [[ $# -ge 2 ]] || { echo "usage: stack.sh up PROFILE [K=V ...]" >&2; exit 2; }; shift; up "$@" ;;
  down) down ;;
  status) status ;;
  patch-vllm) patch_vllm ;;
  *) echo "usage: stack.sh up PROFILE [K=V ...] | down | status | patch-vllm" >&2; exit 2 ;;
esac
