# Prefill and decode: why decisions starve chat on one GPU

A primer on the two phases of LLM inference, plus what our qwen3.6-27b bench runs show.
The vLLM scheduler internals and the experiment plan are in
[ds007-scheduling.md](../appendix/ds007-scheduling.md) ("DS-007" below); this doc
explains the idea and links there for depth.

## Short answer

- **Every request has two phases.** *Prefill* reads the whole prompt at once and is
  limited by the GPU's arithmetic (compute-bound). *Decode* writes the reply one token
  per step and is limited by how fast the weights stream from memory
  (memory-bandwidth-bound).
- **vLLM runs both in the same steps,** up to a budget of 8,192 tokens per step
  (`--max-num-batched-tokens`, our default). A chat stream gets one token per step, so
  its speed is 1 ÷ step time.
- **A systemone decision is all prefill** (`max_tokens: 1`). Chat is mostly decode. A
  burst of decisions fills every step's budget with prefill, so every step gets much
  longer, and chat slows down with it.
- **Measured:** under 4 systemone clients, chat fell from 26.6 to 1.2 chunks/s (~22×
  slower), and one chat request waited 3,287 ms for its first token instead of 144 ms.
- **Prefill saturates the GPU's compute.** vLLM computes ~6,000 prompt tokens/s
  (after prefix-cache hits) whether 1 or 16 clients are sending, up to 213 prompts wait in its queue, and at most
  12% of the KV cache is in use.
- **Priority scheduling (vLLM v0.30) should fix the wait, not the speed.** Chat can jump
  the queue, but every step stays full of prefill. Decode speed needs smaller steps (a
  smaller budget), fewer decisions while chat streams (a gateway governor), or less
  prefill per decision (DS-008). Splitting the GPU (MIG, MPS) is not possible on WSL2.

## 1. The two phases of a request

Terms used below:
- **Step** (or iteration): one forward pass of the model over the current batch. Every
  step reads all the weights from GPU memory once: about 55 GB for Qwen3.6-27B in bf16.
- **KV cache:** the keys and values the model keeps for each token it has already
  processed, so later tokens don't recompute them.
- **Prefill:** processing the prompt, all its tokens in parallel. It fills the KV cache and
  yields the first output token.
- **Decode:** generating the rest of the reply, one token per request per step.
- **TTFT** (time to first token): queueing plus prefill. **ITL** (inter-token latency):
  the gap between streamed tokens, which is one step.

| | Prefill | Decode |
|---|---|---|
| Tokens per request per step | many (a chunk of the prompt) | 1 |
| Arithmetic per weight read | a lot: every token multiplies every weight | little |
| Bottleneck | compute (FLOPs) | memory bandwidth |
| Latency it sets | TTFT | ITL, i.e. how fast chat streams |

Why they differ:

- **Decode is limited by memory.** Reading ~55 GB of weights at the RTX PRO 6000's
  1.79 TB/s takes ~31 ms (a roofline estimate, DS-007 §0). Chat alone streams 26.6
  chunks/s, about 37 ms per step, so a decode step is mostly that read, while the
  arithmetic units sit idle.
- **Prefill is limited by compute.** It pushes hundreds or thousands of tokens through
  each weight read, so arithmetic dominates, and the step time grows with the number of
  tokens.
- **The crossover is roughly 280 tokens per step on this GPU** (an estimate: ~500
  dense bf16 TFLOPS ÷ 1.79 TB/s, DS-007 §0). Below it, extra prefill tokens ride along
  with a decode step almost free; above it, every extra token adds time. That slack is
  the core idea of Sarathi-Serve.

## 2. How vLLM mixes them: continuous batching and the step budget

- **Continuous batching** (iteration-level scheduling, from Orca): the batch is rebuilt
  every step. Finished requests leave and waiting ones join between steps, instead of
  waiting for the whole batch to finish.
- **Chunked prefill** (Sarathi-Serve): a long prompt is cut into chunks so it can share
  steps with running decodes. Without it, a big prefill would stall every decode for
  its full length. vLLM V1 enables it by default.
