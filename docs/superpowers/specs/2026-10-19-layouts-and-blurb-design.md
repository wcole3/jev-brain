# decider_chat orders and an intro blurb, round 4 (text and image)

Date: 2026-10-19. Status: draft for owner review. Models: gemma-4-31b and qwen3.8-27b.
Background: [option-ordering.md](../../background/option-ordering.md) (round 3 order grid),
[prompt-layouts.md](../../background/prompt-layouts.md) (the three layouts),
[answer-labels.md](../../background/answer-labels.md) (round 3 screens),
[2026-10-17-orders-and-labels-design.md](2026-10-17-orders-and-labels-design.md) (round 3 spec, whose tools this reuses).

## Goal

Two questions, on text and image decisions, for both models:

1. **decider_chat under the order grid.** Round 3 ran its order rules on `header` only. Score the same rules on
   `decider_chat`, and collect `decider_chat` on images for the first time.
2. **An intro blurb.** Does one sentence before the prompt, telling the model what is coming, change accuracy or
   calibration, on `header` and on `decider_chat`?

The harness reports; the owner picks. Nothing ships without the owner's pick and the usual live latency, holdout,
JevBench and Index checks.

Done when:

- the round 3 text grid has a `decider_chat` table for both models (stage 1);
- every screen pair below has text and image tables for both models (stage 2);
- every blurb arm that survives the screen has a text and image order grid (stage 3);
- the owner has picked, or kept the defaults.

## Constraints

- Never train, calibrate or tune on Jev API outputs. Dev splits only; never vision holdout rows.
- Served layouts (`prompts/*.toml`) and their label tables stay byte-identical; blurb layouts live in
  `prompts/experiments/`.
- GPU chunks over 10 minutes need the owner's ok; each stage below asks once. Local runs at the owner's power limit
  (510 W). Between collect sets the box cools: at least 10 minutes idle and the GPU at or below 50 °C, whichever is
  later.
- No label, image-budget or thinking changes; letters only.
- Commits stay local; the owner pushes.

## Arms

