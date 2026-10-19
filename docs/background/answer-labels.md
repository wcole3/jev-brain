# Answer labels

Which token the model answers with. Today the gateway shows options as `(A) text` and reads the letter after
`Answer: (` ([decision-readout.md §2](decision-readout.md#2-label-tables-which-token-means-a)). Round 3 (DS-042,
2026-10-18/19) screened eight other label sets against those letters on gemma-4-31b and qwen3.8-27b, text and image.
Design: [the spec](../superpowers/specs/2026-10-17-orders-and-labels-design.md). This doc reports; the owner's
decision is added after the pick.

## Short answer

- **No set beats letters on accuracy or on the image index.** No Δ accuracy or Δ index CI lies above 0 on either
  model.
- **Two sets collapse.**
  - `symbols`: text −5.8 points (gemma) and −7.9 (qwen3.8); image index −10.5 and −39.6.
  - `unused` (gemma only): text −10.2 points, image index −25.7.
- **Shuffled letters cost image index on gemma.**
  - gemma: −2.6 [−4.2, −1.0] (`shuffled`) and −2.2 [−3.9, −0.6] (`shuffled-q`).
  - qwen3.8: −1.4 and −1.7, CIs include 0.
  - On text both are within 0.6 points of letters.
- **`digits` costs gemma −1.8 image index [−3.2, −0.5].** It is level on text.
- **Calibration moves both ways.**
  - `spaced` and `content` lower gemma's text ECE by about 0.011 (CIs below 0).
  - On qwen3.8 `spaced` raises text ECE by 0.017, and `content` by 0.026 on all questions. On `content`'s pure subset
    it is −0.016, CI includes 0.
- **Every set needs a fallback past its size.** A question with more options than the set holds is shown with
  today's letters: 5.6% of text questions for the 26-label sets, 5.2% for `symbols`, 17.9% for `digits`, and
  21.0% for `content` (which also falls back on shared first tokens). Results are given on all questions and on the
  pure subset.

## 1. The sets

Each set is an experiment layout `prompts/experiments/labels-<set>.toml`. It keeps the `header` wording except the
option line, the answer slot and the `labels` key. The gateway never loads these files.

| Set | Option line | Answer slot | Token read | Size, then fallback |
|---|---|---|---|---|
| `letters` (control) | `(A) text` | `Answer: (` | `A` | 255, today's table |
| `lower` | `(a) text` | `Answer: (` | `a` | 26 |
| `spaced` | `A) text` | `Answer:` | ` A` | 26 |
| `digits` | `(1) text` | `Answer: (` | `1` | 9 (1–9) |
| `symbols` | `' text` | `Answer:` | ` '` | 32 ASCII symbols, `'` first, the rest in a fixed seeded order |
| `unused` (gemma) | `<unused0> text` | `Answer:` | `<unused0>` | 255 |
| `content` | `- text` | `Answer:` | first token of ` text` | per question |
| `shuffled` | `(F) text` | `Answer: (` | `F` | 26: A–Z in one fixed seeded order, `FNSRPCAEVBZMKIHYXGJQOUDWTL` |
| `shuffled-q` | `(K) text` | `Answer: (` | `K` | 26: A–Z permuted per question |

**Token checks.**

- Single tokens on both tokenizers:
  - lowercase letters and digits after `(`;
  - space-prefixed capitals and all 32 ASCII symbols after `Answer:`.
- Most symbols merge with `(` (only `]` and `}` stay single), so `symbols` uses the spaced slot.
- Gemma has 6,227 `<unusedN>` tokens (`<unused0>`–`<unused6226>`); qwen3.8's tokenizer has none.
- Building a set's table fails if any of its labels is not one token right after the slot. That check covers every
  label a question can use, not only the first 10.
- The fallback letters are today's letters that stay one token in the set's slot. That is all 255 after `Answer: (`,
  but only 250 (gemma) or 249 (qwen3.8) after a bare `Answer:`. So a 255-option question is unsupported for
  `spaced`, `symbols` and `content`. That hits 15 calib-600 rows, so those sets fit T on 585 calib questions.

## 2. Mechanics

- **Layout keys.**
  - `labels` names the set (default `letters`); served layouts omit it, so their hashes and label tables are
    unchanged.
  - `answer_label` (default `{label}`) is the text read after the answer slot: `" {label}"` for the spaced sets.
- **Per question** ([`question_labels`](../../gateway/labels.py)):
  - A question gets its set's labels when its options fit; otherwise today's letters, tagged `fallback`.
  - `content` reads each option's own first token in context. It falls back when an option text is empty, merges with
    the slot, shares a first token with another option, or starts with a whitespace-only token (gemma reads `" "`
    before a digit) (ruling R4).
  - `unused` shows a fallback as `A text` after a bare `Answer:`, so that letter is read spaced (R4).
  - `shuffled-q` permutes A–Z with a seed built from the question's sorted option texts. Each option takes its
    letter by its text's rank, so it keeps the same letter in the identity and the reversed read (ruling R9).
- **Subsets.** *all* = every question both arms answered. *pure* = the questions the set run showed with its own
  labels.
- **Collects.** Per model and set, identity + reversed reads on three splits:
  - text calib-600: 600 calib rows, seeded per family (`data/splits/calib-600.json`);
  - text index-dev-2k: 2,000 index-dev rows, every k-th whole group; 3,728 questions (`data/splits/index-dev-2k.json`);
  - image dev: 1,462 rows.
  - `collect.py --layout-file F --label S` and `vision_collect.py --layout-file F --label labels-S` read an experiment
    layout with the gateway's own row code.
- **Fits (ruling R2).** T per type on each arm's calib-600 identity reads (`mean-prob`, b = 0). Image rows use the
  choice T. The letters arm is refitted the same way, so its T (gemma 4.092, qwen3.8 1.491) is not the shipped file's.
- **Screen.** [`label_screen.py`](../../scripts/label_screen.py) `screen` pairs each set with letters on the same
  questions and reports:
  - accuracy, ECE and NLL with a paired bootstrap (text);
  - the dev index with `vision_compare` (image);
  - fallback share, identity-vs-reversed flip rate, and predicted vs gold position histograms.
- **Pipeline check.** `label_screen.py check` runs `letters` through the experiment path on 200 seeded rows per split.
  It compares the identity top answer with the existing collects and requires ≥ 0.98:

  | Profile | calib-600 | index-dev-2k | image dev | Run |
  |---|---|---|---|---|
  | gemma-4-31b | 0.985 | 0.997 | 0.985 | [check](../results/archive/2026-10-18T154855Z-r3-labels-check-gemma-4-31b/summary.md) |
  | qwen3.8-27b | 1.000 | 0.997 | 0.995 | [check](../results/archive/2026-10-18T212640Z-r3-labels-check-qwen3.8-27b/summary.md) |

  gemma's 3 calib-600 disagreements are status mismatches. The control collect ran at the old max_len 32,768, so 10
  entity-alignment rows (~39k tokens) were unsupported then and are fine at today's 65,536. That is not a pipeline
  difference (ruling R8). The 26-label, `digits` and `unused` set fits on gemma include those 10 rows; the letters fit
  does not (590 vs 600 calib questions). The 10 rows are also among the 15 unsupported 255-option rows, so `spaced`,
  `symbols` and `content` fit on 585. On qwen3.8 every collect, control and set, ran at the profile's max_len 32,768,
  so the same 10 rows are unsupported in both arms (590; 585 for the spaced-slot sets).

## 3. The `unused` embedding check

Before spending GPU time on `<unusedN>` labels, a CPU check read their embedding rows from gemma's safetensors. Near
zero or near identical rows would have dropped the set
([result](../results/archive/2026-10-18T013307Z-r3-unused-embeddings/summary.md)):

| Group | Rows | Norm min | Norm median | Norm max | Mean pairwise cosine |
|---|---|---|---|---|---|
| `<unused0>`–`<unused254>` | 255 | 0.9561 | 0.9601 | 1.283 | 0.6031 |
| ordinary tokens (seeded) | 2,000 | 0.8886 | 1.119 | 1.58 | 0.0415 |

The rows are neither zero nor identical, so the set stayed in the screen (ruling R5). They are far more alike than
ordinary tokens (cosine 0.603 vs 0.042), which fits the screen's collapse.

## 4. Text results (index-dev-2k)

Δ is set − letters on the same questions, with a 95% paired-bootstrap CI; accuracy in points. The letters row shows
absolute values. The questions are 3,690 choice and 38 noul. Flip rate is the share of questions whose top answer
changes between the identity and the reversed read (noul left out).

**gemma-4-31b:**

| set | fallback | T choice | Δ accuracy, all | Δ accuracy, pure (n) | Δ ECE, all | Δ ECE, pure | Δ NLL, all | flip rate |
|---|---|---|---|---|---|---|---|---|
| letters | — | 4.092 | 80.2 (3,728) | — | 0.125 | — | 0.808 | 0.074 |
| lower | 0.056 | 3.862 | -0.3 [-0.6, +0.0] | -0.3 [-0.6, +0.0] (3,521) | +0.007 [+0.004, +0.010] | +0.005 [+0.002, +0.008] | -0.002 [-0.011, +0.006] | 0.076 |
| spaced | 0.056 | 4.086 | -0.2 [-0.5, +0.2] | -0.1 [-0.5, +0.2] (3,521) | -0.011 [-0.015, -0.006] | -0.010 [-0.015, -0.006] | -0.034 [-0.046, -0.023] | 0.076 |
| digits | 0.179 | 3.876 | -0.1 [-0.4, +0.2] | -0.1 [-0.4, +0.2] (3,061) | -0.002 [-0.006, +0.002] | -0.006 [-0.009, -0.003] | -0.003 [-0.011, +0.005] | 0.073 |
| symbols | 0.052 | 3.834 | -5.8 [-6.8, -4.9] | -6.0 [-7.0, -5.1] (3,536) | -0.015 [-0.025, -0.006] | -0.015 [-0.025, -0.006] | +0.009 [-0.021, +0.038] | 0.180 |
| unused | 0.000 | 2.563 | -10.2 [-11.5, -8.8] | same questions | -0.033 [-0.045, -0.020] | same | +0.198 [+0.149, +0.243] | 0.347 |
| content | 0.210 | 3.971 | +0.0 [-0.4, +0.5] | +0.2 [-0.3, +0.7] (2,944) | -0.011 [-0.016, -0.005] | -0.010 [-0.015, -0.003] | -0.004 [-0.018, +0.008] | 0.071 |
| shuffled | 0.056 | 3.910 | +0.0 [-0.5, +0.5] | +0.1 [-0.4, +0.6] (3,521) | +0.001 [-0.004, +0.006] | -0.001 [-0.006, +0.004] | +0.014 [-0.001, +0.027] | 0.072 |
| shuffled-q | 0.056 | 3.940 | -0.3 [-0.7, +0.2] | -0.2 [-0.7, +0.3] (3,521) | -0.001 [-0.006, +0.004] | -0.002 [-0.007, +0.003] | -0.010 [-0.025, +0.005] | 0.072 |

**qwen3.8-27b:**

| set | fallback | T choice | Δ accuracy, all | Δ accuracy, pure (n) | Δ ECE, all | Δ ECE, pure | Δ NLL, all | flip rate |
|---|---|---|---|---|---|---|---|---|
| letters | — | 1.491 | 78.2 (3,728) | — | 0.021 | — | 0.735 | 0.096 |
| lower | 0.056 | 1.490 | +0.1 [-0.3, +0.5] | +0.0 [-0.4, +0.4] (3,521) | +0.003 [-0.007, +0.009] | +0.003 [-0.006, +0.010] | -0.005 [-0.011, +0.000] | 0.104 |
| spaced | 0.056 | 1.305 | +0.1 [-0.4, +0.5] | +0.1 [-0.4, +0.5] (3,521) | +0.017 [+0.003, +0.022] | +0.018 [+0.005, +0.024] | +0.033 [+0.024, +0.041] | 0.117 |
| digits | 0.179 | 1.531 | +0.0 [-0.5, +0.5] | -0.1 [-0.7, +0.5] (3,061) | -0.001 [-0.011, +0.007] | +0.004 [-0.003, +0.011] | -0.004 [-0.010, +0.002] | 0.111 |
| symbols | 0.052 | 1.119 | -7.9 [-9.2, -6.6] | -8.3 [-9.7, -7.0] (3,536) | +0.062 [+0.042, +0.069] | +0.061 [+0.043, +0.069] | +0.264 [+0.234, +0.294] | 0.365 |
| content | 0.210 | 1.352 | -0.1 [-0.6, +0.5] | -0.0 [-0.6, +0.5] (2,944) | +0.026 [+0.010, +0.031] | -0.016 [-0.024, +0.004] | +0.026 [+0.016, +0.036] | 0.100 |
| shuffled | 0.056 | 1.440 | -0.5 [-1.0, +0.2] | -0.6 [-1.2, +0.0] (3,521) | +0.004 [-0.009, +0.012] | +0.003 [-0.008, +0.012] | +0.025 [+0.015, +0.035] | 0.106 |
| shuffled-q | 0.056 | 1.457 | -0.4 [-1.0, +0.2] | -0.5 [-1.1, +0.1] (3,521) | +0.013 [-0.002, +0.017] | +0.013 [-0.001, +0.019] | +0.014 [+0.004, +0.024] | 0.111 |

- **Where the fallback falls.** The 26-label sets fall back only on 27+ options (all of them). `digits` also falls
  back on 91% of 6–26-option questions. `content` falls back on 7% of 2-option, 10% of 3–5 and 68% of 6–26-option
  questions. So the pure subsets of `digits` and `content` are easier (letters accuracy 87.8% and 88.0% on gemma).
- **Flip rate.** `symbols` and `unused` more than double the identity-vs-reversed flip rate. Every other set stays
  within 0.021 of letters.
- Per type, per option count and the position histograms are in each run: gemma
  [lower](../results/archive/2026-10-18T163801Z-r3-labels-lower-gemma-4-31b/summary.md),
  [spaced](../results/archive/2026-10-18T171503Z-r3-labels-spaced-gemma-4-31b/summary.md),
  [digits](../results/archive/2026-10-18T180457Z-r3-labels-digits-gemma-4-31b/summary.md),
  [symbols](../results/archive/2026-10-18T184322Z-r3-labels-symbols-gemma-4-31b/summary.md),
  [unused](../results/archive/2026-10-18T201608Z-r3-labels-unused-gemma-4-31b/summary.md),
  [content](../results/archive/2026-10-18T192436Z-r3-labels-content-gemma-4-31b/summary.md),
  [shuffled](../results/archive/2026-10-19T015333Z-r3-labels-shuffled-gemma-4-31b/summary.md),
  [shuffled-q](../results/archive/2026-10-19T024433Z-r3-labels-shuffled-q-gemma-4-31b/summary.md); qwen3.8
  [lower](../results/archive/2026-10-18T220610Z-r3-labels-lower-qwen3.8-27b/summary.md),
  [spaced](../results/archive/2026-10-18T224632Z-r3-labels-spaced-qwen3.8-27b/summary.md),
  [digits](../results/archive/2026-10-18T232927Z-r3-labels-digits-qwen3.8-27b/summary.md),
  [symbols](../results/archive/2026-10-19T001012Z-r3-labels-symbols-qwen3.8-27b/summary.md),
  [content](../results/archive/2026-10-19T004859Z-r3-labels-content-qwen3.8-27b/summary.md),
  [shuffled](../results/archive/2026-10-19T034257Z-r3-labels-shuffled-qwen3.8-27b/summary.md),
  [shuffled-q](../results/archive/2026-10-19T042017Z-r3-labels-shuffled-q-qwen3.8-27b/summary.md).

## 5. Image results (dev)

1,462 rows, Δ index against letters with `vision_compare`'s paired group bootstrap (10,000 resamples, seed 0). Image
dev has no question over 10 options, so only `digits` falls back (6.5% of rows). For every other set, pure and all
are the same rows. The letters row's ECE (0.0861 gemma, 0.0376 qwen3.8) uses the calib-600 refit T, not the shipped
one.

**gemma-4-31b:**

| set | index | Δ index, all [95% CI] | Δ index, pure [95% CI] | accuracy | ECE | NLL | agreement | flip rate |
|---|---|---|---|---|---|---|---|---|
| letters | 77.06 | — | — | 80.0 | 0.0861 | 0.6166 | — | 0.124 |
| lower | 76.47 | -0.59 [-1.44, +0.19] | same rows | 79.9 | 0.0858 | 0.6120 | 0.977 | 0.118 |
| spaced | 76.13 | -0.93 [-2.10, +0.19] | same rows | 79.7 | 0.0677 | 0.6097 | 0.954 | 0.140 |
| digits | 75.26 | -1.80 [-3.16, -0.47] | -1.76 [-3.19, -0.40] (1,367) | 78.9 | 0.0882 | 0.6246 | 0.956 | 0.114 |
| symbols | 66.59 | -10.47 [-12.77, -7.86] | same rows | 74.2 | 0.0482 | 0.7006 | 0.834 | 0.220 |
| unused | 51.40 | -25.66 [-28.89, -22.38] | same rows | 61.8 | 0.1442 | 1.0769 | 0.695 | 0.501 |
| content | 76.54 | -0.52 [-1.72, +0.63] | same rows | 79.8 | 0.0723 | 0.6287 | 0.951 | 0.104 |
| shuffled | 74.49 | -2.57 [-4.17, -1.04] | same rows | 77.9 | 0.0931 | 0.6727 | 0.921 | 0.122 |
| shuffled-q | 74.85 | -2.21 [-3.87, -0.59] | same rows | 78.7 | 0.0898 | 0.6496 | 0.915 | 0.124 |

**qwen3.8-27b:**

| set | index | Δ index, all [95% CI] | Δ index, pure [95% CI] | accuracy | ECE | NLL | agreement | flip rate |
|---|---|---|---|---|---|---|---|---|
| letters | 73.31 | — | — | 76.9 | 0.0376 | 0.6008 | — | 0.202 |
| lower | 73.16 | -0.15 [-1.52, +1.20] | same rows | 76.5 | 0.0402 | 0.6105 | 0.946 | 0.178 |
| spaced | 72.76 | -0.54 [-2.10, +1.05] | same rows | 76.5 | 0.0283 | 0.6158 | 0.906 | 0.240 |
| digits | 73.16 | -0.15 [-1.79, +1.50] | -0.38 [-2.02, +1.32] (1,367) | 76.5 | 0.0546 | 0.6314 | 0.926 | 0.185 |
| symbols | 33.75 | -39.56 [-44.04, -34.95] | same rows | 52.3 | 0.2313 | 1.4962 | 0.534 | 0.648 |
| content | 72.63 | -0.68 [-2.51, +1.15] | same rows | 76.7 | 0.0256 | 0.6262 | 0.891 | 0.159 |
| shuffled | 71.88 | -1.42 [-3.63, +0.71] | same rows | 75.4 | 0.0508 | 0.6402 | 0.855 | 0.170 |
| shuffled-q | 71.62 | -1.69 [-3.82, +0.40] | same rows | 75.7 | 0.0388 | 0.6479 | 0.866 | 0.170 |

- **Agreement** is the share of rows with the same top answer as letters. Away from the two collapsed sets it runs
  from 0.977 (`lower`, gemma) down to 0.855 (`shuffled`, qwen3.8).
- **Shuffled letters.** Both sets read the same letter tokens as `letters`; the gemma image cost comes with showing
  them out of alphabetical order, which also moves each letter to another slot. It is one fixed permutation
  (`shuffled`) and one CI among many unadjusted ones.
- Each run dir holds the image `summary.md` with per-benchmark Δ skill under `*-compare-all/` and `*-compare-pure/`:
  gemma
  [lower](../results/vision-experiments/2026-10-18T163801Z-r3-labels-lower-gemma-4-31b/summary.md),
  [spaced](../results/vision-experiments/2026-10-18T171503Z-r3-labels-spaced-gemma-4-31b/summary.md),
  [digits](../results/vision-experiments/2026-10-18T180457Z-r3-labels-digits-gemma-4-31b/summary.md),
  [symbols](../results/vision-experiments/2026-10-18T184322Z-r3-labels-symbols-gemma-4-31b/summary.md),
  [unused](../results/vision-experiments/2026-10-18T201608Z-r3-labels-unused-gemma-4-31b/summary.md),
  [content](../results/vision-experiments/2026-10-18T192436Z-r3-labels-content-gemma-4-31b/summary.md),
  [shuffled](../results/vision-experiments/2026-10-19T015333Z-r3-labels-shuffled-gemma-4-31b/summary.md),
  [shuffled-q](../results/vision-experiments/2026-10-19T024433Z-r3-labels-shuffled-q-gemma-4-31b/summary.md); qwen3.8
  [lower](../results/vision-experiments/2026-10-18T220610Z-r3-labels-lower-qwen3.8-27b/summary.md),
  [spaced](../results/vision-experiments/2026-10-18T224632Z-r3-labels-spaced-qwen3.8-27b/summary.md),
  [digits](../results/vision-experiments/2026-10-18T232927Z-r3-labels-digits-qwen3.8-27b/summary.md),
  [symbols](../results/vision-experiments/2026-10-19T001012Z-r3-labels-symbols-qwen3.8-27b/summary.md),
  [content](../results/vision-experiments/2026-10-19T004859Z-r3-labels-content-qwen3.8-27b/summary.md),
  [shuffled](../results/vision-experiments/2026-10-19T034257Z-r3-labels-shuffled-qwen3.8-27b/summary.md),
  [shuffled-q](../results/vision-experiments/2026-10-19T042017Z-r3-labels-shuffled-q-qwen3.8-27b/summary.md).

## Caveats

- **A screen, not a confirm.** Text is 3,728 index-dev questions, not the full splits. The spec's confirm step (full
  calib, eval and index-dev collects for a picked set) has not run.
