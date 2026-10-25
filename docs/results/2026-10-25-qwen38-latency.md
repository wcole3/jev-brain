# Why qwen3.8 decisions got slower (2026-10-25)

After the move to vLLM 0.32 and the H1q default (`blurb_header_reread`), qwen3.8-27b-nvfp4 failed the latency gate
(latency-v1 at 600 W: 487 / 1,010 / 1,272 / 2,881 ms median / mean / p80 / p95). The 2026-10-20 runs were
88 / 180 / 226 ms. This note finds where the time went. Short answer: not WSL2 and mostly not vLLM 0.32; the
2026-10-20 runs were on hosts with much faster CPUs, the H1q layout and `min_n:4+reversed` read more tokens, and
hybrid-Qwen prefill in vLLM is CPU-bound.

## What the engine is doing

- **The GPU waits on the CPU.** During decision traffic the card runs at full clocks but 18-34% utilization and
  ~200 W of 600 W. py-spy on vLLM's EngineCore: ~93% busy in Python inside the forward pass, 36% in the GDN core
  op (`qwen_gdn_attention_core_fused_norm_packed`).
- **Why:** any step with a prefill above the CUDA-graph cap (512) runs eagerly, and the GDN core runs as an eager
  break in every mixed step (vLLM #62556; #61779 and #61952, both open, capture it).
- **Bare vLLM** (`/v1/completions`, `max_tokens=1`, qwen3.8-27b bf16, local): 16-token prompt 114 ms, cached
  1,600-token prompt 159 ms, fresh 2,400-token prefill ~470 ms.

## Not WSL2

A rented native-Linux box with the same CPU generation (Threadripper 3960X, Zen 2, PCIe 4, 500 W cap), qwen3.8-27b
bf16, vLLM 0.32, H1q default:

| | local (WSL2, Ryzen 7 3800X) | vast (native Linux, 3960X) |
|---|---|---|
| latency-v1 median / mean / p80 / p95 | 287.5 / 622.0 / 822.3 / 1,272.3 ms | 282.3 / 546.8 / 846.3 / 1,269.9 ms |
| CUDA kernel launch | 16 µs | 6.5 µs |
| 16-token prompt | 114 ms | 45 ms |
| fresh 2,400-token prefill | ~470 ms | ~520 ms |

WSL2 makes launches ~2.5× dearer, which shows on tiny requests and in the tail, not in the gate metrics.
Run: [archive/qwen3.8-27b/2026-10-25T174201Z-latency](archive/qwen3.8-27b/2026-10-25T174201Z-latency/summary.md).

## Mostly not vLLM 0.32

Same vast box, vLLM 0.30.0 (pip venv with the 0.30 rejection-sampler patch, not the pinned image) against 0.32:

| | 0.30.0 | 0.32.0 |
|---|---|---|
| latency-v1, H1q default | 282.1 / 511.0 / 823.6 / 1,217.7 ms | 282.3 / 546.8 / 846.3 / 1,269.9 ms |
| bare timings | same | same |
| 150-row sample, old `blurb_header` layout (median / p80 / p95) | 168 / 500 / 991 ms | 163 / 561 / 1,408 ms |
| engine steps per decision row | 2.0 | 3.3 |
| short chat decode, 1 / 4 streams | 68.5 / 67.4 tok/s | 62.1 / 62.1 tok/s |

0.32 costs ~5% in mean and p80, more in the tail, and ~9% in chat decode. Long chat (200k-token prompt, local)
is unchanged from the 0.30 runs: qwen3.8 TTFT 84.3 s and 14.6 tok/s, qwen3.6 85.1 s and 14.8 tok/s
([qwen3.8](archive/qwen3.8-27b/2026-10-25T173535Z-long-context/summary.md),
[qwen3.6](archive/qwen3.6-27b/2026-10-25T172350Z-long-context/summary.md)).
0.30 run: [archive/qwen3.8-27b/2026-10-25T180258Z-latency](archive/qwen3.8-27b/2026-10-25T180258Z-latency/summary.md).

Stock 0.32 without our `scheduler.py` patch took the same 3.3 steps per row and hit `CUDA error: an illegal memory
access` after ~200 decision rows (once). The patch stays.

## Where the latency comes from

- **Host CPU.** The 2026-10-20 runs used Threadripper PRO 7995WX / 9975WX and EPYC hosts; on a CPU-bound path that
  is most of the gap to this box.
- **The H1q layout.** On the vast box, 0.32: `blurb_header` 163 ms median vs H1q 261 ms (150-row sample).
- **The order setting.** `min_n:4+reversed` sends 3.4 vLLM requests and 2,382 freshly computed tokens per row;
  qwen3.6's `identity` sends 2.7 and 1,804. Per engine step the two models cost the same; this is the whole
  qwen3.6 vs qwen3.8 gap.

## nvfp4: the FP8 attention projections

RadixArk's NVFP4 checkpoint keeps every attention projection (GDN `in_proj_qkv`, `in_proj_z`, `out_proj`; full
attention `q/k/v/o_proj`, 208 layers) in FP8 W8A8; MLPs and `lm_head` are NVFP4. vLLM 0.32 runs the FP8 layers with
FlashInfer `bmm_fp8`, which enumerates cuBLASLt algorithms on the CPU for every new token count in eager prefill
(13% of EngineCore time). That is why nvfp4 prefill is ~2× bf16 (fresh 2,400 tokens: ~960 vs ~470 ms); it was
already so on 0.30.

`VLLM_DISABLED_KERNELS=FlashInferFP8ScaledMMLinearKernel` makes vLLM pick `CutlassFP8ScaledMMLinearKernel`
(150-row sample, median / mean / p80 / p95): 344 / 822 / 1,019 / 2,475 ms vs 379 / 1,034 / 1,269 / 3,422 ms;
fresh 2,400-token prefill ~640 ms. Not shipped: reads must be checked for flips first, and p80 is still at the gate.

## Knobs that did not help (qwen3.8-27b bf16, 150-row sample, median / mean / p80 / p95)

| change | result |
|---|---|
| none (reference) | 275 / 661 / 814 / 2,272 ms |
| no vision tower (`LANGUAGE_MODEL_ONLY=1`) | 291 / 695 / 826 / 2,267 ms |
| `--gdn-prefill-backend triton` (nvfp4) | 549 / 1,252 / 1,597 / 3,841 ms vs 379 / 1,034 / 1,269 / 3,422 |
| capture sizes up to 2,400 | 288 / 692 / 855 / 2,236 ms |
| `VLLM_WSL2_ENABLE_PIN_MEMORY=1` | 259 / 650 / 852 / 2,123 ms |
| no prefix caching | 263 / 2,440 / 1,199 / 5,880 ms |
| breakable CUDA graphs + Triton GDN | 297 / 700 / 890 / 2,373 ms |
| + #61779/#61952 backported, `max_num_seqs` 256 | 611 / 1,489 / 1,930 / 5,567 ms |
| same, `max_num_seqs` 64 | 375 / 851 / 1,133 / 2,586 ms |
| same, `max_num_seqs` 32 | 337 / 727 / 965 / 1,950 ms |

The GDN-capture PRs do remove the CPU bottleneck (GPU at 99%, ~500 W), but the captured core pads its grids to
`max_num_seqs` rows and the step to the next capture size, and breakable mode turns torch.compile off. For single
large-prefill decisions that costs more GPU time than it saves on the host.

The 150-row sample is every fifth latency-v1 timed row, sequential, through the gateway, with vLLM metric deltas
per row. Scripts and raw rows stay in `.firecrawl/qwen-slow/` (git-ignored).