| Arm | Layout | Blurb | Collect label |
|---|---|---|---|
| H | `header` | no | `letters` (round 3's fresh collects, reused) |
| D | `decider_chat` | no | `decider` (new) |
| HB | `header` | yes | `blurb-header` (new) |
| DB | `decider_chat` | yes | `blurb-decider` (new) |

**Blurb wording**, identical on both layouts so it is one factor:

```
You will be asked questions about the following context. Answer each with the letter of the best option.

```

It goes before the layout's first part: before `Questions that will be asked about the context:` on `header`, before
`Context:` on `decider_chat`. `prompts/experiments/blurb-header.toml` and `blurb-decider.toml` copy their served
layout and prefix the first part's template with the blurb. Nothing else changes, so no gateway code changes.

The blurb sits in the shared prefix, so it adds about 25 prefill tokens per request and none per question. On qwen
the 800-token prefix pad absorbs it for short states.

## Stage 1: decider_chat text grid (CPU)

- **Data:** the existing full-order collects `.cache/collect/{profile}/{calib,index-dev,eval}.jsonl.gz`. Each holds
  `decider_chat` records with every order the grid reads, beside the `header` records round 3 used.
- **Change:** `scripts/r3_orders.py --layout {header,decider_chat}` (default `header`, today's output unchanged).
- **Calibration:** as round 3. Each arm fits T on calib; gates use the shipped T from
  `data/<profile>/decider_chat/calibration.json`, stamp-checked against the collect.
- **Output:** `docs/results/archive/<UTC>-r4-orders-text-decider_chat-<profile>/`, the same tables as round 3's
  `header` run.

## Stage 2: screen (GPU, about 2.5 h per model with cool-downs)

### Collects

Per model, identity+reversed:

| Arm | Text calib-600 and index-dev-2k | Image dev |
|---|---|---|
| D | `collect.py --layouts decider_chat --label decider` | `vision_collect.py --layout decider_chat --label r4-decider` |
| HB | `collect.py --layout-file prompts/experiments/blurb-header.toml --label blurb-header` | `--layout-file … --label r4-blurb-header` |
| DB | `collect.py --layout-file prompts/experiments/blurb-decider.toml --label blurb-decider` | `--layout-file … --label r4-blurb-decider` |

D also gets an image `--orders cyclic:4` collect (`r4-decider-cyclic4`) so the image grid can run on `decider_chat`.

### Pairs

| Pair | Effect measured |
|---|---|
| HB vs H | blurb on `header` |
| DB vs D | blurb on `decider_chat` |
| D vs H | layout without blurb |
| DB vs HB | layout with blurb |

Each pair is paired on the same rows. T is fitted per type on each arm's calib-600 identity reads (mean-prob, b = 0).

### Metrics

As round 3's label screen: text accuracy and Decision Index skill on index-dev-2k (M3's paired bootstrap), image dev
index (`vision_compare`, paired group bootstrap, 10k, seed 0), ECE and NLL, reversed-order flip rate, and mean input
tokens per row. There is no pure/all split and no fallback share: every arm uses letters.

### Mechanics

`scripts/label_screen.py screen` today compares one label set against `letters`. It becomes
`screen --arm LABEL --control LABEL`, with today's `--set S` kept as shorthand for `--arm S --control letters`.
`header` arms read `letters` reads for H, and both arms of a pair must share profile, split rows and env.

As built ([plan](../plans/2026-10-19-layouts-and-blurb.md), "Ruling against the spec"): pairs live in
`scripts/layout_screen.py --arm A --control C`, and `label_screen.py screen` is unchanged, because round 3's
screen reads its control from the old full collects while H is the fresh `letters` collects.

## Stage 3: order grid on survivors (GPU, about 80 min per arm per model)

- **Survivor rule:** a blurb arm (HB or DB) runs the grid unless its screen shows it significantly worse than its
  control on text accuracy or image index (95% CI entirely below 0). The owner may override either way.
- **Text collects:** `--orders all` on calib-600 and index-dev-2k, labels `blurb-header-all` / `blurb-decider-all`
  (about 70 min per arm per model).
- **Text grid on collect files:** `r3_orders.py` gains `--calib FILE --dev FILE` (and `--layout-file` for an
  experiment layout). It fits on calib-600 and scores index-dev-2k only. Experiment layouts have no shipped
  calibration, so in this mode gates use the arm's own identity T fitted on calib-600.
- **Like-for-like control:** H and D are rerun in the same mode, on the old full-order collects restricted to the
  calib-600 and index-dev-2k rows (all 600 and 1,994 rows are present there). The blurb's effect on the grid is the
  difference between these runs, not a comparison with stage 1.
- **Image:** one `--orders cyclic:4` dev collect per surviving arm (about 8 min), merged with its stage 2 collect by
  `vision_orders.py` and scored with that arm's text fit.

## GPU budget

| Item | Estimate |
|---|---|
| Stage 2, both models (D, HB, DB, D cyclic:4) | ~5 h with cool-downs |
| Stage 3, up to 2 arms × 2 models | up to ~5.5 h with cool-downs |

## Outputs

- Results: `docs/results/archive/<UTC>-r4-*` (text) and `docs/results/vision-experiments/<UTC>-r4-*` (image).
- Docs:
  - `prompt-layouts.md`: a blurb section and the `decider_chat` image numbers;
  - `option-ordering.md`: the `decider_chat` grid and the blurb grids beside round 3's `header` grid;
  - fix `prompt-layouts.md`'s stale "only qwen3.6 is calibrated" line (both models have `decider_chat` and `header`
    calibration files).
- Ticket: one DoStuff ticket for the round.

## Testing

- Each blurb layout loads, and differs from its served layout only by the blurb prefix on the first part (all
  other fields equal).
- For one hand-made request, a blurb layout's built ids after its first part equal the served layout's, and its first
  part decodes to the blurb plus the served first part.
- `r3_orders.py --layout decider_chat` reads only `decider_chat` records; `--layout header` output is byte-identical
  to today's on a fixture.
- `r3_orders.py --calib/--dev` mode: gates use the identity fit; a row-restricted control reads only the given rows.
- `layout_screen.py --arm/--control` (built in place of `label_screen.py screen --arm/--control`, see Mechanics):
  pairs on shared rows only; `label_screen.py screen --set S` output is unchanged.

## Caveats carried from round 3

- Image options carry their own letter keys (`(A) A: 1`). All arms here use letters, so the clash with non-letter
  labels does not apply, but reversed image reads still show `(A) D: 2`.
- Many arms, uncorrected intervals: tables give the arm count beside each result.

## Out of scope

- Blurb wording variants beyond the one above; a system-message blurb.
- `question_first`.
- Changing a served layout, label table or `OPTION_ORDERS` before the owner picks.