- **Many comparisons.** 15 sets × 2 subsets × text and image; the CIs are unadjusted.
- **Pure subsets differ per set.** `digits` and `content` drop their hard many-option questions from pure, so a pure Δ
  is not comparable across sets; compare each set with letters on its own rows.
- **Small type cells.** index-dev-2k has 38 noul and no score questions, so the screen speaks for choice.
- **Fits.** Each arm is refitted on calib-600 (600 rows), so ECE differences include fit noise. `unused`'s much
  lower choice T (2.563 vs 4.092) is part of its result.
- **Image rows reuse the text choice T.** Nothing was fitted on image rows.
- **One permutation for `shuffled`.** Another seed could cost more or less; `shuffled-q` averages over permutations
  only across questions.
- **bf16 noise.** Collects of the same config agree on 98.5–100% of top answers (§2).

## Sources

- Our code: [`labels.py`](../../gateway/labels.py), [`layouts.py`](../../gateway/layouts.py),
  [`prompts.py`](../../gateway/prompts.py), [`experiment_layouts.py`](../../scripts/experiment_layouts.py),
  [`collect.py`](../../scripts/collect.py), [`vision_collect.py`](../../scripts/vision_collect.py),
  [`label_screen.py`](../../scripts/label_screen.py), [`index_dev_2k.py`](../../scripts/index_dev_2k.py),
  `prompts/experiments/labels-*.toml`.
- Related: [decision-readout.md](decision-readout.md) (label tables, piecewise tokens),
  [option-ordering.md](option-ordering.md) (position and letter bias, PriDe),
  [calibration.md](calibration.md) (T and ECE).
- Zheng et al., Large Language Models Are Not Robust Multiple Choice Selectors (letter-ID prior): https://arxiv.org/abs/2309.03882
