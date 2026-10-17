# Vision research for round 2 (2026-10-16)

What could still raise the Public Vision Index (PVI) or cut image latency after round 1 kept every default
([vision-experiments.md](../background/vision-experiments.md) §9). Five research agents covered the board entrants,
the vision tower in vLLM 0.30, test-time VLM techniques, classification and diffusion research, and our own dev
errors; the vLLM claims below were checked against the source in the `v0.30.0` image. Raw notes and full reports:
`.firecrawl/vision-research/` (git-ignored; `board-report.md`, `tower-report.md`, `vlm-report.md`,
`transfer-report.md`, `errors-report.md`).

Labels: **[board]** measured by the board, **[author]** an entrant's claim, **[ours]** our measurement,
**[inf]** inference.

## Short answer

- **The board fixes the image budget.** Kit README L246: native resolution capped at 1.6 MP; a fixed-budget model
  uses its largest setting at or below that, which for Gemma 4 is 560 soft tokens. Budget 1120 and tiling past the
  cap are out. Median, mean and p80 must each stay ≤ 1,000 ms on one RTX PRO 6000.
- **No entrant uses a technique we can copy onto stock Gemma for a large gain.** The leaders' public-score leads come
  from fine-tuning, and several fall apart on the private half the board ranks by.
- **Our errors are mostly confident perception errors** (59% of gemma's dev errors have a top-two margin ≥ 0.5), so
  calibration, priors and option orders cannot fix them; round 1 already showed that.
- **What is left:** gated short thinking on uncertain rows (the only test-time lever with a published gain on
  Gemma 4), calibration (ECE 0.090 against 0.010-0.025 for the leaders; not in PVI), two vLLM correctness checks on
  image attention, and small latency wins.

## 1. The board

Space data generated 2026-10-16T19:00Z, edition 0.3.2. Skill × 100. Full = ½ public + ½ private; the board ranks by
Full. Our rows are self-run, public only.

| # | Entrant | Base, kind | PVI | Private | Full | ECE | ms/row |
|---|---|---|---|---|---|---|---|
| 1 | Perplexity Decider v1.2 | Qwen3.8-27B, full FT | 77.25 | 66.18 | 71.72 | 0.011 | 395 |
| 2 | Amos 1 Large | Qwen3.8-27B, full FT | 76.10 | 68.71 | **72.40** | 0.024 | 386 |
| 3 | OneJev1.5-27B | Qwen3.8-27B, full FT | 75.65 | 62.15 | 68.90 | 0.019 | 365 |
| 4 | vLLM-SR d3 | Qwen3.8-27B, full FT | 74.08 | 68.45 | 71.26 | 0.016 | 299 |
| 5 | StartLux v1.1 | Qwen3.8-27B, full FT | 73.83 | 69.39 | 71.61 | 0.025 | 252 |
| – | **ours, gemma-4-31b** | stock, inference | **73.70** | – | – | 0.090 | 334 p50 |
| – | Aleria Judge 1.1.0 (PR #194, not listed) | stock Gemma 4 31B | 73.38 [author] | – | – | – | 245 p50 |
| 11 | span-02 | Gemma 4 26B-A4B, full FT | 70.69 | 60.85 | 65.77 | 0.089 | 265 |
| – | ours, qwen3.8-27b | stock, inference | 70.55 | – | – | 0.034 | 237 p50 |

Where we trail the best entrant, in PVI points (gap × weight ÷ 9.75): RealWorldQA 1.40 (62.5 vs 76.1), BLINK 1.37
(66.0 vs 79.4), Mind2Web 0.94, Hateful Memes 0.71, CharXiv 0.59. On R-Bench-M (35.0, best 37.2) and MMMU-Pro (43.4,
best 47.4) we are already near the top in skill.

What drives the leads:

- **BLINK** is mostly one subtask, Multi-view reasoning (camera motion): Amos and OneJev 19/19 on our dev rows, our
  gemma 10/19 by answering "right" on 18 of 19 [ours]. StartLux and jev-vision score 0-3/19, exactly mirrored. Only
  trained models perceive it.
- **RealWorldQA** follows the base model: our stock Qwen scores 70.3, every Qwen3.8 entrant 63-76, gemma 62.5. On dev
  the gap is in the 39 yes/no rows, where 7 of gemma's 10 errors answer No on small details (brake lights, a stop
  sign, a hydrant) [ours].
- **Mind2Web and Hateful Memes** leads come from the benchmarks' own train splits. pplx v1.2 rose 13 points on public
  Hateful Memes and fell 22 on private (55.3 → 19); OneJev shows the same pattern [board]. Stock models drop on
  private too (Qwen3.5-397B −10.2), so the private half is harder for everyone.

What the entrants do with images: nearly all put images first with no labels, send native resolution up to 1.6 MP,
read one order, and use one temperature (several have per-type T). The two that use more than one pass:

- **Aleria** (stock Gemma 4 31B): identity + a rotation by n/2, two more rotations when they disagree on ≥ 3 options,
  a temperature per option count T(n) = max(0.05, 6.9 − 0.7 ln n) fitted on text, and the arithmetic mean of
  probabilities. Against our run: R-Bench-M +5.4, CharXiv +3.5, BLINK −5.2, Mind2Web −4.4, net −0.32 [board + author].
  On our dev split the accuracies tie (0.806 vs 0.803), but its ECE is 0.028 against our 0.076 [ours].
- **span-02 and Blink v0.5** (Gemma 4 26B-A4B fine-tunes) think when unsure. span-02 thinks when the top
  probability is under 0.8, with a token cap from a fixed cost model aimed at 750 ms, and blends 0.5/0.5 with the
  first read; it is listed on the vision board with this on. Blink thinks on the ~16% least confident rows and
  claims 68.58 → 69.92 PVI on the same weights [author]. A separate Reasoning board is announced.

## 2. The vision tower

Read from the vLLM 0.30 and transformers source in the image and the HF configs.

- **Gemma 4 at 560 is served correctly.** The checkpoint sets `use_bidirectional_attention: "vision"`. vLLM's V2
  model runner passes each image's range and the TRITON_ATTN kernel makes sliding-window layers bidirectional within
  the image, as transformers does; full-attention layers stay causal. The openjev `vision_prefix_lm.py` patch only
  fixes DiffusionGemma's own code path.
- **At budget 1120 the bidirectional mask is silently off.** `compute_mm_prefix_ranges`
  (`vllm/v1/worker/gpu/attn_utils.py`) skips any image range longer than the 1,024-token sliding window; at 1120,
  1,542 of 1,543 dev images were longer. Round 1's 1120 arm (+1.0) was therefore read with causal image attention.
  The board's 560 rule makes this moot for the board.
- **Two gaps in the "never split an image across prefill chunks" rule** (`v1/core/sched/scheduler.py`, around
  L1750-1777): the check is skipped when the image is already in the encoder cache or scheduled in the same step
  (later rows of the same request), and a chunk starting exactly at the image is not checked. A split image is
  attended partly causally, and those KV blocks are reused by later rows through the prefix cache. Load-dependent;
  likely small, and a possible source of gemma's image run-to-run noise [inf].
- **Qwen3.8** is causal in both transformers and vLLM, has no DeepStack (`deepstack_visual_indexes: []`), full
  attention in all 27 ViT blocks, and M-RoPE matching transformers. It never upscales: median 116 soft tokens on
  R-Bench-M and 260 on CV-Bench, where gemma always gets ~560. That matches where Qwen trails gemma most.
- **Preprocessing is not costing accuracy.** No dev image with alpha has a transparent pixel; one dev image loses
  its EXIF rotation (the kit drops it too); the kit's LANCZOS resize followed by the processor's bicubic is a small
  double resample. Images under the cap reach us as their original bytes.
- **Latency.** Both vision encoders run eagerly; `--compilation-config '{"cudagraph_mm_encoder": true}'` turns on
  CUDA graphs for them. Gemma's encoder is about 20% of image compute at 560. The gateway fully decodes each image
  (2-32 ms CPU) and vLLM decodes it again.

## 3. Our dev errors (gemma, 1,462 rows)

| Benchmark | Index points to 100% | What the errors look like |
|---|---|---|
| Hateful Memes | 4.4 | Confidently wrong (median error margin 0.97); no yes/no bias to shift (offset sweep −2..+2 flat) |
| BLINK | 3.8 | Multi-view 0.47 (chance 0.5), counting, correspondence; 2-image rows 0.69; 94% of errors margin ≥ 0.5 |
| R-Bench-M | 3.1 (weight 0.5) | Reasoning; 57% of rows flip under reversed order; "Other options are incorrect" is gold on 23%, we get 6-10% of those |
| RealWorldQA | 3.0 | Small-detail yes/no |
| CV-Bench | 2.2 | 15 of 18 errors are Count |
| MMMU-Pro | 1.8 (weight 0.25) | Reasoning; 35% of rows flip under reversed order |

- Image size, aspect and gemma's upscale factor are not first-order (every bucket within ±0.035 of its benchmark's
  mean).