- **Token budget:** `--max-num-batched-tokens` caps the tokens in one step.
  - Each running decode costs 1 token of the budget; prefill chunks fill the rest.
  - Our [entrypoint](../../docker/vllm-entrypoint.sh) doesn't set it, so vLLM picks
    8,192 on this GPU (startup log, DS-007 §0).

The budget is a trade-off knob. vLLM's docs: "Smaller values (e.g., 2048) achieve better
ITL because there are fewer prefills slowing down decodes. Higher values achieve better
time to first token (TTFT) as you can process more prefill tokens in a batch."

```
chat alone             step = [chat 1 tok]                                         ~37 ms (measured)
chat + decision burst  step = [chat 1 tok][systemone prefill ... up to 8,191 tok]  up to ~1.4 s (estimate)
                       chat still gets 1 token per step  ->  ~1 token/s
```

The ~1.4 s is 8,191 tokens ÷ ~5.8k computed tokens/s, DS-007's step-time model.

## 3. A decision is all prefill; chat is mostly decode

[readout.py](../../gateway/readout.py) asks `/v1/completions` for `max_tokens: 1` and
reads the answer letters' log-probabilities at the answer slot. Each question is its own
prompt row ([prompt-sharing.md §1](prompt-sharing.md)), so vLLM prefills every row and
emits one token per row: there is no real decode phase.

| | systemone (bench shape: 2,048-token state × 16 questions × 26 options) | chat (bench) |
|---|---|---|
| Prompt | 16 rows; ~14.4k tokens computed after prefix-cache hits | one sentence |
| Output | 1 token per row | up to 512 tokens |
| Engine steps | a few, each packed with prefill | one per output token |
| Limited by | compute | memory bandwidth |

After row 1 warms the prefix cache, the other 15 rows arrive in one call and need more
than a full 8,192-token budget of prefill. So one systemone client can keep the steps full.

## 4. What we measured

### 4a. Chat alone vs under decisions

`bench.py --chat` ([`chat_under_load`](../../scripts/bench.py)) streams two chat
prompts with `max_tokens: 512`, first alone, then while 4 clients loop 2,048×16×26
systemone requests. "Short" and "long" name the expected reply; both prompts are one
sentence. Phase-1 full run ([summary](../results/qwen3.6-27b/2026-09-28T000000Z/summary.md)):

| chat prompt | load | TTFT ms | chunks/s |
|---|---|---|---|
| short | none | 140 | 26.6 |
| long | none | 144 | 26.8 |
| short | 4 systemone | 105 | 1.2 |
| long | 4 systemone | 3,287 | 1.2 |

- **Decode: 26.6 → 1.2 chunks/s for both prompts.** A chunk is about one token, so the
  average step grew from ~37 ms to ~0.8 s. vLLM's log in this phase showed ~5.77k prompt
  tokens/s against ~7.6 generated tokens/s (DS-007 §0): the steps were full of prefill.
- **TTFT: 144 → 3,287 ms for the second chat request.** Under first-come-first-served
  (FCFS) it joined the back of vLLM's waiting queue, which held up to 15 systemone rows,
  and waited for all of them.
- **The first request's 105 ms is likely a timing effect.** It was sent the moment the
  load started, probably before the first systemone rows reached vLLM. Not verified.

Only qwen3.6-27b has this table: the gemma-4-31b and qwen3.8-27b phase-1 runs didn't
include chat.

### 4b. Prefill saturates the GPU

From the `--quick` run's per-phase table ([summary](../results/archive/qwen3.6-27b/2026-09-29T210957Z-quick/summary.md));
computed tokens/s = computed tokens ÷ phase wall time in
[raw.jsonl](../results/archive/qwen3.6-27b/2026-09-29T210957Z-quick/raw.jsonl), as in
[prompt-sharing.md §5](prompt-sharing.md):

