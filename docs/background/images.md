# Images in decisions

Based on the DS-024 design ([spec](../superpowers/specs/2026-10-15-vision-decisions-design.md)), the gateway code
(listed under Sources), a spike on the local RTX PRO 6000 (2026-10-15) and runs on rented 600 W RTX PRO 6000 boxes
(2026-10-16). Two profiles serve images: `gemma-4-31b` and
`qwen3.8-27b`.

## Short answer

An image arrives as base64 in the request, either in a top-level `images` list or as an `{"image": ...}` item inside a
list `state`. The gateway decodes it, refuses anything that is not a PNG, JPEG, WEBP or GIF, and downscales it past
1,638,400 pixels. In the row's token ids it writes the model's image placeholder inside `Context:`, where the state text
would go. It computes how many ids vLLM will expand that placeholder into, using ports of vLLM's and transformers' own
formulas. Image rows are read one per call through vLLM's token-in endpoint `/inference/v1/generate`, with the image
attached and named by its SHA-256, so every row of a request hits the same cache entry. From the letter logprobs on,
the flow is the same as for text: same layout, same label tables, same T and b.

## 1. From request to rows

### Wire formats

Both formats become one ordered list of context items ([`context_items`](../../gateway/images.py)):

```json
{"images": ["data:image/png;base64,..."], "state": {}, "questions": {...}}
{"state": ["Step 3 of checkout", {"image": "data:image/png;base64,..."}], "questions": {...}}
```

- **Order:** top-level images first, then the state. A list `state` that holds image items is split per item; the other
  items render with `render_state`, as text state does.
- **No images anywhere:** the context is exactly today's `render_state(state)`, so text requests build the same ids as
  before.
- **Empty state** (`None`, `""`, `{}`, `[]`) adds no text next to the images. The decision-index kit sends `state: {}`
  with its images.

### Sources, formats, limits

| Check | Rule | Refusal |
|---|---|---|
| Source | `data:` URLs (base64) or raw base64 only. Any other string, including `https://`, is refused; the gateway never fetches | 400 |
| Format | PNG, JPEG, WEBP, GIF only (Pillow `formats=`; an open-ended open would accept EPS, which can invoke Ghostscript) | 400 |
| Header size | Width × height checked against Pillow's `MAX_IMAGE_PIXELS` before the pixels are decoded | 400 |
| Image item | A `state` item with an `"image"` key and any other key (e.g. `"detail"`), rather than rendering its base64 as text | 400 |
| Count | At most 4 images per request | 400 |
| Body | At most 20,000,000 bytes, checked on `Content-Length` by a plain ASGI middleware ([`body_limit.py`](../../gateway/body_limit.py)) before the body is read | 400 |
| Aspect (Qwen) | Over 200:1 refused, as transformers does | 400 |
| Placeholder in text | Question or state text that spells a placeholder token (e.g. `<\|image\|>`) in an image request | 400 |
| Images on a text-only profile | `SYSTEMONE_IMAGES` is off | 400 |
| Length | The prompt with images expanded reaches `SYSTEMONE_MAX_LEN` | 422 |

Image errors are 400 (`ImageError`); a prompt that is too long stays 422, as for text.

### Downscaling

An image over 1,638,400 pixels (1,600 × 32 × 32) is shrunk with the kit's fit rule: the largest size with the same
aspect ratio inside the budget, resampled with LANCZOS. A PNG stays a PNG (RGBA when it has alpha); everything else is
re-encoded as JPEG quality 95. 4000×3000, for example, becomes 1478×1108. Decoding and downscaling take CPU time, so
they run off the event loop, in the same thread as `build_rows`.

A downscaled WEBP or GIF therefore becomes a JPEG and loses its transparency; a PNG keeps its alpha.

### Where the image sits

Images go inside the layout's `Context:` part, in context order. The text pieces between images are encoded per piece
(one tokenizer call for all of them) and the placeholder ids are spliced in between
([`image_context`](../../gateway/prompts.py)). With the default `header` layout, a one-image request looks like:

