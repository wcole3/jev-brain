#!/usr/bin/env bash
# Rent a vast.ai offer for PROFILE with the compose vLLM image; its onstart runs start.sh at every boot.
# usage: rent.sh OFFER_ID PROFILE [--disk GB] [--dry-run]   (--dry-run prints the vastai command only)
set -euo pipefail
cd "$(dirname "$0")/../.."
image=vllm/vllm-openai:v0.30.0@sha256:8a69ffad015f138d7170c4ddc429e230a3bc1c1719f67e14324749df200a4b90
usage() { echo "usage: rent.sh OFFER_ID PROFILE [--disk GB] [--dry-run]" >&2; exit 2; }

[[ $# -ge 2 && $1 =~ ^[0-9]+$ ]] || usage
offer=$1 profile=$2 disk=250 dry=0
shift 2
while (( $# )); do
  case $1 in
    --disk) [[ ${2:-} =~ ^[0-9]+$ ]] || usage; disk=$2; shift 2 ;;
    --dry-run) dry=1; shift ;;
    *) usage ;;
  esac
done
[[ -f scripts/remote/jobs/$profile.txt ]] || { echo "unknown profile $profile" >&2; usage; }

# No --env '--shm-size=16g': vastai's argparse rejects it, and it keeps only -e/-p/-h/-v/-n options.
command=(vastai --raw create instance "$offer" --image "$image" --disk "$disk" --ssh --direct
  --label "jev-$profile" --cancel-unavail --onstart-cmd "bash /workspace/jev-brain/scripts/remote/start.sh")
if (( dry )); then
  printf '%q ' "${command[@]}"
  echo
  exit 0
fi
reply=$("${command[@]}") || { echo "vastai create instance failed (exit $?): $reply" >&2; exit 1; }
id=$(python3 -c '
import json, sys
try:
    reply = json.loads(sys.argv[1])
except ValueError:
    reply = None
if not (isinstance(reply, dict) and reply.get("success")):
    sys.exit(f"vastai did not rent: {sys.argv[1]}")
print(reply["new_contract"])' "$reply")
echo "rented instance $id for $profile"
echo "when it is running: vastai ssh-url $id, then scripts/remote/push.sh SSH_URL $profile"
