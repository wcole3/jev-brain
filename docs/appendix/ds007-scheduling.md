# DS-007: chat vs systemone on one vLLM v0.30.0 GPU: priority, prefill/decode knobs, queuing, partitions

Research date 2026-09-28. Raw material is in `.firecrawl/ds007/`:
- `src/`: vLLM files at tag v0.30.0 (commit ced6857, released 2026-09-22)
- `gh/`: GitHub issues and PRs as JSON
- `web/`: papers and NVIDIA docs
- `vllm-startup-excerpt.log` and `vllm-chat-under-load-stats.log`: taken from the running `jev-brain-vllm-1` container

Source links use `https://github.com/vllm-project/vllm/blob/v0.30.0/<path>#L<n>`, shortened below to `path:L<n>`.

## 0. What the live system shows (local evidence)

Startup log of the running v0.30.0 container (`vllm-startup-excerpt.log`):
- `Chunked prefill is enabled with max_num_batched_tokens=8192`. This is the default for GPUs with 70 GiB or more that are not A100, under the OpenAI server (`vllm/engine/arg_utils.py:L2740-L2749`).
- `Mamba cache mode is set to 'align' ... when prefix caching is enabled`, and `Setting attention block size to 784 tokens`. For this hybrid GDN model, prefix-cache and Mamba-state granularity is **784 tokens**.
- `cudagraph_capture_sizes` go up to **512**, with `cudagraph_mode FULL_AND_PIECEWISE`. Batches larger than 512 tokens run without CUDA graphs.
- Weights plus non-torch memory is 50.95 GiB. The KV cache is 31.84 GiB, which holds 453,973 tokens.
- Async scheduling is on by default (`vllm/config/vllm.py:L1438-L1487`), so the scheduler class is `AsyncScheduler`.

Engine stats during `chat_under_load` (`vllm-chat-under-load-stats.log`, 01:03 to 01:14):
- Avg prompt throughput holds at **~5.77k tok/s** and generation at ~7.6 tok/s. The 7.6 tok/s is about 0.4 req/s × 16 one-token systemone outputs plus the chat stream at ~1.2 tok/s.
- Running was 9 to 15 requests. Waiting was 0 to 15, which is one gateway request's 15 sibling prompts.
- Prefix cache hit rate was ~60%. KV usage was 9 to 12%, so there is no KV pressure and no preemption.
- 5.77k computed tok/s ÷ 0.4 req/s ≈ **14.4k computed tokens per systemone request**, out of ~36k prompt tokens. That fits block-granular hits of 2×784 = 1,568 of the ~2,048 shared state tokens per sibling prompt. Each of the 15 siblings recomputes about 480 state tokens plus its question. See §6.

Measured bench (`docs/results/qwen3.6-27b/2026-09-28/summary.md`):
- Chat idle: 26.6 chunks/s, TTFT ~140 ms.
- Chat under 4 systemone workers: 1.2 chunks/s, TTFT 105 / 3287 ms.
- Systemone: 0.4 req/s at 1, 4 and 16 workers. **One systemone client already saturates the GPU.**

A step-time model built from these numbers is used for the estimates below. They are my estimates, not measurements.
- A decode-only step takes ~37 ms (27 tok/s). The roofline gives 55 GB of weights ÷ 1.79 TB/s ≈ 31 ms. The RTX PRO 6000 has 1792 GB/s and "4000 AI TOPS" (FP4 sparse), roughly 500 dense BF16 TFLOPS: https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/rtx-pro-6000-blackwell-workstation-edition/workstation-blackwell-rtx-pro-6000-workstation-edition-nvidia-us-3519208-web.pdf
- The effective prefill rate is R ≈ 5.8k computed tok/s, about 310 TFLOPS.
- A mixed step with B prefill tokens takes about T(B) ≈ max(37 ms, B/R), plus a few ms. The chat stream gets **at most 1 token per step**, so chat tok/s ≈ 1/T(B).

| budget B (prefill tokens/step) | est. step | est. chat tok/s under full systemone load |
|---|---|---|
| 8192 (today) | ~1.4 s (not every step is full) | 0.7–1.2 (measured 1.2) |
| 2048 | ~0.35 s | ~3 |
| 1024 | ~0.18 s | ~5.5 |
| 784 (= Mamba block) | ~0.14 s | ~7 |
| 512 | ~0.09–0.10 s | ~10 |
| 256 | ~0.045–0.055 s | ~18–20 |

