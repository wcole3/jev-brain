# Vision decisions design (DS-024)

Date: 2026-10-15. Status: approved in brainstorming, pending spec review.
Ticket: DS-024. Background: [prompt-sharing.md](../../background/prompt-sharing.md),
[prompt-layouts.md](../../background/prompt-layouts.md), [decision-readout.md](../../background/decision-readout.md),
[calibration.md](../../background/calibration.md), the kit's [docs/vision.md](https://github.com/apolinario/decision-index/blob/f5a6e4f/docs/vision.md).

## Goal

`/v1/systemone` answers decisions about images (screenshots, documents, photos) with the same readout,
calibration and prompt sharing as text, on gemma-4-31b and qwen3.8-27b. The Decision Index Vision board
is the yardstick and a later submission.

Done when, for both profiles:

- a request with images returns typed answers, and several questions on one image share its prefill;
- text-only answers are unchanged within bf16 noise after the profile edits (section 6, step 2);
- the full public vision suite (12,210 rows) is scored through our gateway, next to the stock kit
  baseline, with single-client latency and ECE on image rows;
- `docs/background/images.md` explains how image prompts are built and shared.

## What the spike showed (2026-10-15)

| Finding | Evidence |
|---|---|
| vLLM 0.30 `/v1/completions` silently drops image fields | source, `completion/protocol.py:50-56`; `extra="allow"` |
| `/inference/v1/generate` (with `--enable-scale-out`) takes our token ids plus image parts | gemma: expanded ids equal the chat path's on 60/60 rows; same top answer 60/60 |
| Cold token-in logprobs equal the chat path's | median gap 0, 17/20 bit-identical (chat vs itself: 17/20) |
| A cache hit moves logprobs by one bf16 step | median 0.125 (about 0.03 in probability after T), max 0.26 |
| One image shared by 8 questions is cached | 544/605 tokens hit; 218 ms first, 57 ms each after |
| Gemma starts with 560 soft tokens and the 1,024-token long-prefill threshold | vLLM forces `--disable_chunked_mm_input`; an image fits the 8,192-token step |
| Stock kit readout, 2,064-row slice, 10 benchmarks | gemma-4-31b 70.29; qwen3.8-27b 66.98 with thinking off, about chance with it on |

Spike code is throwaway (scratchpad and `.cache/decision-index-vision/`), not part of this design.

## Decisions

| Topic | Decision | Why |
|---|---|---|
| Wire format | Accept top-level `images: [...]` **and** `{"image": ...}` parts inside `state`; normalize to one ordered context | Both are common on the board; the kit's `decide` engine sends `images`, RPA clients want text and images interleaved |
| Image sources | `data:` URLs and raw base64 only; `https://` refused | The server must not fetch URLs a client names (SSRF) |
| Limits | 4 images, 20 MB body; images over 1.6 MP downscaled in the gateway (aspect kept, LANCZOS) | The board's rule and the suite's maximum |
| Layout | `header`, unchanged wording; images sit inside `Context:` | Same label tables and calibration as text; within-request sharing measured |
| Readout path | Image rows via `/inference/v1/generate`; text rows stay on `/v1/completions` | Only path that keeps our token ids, label checks and calibration (spike) |
| Calibration | Reuse each profile's text T and b; measure ECE on image rows, do not fit on the suite | The suite is a test set |
| Profiles | Edit `gemma-4-31b` and `qwen3.8-27b` in place, then check text answers did not move | One serving config per model; regression step below |
| Thinking | Off for decisions, as today | Qwen with thinking on reads letters at `<think>` and answers "A" 78% of the time |

## 1. Request flow

```
POST /v1/systemone {state, questions, images?}
  1. images.parse      -> Context: ordered items, each text or Image(bytes, mime, sha256, w, h)
  2. questions.render  -> question texts (unchanged)
  3. prompts.build_rows-> rows of token ids; each image is the model's placeholder ids
  4. readout           -> text rows: /v1/completions (unchanged)
                          image rows: /inference/v1/generate, one row per call, images attached
  5..7 probabilities, average_back, answers (unchanged)
```

- **Parse** (`gateway/images.py`, new). Top-level images come first, then `state`. In a list `state`, an
  `{"image": ...}` item is an image and everything else renders as today (`render_state`). Decoding,
  size checks and downscaling happen here, once per request.
- **Placeholders** (`gateway/images.py`). One small table keyed by model family:
  - Gemma 4: `<|image|>` (258880) alone; vLLM adds `<|image>` and `<image|>` around the soft tokens.
  - Qwen 3.x: `<|vision_start|><|image_pad|><|vision_end|>`; vLLM expands `<|image_pad|>`.
  The ids come from the tokenizer at startup and are checked to be single tokens.
