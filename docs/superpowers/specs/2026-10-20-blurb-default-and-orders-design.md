# Blurb by default, gated option orders, Index reruns

Date: 2026-10-20. Status: draft for owner review. Profiles: gemma-4-31b, gemma-4-31b-fp8, qwen3.8-27b,
qwen3.8-27b-fp8, qwen3.8-27b-nvfp4, qwen3.6-27b, qwen3.6-27b-fp8.
Background: [option-ordering.md §10](../../background/option-ordering.md) (round 4 grids),
[prompt-layouts.md §5](../../background/prompt-layouts.md) (blurb screen),
[2026-10-19-layouts-and-blurb-design.md](2026-10-19-layouts-and-blurb-design.md) (round 4 spec).

## Goal

Ship the owner's round 4 picks, then rerun the full Decision Index on every gemma and qwen profile.

| Profile | Layout | Text orders | Image orders | Index runs |
|---|---|---|---|---|
| gemma-4-31b, gemma-4-31b-fp8 | `blurb_header` | `top_p:0.9+reversed` | `identity` | text + image |
| qwen3.8-27b, -fp8, -nvfp4 | `blurb_header` | `min_n:4+reversed` | `min_n:4+reversed` | text + image |
| qwen3.6-27b, qwen3.6-27b-fp8 | `blurb_header` | `identity` | (text only) | text |

Combine rule for every setting: `mean-logprob` (owner pick). qwen3.6 keeps `identity` because no round has
measured its orders.

Done when:

- the gateway serves the table above, and unit, parity and lint pass;
- every profile has `blurb_header` label tables and a calibration fitted on fresh `blurb_header` collects;
- the box queues and runbook are ready to rent (stage 1 and stage 2 below). Renting waits for the owner's ok.

## Constraints

- Never train, calibrate or tune on Jev API outputs. Fits use the calib split; eval picks what ships, as today.
- `header`, `decider_chat` and `question_first` stay byte-identical, as do their label tables and calibrations.
- GPU jobs over 10 minutes need the owner's ok; renting boxes needs it too.
- Commits stay local; the owner pushes.

## 1. Layout

`prompts/blurb_header.toml` is `prompts/experiments/blurb-header.toml` byte for byte, minus its "Experiment (never
loaded by the gateway)" comment line. Every profile above sets `PROMPT_LAYOUT=blurb_header`.
`scripts/build_labels.py` writes `data/<profile>/blurb_header/labels.json` for all 7 profiles (CPU, local
tokenizers). The experiment file stays, so round 4 collects still replay.

## 2. Order settings

`gateway/orders.py` grammar, in the style of `cyclic:<k>`:

| Setting | Orders read |
|---|---|
| `identity`, `identity+reversed`, `cyclic:<k>` | unchanged |
| `min_n:<k>+reversed` | identity; plus reversed when the question has ≥ k options |
| `top_p:<τ>+reversed` | identity; plus reversed when the identity top probability is < τ |

- `min_n` is fixed per option count, so `option_orders(n, setting)` returns both orders up front, like today.
- `top_p` is gated. `option_orders` returns the identity order only. A new `gated(setting)` returns τ, or `None`
  for fixed settings.
- Both mirror `scripts/order_policies.py` (`min_n`, `top_p` gates with `second = reversed`). A unit test checks
  that both give the same perms on the round 4 collects.

New setting `OPTION_ORDERS_IMAGES` (`Settings.option_orders_images`). When empty it uses `OPTION_ORDERS`. A request
with images uses it; a text request uses `OPTION_ORDERS`. A request's `option_orders` override still wins for
both.

## 3. Gateway flow

`decide.read_rows` for a gated setting:

1. Build and read the identity rows, as today.
2. Gate each question: softmax of its identity logprobs at the identity calibration's T for its type, no b (as
   rounds 3 and 4 gated). Keep the questions whose top probability is < τ.
3. If any are kept, build the reversed rows for those questions only (same state, so the prefix is cached), read
   them, and append them to those questions' reads.

- `input_tokens` sums both passes. The `systemone_max_len` check applies to both.
- `build_batch` takes per-question perms instead of one `OrderFn` for all, so step 3 can ask for one question's
  reversed order.
- Image rows go through the same steps. No profile gates images today, but nothing refuses it.

**Combine: `mean-logprob`.** `probabilities` averages the raw logprobs back to caller order (`average_back`), adds
the noul b·T to "yes", then takes one softmax at T. With one order this is the same as today's `blend`, so identity
profiles answer exactly as before. `blend` (`mean-prob`) stays for `scripts/order_policies.py`.

## 4. Calibration per order setting

- `calibration.json` (or `calibration-<prefix_block>.json`, as today) is the fit for `OPTION_ORDERS`.
- `calibration-identity.json` is the identity fit. It is loaded when a gate needs its T, or when
  `OPTION_ORDERS_IMAGES` is `identity` and `OPTION_ORDERS` is not. gemma needs it for both reasons.
- For any other setting, the file name is the setting, with each `:` and `+` replaced by `-`. No profile needs one
  yet.
