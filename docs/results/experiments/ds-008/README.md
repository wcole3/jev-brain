# DS-008: making hybrid Qwen reuse the whole shared prefix

qwen3.6-27b, bf16 weights, vLLM 0.30.0, 2026-09-30. Background:
[prompt-sharing.md](../../../background/prompt-sharing.md) and
[model-architectures.md](../../../background/model-architectures.md).

## Outcome

**Adopted: front padding** (`PREFIX_PAD=front`, `PREFIX_BLOCK=784`, `WARM_MIN_PREFIX_TOKENS=784`)
on both Qwen profiles, keeping vLLM's default fp32 recurrent state.

| | Before | After (front padding) |
|---|---|---|
| Computed ÷ usage, 16 clients | 2.67 | **1.05** |
| Throughput, 16 clients | 0.5 req/s | **1.1 req/s** |
| Cold p50, 2,048-token state × 16 questions × 26 options | 2,389 ms | **982 ms** |
| JevBench answers changed (padding forced on every row) | – | 1.4% (target ≤ 2%) |

Gemma is not hybrid and keeps padding off (`PREFIX_BLOCK=0`).

## What was tried

Each folder here is one run; its name ends with the experiment it belongs to.

### Cost (`--quick`)

| Setup | Cold p50 ms | Req/s ×16 | Computed ÷ usage ×16 | Cached ×16 | Cold mix computed ÷ usage |
|---|---|---|---|---|---|
| Baseline (padding off) | 2,389 | 0.5 | 2.67 | 60% | 2.30 |
| Pad end, 784 | 1,023 | 1.1 | 1.05 | 86% | 1.09 |
| **Pad front, 784** | 1,006 | 1.1 | **1.05** | 86% | 1.09 |
| Pad middle, 784 | 1,016 | 1.0 | 1.05 | 86% | 1.09 |
| bf16 recurrent state (400-token blocks) | 1,350 | 0.8 | 1.55 | 77% | 1.64 |
| bf16 + front pad, 400 | 1,427 | 0.8 | 1.51 | 81% | 1.20 |
| Pad spread, 784 (prefix-only warm-up) | 1,419 | 0.8 | 1.47 | 82% | 1.42 |
| Pad front, 784 (prefix-only warm-up) | 1,315 | 0.8 | 1.47 | 82% | 1.42 |
| Verification: adopted profile | 982 | 1.1 | 1.05 | 86% | 1.09 |

### Answer fidelity (full JevBench vs the baseline run)

Padding was forced onto every row (`PREFIX_PAD_ALWAYS=1`). Every JevBench request has one
question, so this is a worst case: in real use a single-question request is never padded.

| Setup | Accuracy (baseline 84.2%) | Answers changed | Max \|Δp\| | ECE (baseline 0.077) |
|---|---|---|---|---|
| Pad end | 84.3 | 2.3% | 0.35 | 0.035 |
| **Pad front** | 83.9 | **1.4%** | 0.33 | 0.046 |
| Pad middle | 85.1 | 3.0% | 0.45 | 0.050 |
| Pad spread (owner's idea: pads spread through the state) | 81.6 | 8.6% | 0.83 | 0.071 |
| bf16 state, no padding | 84.3 | 0.2% | 0.08 | 0.068 |
| bf16 + front pad (400) | 84.1 | 1.1% | 0.35 | 0.065 |
| bf16 + spread pad (400) | 82.8 | 7.3% | – | – |

Chat fidelity could not separate bf16 from noise: greedy chat matched on 9 of 20 prompts vs
the fp32 baseline, while the baseline matched itself on only 10 of 20
([determinism.md](../../../background/determinism.md)).

## Findings

- **`--mamba-block-size` is ignored in vLLM 0.30.** With 256 requested, vLLM reports
  `user_specified_mamba_block_size="True"` but `mamba_block_size="784"`: align mode overwrites it.
- **A bf16 recurrent state halves the block** (400 tokens, 1,304 blocks instead of 665), with
  almost no change in answers. It saves less than padding because 400 still leaves a remainder.
- **Padding works because of where vLLM saves recurrent state.** In align mode, state is saved
  only at a prefill's last block boundary. The warm-up row is the shared prefix plus row 1's
  question (~480 tokens). With 784-token blocks that question fits in the last block, so the
  saved state lands exactly at the padded prefix end. With 400-token blocks it spills past
  (e.g. 2,800 instead of 2,400), which is why bf16 + padding gained little.
- **A prefix-only warm-up was worse**, not better (1.47 instead of 1.05), so the gateway keeps
  warming with row 1. Why a prompt ending exactly on a block boundary doesn't leave a reusable
  state was not investigated.
- **Where the pad goes matters for answers, not cost.** Pads near the question (end) or inside
  the state (spread, middle) shift answers more; front padding, far from the question, shifts
  them least. Padding also lowered ECE in every placement, an effect not investigated.
- **Temperature:** padding changes the prompt, so decider's T = 1.943 no longer strictly
  applies to qwen3.6 and decider token parity no longer holds when padding is active. Phase 2
  (DS-002) refits temperatures on the adopted setup.

## Reproduce

Run the bench against a stack started with the env overrides from the table, e.g.
`PREFIX_PAD=end docker compose --env-file profiles/qwen3.6-27b.env up -d gateway`, or
`EXTRA_ARGS="--mamba-ssm-cache-dtype bfloat16" ... up -d vllm`. Compare runs with
`uv run python scripts/compare_runs.py <baseline dir> <candidate dir>`.
