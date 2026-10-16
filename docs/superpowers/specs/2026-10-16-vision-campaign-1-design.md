# Vision experiment campaign, round 1 (DS-035, DS-036, DS-037)

Date: 2026-10-16. Status: approved in brainstorming, pending spec review.
Tickets: DS-035 (prompt and layout), DS-036 (image budget and calibration), DS-037 (latency).
Builds on: the DS-034 harness ([vision-experiments.md](../../background/vision-experiments.md)) and its
dev baselines (`docs/results/vision-experiments/*-ds034-*-baseline`).

## Goal

Find image-decision changes that raise the board index or cut latency on gemma-4-31b and qwen3.8-27b, and
give the owner tables to pick from. Nothing ships without the owner's pick, one logged holdout confirmation,
and a JevBench check that text answers did not move.

Done when:

- the 3 × 2 × 2 grid is collected on dev for both models, with factorial tables (main effects, two-way
  interactions, per-benchmark effects, ECE, latency per budget level);
- `T_image` is fitted on a non-suite image calibration set for both models and its ECE is measured on dev;
- E5 (cyclic orders × PriDe) and E6 (latency probes) have results;
- the owner has picked per model, and the picks are confirmed once on the holdout.

## Baselines (DS-034, dev, 510 W)

| | gemma-4-31b | qwen3.8-27b |
|---|---|---|
| index (text arm, identity) | 77.06 | 73.31 |
| ECE text → fit-T | 0.081 → 0.043 | 0.042 → 0.026 |
| latency p50 / p80 | 328 / 389 ms | 389 / 606 ms |
| minimum detectable Δindex (80% power, d = 8%) | ≈ 3.5 | ≈ 3.5 |

## Experiments

| ID | Ticket | Question | Design |
|---|---|---|---|
| E1 | 036 | Does one image temperature calibrate image rows better than the text T? | `T_image` fitted on the non-suite calibration set; ECE on dev |
| E2–E4 | 035/036 | Do image budget, image placement and wording change accuracy? | 3 × 2 × 2 factorial on dev (below) |
| E5 | 035 | Does a letter prior help once gold-position skew is removed? | One cyclic-orders collect per model at base; `pride` vs `fit-T` offline |
| E6 | 037 | Where does image-request latency go? | Probes: row-first warm-up arm; per-row resend cost; uuid-only reuse check |

E7 (Hateful Memes OCR or definitions) is deferred: benchmark-specific, highest overfit risk.

### Factorial grid (E2–E4)

| Factor | gemma-4-31b | qwen3.8-27b |
|---|---|---|
| Image budget | `max_soft_tokens` 280 / **560** / 1120 | `max_pixels` 0.4 / 0.8 / **1.64** MP (1.64 MP is also the gateway cap) |
| Placement | **images in `Context:` after the question list** / images before the question list | same |
| Wording | **none** / `Image N:` before each image + "Answer from the image(s)." in the question block | same |

Bold is today's config. 12 configs per model, each one dev collect with `identity+reversed` orders; option
orders and calibration are offline factors on top. Under identity orders T never changes the top answer, so
index comparisons do not depend on the calibration arm; ECE uses cross-fitted `fit-T`.

## 1. Code and data (no GPU)

1. **Experiment layouts outside `prompts/`.** The gateway loads every `prompts/*.toml` at startup and refuses
   a layout without label tables and calibration for all profiles. Experiment layouts live in
   `prompts/experiments/*.toml`, which the gateway does not load. `vision_collect.py --layout-file PATH`
   loads one, builds and checks its label table in memory (the `build_labels.py` single-token check), and
   stamps the layout and label hashes. The `text` arm is unavailable for these layouts; `fit-T` and index
   comparisons are not affected.
2. **Optional layout key `image_label`** (for example `"Image {n}:\n"`, `{n}` from 1): `image_context` writes
   it before each image. Layouts without the key are unchanged (same file hash, same ids).
3. **Three layouts:** `header-imgfirst` (order context, questions, question, options); `header-worded`
   (`image_label` and the instruction line); `header-imgfirst-worded` (both).
4. **`scripts/vision_factorial.py`:** reads the 12 scored configs with factor labels; reports main effects and
   two-way interactions on the index with a paired group bootstrap (one resample shared by all configs),
   per-benchmark main effects, ECE, mean input tokens, and latency per budget level. It reports; the owner
   picks.
5. **Image calibration set** (`scripts/vision_calib_set.py`): about 1,800 multiple-choice image questions from
   train splits outside the suite (ScienceQA-IMG, AI2D, A-OKVQA, about 600 each), in the suite row format.
   Rows whose image SHA-256 matches any suite image are dropped and counted (CV-Bench draws on COCO).
   `vision_collect.py --rows FILE` collects them. `T_image` is fitted on the whole set (no folds) and written
   to `data/<profile>/header/calibration.json` with its stamp; the gateway uses it for image rows when
   present.
6. **Latency probes:** `image_share_probe.py` gains a `row` arm; a resend probe times the gateway's per-row
   JSON encoding and vLLM's per-row image decode; a one-shot check of whether vLLM 0.30 accepts a
   `uuid`-only image part for an image it already cached.

## 2. Runs (GPU, local at 510 W)

Per model, for each budget level: restart vLLM with that `MM_PROCESSOR_KWARGS`, collect the four layouts on
dev, and run one 320-row single-client latency set on today's layout (the gateway serves only `prompts/`
layouts, so placement and wording get Δ input tokens, not latency). At base budget, also the cyclic collect,
the calibration-set collect and the E6 probes.

Estimate: 6 restarts, 24 grid collects, 2 cyclic collects, 2 calibration collects, 6 latency runs, probes:
about 5.3 h. Each chunk runs with the owner's ok (GPU over 10 minutes).

## 3. Decisions and shipping

- The owner picks per model from the factorial tables.
- Shipping paths: budget is a profile env change (image requests only); `T_image` is a calibration file plus a
  gateway change (image rows only); a placement or wording winner would need a gateway option to use another
  layout for image requests, designed only if a winner appears.
- Before shipping: one holdout confirmation of the picked config per model (logged), and a JevBench check that
  text answers did not move.
- E6 gateway changes (send an image once, uuid-only reuse) get their own design if the probes justify them.

## 4. Docs and results

- Results: `docs/results/vision-experiments/<UTC>-<label>/` per comparison; factorial tables per model.
- `docs/background/vision-experiments.md` gains a "Round 1 results" section; DS-035, DS-036, DS-037 get notes.

## Out of scope

- E7 (Hateful Memes OCR or definitions), token pruning, crop or zoom passes, thinking fallbacks.
- Shipping any change before the owner's pick and the holdout confirmation.
- DS-039 (submission), which follows the picks.