Below about 280 tokens a step is memory-bound (ridge ≈ 500 TFLOPS ÷ 1.79 TB/s). Prefill tokens there are close to free for decode. This is the Sarathi-Serve argument (§3). Systemone throughput at small B should fall only modestly: roughly 5–15% at 512 and 10–30% at 256, from per-step overhead, attention re-reads of the prefix per chunk, and tile quantization. This needs measuring.

## 1. vLLM v0.30.0 priority scheduling: what it actually does

### Configuration and API
- Flag: `--scheduling-policy {fcfs,priority}` (`vllm/engine/arg_utils.py:L1615`, `vllm/config/scheduler.py:L22,L141-L147`).
- The docstring says: "requests are handled based on given priority (**lower value means earlier handling**) and time of arrival deciding any ties."
- Per-request field: `priority: int = 0` on both `/v1/chat/completions` (`vllm/entrypoints/openai/chat_completion/protocol.py:L381-L390`) and `/v1/completions` (`vllm/entrypoints/openai/completion/protocol.py:L134-L143`).
- The field description reads: "lower means earlier handling; default: 0. Any priority other than 0 will raise an error if the served model does not use priority scheduling."
- Consequence: the gateway can leave chat at 0 and send `"priority": 1` on systemone. This only works when vLLM runs with `--scheduling-policy priority`, otherwise vLLM returns errors, so the gateway setting must be gated on the profile.
- Ordering is `Request.__lt__`: priority, then arrival_time, then request_id (`vllm/v1/request.py:L350-L362`).
- The queue is a heap, `PriorityRequestQueue` (`vllm/v1/core/sched/request_queue.py:L131-L199`). "Prepend" means re-insert in priority order (L160-L173).

### Scheduler mechanics (`vllm/v1/core/sched/scheduler.py`, `schedule()` at L561)
1. `token_budget = self.max_num_scheduled_tokens` (L581). This equals `max_num_batched_tokens` unless set separately.
2. **RUNNING requests go first, in `self.running` list order** (L611-L807).
   - That list is append-only, in admission order (L1241). It is never sorted by priority. The only mutations are append, remove and victim deletion: see the grep in notes.
   - Each running request, whether a partial prefill chunk or a decode, takes `min(remaining, token_budget)` (L661-L665).
   - The loop stops when `token_budget` reaches 0 (L612).
   - So a systemone prefill admitted before a chat request is scheduled before that chat's decode and can take the whole budget.
3. Priority affects the running phase only when **KV blocks cannot be allocated**. Then the victim is `max(self.running, key=(priority, arrival_time))`, i.e. the lowest-priority request (L745-L785). FCFS instead preempts `running[-1]`.
4. **WAITING requests are admitted only if no preemption happened in this step and budget is left** (L855-L858).
   - With priority, the waiting-queue head is the lowest priority value (L2317-L2327).
   - A new chat request jumps ahead of queued systemone prompts, but it only gets the budget left over after the running prefills.
5. **Nothing in v0.30.0 preempts a running low-priority request to make room for a waiting high-priority one, except KV exhaustion.**
   - Issue #40004 (open) and PRs #45561 and #54530 (open) add preemption at `max_num_seqs`. None is merged.
   - Our running count is ~15, far below 256, so this would not matter to us anyway.
   - A running low-priority prefill is never interrupted mid-prompt. It keeps its chunk each step until done.

### Interactions
- **Chunked prefill and per-step budget.** Priority does not change the budget. Every step is still filled with up to `max_num_batched_tokens` of prefill whenever systemone work exists. A chat decode's inter-token latency equals the step time, so **priority fixes waiting-queue order, which is TTFT, but not decode starvation.**
- **Decode slots are not guaranteed.** Docs say V1 "batches all pending decode requests before scheduling any prefill" (`docs/configuration/optimization.md:L53`). The code actually gives running requests the budget in admission order, and in-flight prefill chunks count as running.
  - In steady state, chat's decode moves to the front once the systemone requests admitted before it finish. Those have max_tokens=1 and leave right after prefill. From then on chat gets 1 token per step.
  - With a small budget there is a one-time stall of a few steps after chat admission. This is a reason to consider a custom scheduler that sorts `running` by priority (§3c).