| Phase | Requests/s | Computed tokens/s | Waiting peak | KV peak | Preemptions |
|---|---|---|---|---|---|
| throughput x1 | 0.40 | 5,758 | 2 | 8.9% | 0 |
| throughput x4 | 0.42 | 6,093 | 47 | 10.2% | 0 |
| throughput x16 | 0.42 | 6,066 | 213 | 10.2% | 0 |

- **Flat at ~6k tokens/s from 1 to 16 clients.** One client already uses the compute.
  More clients only lengthen the queue; running prompts peak at 13 in all three phases
  (raw.jsonl).
- **Memory is not the limit.** KV use peaks at 12.2% across all phases and nothing is
  preempted. Requests wait for compute.
- **~6k tokens/s is about 310 TFLOPS of useful work** (an estimate, DS-007 §0), a large
  share of the GPU's dense bf16 peak.
- **The same pattern holds on the other profiles.** Their phase-1 runs are also flat
  from 1 to 16 clients: qwen3.8-27b at 0.4 req/s
  ([summary](../results/qwen3.8-27b/2026-09-28T000000Z/summary.md)), gemma-4-31b at
  0.6 → 0.5 ([summary](../results/gemma-4-31b/2026-09-28T000000Z/summary.md)).

For chat this means two things:
- whenever decisions are in flight, nearly every step is full of prefill, so chat
  decodes at one token per full step;
- under FCFS, a chat request arriving at 16 clients queues behind 213 rows. At ~900
  computed tokens per row that is ~190k tokens, about 30 s (an estimate, not measured).

## 5. What priority scheduling does and doesn't fix

Today the stack is FCFS: the entrypoint sets no scheduling policy and
[readout.py](../../gateway/readout.py) sends no priority. vLLM v0.30 offers
`--scheduling-policy priority` plus a per-request `priority` field, where "lower value
means earlier handling". DS-007's plan: chat at 0, systemone at 1.

How the v0.30 scheduler fills a step (read from source, DS-007 §1):
1. **Running requests go first,** in the order they were admitted. Systemone rows in the
   middle of their prefill count as running, and each takes the budget it needs.
2. **Waiting requests are admitted from what is left,** highest priority first.
3. **A running request is never paused** for a higher-priority waiting one. The only
   exception is the KV cache running out, which doesn't happen here.

