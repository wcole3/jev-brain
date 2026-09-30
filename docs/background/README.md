# Background

Detailed technical explanations for interested readers: how the pieces of jev-brain
actually work, and what our measurements show about them. Each doc stands on its own;
the order below goes from "how a request works" to "how good the answers are".

| Doc | Read it for |
|---|---|
| [Decision readout](decision-readout.md) | One request traced through the code: label tables, piecewise tokens, one-token readout, softmax, Jev answers (real token ids) |
| [Request lifecycle](request-lifecycle.md) | Client → gateway → vLLM sequence diagrams, auth, error codes, disconnect cancellation, timeouts |
| [Prompt layouts](prompt-layouts.md) | The three layouts, where the question should go for long documents, option-order bias, and what each costs in prefix sharing |
| [Prompt sharing](prompt-sharing.md) | Why hybrid Qwen reuses the shared state only in 784-token blocks, and what that costs in throughput |
| [Model architectures](model-architectures.md) | Qwen's Gated DeltaNet hybrid vs Gemma's sliding window: memory per token, why blocks are 784 tokens, why Gemma is KV-bound |
| [Prefill and decode](prefill-and-decode.md) | Why decision traffic starves chat on one GPU, what priority scheduling can and can't fix |
| [Determinism](determinism.md) | Why identical requests can give different answers (bf16, batching), our noise floor, deterministic modes |
| [Yes/no bias](noul-bias.md) | Why Qwen leans "no" and Gemma "yes" on noul questions, where it happens, and what a bias term can and can't fix |
| [Calibration](calibration.md) | Temperature scaling, ECE and Brier, Jev's confidence formulas, why a yes/no bias needs more than a temperature |
| [Benchmarks](benchmarks.md) | Decision Index vs JevBench vs our bench: what each measures and why their numbers differ |
