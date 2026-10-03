# Numerics and determinism

Why the same systemone request can return slightly different probabilities, and now and
then a different answer.

## Short answer

- **Identical requests can give different numbers, and that is expected.** A GPU adds
  numbers in an order that depends on how much other work shares the batch. Floating-point
  addition gives slightly different results in different orders. vLLM does not promise
  reproducible results by default.
- **bf16 turns tiny differences into visible steps.** A bf16 number carries only 8
  significant bits, so a logit near 20 can only move in steps of 0.125. Near p = 0.5, one
  step moves a two-way probability by about 0.03 (at temperature 1).
- **What we see:**
  - under chat load, probabilities drift by 0.028–0.032, and the stability test allows 0.05;
  - repeat JevBench runs of qwen3.6 scored 84.2, 84.4 and 84.3;
  - Jev itself answered 17 of 1,682 rows differently across identical calls.
- **Treat ±0.2 points on JevBench as noise.** Compare runs row by row. Do not read meaning
  into smaller differences.
- **A deterministic mode exists, but it doesn't fit us yet.** vLLM's
  `VLLM_BATCH_INVARIANT=1` is in beta, and published tests show it costs tens of percent
  of speed. It also reportedly doesn't cover the Gated DeltaNet layers of the hybrid Qwen
  models. So we design for the noise instead of removing it.

## 1. The root cause: the order of addition

A floating-point number keeps a fixed number of significant digits. When you add a large
number and a small one, the small one's last digits are lost. With 3 digits,
1230 + 23.4 = 1250, not 1253.4. So `(a + b) + c` can differ from `a + (b + c)`.

A matrix multiply or an attention step sums thousands of products. The kernel's plan decides
the order: how it splits the work into tiles and whether it splits one sum across cores.
Thinking Machines showed that these kernels are **run-to-run deterministic**: the same
inputs in the same batch give the same bits every time. What changes the bits is the
**batch**. A kernel picks a different plan for a different number of tokens, so one
request's result depends on what else is running. They call the missing property
**batch invariance**.

Illustrative numbers:

```
same prompt ─┬─ batch of 16 rows       ─► kernel plan A ─► logit 20.061 ─► bf16 20.000
             └─ same + 4 chat streams  ─► kernel plan B ─► logit 20.064 ─► bf16 20.125
                                                        (a 0.003 difference became one 0.125 step)
```

Where the plan changes for our requests:

| Cause | What changes | Where it hits us |
|---|---|---|
| **Batch size** | Matmul and attention kernels pick different tiles or split a sum differently for a different token count | Any chat stream or other systemone request running at the same time |
| **Chunked prefill** | Prompts are fed to the GPU in steps of up to 8,192 tokens (the default here, [ds007-scheduling.md](../appendix/ds007-scheduling.md)). Where a prompt is cut depends on what else is scheduled | Requests with many long rows; DS-007 tuning of `--max-num-batched-tokens` moves the cuts |
| **Prefix cache hit vs miss** | A miss computes the whole prompt; a hit computes only the uncached tail, so the same token goes through differently shaped matmuls | Row 1 is sent alone to warm the cache and later rows hit it ([readout.py](../../gateway/readout.py)); the hybrid Qwen models cache in 784-token blocks ([prompt-sharing.md](prompt-sharing.md)) |
| **Recurrent layers** | 48 of Qwen3.6's 64 layers carry a running state between chunks. Resuming from a stored state rounds differently from one continuous pass (shown for Mamba2 in vLLM RFC #55524) | qwen3.6-27b and qwen3.8-27b, not gemma-4-31b |
| **More than 128 labels** | vLLM reads at most 128 label ids per call, so the gateway sends the same rows again for the rest ([readout.py](../../gateway/readout.py)). Each call is a separate forward pass | Choices with more than 128 options compare letters from different passes |

Each difference starts tiny, often one unit in the last place of one number, but it grows
through the layers. In vLLM PR #34046's example, one element that differed by one unit at
layer 0 became a logit difference of up to 8.0 at the output, enough to flip the top token.

## 2. bf16: why the noise comes in steps

bf16 is a 16-bit float with fp32's range but only 8 significant bits (7 stored plus 1
implicit). The gap between neighbouring values grows with size:

| Logit size | Smallest step |
|---|---|
| 8–16 | 0.0625 |
| 16–32 | 0.125 |
| 32–64 | 0.25 |

vLLM's output layer produces bf16 logits, and its sampler converts them to fp32 only
afterwards (`logits.to(torch.float32)` in `vllm/v1/sample/sampler.py`). So the logprobs
the gateway reads are bf16 values in disguise. The gateway then applies a softmax over
the letters only, divided by a temperature `T` ([calibration.py](../../gateway/calibration.py)).
With two options, p = σ(Δ / T), where Δ is the gap between the two letters' logits. Near
p = 0.5 the slope is 1 / (4T), so for letter logits in the 16–32 range:

| Setup | Δ moves one step (0.125) | Δ moves two steps (0.25) |
|---|---|---|
| T = 1 (uncalibrated: qwen3.8, gemma) | p moves ~0.031 | ~0.062 |
| T = 1.943 (decider's value, qwen3.6 before 2026-10-02) | ~0.016 | ~0.032 |
| T = 1.386 (qwen3.6 `decider_chat` noul, our [fit](../../data/qwen3.6-27b/decider_chat/calibration.json)) | ~0.023 | ~0.045 |

Two steps is the usual worst case, because each of the two logits can round one step in
opposite directions. The slope is steepest at p = 0.5 and falls towards 0 and 1 (at
p = 0.9 it is 0.09 / T). **The noise is largest exactly on near-ties.** That is why answers
flip only on rows where the model was nearly undecided.

## 3. What we measured

| Evidence | Result | Source |
|---|---|---|
| Stability test: 1 idle read vs 5 reads under 4 chat streams | Max drift 0.028–0.032. The test allows 0.05 and requires the same top answer when the idle top-two gap > 0.10 | [test_stability.py](../../tests/live/test_stability.py) |
| qwen3.6 JevBench, 2026-09-28 vs 2026-09-29 | 84.2 → 84.4: 3 of 1,682 rows changed correctness, all wrong → right. The gateway's prompt code was the same | [09-28](../results/qwen3.6-27b/2026-09-28T000000Z/summary.md), [09-29](../results/qwen3.6-27b/2026-09-29T130343Z-jevbench/summary.md) |
| qwen3.6 JevBench, third rerun | 84.3 | not committed |
| qwen3.6 quick run (first 50 rows) vs the 09-29 full run | 0 of 50 predictions differ | [quick raw.jsonl](../results/archive/qwen3.6-27b/2026-09-29T210957Z-quick/raw.jsonl) |
| Jev, two full passes | 18 rows differ: 17 near-ties that change when re-asked, plus 1 HTTP error | [jevbench-vs-jev.md](../results/archive/jevbench-vs-jev.md#why-we-trust-the-comparison) |
| Other projects | Prefix caching flipped 59 of 13,500 near-tie answers (mini-jev); bf16 fast paths changed 5–6 of 777 (SemIf) | [ordering-and-layout.md](../appendix/ordering-and-layout.md), [inference-other-projects.md](../appendix/inference-other-projects.md) |

Notes:

- **Between the two qwen3.6 runs**, the only gateway changes were a richer `/health` and a
  clamp in the unused `cyclic` order setting (`git diff 771fd88 4de0f45 -- gateway prompts`).
  The 09-28 run came at the end of a full bench, after heavy synthetic traffic. The 09-29
  run was JevBench only. So cache contents and batch makeup differed.
- **Jev is not deterministic either.** Independent testers saw the same thing
  ([jev-notes.md](../appendix/jev-notes.md)).
- **Follow-up:** a controlled repeat-request measurement hasn't been run yet. The plan:
  - send the SDK quickstart (`QUICKSTART`/`STATE` in [helpers.py](../../tests/helpers.py))
    plus one wider choice 10 times in a row;
  - send it 10 more times while up to 4 identical requests run in parallel;
  - report the max |Δp| and any flipped answers;
  - log the raw letter logprobs to confirm the gaps move in bf16 steps.

**Gemma is the least stable of our models.** On a few near-saturated rows its answer can swing
between two identical asks on an idle server (invoice 1168: `yes` 0.50, then `no` 0.73), and
flips of rows with a large top-two gap happen between runs without any setting change
([DS-015](../results/archive/experiments/ds-015/README.md)). A large-gap flip on Gemma is therefore
weaker evidence of a bug than on Qwen.

## 4. Deterministic modes, and what they cost

| Option | What it removes | Published cost | Fits us? |
|---|---|---|---|
| vLLM `VLLM_BATCH_INVARIANT=1` (env var, v0.30.0 docs) | Dependence on batch size and order | Not stated by vLLM ("may impact performance") | Not yet; see below |
| SGLang `--enable-deterministic-inference` (≥ 0.5.3) | Batch, chunked-prefill cuts; radix cache on the FA3 backend | 25–45% slower, 34.35% on average (Qwen3-8B, H200) | No: SGLang is ruled out for mixed chat and decision traffic (issue #34719) |
| fp32 for the letter logits ([4-inference-technique.md](../4-inference-technique.md)) | The final bf16 rounding step | Small (an estimate: only K letters per row) | Needs a vLLM change. It smooths the steps but doesn't remove the upstream differences |
| Design for the noise (§5) | Nothing; we measure around it | None at serving time | Yes, the current choice |

About vLLM's mode:

- **What it covers:**
  - it needs NVIDIA compute capability 8.0 or higher, which our sm_120 meets;
  - in server mode it is vLLM's only route to reproducible results;
  - even then, results only repeat on the same hardware and the same vLLM version.
- **Tested models:** the list includes dense Qwen3 and Qwen3-Next, but not Qwen3.5/3.6/3.8
  or Gemma 4. The tracking issue (#27433) still lists prefix-caching support as a "nice to
  have". Our throughput depends on prefix caching ([prompt-sharing.md](prompt-sharing.md)).
- **Hybrid Qwen:**
  - LMCache's recipe for Qwen3.5/3.6/3.8 says "GDN backends do not support vLLM's
    batch-invariant mode";
  - vLLM RFC #55524 says the Mamba2 prefill and decode kernels "are not bit-identical",
    which "blocks batch-invariant / deterministic serving for hybrid models".
- **Cost:** Thinking Machines timed Qwen3-8B serving 1,000 sequences:
  - 26 s by default;
  - 55 s in their first deterministic version;
  - 42 s with a better attention kernel (+62%).

  vLLM's tracking issue lists speed-up PRs since then, for example #53649 ("33.6% E2E
  latency reduction" on Blackwell). Our own cost is unmeasured.
- **A cheaper partial fix won't land.** `--deterministic-prefix-caching` (PR #34046) made
  cache misses split at the same point as cache hits, but it was closed unmerged.

## 5. What it means for us

**Tests:**

- **Never assert exact probabilities from a live server.**
  - `MAX_DRIFT = 0.05` covered two bf16 steps at T = 1.943 (0.032) with margin; at the
    fitted noul T = 1.386 two steps are ~0.045, little margin.
  - `DECISIVE_GAP = 2 × MAX_DRIFT`, because each of the top two can move by 0.05.
  - Unit and parity tests check tokens on the CPU, so exact equality is right there.
- **Revisit the bound when T changes.** Near p = 0.5 drift scales with 1 / T (an estimate).
  One step at T = 1 is already 0.031, and two steps (0.062) would exceed 0.05; so would
  `question_first`'s noul T = 1.145 (~0.055).

**Benchmarks and comparing runs:**

- **The noise floor is about ±0.2 points on 1,682 rows.** An estimate that agrees: if ~17
  near-tie rows each land either way at random, run-to-run spread is √(17 × 0.25) ≈ 2 rows
  ≈ 0.12 points, or ±0.25 points at two standard deviations.
- **This is not sampling error.** At 84% on 1,682 rows, the standard error is
  √(0.84 × 0.16 / 1682) ≈ 0.9 points. That bounds how well JevBench predicts new data, not
  how much a rerun moves. Compare models on the same rows, pairing each row, rather than
  comparing two headline numbers.
- **Diff runs by row `id`** in `raw.jsonl` and count the flips. Flips on near-ties are
  noise. A flip on a row with a wide gap is a bug signal. From 2026-09-30 the bench records
  each row's probabilities in `raw.jsonl`, so the top-two gap is available for this check.
- **Scheduler changes move chunk cuts.** DS-007's `--max-num-batched-tokens` and DS-008's
  prefix padding should "not change the maths" but will flip some
  near-ties. Judge fidelity against this noise floor, not bitwise
  ([ds007-scheduling.md §6a](../appendix/ds007-scheduling.md)).

**Phase-2 calibration:**

- **What gets fitted:** the plan fits `T` per profile and question type by NLL on a
  calibration split ([design spec](../superpowers/specs/2026-09-28-systemone-server-design.md)),
  and possibly a noul bias (DS-002, [jevbench-vs-jev.md](../results/archive/jevbench-vs-jev.md)).
- **Each read is one noisy draw,** so averaging matters:
  - the noise is largest on near-ties, which is exactly where a bias shift changes answers;
  - a fit on one pass partly fits that pass's batch layout;
  - the eval split carries the same ±noise, so gains below the floor are not real.
- **Suggested method:**
  - read each calibration row 2–3 times, under realistic conditions (cache warm and cold,
    idle and loaded);
  - fit on the averaged or pooled logprobs;
  - report accuracy and ECE as a mean with the spread across repeats.
- **It's cheap:** one JevBench-sized pass takes about 1,682 × 89 ms ≈ 2.5 min (an estimate
  from the p50).
- **A fitted T belongs to one exact setup.** Turning on batch-invariant kernels would
  change the numerics, so treat it like a precision change and refit.

## Caveats

- **Drift numbers:** the 0.028–0.032 drift comes from when the bound was widened (commit
  `56b7af2`). The repo doesn't record the raw values or which profile was running.
- **The 84.3 rerun** isn't committed anywhere.
- **The 09-28 comparison** has no row ids. Rows are matched by position (the question types
  line up row for row), and only correctness changes show, not switches between two wrong
  answers.
- **Step sizes** assume letter logits of 16–32, the same assumption as the test's comment.
  Smaller logits give finer steps.
- **Sampler detail:** the bf16-then-fp32 conversion was read in vLLM's main branch, not
  the v0.30.0 source.
- **Borrowed evidence:** the hybrid-model claims come from LMCache's docs and a Mamba2 RFC,
  not from our own tests. All cost figures come from other GPUs and 8B dense models.

## Next steps

1. Run the controlled repeat-request measurement in §3 once the stack is back.
2. Add a small script that diffs two runs' `raw.jsonl` by row `id` and sorts flips by the
   top-two gap (the probabilities are recorded from 2026-09-30).
3. Phase 2: repeat-read calibration rows and report the spread across repeats.
4. Optional: time `VLLM_BATCH_INVARIANT=1` on gemma-4-31b, which has no recurrent layers,
   and check whether it actually holds.

## Sources

- Thinking Machines, "Defeating Nondeterminism in LLM Inference" (Sept 2025):
  https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
- vLLM batch invariance, v0.30.0: https://docs.vllm.ai/en/v0.30.0/features/batch_invariance/
- vLLM reproducibility: https://docs.vllm.ai/en/latest/usage/reproducibility/
- vLLM batch-invariance tracking issue #27433: https://github.com/vllm-project/vllm/issues/27433
- vLLM PR #34046, `--deterministic-prefix-caching` (closed): https://github.com/vllm-project/vllm/pull/34046
- vLLM RFC #55524, Mamba2 exact-replay decode: https://github.com/vllm-project/vllm/issues/55524
- vLLM sampler, main branch (fp32 conversion of logits): https://github.com/vllm-project/vllm/blob/main/vllm/v1/sample/sampler.py
- vLLM PR #53649, Blackwell batch-invariance autotune: https://github.com/vllm-project/vllm/pull/53649
- LMCache recipe for Qwen3.5/3.6/3.8 (caveats): https://docs.lmcache.ai/recipes/qwen3_5.html
- LMSYS, "Towards Deterministic Inference in SGLang" (Sept 2025):
  https://lmsys.org/blog/2025-09-22-sglang-deterministic/
- Raw scrapes: `.firecrawl/background/determinism/` (git-ignored).