```
<chat head>Questions that will be asked about the context:
- Is the cart empty?
- Which button submits?

Context:
[placeholder ids]                    <- vLLM replaces this with the image's soft tokens
Step 3 of checkout

Question: Is the cart empty?
Options: ...
Answer: (
```

The wording is unchanged, so the label tables and calibration files of the text layout still apply.

## 2. Placeholders and expanded lengths

A vision model does not see an image as text tokens. Its vision encoder turns the image into a run of **soft tokens**:
embedding vectors that each take one position in the prompt, like a token, but have no id in the vocabulary. The
gateway writes a short placeholder; vLLM swaps in the soft tokens and two marker ids around them.

| Family | Gateway writes (ids from the HF config) | vLLM puts in |
|---|---|---|
| `gemma4` | `<\|image\|>` 258880 | boi 255999, the soft tokens, eoi 258882 |
| `qwen3_5` | `<\|vision_start\|><\|image_pad\|><\|vision_end\|>` 248053, 248056, 248054 | expands `<\|image_pad\|>` into the soft tokens, between the start and end marks |

So an image's expanded length is soft tokens + 2 on both families. The soft-token counts are ports of the model code,
not estimates ([`vision.py`](../../gateway/vision.py)):

- **Gemma** (vLLM 0.30 `Gemma4ProcessingInfo._compute_num_soft_tokens`): every image is rescaled to fill the
  `max_soft_tokens` budget, each side rounded down to 48-px units (patch 16 × pool 3), then patches ÷ 9, capped.
  Small images are scaled up, so nearly every image costs close to the cap.
- **Qwen** (transformers `smart_resize`): each side rounded to a multiple of 32 (patch 16 × merge 2), then shrunk into
  1,638,400 px or grown to 65,536 px; one soft token per 32×32 tile.

| Image | gemma-4-31b (max 560) | qwen3.8-27b |
|---|---|---|
| 1024×1024 | 529 | 1,024 |
| 1280×1092 | 525 | 1,360 |
| 10×10 | 529 (scaled up) | 64 |
| 3×900 | 409 | refused (over 200:1) |
| 1600×1024 | – | 1,600 |
| 4000×3000 (downscaled by the gateway) | 540 | 1,564 |

`MM_PROCESSOR_KWARGS` in the profile is the single source for the budget: the vLLM entrypoint passes it as
`--mm-processor-kwargs`, and the gateway reads it for these formulas (gemma `{"max_soft_tokens":560}`, qwen
`{"max_pixels":1638400}`). A fuzz check found the ports equal to the vLLM and transformers source on 80,000 random
sizes.

### Why the gateway must know the count

The token ids the gateway holds are short by `expanded − placeholder` ids per image. Everything that counts tokens uses
the expanded length ([`Batch`](../../gateway/prompts.py)):

- **Length cap:** `longest` includes the images, so a prompt pushed over `SYSTEMONE_MAX_LEN` by its image gets 422
  instead of a vLLM error.
- **`usage.input_tokens`:** the shared prefix once, images included once when they sit in it (once per row otherwise).
- **Warm-up threshold:** compared with `shared_tokens`, the shared prefix as vLLM sees it.
- **Qwen padding:** the pad that brings the shared prefix to an 800-token block boundary is computed on the expanded
  length; a pad computed on the short ids would miss the boundary. Middle padding is off for image rows (it cuts the
  state text, and image rows have none); the Qwen profiles pad at the front.

## 3. Reading image rows

**Why not `/v1/completions`.** Text rows send token ids to `/v1/completions`. In vLLM 0.30 that endpoint accepts
unknown fields (`extra="allow"`, `completion/protocol.py:50-56`) and silently drops image fields: the row would be read
with a bare placeholder and no image. The chat endpoint does take images, but it tokenizes the messages itself, so our
piecewise token ids and the single-token label checks would no longer hold.

**The token-in endpoint.** `/inference/v1/generate` (enabled by `--enable-scale-out`, which the entrypoint adds when
`SYSTEMONE_IMAGES=1`) takes `token_ids` plus `content_parts`. Each row is one call:

- **Images:** each part is the image's data URL with `uuid` = SHA-256 of its bytes. vLLM uses the uuid as the image's
  cache key, so every row of a request, and any later request with the same bytes, names the same cache entry.