- **Prefix caching.** The waiting heap does not consider cache hits. Open feature #53277 (cache-aware QoS) and PR #54625 (cache-aware admission) address that. Priority preemption frees blocks, and priority-aware KV eviction is only an open PR (#47837).
- **Hybrid Mamba/GDN models.** The Mamba align split `_mamba_block_aligned_split` (L413-L526) runs identically under both policies. Two issues matter:
  - **#52897** (open). The title blamed `--scheduling-policy priority` for zero align-mode prefix hits on a hybrid GDN model. The thread concluded the policy was "fully exonerated": the cause is **budget-pressure fragmentation of chunk ends** under concurrent load, plus an EAGLE one-block back-off (not relevant to us, no spec decode). https://github.com/vllm-project/vllm/issues/52897
  - In v0.30.0 the split has explicit `next_block_boundary` stops, so a chunk starting mid-block stops at the boundary (L481, L507-L525). Small budgets should still materialise 784-token boundary states. **Verify the prefix-hit rate in the experiments.**
  - **#57580** (open, 2026-09-18). With align mode plus priority, a request **withdrawn by same-step priority preemption** can leave an uncomputed Mamba checkpoint visible to a later prefix hit. That is a correctness risk, but it only triggers on KV-pressure preemption. Our KV usage is 9–12%. Guard: alert if `vllm:num_preemptions_total` > 0. https://github.com/vllm-project/vllm/issues/57580