- Startup refuses the served layout's (`PROMPT_LAYOUT`) file when its `fit.orders` differs from the setting it
  serves. Other layouts, and a request's `option_orders` override, still only warn.
- A setting with no `calibration-<setting>.json` falls back to `calibration.json`, so `header`'s identity fit still
  serves the latency A/B's `--layout header --option-orders identity`.
- Images use the text fit for their setting, as every round has done.

`scripts/calibrate.py`:

- `--orders X` fits under `mean-logprob` and writes the file for X. A gated X reads its gate T from the identity
  file, which must already exist.
- `collect.py` refuses non-identity profiles today (its pad mirrors one identity row per question). It now pads as
  the profile's live text setting would: one row per order `option_orders` returns (identity only for `top_p`,
  whose second pass reuses the first pass's pad decision).
- New `--collect-label L` reads `<split>-L.jsonl.gz`, so the reduced-orders collect below can be used.
- `scripts/offline.py` `chosen_reads` learns both gates, so `evaluate.py offline` scores the shipped settings.

Fits per profile:

- gemma ×2: `--orders identity`, then `--orders top_p:0.9+reversed`.
- qwen3.8 ×3: `--orders min_n:4+reversed`.
- qwen3.6 ×2: `--orders identity`.

## 5. Profiles

- All 7 set `PROMPT_LAYOUT=blurb_header` and their `OPTION_ORDERS`; gemma also sets `OPTION_ORDERS_IMAGES=identity`.
- The quantized gemma and qwen3.8 profiles get vision, copied from their bf16 base:
  - `SYSTEMONE_IMAGES=1` and `MM_PROCESSOR_KWARGS` (gemma `{"max_soft_tokens":560}`, qwen
    `{"max_pixels":1638400}`);
  - `--limit-mm-per-prompt` with `"image":4` and `--max-logprobs 128` in `EXTRA_ARGS`;
  - qwen3.8 fp8 and nvfp4: `LANGUAGE_MODEL_ONLY=0`.
- Every quantized checkpoint ships vision weights (checked 2026-10-20: gemma fp8 leaves `vision` unquantized,
  qwen fp8 keeps `visual` in bf16, nvfp4 has 333 `model.visual` tensors).
- Risk: vision costs KV headroom. Each quant box's stage 1 checks this first (below).

## 6. Runs

One vast box per profile, all 7 rented and run in parallel (owner, 2026-10-20).

**Stage 1, collect** (`scripts/remote/jobs/<profile>.txt`):

1. `stack` (bootstrap, weights, vLLM up). Quant profiles with vision also run one image request before the
   collects; a vLLM start or image error stops the queue there.
2. `collect-calib` and `collect-eval`: `collect.py --layouts blurb_header --orders X --label blurb`, with X the
   profile's live setting (qwen3.8 `min_n:4+reversed`, qwen3.6 `identity`) and `identity+reversed` for gemma, whose
   `top_p` gate reads reversed only for some questions. Reason (owner, 2026-10-20): same row composition as live
   requests; extra co-batched rows move nvfp4 reads by up to 0.23, same composition is bit-identical.
3. Pull. Locally: `calibrate.py` per section 4. The owner reviews and commits the calibration files.

**Stage 2, latency and Index.** Push the committed tree to the same box; the queue restarts the stack (new
calibrations), then runs:

- latency A/B on the same box, idle stack, before the Index: `latency.py --profile P --layout header
  --option-orders identity` (old defaults; the quant profiles keep vision on) and `latency.py --profile P` (new
  defaults), all 7;
- image latency: `vision_run.py --sample 300 --workers 1` (new defaults only; the kit sends its own requests, so no
  override). Compared against the 2026-10-16 bf16 runs; the quants have no earlier image baseline;
- text: `evaluate.py index --profile P --shards 4 --strict` (all 7);
- image: `vision-setup`, then `vision_run.py --profile P` on the full suite (the 5 gemma and qwen3.8 profiles).

Results land in `docs/results/<profile>/`, stamped with a clean commit, since the calibrations are committed
before the push. `docs/remote-gpu.md` gets the two-stage flow.

## Testing

- Unit tests:
  - the order grammar;
  - `min_n`/`top_p` perms matching `order_policies.perms`;
  - the two-pass read with a fake readout: gated questions get a second row, the others don't;
  - `mean-logprob` equal to `blend` with one order;
  - calibration loading per setting, and the startup refusal on a wrong `fit.orders`;
  - `OPTION_ORDERS_IMAGES` routing;
  - `calibrate.py --collect-label`.
- `uv run pytest -q`, `uv run pytest tests/parity -q`, `uv run ruff check .`.
- Before renting: a local live smoke test (`tests/live`) on one gemma and one qwen3.8 profile, with uncalibrated
  `blurb_header` (T = 1), to check that the stack starts and both passes run.

## Out of scope

- JevBench and holdout runs for the new settings.
- A latency threshold: the owner judges the A/B numbers.
- Any orders for qwen3.6 other than `identity`.
- Refits at `prefix_block` 784.