- Identity/reversed disagreement is a strong error detector: identity accuracy is 0.86 when the orders agree and
  0.39 when they disagree. Averaging the two fixes 24 rows and breaks 24 (net 0).
- Gemma and Qwen are complementary (either-model-right index 84.2 vs gemma 77.1), but averaging them gives +0.2 only.

## 4. Techniques from the literature and other fields

| Idea | Verdict | Why |
|---|---|---|
| Short thinking, gated to uncertain rows, then the letter readout | **try** | Only lever with a Gemma 4 result (Blink +1.34 PVI [author]); Gemma 4's card reports MMMU-Pro vision 76.9 with thinking vs our 50.6 one-token |
| Temperature per option count, mean of probabilities (Aleria) | **try (ECE)** | ECE 0.028 vs 0.076 on the same dev rows; CPU-only to test |
| Null-image contrast (classifier-free guidance / VCD on the letter logits) | maybe, low prior | One cheap text-only read; but VCD loses under greedy readouts (−85 on MME-P, 2504.10020) |
| Reversed-order averaging only on ≥ 5 options | maybe | Offline from the existing collect; Aleria's gains sit on many-option sets |
| More image tokens, tiling, zoom crops | out | Board caps Gemma at 560 and images at 1.6 MP |
| Visual token pruning (FastV, VisionZip, ...) | skip | vLLM 0.30 prunes video only; InfoVQA −8.4 at 50% |
| Flip/crop test-time augmentation, multi-budget ensembles | skip | Label-changing for spatial and text tasks; budget fixed |
| Caption or OCR first, then answer | skip | MMMU-Pro 49.7 → 49.4 |
| Set-of-Mark or grid overlays | skip | Untrained models ignore marks; fragile on BLINK |
| Content-free calibration, PriDe, letter priors | skip | Same family as round 1's nulls |
| Whole-prompt bidirectional attention (StartLux) | skip | Needs training for it |
| Diffusion classifiers, super-resolution | skip | Seconds per image; no evidence for MCQ |
| Train-split fine-tuning | owner's call | The only route to BLINK Multi-view, Mind2Web, Hateful Memes; public gains have not survived the private half |

