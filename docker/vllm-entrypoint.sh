#!/usr/bin/env bash
# Build `vllm serve` flags from the profile env; optional flags only when set.
set -euo pipefail
args=(
  "$HF_MODEL" --revision "$HF_REVISION" --tokenizer-revision "$HF_REVISION"
  --served-model-name "$SERVED_MODEL" --host "${VLLM_HOST:-0.0.0.0}" --port 8000
  --enable-prefix-caching --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION:-0.90}"
  --max-model-len "$MAX_MODEL_LEN"
  --max-num-seqs "${MAX_NUM_SEQS:-256}"
  --reasoning-parser "$REASONING_PARSER" --enable-auto-tool-choice --tool-call-parser "$TOOL_PARSER"
)
if [[ "${LANGUAGE_MODEL_ONLY:-0}" == "1" ]]; then args+=(--language-model-only); fi
if [[ -n "${CHAT_TEMPLATE:-}" ]]; then args+=(--chat-template "$CHAT_TEMPLATE"); fi
if [[ -n "${CHAT_TEMPLATE_KWARGS:-}" ]]; then args+=(--default-chat-template-kwargs "$CHAT_TEMPLATE_KWARGS"); fi
# EXTRA_ARGS comes from our own profile env, so plain word splitting is intended.
if [[ -n "${EXTRA_ARGS:-}" ]]; then read -r -a extra <<< "$EXTRA_ARGS"; args+=("${extra[@]}"); fi
exec vllm serve "${args[@]}"
