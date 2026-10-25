# Background

Detailed technical explanations for interested readers: how the pieces of jev-brain
actually work, and what our measurements show about them. Each doc stands on its own;
the order below goes from "how a request works" to "how good the answers are".

| Doc | Read it for |
|---|---|
| [Decision readout](decision-readout.md) | One request traced through the code: label tables, piecewise tokens, one-token readout, softmax, Jev answers (real token ids) |
| [Request lifecycle](request-lifecycle.md) | Client → gateway → vLLM sequence diagrams, auth, error codes, disconnect cancellation, timeouts |
| [Prompt layouts](prompt-layouts.md) | The three layouts, where the question should go for long documents, what each costs in prefix sharing, and the round 4 intro-blurb screen (DS-043) |
| [Read-twice](read-twice.md) | Block stacking: writing the shared block twice for one-question requests, the four arms, the gate, letter names, H1q (question and options read twice), calibration and latency of `blurb_header_reread` (DS-045) |
| [Option ordering](option-ordering.md) | Showing options in several orders and averaging back: position and letter bias, PriDe, cost, and the M3 and round 1-4 order results on text and images (DS-041, DS-043) |
| [Answer labels](answer-labels.md) | Which token the model answers with: letters vs lowercase, spaced, digits, symbols, unused, content and shuffled labels, their token checks and round 3 screen (DS-042) |
| [Images](images.md) | How `/v1/systemone` decides about images: placeholders and soft-token counts per model, the token-in readout, image prompt sharing, and the vision suite (DS-024) |
| [Vision experiments](vision-experiments.md) | The dev/holdout/latency splits of the vision suite, holdout rules, collect and offline arms, how to read the paired compare table, latency procedure (DS-034) |
| [Prompt sharing](prompt-sharing.md) | Why hybrid Qwen reuses the shared state only in 784-token blocks, and what that costs in throughput |
| [Model architectures](model-architectures.md) | Qwen's Gated DeltaNet hybrid vs Gemma's sliding window: memory per token, why blocks are 784 tokens, why Gemma is KV-bound |
| [KV cache](kv-cache.md) | What K and V are, vLLM's paged blocks, block pool and prefix hashing, how hybrid Qwen's state fits the pool (784/800-token blocks), fp8 KV, `max_model_len` vs capacity |
| [Prefill and decode](prefill-and-decode.md) | Why decision traffic starves chat on one GPU, what priority scheduling can and can't fix |
| [Speculative decoding and Mamba](speculative-decoding-and-mamba.md) | Draft/verify and MTP, recurrent state vs KV, and what MTP does to label scoring and prefix caching on hybrid Qwen (DS-004) |
| [Determinism](determinism.md) | Why identical requests can give different answers (bf16, batching), our noise floor, deterministic modes |
| [Yes/no bias](noul-bias.md) | Why Qwen leans "no" and Gemma "yes" on noul questions, where it happens, and what a bias term can and can't fix |
| [Calibration](calibration.md) | Temperature scaling, ECE and Brier, Jev's confidence formulas, why a yes/no bias needs more than a temperature |
| [Benchmarks](benchmarks.md) | Decision Index vs JevBench vs our bench: what each measures and why their numbers differ |