- **Other priority bugs**
  - #49097 (a running request silently skipped for a step): fixed by #49206, merged 2026-08-06, so included in v0.30.0.
  - Earlier crash bugs are fixed: #23347 / #23713 (preemption crash) and #29747 / #29764 (n>1 crash).
  - Historical reports that "priority doesn't improve tokens/s" (#11361, #24365, V0-era) show the same symptom we have. Priority reorders admission but does not speed decode under saturation.
- **Metrics.** Per-priority metrics are only proposed (#58077 issue, #58078 PR, open).

**Verdict on Q1:** turning on priority and marking systemone low
- **Should** cut long-prompt chat TTFT from ~3.3 s to about 1–3 steps. Chat stops waiting behind ~15 queued sibling prompts (~13k computed tokens ≈ 2.3 s).
- **Will not** fix the 1.2 tok/s decode, because each step is still ~8k prefill tokens.
- Only a smaller per-step prefill budget, or less systemone work admitted, fixes decode.
- ConServe measured the same thing on vLLM. A priority scheduler for co-served online and offline work still raised online P99 TTFT 59.7× and P99 TPOT 3.16×, "because offline requests are batched with online requests and cannot be preempted selectively" (arXiv 2410.01228 §2.3, `web/conserve-arxiv.md` L138-L141).

## 2. Prefill/decode mixing knobs in v0.30.0

| knob | v0.30.0 status | bounds prefill tokens sharing a step with decode? |
|---|---|---|
| `--max-num-batched-tokens` | Supported. Default here is 8192 (`arg_utils.py:L2740-L2749`). Also sets compile ranges and profiling. | **Yes, this is the main knob.** Per step, total prefill ≤ B − (#decodes). Docs: "Smaller values (e.g., 2048) achieve better ITL" (`docs/configuration/optimization.md:L64`). |
| `--max-num-scheduled-tokens` | Supported (`config/scheduler.py:L56-L61`, `arg_utils.py` group). Normally equals B; meant for spec decode. | **Yes.** It is the `token_budget` used in `schedule()` (L581). It can be set below B while keeping compile/cudagraph ranges. Also the attribute a custom scheduler would change per step. |
| `--long-prefill-token-threshold` | Supported. Default 0 = off (`config/scheduler.py:L70-L72`). | **No, not for the total.** It caps each request's chunk (L661-L662, L1066-L1068). 16 systemone prompts × 512 still fill an 8192 budget. It helps one long chat prompt share with others; it does not bound prefill vs decode. |
| `--max-num-partial-prefills`, `--max-long-partial-prefills` | **Removed.** PR #49244 "Remove old now unsupported" was merged 2026-07-21. Passing the flags gives `unrecognized arguments` (#57413). Revival PRs #49075, #41399 and `max_concurrent_prefills` #55256 (closed unmerged) / #57427 are not in v0.30.0. | n/a |
| `--prefill-schedule-interval N` | Exists (`config/scheduler.py:L185-L188`) but **only active for data-parallel engines**. Base `EngineCore._should_throttle_prefills()` returns False (`v1/engine/core.py:L584-L587`); the DP core overrides it (L2171-L2178). PR #54627 (open) would apply it at DP=1. | Would be a duty-cycle knob ("prefill only every Nth step when decodes are running"), but it is a **no-op for us** in v0.30.0. |
| `--max-num-queued-tokens`, `--max-num-queued-reqs` | New. Enforced in the API server, which rejects with 503 (`config/scheduler.py:L74-L114`). | No. This is class-blind admission control ("target_TTFT × prefill_throughput"). It would reject chat as readily as systemone, so it is not suitable unless systemone moves to a separate front door. |
| `--watermark` | New KV headroom (`L178-L183`). | No, it concerns KV only. |
| `--max-num-seqs` | Supported. | Not a token bound, and it hurts chat concurrency. |
| `--performance-mode interactivity` | New (`config/vllm.py:L446-L451`). Finer CUDA graphs ≤32. | No. It does not address prefill interference. |
| `--async-scheduling` | On by default. | n/a. A custom scheduler must subclass `AsyncScheduler` (`config/scheduler.py:L212-L233` warns otherwise). |
| `--scheduler-cls` | Supported. The interface is **not public** ("compatibility may not be maintained", `config/scheduler.py:L224-L230`). | Enables option 3c. |

Quantitative references:
- Sarathi-Serve (arXiv 2403.02310, `web/sarathi-arxiv.md`):
  - Token budgets of **512 for strict TBT SLOs and 2048 for relaxed** (L472).
  - "3.5× higher capacity compared to vLLM under strict SLO (100ms, Mistral-7B) using a small token budget of 512" (L484).
  - Linear-layer time is "largely stagnant in the 128–512 tokens range" (Fig. 6 caption, L256).
  - Tile quantization: "chunk size of 257 can increase prefill time by 32% compared to 256" (L380). Use multiples of 64 or 128.
  - Naive hybrid batching increases TBT up to 28.3× vs decode-only (L368).
- vLLM docs (`docs/features/disagg_prefill.md:L12-L16`): "Chunked prefill with a proper chunk size also can achieve the same goal [controlling tail ITL], but in practice it's hard to figure out the correct chunk size", and "Disaggregated prefill DOES NOT improve throughput."
- Hybrid caveat: B < 784 makes most chunks sub-block. The v0.30.0 split re-aligns at the next boundary, so states still land on 784 multiples. B = 768 is 64-aligned and just under a block; B = 784 exactly matches the block. Test both 512 and 768/784.
- Gemma-4 caveat: it is multimodal prefix-LM and `LANGUAGE_MODEL_ONLY=0`. vLLM only raises B to fit one image when B was left at the default (`arg_utils.py:L2943-L2969`). An explicit small B could stop image requests from fitting. Keep B ≥ the largest per-image token count for that profile, or set LANGUAGE_MODEL_ONLY=1.

## 3. Queuing, admission control, and adaptive budgets

### (a) Gateway-side governor: pure queuing, no vLLM change
The gateway already proxies chat (`gateway/chat.py`, `StreamingResponse` plus `BackgroundTask` close) and owns systemone (`gateway/readout.py._call`), so it knows when chat streams are live.

Policy sketch:
- `chat_active` counter: increment at stream start, decrement in the BackgroundTask.
- While `chat_active > 0`, systemone uses **waves**: split `prompts[1:]` (currently 15 per call) into chunks of k (e.g. 2–4).
- Throttle with a token bucket on estimated computed prompt tokens/s, or a semaphore on in-flight systemone calls (1 while chat is active, unlimited otherwise).
- Optionally pause entirely when p95 chat TBT (measured by the gateway on SSE chunk gaps) exceeds the SLO. That is the adaptive, SLO-driven variant (HyGen/ConServe-style control loop).
- Also add `"priority": 1` to the systemone payload when the profile enables priority.

Pros:
- Engine-agnostic, adaptive (full systemone speed when chat is idle), cheap, testable offline.
- Caps the *fraction of steps* that carry prefill.

Cons:
- Cannot shape a single step. With B=8192, each admitted prompt (~900–2,300 computed tokens) is still a 0.15–0.4 s stall for chat. Pair it with a smaller B.
- Requests already in vLLM when chat starts keep running.
- Systemone latency rises while chat streams. A 512-token thinking reply at ~20 tok/s lasts ~25 s.
- Clients hitting vLLM :8000 directly bypass it.
- Wave splitting keeps prefix reuse (same shared prefix) but adds round-trips.

Prior art:
- ConServe (arXiv 2410.01228): SLO-aware budget when online requests are present, "offline batching mode" with maximal batches when none are; preempts offline work. 2.35× throughput vs separate serving, 84× lower tail latency than prior co-serving.
- HyGen (arXiv 2501.14808, `web/hygen-arxiv.md` L144): latency predictor, and offline requests fill only the remaining latency budget. 3.9–5.8× throughput gains while meeting SLOs.
- Niyama (arXiv 2503.22562): QoS classes plus **dynamic chunking** plus relegation. +32% capacity vs siloed deployments.
- Gateway API Inference Extension "serving priority" / criticality (Critical vs Sheddable): https://gateway-api-inference-extension.sigs.k8s.io/
- vLLM production-stack priority routing is only a proposal doc (production-stack PR #996, merged 2026-08-18 as `proposals/priority-routing.md`). It is multi-instance routing plus forwarding `priority` to vLLM, so it is of no use on one GPU.

### (b) Static budget (Sarathi-style)
`--max-num-batched-tokens` 512–784, optionally plus priority. It costs nothing to try. Chat still starves in proportion to 1/T(B), and systemone pays per-step overhead even when chat is idle.

### (c) Custom scheduler class: dynamic budget plus latency-class-first ordering
> **Dropped by the owner (2026-09-28).** We will not maintain a monkeypatched `--scheduler-cls` entry point against vLLM's private scheduler interface. Kept below for reference only.

This is the in-engine "clever" option (ConServe / Niyama dynamic chunking in ~40 lines). It is an untested sketch, mounted like the entrypoint:
```python
# jev_sched.py  ->  --scheduler-cls jev_sched.ChatFirstScheduler
from vllm.v1.core.sched.async_scheduler import AsyncScheduler

class ChatFirstScheduler(AsyncScheduler):
    CHAT_BUDGET = 512                        # tune: 256..784
    def schedule(self, throttle_prefills: bool = False):
        full = (self.scheduler_config.max_num_scheduled_tokens
                or self.scheduler_config.max_num_batched_tokens)
        # systemone = max_tokens == 1 (or priority > 0 when using the priority policy)
        chat_live = any(r.max_tokens > 1 for r in self.running)
        if chat_live:
            self.running.sort(key=lambda r: r.max_tokens == 1)   # stable: chat first
            self.max_num_scheduled_tokens = self.CHAT_BUDGET
        try:
            return super().schedule(throttle_prefills)
        finally:
            self.max_num_scheduled_tokens = full
```
- `token_budget` is read from `self.max_num_scheduled_tokens` each step (L581). The final assert compares against the same attribute (L1301). The Mamba split reads it too (L473).
- The `running` sort puts chat decodes ahead of earlier-admitted systemone chunks, which removes the one-time stall described in §1.
- Risks:
  - Private interface; re-check on every vLLM bump.
  - Reordering `running` is not a documented invariant. Test with async scheduling and prefix caching; watch for the #57580-type interactions if preemption ever occurs.
  - Gemma multimodal floor, as in §2.

### (d) SLO-aware and research schedulers, reference only
- Andes (arXiv 2404.16283): QoE-aware token-level preemption.
- FastServe (arXiv 2305.05920): skip-join MLFQ, preemptive.
- Llumnix (OSDI'24): migration-based priority, "accelerates high-priority requests by up to 1.5×" and needs multiple instances.
- Open vLLM PRs, none merged in v0.30.0:
  - #53571 SLO policy: reorders waiting only, with a waiting-token reserve. Short-request TTFT −42…−55%.
  - #58420 SRPF with aging.
  - #54627 prefill interval at DP=1.
  - #55256 / #57427 `max_concurrent_prefills`.

## 4. Partitions

### (a) MIG on RTX PRO 6000 Blackwell
- **Supported profiles** (https://docs.nvidia.com/datacenter/tesla/mig-user-guide/latest/supported-mig-profiles.html, `web/mig-rtxpro6000.json`): 4× `1g.24gb`, 2× `2g.48gb`, or 1× `4g.96gb`. Each slice gets a 1/4 or 1/2 share of memory, SMs and L2.
- **Deployment:** MIG supports "Bare-metal ... GPU pass-through virtualization to Linux guests ... vGPU" (`supported-configurations.html`). WSL2 is not listed.
- **On this host:** `nvidia-smi` reports "RTX PRO 6000 Blackwell Workstation Edition, MIG mode [N/A]" under WSL2 (driver 610.62).
- **Workstation Edition:** users report needing VBIOS ≥ 98.02.55 plus the display-mode selector to disable display outputs before MIG works (NVIDIA forum thread 334906, page 2).
- **Memory fit:** Qwen3.6-27B bf16 is 27.78B params, 55.6 GB of safetensors (HF API; ~51 GiB loaded language-only). **It does not fit a 48 GB slice.** Qwen/Qwen3.6-27B-FP8 is 30.9 GB (24.7B FP8 + 3.1B BF16 params) and fits with ~12–14 GB for KV.
- **Verdict: not feasible here.** It would need a bare-metal Linux host, a VBIOS/display-mode change, and FP8 for both halves, which means systemone recalibration. Each half gets 1/2 SMs and bandwidth: chat decode with FP8 would be roughly idle speed, while systemone prefill capacity halves unless FP8 GEMMs recover it.

### (b) MPS, green contexts, two processes sharing weights
- **vLLM cannot share weights across processes.** Co-tenancy is documented only as independent instances with split `--gpu-memory-utilization` ("if you have two vLLM instances running on the same GPU, you can set ... 0.5 for each instance", `vllm/config/cache.py:L103-L110`). Each loads its own weights.
- Co-tenancy has a live startup bug: the memory-profiling assert aborts if a neighbour frees memory during profiling (#56830, open). No vLLM weight-sharing or green-context feature was found in issue search.
- **MPS:** "MPS is only supported on the Linux and QNX operating systems. The MPS server will fail to start ... other than Linux" (https://docs.nvidia.com/deploy/mps/latest/when-to-use-mps.html). A WSL2 user reports the MPS control daemon starts but "no nvidia-cuda-mps-server process ever starts" (NVIDIA forum 346928). So it is **infeasible under WSL2**.
- On bare metal, MPS would give `CUDA_MPS_ACTIVE_THREAD_PERCENTAGE` SM caps and client priority 0/1 as a "hint". It still needs two weight copies.
- **Reference designs that share weights:**
  - semi-PD (arXiv 2504.19867): SM-level split with unified storage, i.e. weights and KV shared.
  - SGLang **PD-Multiplexing** (`--enable-pdmux`, `--sm-group-num`) runs prefill and decode on intra-process **GreenContext** streams. LMSYS blog 2025-09-28 reports up to 3.06× goodput vs chunked prefill, and notes "GreenContext partitions SMs, it does not partition memory bandwidth".
  - Both are in-process, which is exactly what vLLM v0.30.0 lacks.

### (c) P/D disaggregation (NIXL/LMCache) on one GPU
- It needs separate prefill and decode vLLM instances, each with its own weights: 2 × ~55 GB bf16 is more than 96 GB. The docs call it experimental and say it "DOES NOT improve throughput" (`docs/features/disagg_prefill.md:L5-L16`).
- Systemone never decodes, so the "P" instance would carry all systemone work plus chat prefill. That is the same compute contention unless the GPU is also partitioned, which runs into (a) and (b).
- **Verdict: not feasible and not useful here.**

### (d) Two model copies, one smaller or quantized
Memory math on 97,887 MiB (102.6 GB):
- bf16 (~55 GB) + FP8 (~31 GB) = ~86 GB of weights.
- Two CUDA contexts and activations take ~3–6 GB.
- That leaves **~10–12 GB of KV total** across both. With the observed ~75 KB/token (31.84 GiB ↔ 454k tokens), that is ~140k tokens to split. Workable, but tight, and each GDN sequence also needs Mamba state.
- Two FP8 copies (~62 GB) leave ~35 GB of KV.
- Without MIG/MPS on WSL2, the two processes **time-share the GPU**: no SM partition, and kernels from different contexts do not overlap. Chat would get roughly its share of time slices rather than isolation.
- An FP8 systemone copy changes logprobs, requiring recalibration and new labels. An FP8 chat copy keeps systemone numerics but changes chat quality slightly.
- **Verdict: feasible on memory, unproven on isolation, highest operational cost. Try only if §3 options miss the SLO.**

## 5. SGLang and others, as ideas only

The SGLang server args (https://sgl-project.github.io/advanced_features/server_arguments.html) show useful features:
- `--enable-priority-scheduling`. By default, higher values are higher priority; `--schedule-low-priority-values-first` flips it.
- **`--priority-scheduling-preemption-threshold` (default 10):** an incoming request whose priority is higher by at least this margin **preempts running requests**. This is exactly what vLLM lacks (#40004).
- `--retraction-policy priority`.
- `--radix-eviction-policy priority`: priority-aware prefix-cache eviction. vLLM has this only as open PR #47837.
- `--enable-mixed-chunk` is off by default, so SGLang does not mix prefill and decode unless asked.
- `--enable-pdmux`: green-context SM partition.

Ideas worth porting through the gateway or a custom scheduler: preempt-on-arrival with a margin, priority-aware cache eviction, and SM partition. Per project policy, this is not a recommendation to switch engines (SGLang #34719).

## 6. A lever outside scheduling: make systemone cheaper

- Hybrid prefix caching is block-granular at **784 tokens** here. Chunk ends are also the only places Mamba state is saved (#52897 thread; `_mamba_block_aligned_split`).
- A ~2,048-token shared state caches only up to 1,568. Each sibling prompt recomputes ~480 state tokens plus its question: **~14.4k computed tokens per 16-question request, observed**.
- If the whole shared state hit cache, the cost would be ~6k per request, about **2.4× less GPU time per systemone request**. Interference would halve at the source, or systemone throughput would double.
- Candidate approaches (separate ticket; each changes model input or depends on unverified vLLM behaviour):
  - Lay out prompts so the shared part ends on a multiple of 784 tokens, then re-check calibration.
  - Test a smaller `--mamba-block-size`. Not verified that align mode accepts it independently of the attention block size.
- Measure with `vllm:prefix_cache_hits` / `queries` deltas around one systemone request.

### 6a. Options to test (owner request, 2026-09-28; implementation ticket DS-008)

The goal is that the whole shared state is cached once, so each sibling prompt pays only for its own question.

**Padding the shared prefix to a multiple of the block size.** The gateway inserts pad token ids (the model's single `\n` token, inserted as ids so nothing merges) until the shared prefix ends exactly on a multiple of the cache block (784 on Qwen3.6 bf16; read the per-profile value from the vLLM startup log). Only systemone prompts change; chat prompts are untouched. Three placements:

| Placement | Where the pad goes | Expected effect on answers |
|---|---|---|
| **end** | after the state, before the first per-question part (`\n\nQuestion:`) | pad sits right next to the question; most likely to shift answers |
| **front** | right after the chat-template head, before `Context:` | far from the question; smallest expected shift, but moves every position |
| **middle** | between the `Context:` label and the state text | similar to front; tests whether the label/state join matters |

Every padded variant breaks token parity with decider's layout, so its answers need their own fidelity check and, if kept, its own fitted temperature (phase 2).

**A smaller Mamba cache block (no prompt change).** `--mamba-block-size N` exists in v0.30.0 (multiple of 8; only with prefix caching). A finer block (e.g. 256, then 128) would cache more of the shared state without touching prompts. Unknowns to measure: whether align mode accepts it independently of the 784-token attention block, how much memory the extra cached Mamba states cost (fewer cache blocks lowers the usable `max_num_seqs`, currently 256 of 638), and whether smaller aligned chunks slow prefill.

**Fidelity: what we measure before adopting either.**
- **Decision fidelity** (padding and block-size rows): the same fixed request set (JevBench `--quick` 50 rows plus a seeded synthetic set) against the baseline. Report the max |Δp| per answer, the argmax flip rate, and the JevBench accuracy delta.
- **Chat fidelity** (block-size rows only; padding never touches chat): 20 fixed chat prompts at temperature 0, compared token by token with the baseline's output (match rate and first divergence position), plus chat TTFT and chunks/s alone. A block-size change should not change the maths, only where bf16 chunk boundaries fall, so we expect near-identical outputs; this measures it.
- **Cost side:** `vllm:prefix_cache_hits_total / queries_total`, computed tokens per systemone request (prompt tok/s ÷ req/s from the log), cold p50 for `2048×16×26`, and systemone req/s at 4 workers.

## 7. Experiment plan (bench.py)

Note: `scripts/bench.py` on `phase-1-server` @771fd88 has **no `--chat` flag**. `chat_under_load` runs only at the end of the full suite, after `throughput()` at 1, 4 and 16 workers. If `--chat` is not added yet, add it to run `chat_under_load` plus `throughput(workers=4)`. Also consider:
- ≥5 chat repeats per prompt,
- recording per-chunk timestamps to report TBT p50/p95 (averages hide stalls),
- counting systemone completions during the chat window.

Matrix. Restart vLLM per row, ~6 min startup. Keep everything else fixed.

| id | vLLM flags added | gateway | purpose |
|---|---|---|---|
| A0 | none (fcfs, B=8192) | as is | baseline (reproduce 1.2 tok/s, 3.3 s) |
| A1 | `--scheduling-policy priority` | systemone `priority: 1` | TTFT fix only? |
| A2 | A1 + `--max-num-batched-tokens 2048` | same | |
| A3 | A1 + `--max-num-batched-tokens 768` (also try 784) | same | Mamba block-sized |
| A4 | A1 + `--max-num-batched-tokens 512` | same | expected sweet spot |
| A5 | A1 + `--max-num-batched-tokens 256` (`max_num_seqs` must be ≤ B) | same | near-roofline |
| G1 | best of A3–A5 | chat-aware governor: waves of 4, ≤1 in-flight systemone call while chat active | queuing on top |
| P0 | A0 flags | as is | prefix baseline: hit rate and computed tokens per request |
| P1 | A0 flags | pad shared prefix to the block multiple at the **end** | alignment, pad next to question |
| P2 | A0 flags | pad at the **front** | alignment, pad far from question |
| P3 | A0 flags | pad in the **middle** (between `Context:` and state) | alignment, label/state join |
| M1 | A0 + `--mamba-block-size 256` | as is | finer cache blocks, no prompt change |
| M2 | A0 + `--mamba-block-size 128` | as is | finer still (memory / prefill-speed cost) |
| X1 | best A/G row + best P or M row | combined | final candidate |

Collect per row:
- From bench: chat TTFT and chunks/s, alone and under 4 systemone workers (short and long prompt).
- Systemone req/s at 4 workers.
- Systemone cold p50 for `2048×16×26` alone, the idle penalty of a small B.
- JevBench `--quick` accuracy, to check that chunk-boundary numerics do not move labels.
- For P and M rows: the decision-fidelity and chat-fidelity checks in §6a.
- From `/metrics` before and after: `vllm:prefix_cache_hits_total` / `queries_total`, `vllm:num_preemptions_total` (must stay 0, see #57580), the prompt-throughput log line, and KV usage.

Suggested acceptance:
- Under load: chat TTFT p50 ≤ 0.5 s and chat ≥ 10 chunks/s (≥ 40% of idle).
- Systemone ≥ 0.32 req/s under load (≥ 80% of baseline), and cold single-request latency ≤ +15%.
- Prefix hit rate within 5 points of baseline, and zero preemptions.

Expected (model, §0):
- A1: TTFT fixed, decode ~unchanged.
- A4: ~10 tok/s.
- A5: ~15–20 tok/s.
- P1–P3 / M1–M2: up to ~2.4× less systemone GPU work per request (§6), which lowers interference at the source.
- G1 moves chat toward idle speed in proportion to the systemone duty cycle.

Acceptance for the P and M rows (owner may adjust):
- Systemone computed tokens per request down ≥ 40% or throughput up ≥ 1.5×.
- Decision fidelity: JevBench accuracy within ±1 point, argmax flips ≤ 2%, max |Δp| reported.
- Chat fidelity (M rows): ≥ 99% greedy token match with baseline, no TTFT or chunks/s regression when idle.
- `max_num_seqs` 256 still fits the Mamba cache blocks (M rows).