- **Expanded length.** vLLM expands each placeholder to a size the gateway must know for
  `SYSTEMONE_MAX_LEN`, `usage.input_tokens` and Qwen's prefix padding:
  - Gemma: `min(floor(patches / 9), max_soft_tokens) + 2`;
  - Qwen: `(H / 32) × (W / 32)` after the processor's resize, plus 2.
  A live test compares both formulas with vLLM's `return_token_ids` count.
- **Build rows** (`gateway/prompts.py`). The context part becomes a list of segments (text ids or
  placeholder ids) encoded once and shared by every row, as today. Qwen's front padding is computed on
  expanded lengths.
- **Readout** (`gateway/readout.py`). For image rows, one `/inference/v1/generate` call per row with
  `content_parts` (data URLs), `max_tokens=1`, `logprob_token_ids = labels + [one extra id]` and
  `logprobs = len(labels) + 1`, so the response cut keeps every label. Warm-up follows the profile:
  gemma sends the shared prefix, images included, alone first and then all rows (`WARM_UP=prefix`;
  rows sent together under chunked prefill each recompute the prefix, 2026-10-15 probe); qwen sends
  row 1 then the rest. `priority` and the DS-007 governor apply as for text.
- **Route** (`gateway/decide.py`). A request goes the image path only when it has images.

## 2. Profiles

| Profile | Changes |
|---|---|
| `gemma-4-31b` | `EXTRA_ARGS` + `--enable-scale-out --mm-processor-kwargs {"max_soft_tokens":560}`, `--limit-mm-per-prompt {"video":0,"image":4}` |
| `qwen3.8-27b` | `LANGUAGE_MODEL_ONLY=0`, `--enable-scale-out`, `--mm-processor-kwargs {"max_pixels":1638400}`, `--limit-mm-per-prompt {"video":0,"image":4}` |

Qwen risks, measured before the gateway work depends on them:

- KV blocks lost to the vision tower (startup log, before vs after);
- images inside the 800-token padded blocks still hit the cache;
- MTP's patched rejection sampler with image rows.

Other profiles (`qwen3.6-*`, quantized ones) are out of scope for this design.

## 3. Errors

| Case | Response |
|---|---|
| `https://` or unknown image source | 400, names the item |
| Undecodable image, more than 4 images, body over 20 MB | 400 |
| Image request on a profile without vision | 400 "this profile serves text only" |
| Expanded prompt over `SYSTEMONE_MAX_LEN` | 422, recorded by the kit as `unsupported` (as today) |
| vLLM error on the image route | 502, as for text |

## 4. Prompt sharing with images

- **Within a request:** images are in the shared prefix, so the second and later questions reuse them
  (spike: 544/605 tokens).
- **Across requests:** in `header` the question list comes before `Context:`, so the same screenshot with
  a different question set is recomputed. Accepted: RPA steps usually send a new screenshot anyway.
- **vLLM image identity:** an image's cache hash comes from its bytes, so the gateway sends the bytes it
  decoded, unchanged, on every row of a request.

## 5. Docs

- `docs/background/images.md` (new): request to rows, where images sit, placeholder and expanded-length
  rules per model, what is cached within and across requests, the spike's numbers.
- `prompt-layouts.md`: images inside `Context:`. `prompt-sharing.md`: image prefixes and the
  cross-request caveat.
- README: request format, limits, errors.

## 6. Testing and evaluation

1. **Unit** (`uv run pytest -q`): both formats parse to the same context; refused sources and sizes;
   downscaling; placeholder ids and expanded-length formulas; routing; the extra label id.
2. **Text regression after the profile edits** (both profiles), against today's results:
   - JevBench gold: accuracy and flips (`scripts/compare_runs.py`);
   - the 3,120-row Index sample (`.cache/submit-gemma/agree-ids.json`): top-answer agreement, max |dp|;
   - latency-v1; KV cache blocks from the startup log.
   Pass: no top-answer flip where the top-two gap exceeds 0.10, and latency within run-to-run noise.
3. **Live** (`tests/live`): one image with several questions; image parts in `state`; a cache hit on the
   second question; expanded lengths match vLLM; a text request is unchanged.
4. **Vision evaluation**, both profiles:
   - full public suite through the gateway: kit `decide` engine, `protocol=decisions`,
     `path=/v1/systemone`;
   - stock baseline on the full suite: kit `vllm-vl` (qwen with thinking off);
   - single-client latency on a vision sample (gate: median, mean, p80 ≤ 1,000 ms);
   - ECE on image rows.
   Results in `docs/results/<profile>/<timestamp>-vision/`.

GPU runs over 10 minutes wait for the owner's ok, with an estimate.

## Out of scope

- Fitting temperatures on images, and any training.
- Fetching image URLs, video, audio.
- A context-first layout for cross-request image reuse.
- A Vision board submission (follows the evaluation, as its own step).