- **Labels:** `logprob_token_ids` takes at most 128 ids, and with only label ids in it vLLM's answer comes back one
  entry short. Each call therefore asks for a chunk of up to 127 labels plus one spare id (the smallest non-negative id
  not in the chunk) and `logprobs` = N + 1. The spare is ignored. vLLM refuses sample `logprobs` above
  `--max-logprobs` (default 20), so the vision profiles start vLLM with `--max-logprobs 128`.
- **Warm-up:** as for text, but measured on the expanded shared tokens. gemma (`WARM_UP=prefix`): when the shared
  prefix reaches 4,096 tokens, it is sent alone first, with its images. qwen (`WARM_UP=row`): from 800 shared tokens,
  row 1 goes first and the rest follow; one image takes a request past 800.
- **Scheduling:** the DS-007 governor (waves while chat decodes) and decision priority apply as for text.

Text-only requests take the old `/v1/completions` path unchanged ([`read_batch`](../../gateway/decide.py)).

## 4. Prompt sharing with images

### Within a request

[`scripts/image_share_probe.py`](../../scripts/image_share_probe.py): one 1280×1092 image, a ~200-token state, a fresh
image per repeat, rows sent straight to vLLM. Computed ÷ usage (as in [prompt-sharing.md](prompt-sharing.md); 1.00 means
the image and state were computed once), medians of 3:

| Questions | gemma, all rows together | gemma, prefix first | qwen, all rows together | qwen, prefix first |
|---|---|---|---|---|
| 4 | 0.96 (388 ms) | 0.98 (445 ms) | 1.05 (462 ms) | 1.07 (545 ms) |
| 16 | 0.85 (525 ms) | 0.87 (591 ms) | **3.01** (1,310 ms) | 1.62 (859 ms) |

Results: [gemma](../results/archive/gemma-4-31b/2026-10-16T014917Z-image-sharing/summary.md),
[qwen](../results/archive/qwen3.8-27b/2026-10-16T012611Z-image-sharing/summary.md).

- **Gemma:** rows share the image without any warm-up; sending the prefix first only adds a round trip, so the
  4,096-token prefix warm-up is left for long states.
- **Qwen:** rows sent together recompute the image, as text rows recompute the state (prompt-sharing.md §2). Sending
  the prefix first cuts that to 1.62 (the 800-block pad included). The profile's `WARM_UP=row` (row 1 first, then the
  rest) was not measured here; it runs on every image request, since one image reaches its 800-token threshold.

### Across requests

With `header`, the question list comes before `Context:`. The same image asked about with a different set of questions
therefore has a different prefix and is computed again. This is accepted: RPA steps usually send a new screenshot each
time. Layouts that put the context first, such as `decider_chat`, do share an image across requests with different
questions; the live cache test below uses that.

## 5. What was checked

### The spike (2026-10-15, local, gemma-4-31b)

| Finding | Evidence |
|---|---|
| `/inference/v1/generate` builds the same prompt as the chat path | expanded ids equal on 60/60 rows; same top answer 60/60 |
| Cold token-in logprobs equal the chat path's | median gap 0, 17/20 bit-identical (chat vs itself: 17/20) |
| A cache hit moves logprobs by one bf16 step | median 0.125 logit (~0.03 probability after T), max 0.26 |
| One image shared by 8 questions sent one after another is cached | 544/605 tokens hit; 218 ms first, 57 ms each after |
| Stock kit readout, 2,064-row slice of 10 benchmarks | gemma-4-31b 70.29; qwen3.8-27b 66.98 with thinking off |

With thinking on, qwen3.8 scores about chance: it reads the letters at `<think>` and answers "A" 78% of the time.
Decisions keep thinking off.

### Live tests (2026-10-16, both profiles)

All 11 image tests in [`test_image_decisions.py`](../../tests/live/test_image_decisions.py) pass on both models
([gemma](../results/archive/gemma-4-31b/2026-10-16T000616Z-vast-live/junit.xml),
[qwen](../results/archive/qwen3.8-27b/2026-10-16T000604Z-vast-live/junit.xml)):