## 5. Candidate experiments for round 2

Ordered by cost. Offline items reuse the DS-034 baseline collects; GPU items each need the owner's ok.

| ID | Experiment | Cost | Expect |
|---|---|---|---|
| R1 | T(n) per option count fitted on text calib data, mean of probabilities; ECE and index on dev | CPU | ECE toward 0.03; index ±0 |
| R2 | Reversed-order averaging only on ≥ 5 options | CPU | ±0.3 index |
| R3 | Gate simulation: rows selected by top-p < τ or order disagreement, the errors they capture, and the token budget the latency rule allows | CPU | Sizes R6 |
| R4 | `--hf-overrides` with bidirectional image attention off, one dev collect; and 1 vs 8 workers on BLINK to detect split images | ~25 min GPU | Says whether the scheduler gaps matter |
| R5 | Encoder CUDA graphs, one latency run | ~10 min GPU | −10 to −40 ms p50 [inf] |
| R6 | Gated thinking pilot: the R3-gated dev rows with thought caps 64/128/256, then the letter readout; blend vs replace | ~1 h GPU + harness work | +0.5 to +1.5 PVI [inf] |
| R7 | Null-image contrast: one text-only dev collect, offline sweep of the weight | ~10 min GPU | Likely null |

Thinking budget under the latency rule: today's mean is ~384 ms, so the mean leaves ~600 ms per row. At Gemma's
24.3 tok/s that is ~15 thought tokens per row on average: ~150 tokens on 10% of rows, or ~300 with MTP speculative
decoding (DS-004) if it doubles decode speed. p80 stays under 1,000 ms only if fewer than ~20% of rows think.

## Caveats

- Entrant numbers are public-half PVI unless marked private; ours are self-run with the kit.
- Per-benchmark dev cells have ~136 rows (SE 3-4 accuracy points); sub-task cells of 15-60 rows are hints.
- Thinking rows would need their own calibration: reasoning makes the letter probabilities overconfident.
- Never train, calibrate or tune on Jev API outputs; anything fitted uses gold labels or our own data, never the
  holdout.
