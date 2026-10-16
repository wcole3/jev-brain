#!/usr/bin/env bash
# Stock vLLM baseline on the full Vision suite: the kit's own vllm-vl engine, no gateway, no docker.
# usage: vision_baseline.sh PROFILE   (env: KIT_PYTHON=python3, KIT_DIR=.cache/decision-index-vision, RUN_DIR)
# The GPU must be free: the stack is down. An existing RUN_DIR resumes.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
profile=$1
env_file=$root/profiles/$profile.env
py=${KIT_PYTHON:-python3}
kit=$(realpath "${KIT_DIR:-$root/.cache/decision-index-vision}")
suite=$kit/work/vision
utc=$(date -u +%Y-%m-%dT%H%M%SZ)
run=${RUN_DIR:-$root/.cache/vision-runs/$profile/stock-$utc}

if curl -s -m 2 -o /dev/null http://127.0.0.1:8000/health; then
  echo "port 8000 answers: bring the stack down first" >&2
  exit 1
fi

setting() { sed -n "s/^$1=//p" "$env_file" | head -n 1; }
model=$(setting HF_MODEL)
revision=$(setting HF_REVISION)
mm_kwargs=$(setting MM_PROCESSOR_KWARGS)
case $profile in
  qwen*) engine=vision_engines:NoThinkVl ;;
  *) engine=vllm-vl ;;
esac

llm_options=$(REV=$revision "$py" -c 'import json, os; r = os.environ["REV"]; print(json.dumps({"revision": r, "tokenizer_revision": r, "max_num_seqs": 256}))')
options=(--option "llm_options=$llm_options" --option max_model_len=16384 --option max_images=4)
[[ -n $mm_kwargs ]] && options+=(--option "mm_processor_kwargs=$mm_kwargs")

mkdir -p "$run"
cd "$kit/src"
export PYTHONPATH=$root/scripts${PYTHONPATH:+:$PYTHONPATH}
"$py" -m decision_index vision run --dir "$suite" --no-verify --engine "$engine" --model "$model" \
  "${options[@]}" --compact --out "$run"
"$py" -m decision_index vision score --results "$run/results.jsonl" --dir "$suite" --out "$run"

out=$root/docs/results/$profile/$utc-vision-stock
cd "$root"
"$py" -m scripts.vision_summary "$run" "$suite" "$out" "Vision suite, $profile stock vLLM"
echo "$out"