- expanded lengths equal vLLM's `prompt_token_ids` for 1024², 1280×1092, 10×10, 3×900 (gemma; qwen refuses it with
  400), 4000×3000 after downscaling, and two images in one request;
- a second request with another question (`decider_chat`) reuses the image from the cache: hits run past the image's
  end, rounded to blocks;
- a body over 20 MB gets 400; a prompt pushed over the cap only by its image gets 422.

### Text regression after the profile edits

The profile edits (`SYSTEMONE_IMAGES=1`, `MM_PROCESSOR_KWARGS`, up to 4 images per prompt, and qwen's vision tower
loaded with `LANGUAGE_MODEL_ONLY=0`) could move text answers. Each
model ran before and after on the same box: JevBench, and a Decision Index subset
(`data/splits/vision-regression.json`, 3,120 rows, 8,099 questions). A "flip" is a changed top answer; "over gap" means
the top-two gap was above 0.10, where the stability test would fail.

| | qwen3.8-27b | gemma-4-31b |
|---|---|---|
| JevBench | 89.7% → 89.7%; 6 flips, all gaps < 0.10, max \|Δp\| 0.037 | 88.2% → 88.2%; 2 flips (gaps 0.000, 0.092), max \|Δp\| 0.124 |
| Index subset | 52 flips, 1 over gap (0.103), max \|Δp\| 0.068, median 0.0007 | 33 flips, 10 over gap, max \|Δp\| 0.66 |
| Same subset, no change, run against itself | – | 43–47 flips, 17–18 over gap, max 0.41–0.64 (three pairs) |

Gemma's subset numbers look large next to qwen's, but they are smaller than gemma's own run-to-run noise with nothing
changed, so this is noise ([determinism.md](determinism.md) covers bf16 noise). Results:
JevBench gemma [before](../results/gemma-4-31b/2026-10-16T002251Z-jevbench/summary.md) /
[after](../results/gemma-4-31b/2026-10-16T011836Z-jevbench/summary.md),
qwen [before](../results/qwen3.8-27b/2026-10-16T002745Z-jevbench/summary.md) /
[after](../results/qwen3.8-27b/2026-10-16T010651Z-jevbench/summary.md);
subset gemma [before](../results/archive/gemma-4-31b/before-2026-10-16T000616Z-vast-index-subset/summary.md) /
[after](../results/archive/gemma-4-31b/after-2026-10-16T000616Z-vast-index-subset/summary.md),
qwen [before](../results/archive/qwen3.8-27b/before-2026-10-16T000604Z-vast-index-subset/summary.md) /
[after](../results/archive/qwen3.8-27b/after-2026-10-16T000604Z-vast-index-subset/summary.md).

**KV cache.** gemma has 84,944 tokens after the edits (86,964 before, measured locally); qwen has 460,853 with the
vision tower loaded.

## 6. The vision suite

The decision-index kit's `decide` engine sends each vision row through `/v1/systemone` as protocol decisions. A
300-row stratified sample (seed 24), one client, 600 W boxes:

| Profile | Public Vision Index | Latency median / mean / p80 | ECE | Accuracy | Result |
|---|---|---|---|---|---|
| gemma-4-31b | 75.59 | 334 / 384 / 445 ms | 0.086 | 0.790 | [vision-sample](../results/gemma-4-31b/2026-10-16T015117Z-vision-sample/summary.md) |
| qwen3.8-27b | 68.92 | 237 / 300 / 466 ms | 0.062 | 0.750 | [vision-sample](../results/qwen3.8-27b/2026-10-16T014124Z-vision-sample/summary.md) |

**Calibration.** Image rows reuse each profile's text T and b. ECE is measured on the image rows; nothing is fitted on
the suite, because it is a test set.

### Full suite against stock

All 12,210 rows, every one `ok`. The gateway runs go through `/v1/systemone`; the stock runs use the kit's `vllm-vl`
engine on plain vLLM (qwen3.8 with thinking off). Both used the kit's default 8 workers.