(vLLM's docs say V1 "batches all pending decode requests before scheduling any prefill
operations", but in the v0.30 code in-flight prefill chunks count as running too.)

| Symptom under load | Cause | Fixed by priority? |
|---|---|---|
| Slow first token (3,287 ms) | chat waits behind queued systemone rows | **Yes, expected.** Chat jumps the waiting queue and waits only for rows already running: a few steps (DS-007 estimate) |
| Slow decode (1.2 chunks/s) | every step carries up to ~8k prefill tokens | **No.** Neither the budget nor the step size changes |

ConServe measured the same on vLLM. A priority scheduler serving online and offline work
together still raised online P99 time per output token 3.16×, because offline requests
"are batched together with online requests and cannot be preempted selectively". We
have not measured priority yet: that is row A1 of DS-007 §7.

## 6. What can fix decode speed

| Option | What it does | Expected effect | Cost and risk |
|---|---|---|---|
| **Smaller step budget** (`--max-num-batched-tokens` 512–784) | Caps prefill per step, so steps stay short | Chat ~7–10 tokens/s under full load, vs 1.2 today (estimate) | Some systemone throughput lost to per-step overhead, maybe 5–15% at 512 (estimate), even with chat idle |
| **Gateway governor** | While a chat stream is live, send systemone rows in small waves and cap in-flight calls | Fewer steps carry prefill; decisions run at full speed when chat is idle | Can't shape a single step, so pair it with a smaller budget. Decisions slow down while chat streams. Clients calling :8000 directly bypass it |
| **Less prefill per decision** (DS-008) | Cache the whole shared state instead of 784-token blocks ([prompt-sharing.md](prompt-sharing.md)) | ~2.4× fewer computed tokens per request (simulated) | Padding changes the prompts: fidelity check and refit. Finer blocks are untested |
| **Split the GPU** (MIG, MPS, prefill/decode disaggregation) | Give chat its own slice or engine | Isolation | Not available here: MIG and MPS don't work under WSL2, and disaggregation needs two ~55 GB weight copies on a 96 GB card |

- **Smaller budget:** Sarathi-Serve used 512 for strict latency targets and 2,048 for
  relaxed ones. DS-007's step-time model estimates chat at ~3 tokens/s with a 2,048
  budget, ~7 at 784 and ~10 at 512. Hybrid Qwen chunk alignment (784-token blocks) and
  Gemma's one-image floor both constrain the choice (DS-007 §2).
- **Less prefill per decision** doesn't shorten a full step, but the same decisions keep
  the steps full for much less time.
- **Splitting the GPU:** vLLM's docs also say disaggregated prefill "DOES NOT improve
  throughput". Two separate model copies fit only if at least one is quantized, and
  would still time-share the GPU without isolation (DS-007 §4).
- **Custom scheduler class** (chat first, smaller budget while chat is live): dropped by
  the owner on 2026-09-28 (DS-007 §3c).

DS-007 §7 lists the experiment matrix (priority, budgets 2,048 → 256, governor, DS-008
rows) and its acceptance targets: under load, chat TTFT p50 ≤ 0.5 s and ≥ 10 chunks/s,
with systemone ≥ 0.32 req/s. Until then, `bench.py --chat` stays on demand.

## Caveats

- **Tiny chat sample.** The chat table is four single requests, with no repeats. Chunks/s
  is an average, so it hides individual stalls (per-token gaps are not recorded).
- **Chunks are not exactly tokens.** vLLM usually streams one token per SSE chunk, but
  this is not guaranteed.
- **Estimates:** the step times, the ~280-token crossover, the TFLOPS figure and the
  per-budget chat speeds come from DS-007's step-time model, not from measurements.
- **Server-wide counters:** computed tokens/s assumes an otherwise idle stack; gauges
  are sampled every 0.25 s.
- **One model with chat data:** only qwen3.6-27b has a chat-under-load run. Gemma 4 has
  no recurrent layers and a different prefill cost, so its numbers may differ.
- **vLLM v0.30.0 only:** the scheduler behaviour in §5 is read from source at that tag,
  and it changes between releases.

## Sources

Ours: [ds007-scheduling.md](../appendix/ds007-scheduling.md) (scheduler source,
step-time model, knobs, partitions, experiment plan),
[prompt-sharing.md](prompt-sharing.md) (computed vs cached tokens, DS-008), and the
results and code linked inline above.

External:
- Agrawal et al., "Taming Throughput-Latency Tradeoff in LLM Inference with
  Sarathi-Serve": prefill compute-bound and decode memory-bound, chunked
  prefills, stall-free batching, 512/2,048 budgets. https://arxiv.org/abs/2403.02310
- Zhong et al., "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized
  Large Language Model Serving": prefill-decoding interference, disaggregation.
  https://arxiv.org/abs/2401.09670 and https://hao-ai-lab.github.io/blogs/distserve/
- vLLM docs, Optimization and Tuning, chunked prefill and `max_num_batched_tokens`:
  https://docs.vllm.ai/en/latest/configuration/optimization/
- vLLM API docs, `SchedulerConfig` (`policy`, `max_num_batched_tokens`):
  https://docs.vllm.ai/en/latest/api/vllm/config/scheduler/
- vLLM docs, Disaggregated Prefilling (experimental):
  https://docs.vllm.ai/en/latest/features/disagg_prefill/
- Anyscale, "How continuous batching enables 23x throughput in LLM inference", on
  Orca's iteration-level scheduling:
  https://www.anyscale.com/blog/continuous-batching-llm-inference
- ConServe (arXiv 2410.01228), §3 on a priority scheduler atop vLLM:
  https://arxiv.org/abs/2410.01228
- NVIDIA RTX PRO 6000 Blackwell datasheet (1,792 GB/s), via DS-007 §0.