| Profile | Gateway PVI | Stock PVI | Δ | Gateway ECE | Stock ECE | ok rows |
|---|---|---|---|---|---|---|
| gemma-4-31b | 73.70 | 71.81 | +1.89 | 0.090 | 0.191 | 12,210 / 12,210 |
| qwen3.8-27b | 70.55 | 64.62 | +5.93 | 0.034 | 0.038 | 12,210 / 12,210 |

Runs: [gemma gateway](../results/gemma-4-31b/2026-10-16T023752Z-vision/summary.md),
[gemma stock](../results/gemma-4-31b/2026-10-16T023758Z-vision-stock/summary.md),
[qwen gateway](../results/qwen3.8-27b/2026-10-16T022903Z-vision/summary.md),
[qwen stock](../results/qwen3.8-27b/2026-10-16T022908Z-vision-stock/summary.md).

Accuracy per benchmark, gateway / stock:

| Benchmark | Rows | gemma gateway | gemma stock | qwen gateway | qwen stock |
|---|---|---|---|---|---|
| CV-Bench | 2038 | 0.856 | 0.834 | 0.841 | 0.836 |
| BLINK | 961 | 0.780 | 0.755 | 0.751 | 0.702 |
| RealWorldQA | 589 | 0.771 | 0.781 | 0.818 | 0.800 |
| CharXiv | 532 | 0.833 | 0.791 | 0.801 | 0.733 |
| InfographicVQA | 244 | 0.963 | 0.963 | 0.955 | 0.939 |
| Mind2Web | 973 | 0.881 | 0.823 | 0.876 | 0.822 |
| Winoground | 800 | 0.925 | 0.930 | 0.904 | 0.800 |
| KIE (CORD+FUNSD) | 2465 | 0.953 | 0.953 | 0.944 | 0.928 |
| Moderation (Hateful Memes) | 1213 | 0.757 | 0.763 | 0.697 | 0.676 |
| R-Bench-M | 665 | 0.459 | 0.435 | 0.350 | 0.343 |
| MMMU-Pro vision | 1730 | 0.506 | 0.499 | 0.460 | 0.461 |

Where the gain comes from: on both models the largest steps are Mind2Web (+5.8 gemma, +5.4 qwen) and CharXiv (+4.2,
+6.8); BLINK adds +2.5 and +4.9. Qwen's biggest step is Winoground, 0.800 to 0.904. Gemma ties or loses a little on
RealWorldQA, Winoground and Moderation (at most 1 point), and ties on InfographicVQA and KIE. Gemma's ECE halves
(0.191 to 0.090); qwen's is close (0.034 vs 0.038).

**Latency is under load.** Eight workers share the GPU, so the gateway medians (gemma 1,750 ms, qwen 1,475 ms) are not
the single-client numbers; the 300-row one-client samples above are the latency gate. The stock medians (222 and
177 ms) are on the same 8 workers but are a different kind of request, so they are not a gateway comparison.

## Caveats

- **The 300-row sample is small.** 300 rows over 11 benchmarks, some with fewer than 20 rows. Read the per-benchmark accuracies
  in the result files loosely.
- **Calibration is borrowed.** T and b were fitted on text. The ECE above says how well they carry over; it is not a
  fit.
- **Ports follow one version.** The soft-token formulas match vLLM 0.30 and the pinned transformers. A vLLM upgrade
  needs the live length test rerun.
- **One image shape in the sharing probe.** 1280×1092 with a ~200-token state; larger states move the ratios as in
  [prompt-layouts.md](prompt-layouts.md) §3.

## Sources

- Our code: [`images.py`](../../gateway/images.py), [`vision.py`](../../gateway/vision.py),
  [`prompts.py`](../../gateway/prompts.py), [`readout.py`](../../gateway/readout.py),
  [`decide.py`](../../gateway/decide.py), [`body_limit.py`](../../gateway/body_limit.py),
  [`image_share_probe.py`](../../scripts/image_share_probe.py).
- Design: [2026-10-15-vision-decisions-design.md](../superpowers/specs/2026-10-15-vision-decisions-design.md).
- Related: [prompt-sharing.md](prompt-sharing.md), [prompt-layouts.md](prompt-layouts.md),
  [decision-readout.md](decision-readout.md), [calibration.md](calibration.md).
