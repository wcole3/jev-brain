# Vision Decisions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/v1/systemone` answers decisions about images on gemma-4-31b and qwen3.8-27b, with the text readout,
calibration and prompt sharing, and is scored on the Decision Index Vision suite.

**Architecture:** The request's images become an ordered `Context:` of text and images (`gateway/images.py`). A
per-model table gives each image's placeholder ids and the number of ids vLLM expands it to (`gateway/vision.py`).
`build_rows` writes the placeholders into the shared context and counts expanded tokens. Image rows are read one per
call through vLLM's `/inference/v1/generate`, which takes our token ids plus the images. Text requests take the
existing path unchanged.

**Tech Stack:** Python 3.12, FastAPI, httpx, Pillow (new), transformers (configs and tokenizers only), vLLM 0.30
(`--enable-scale-out`), the Decision Index kit at `.cache/decision-index-vision/` (f5a6e4f).

**Spec:** `docs/superpowers/specs/2026-10-15-vision-decisions-design.md`

## Global Constraints

- Image sources: `data:` URLs and raw base64 only. Any other string (`https://`, `http://`, `file:`, a path) is
  refused with 400. The gateway never fetches a URL.
- Limits: at most 4 images per request. Bodies over 20,000,000 bytes are refused with 400. Images over 1,638,400
  pixels are downscaled in the gateway, keeping the aspect ratio, with LANCZOS.
- Text-only requests must build byte-identical token ids: the golden files in `tests/unit/golden/` do not change.
- The `header` wording is unchanged. Images sit inside `Context:`.
- Calibration: reuse each profile's text T and b. Never fit on the vision suite, and never on Jev API outputs.
- Thinking stays off for decisions.
- Errors: a bad image, too many images, an oversized body, or images on a text-only profile give 400. An expanded
  prompt at or over `SYSTEMONE_MAX_LEN` gives 422 with the existing "maximum context length" text. A vLLM error
  behaves as it does for text (500).
- Code style: small focused files; comments at most two lines; names that explain.
- Commits: Conventional Commits in caveman style, subject ≤ 50 characters. Stage explicit paths only; never
  `git add -A`. End each commit with the attribution line from the session.
- GPU:
  - Check the power limit before every GPU run: 600 W for latency and evaluation runs
    (`nvidia-smi --query-gpu=power.limit --format=csv`). The owner sets it.
  - A GPU job over 10 minutes waits for the owner's ok, with an estimate.
- Shell:
  - Load keys with `set -a; . ./.env; set +a`; never print them.
  - The gateway is `G=http://127.0.0.1:${GATEWAY_PORT}`, and every script takes `--gateway $G`.
  - Never `pkill -f`.
- Ticket: after each task, record a one-line DS-024 progress note and the commit sha (`dostuff-tickets` skill).

## Review Focus

1. **Placeholder text.** A state or question that contains `<|image|>` (gemma) or `<|vision_start|>`/`<|image_pad|>`
   (qwen) in an image request is refused with 400. It never reaches vLLM with more placeholders than images.
   Test: Task 4.
2. **Decompression bombs.** An image whose header declares more pixels than Pillow's `Image.MAX_IMAGE_PIXELS` is
   refused with 400 before its pixels are decoded. Test: Task 2.
3. **Extreme aspect ratios.** On qwen, an image wider than 200:1 (the processor raises) is refused with 400 and the
   image is named. On gemma, the count is clamped to `max_soft_tokens`. Test: Task 3.
4. **Image modes on downscale.** RGBA PNG, palette PNG with transparency and CMYK JPEG all downscale to a decodable
   image, and alpha is kept for PNG. Test: Task 2.
5. **Many options.** An image question with more than 127 options splits its label ids across calls, so every
   label is read. Test: Task 5.

---

### Task 1: Image settings and vLLM flags

**Files:**
- Modify: `gateway/config.py`, `docker/vllm-entrypoint.sh`, `compose.yaml`, `pyproject.toml`, `uv.lock`
- Test: `tests/unit/test_config.py`, `tests/unit/test_entrypoint.py`

**Interfaces:**
- Produces:
  - `Settings.systemone_images: bool = False`, from `SYSTEMONE_IMAGES == "1"`;
  - `Settings.mm_processor_kwargs: dict = field(default_factory=dict)`, from `json.loads(MM_PROCESSOR_KWARGS or "{}")`.
  A bad value raises `ValueError` naming `MM_PROCESSOR_KWARGS`.
- The same two variables drive vLLM: `SYSTEMONE_IMAGES=1` adds `--enable-scale-out`, and a non-empty
  `MM_PROCESSOR_KWARGS` adds `--mm-processor-kwargs "$MM_PROCESSOR_KWARGS"`. One source for the gateway's
  expanded-length formulas and vLLM's processor.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_config.py
def test_image_settings_are_off_by_default():
    s = Settings.from_env(MINIMAL_ENV)
    assert s.systemone_images is False and s.mm_processor_kwargs == {}

def test_image_settings_from_env():
    s = Settings.from_env(MINIMAL_ENV | {"SYSTEMONE_IMAGES": "1", "MM_PROCESSOR_KWARGS": '{"max_soft_tokens":560}'})
    assert s.systemone_images is True and s.mm_processor_kwargs == {"max_soft_tokens": 560}

def test_bad_processor_kwargs_name_the_key():
    with pytest.raises(ValueError, match="MM_PROCESSOR_KWARGS"):
        Settings.from_env(MINIMAL_ENV | {"MM_PROCESSOR_KWARGS": "{"})

# tests/unit/test_entrypoint.py
def test_images_turn_on_scale_out_and_processor_kwargs(tmp_path):
    out = served_args(tmp_path, SYSTEMONE_IMAGES="1", MM_PROCESSOR_KWARGS='{"max_soft_tokens":560}')
    assert "--enable-scale-out" in out and '--mm-processor-kwargs {"max_soft_tokens":560}' in out

def test_text_profiles_get_no_scale_out(tmp_path):
    assert "--enable-scale-out" not in served_args(tmp_path) and "--mm-processor-kwargs" not in served_args(tmp_path)
```

`MINIMAL_ENV` is whatever the existing config tests use for a minimal profile; reuse it.

- [ ] **Step 2: Run the tests and see them fail.** Run
  `uv run pytest tests/unit/test_config.py tests/unit/test_entrypoint.py -q`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
  - Add the two settings.
  - Add the two `if` lines to the entrypoint, next to the `LANGUAGE_MODEL_ONLY` line.
  - Pass `SYSTEMONE_IMAGES: ${SYSTEMONE_IMAGES:-0}` and `MM_PROCESSOR_KWARGS: ${MM_PROCESSOR_KWARGS:-}` to both
    compose services.
  - Run `uv add pillow`.
- [ ] **Step 4: Run the tests and see them pass.** Run the same command, then `uv run pytest -q` and
  `uv run ruff check .`. Expected: all pass.
- [ ] **Step 5: Commit.** Stage the six files. Message: `feat(config): image settings for vision profiles`.

### Task 2: Parse request images into a context

**Files:**
- Create: `gateway/images.py`
- Modify: `gateway/schema.py`
- Test: `tests/unit/test_images.py`, `tests/unit/test_schema.py`

**Interfaces:**
- Produces:
  - `schema.ImageError(RequestError)`: refused with 400.
  - `SystemOneRequest.images: list[str] | None = None`.
  - `images.MAX_IMAGES = 4`, `MAX_PIXELS = 1_638_400`, `MAX_BODY_BYTES = 20_000_000`.
  - `@dataclass(frozen=True) class Image: data: bytes; mime: str; width: int; height: int; sha256: str`, with
    `def part(self) -> dict` returning
    `{"type": "image_url", "url": f"data:{mime};base64,{b64}", "uuid": sha256}`. vLLM uses `uuid` as the image's
    cache key.
  - `decode_image(source: Any, where: str) -> Image`. `where` names the item in errors, such as `images[0]` or
    `state[2].image`.
  - `context_items(state: Any, images: list[str] | None) -> list[str | Image]`.
- Rules for `context_items`:
  - **No images anywhere:** return `[render_state(state)]`, today's text exactly.
  - **Otherwise:** the top-level images come first, then the state.
  - **List state with image items:** an image item is a dict whose only key is `"image"`. The list is split per
    item: an image item becomes an `Image`, and any other item becomes `render_state(item)`.
  - **Any other state:** it stays one `render_state(state)` item.
  - **Empty state** (`None`, `""`, `{}`, `[]`): adds no text when there are images. The kit sends `state: {}`.
  - **More than `MAX_IMAGES` images:** `ImageError("at most 4 images per request")`.
- Rules for `decode_image`:
  - **Sources:** a `data:<mime>;base64,` URL or raw base64 (`b64decode(validate=True)`). Anything else is
    `ImageError(f"{where}: images must be data: URLs or base64; URLs are not fetched")`.
  - **Size check:** open with Pillow and read `size` before `load()`. A size over `PIL.Image.MAX_IMAGE_PIXELS` is
    `ImageError(f"{where}: image too large")`.
  - **Decode failures:** any decode error is `ImageError(f"{where}: not a decodable image")`.
  - **At or under `MAX_PIXELS`:** the bytes pass through unchanged.
  - **Over `MAX_PIXELS`:** resize with the kit's `fit()` rule (`decision_index/vision/images.py`). Pass LANCZOS.
    Save PNG as PNG (RGBA when the source has alpha or transparency, else RGB). Save everything else as JPEG,
    quality 95, RGB.
  - **Fields:** `mime` comes from `PIL.Image.MIME[format]`; `sha256` is of the final bytes.

- [ ] **Step 1: Write the failing tests.** Build the images in the tests with Pillow
  (`png(w, h, mode="RGB") -> bytes`, `b64(bytes) -> str`).

```python
def test_both_wire_formats_give_the_same_context():
    a = context_items("Pick", [b64(png(64, 32))])
    b = context_items([{"image": "data:image/png;base64," + b64(png(64, 32))}, "Pick"], None)
    assert [type(x) for x in a] == [Image, str] and a[1] == "Pick"
    assert a[0].sha256 == b[0].sha256 and b[1] == "Pick"

@pytest.mark.parametrize("state", ["x", {"a": 1}, [1, 2], [{"a": 1}] * 9, {}, None])
def test_text_only_context_is_todays_state(state):
    assert context_items(state, None) == [render_state(state)]

@pytest.mark.parametrize("state", [None, "", {}, []])
def test_empty_state_adds_no_text_next_to_images(state):
    assert [type(x) for x in context_items(state, [b64(png(8, 8))])] == [Image]

def test_list_state_without_image_items_stays_whole():
    items = context_items([{"a": 1}], [b64(png(8, 8))])
    assert items[1] == render_state([{"a": 1}])

@pytest.mark.parametrize("src", ["https://x/a.png", "http://x/a.png", "file:///etc/passwd", "a.png", 7])
def test_url_and_path_sources_are_refused(src):
    with pytest.raises(ImageError, match=r"images\[0\]"):
        context_items("", [src])

def test_more_than_four_images_are_refused():
    with pytest.raises(ImageError, match="at most 4"):
        context_items([{"image": b64(png(8, 8))}] * 2, [b64(png(8, 8))] * 3)

def test_undecodable_image_is_refused():
    with pytest.raises(ImageError, match="not a decodable image"):
        decode_image(b64(b"not an image"), "images[0]")

def test_small_images_pass_through_unchanged():
    raw = png(640, 480)
    assert decode_image(b64(raw), "images[0]").data == raw

@pytest.mark.parametrize("fmt, mime", [("PNG", "image/png"), ("JPEG", "image/jpeg")])
def test_large_images_are_downscaled_keeping_aspect(fmt, mime):
    img = decode_image(b64(encoded(2000, 1000, fmt)), "images[0]")
    assert img.width * img.height <= 1_638_400 and abs(img.width / img.height - 2) < 0.01 and img.mime == mime

def test_decompression_bombs_are_refused_before_decoding(monkeypatch):
    monkeypatch.setattr(PIL.Image, "MAX_IMAGE_PIXELS", 1000)
    with pytest.raises(ImageError, match="too large"):
        decode_image(b64(png(100, 100)), "images[0]")

@pytest.mark.parametrize("mode, fmt, out_mode", [("RGBA", "PNG", "RGBA"), ("P+transparency", "PNG", "RGBA"), ("CMYK", "JPEG", "RGB")])
def test_downscale_handles_image_modes(mode, fmt, out_mode):
    img = decode_image(b64(encoded(2000, 1000, fmt, mode)), "images[0]")
    assert PIL.Image.open(io.BytesIO(img.data)).mode == out_mode

# tests/unit/test_schema.py
def test_images_field_is_optional():
    assert SystemOneRequest(questions={}).images is None
```

- [ ] **Step 2: Run the tests and see them fail.** Run
  `uv run pytest tests/unit/test_images.py tests/unit/test_schema.py -q`. Expected: FAIL (no module).
- [ ] **Step 3: Implement** `gateway/images.py` and the schema additions, following the rules above.
- [ ] **Step 4: Run the tests and see them pass.** Run the same command, then `uv run pytest -q`. Expected: all pass.
- [ ] **Step 5: Commit.** Stage `gateway/images.py`, `gateway/schema.py` and both test files. Message:
  `feat(images): parse and check request images`.

### Task 3: Placeholders and expanded lengths per model

**Files:**
- Create: `gateway/vision.py`
- Test: `tests/unit/test_vision.py`

**Interfaces:**
- Consumes: `Settings.systemone_images`, `Settings.mm_processor_kwargs` (Task 1); `Image`, `ImageError` (Task 2).
- Produces:
  - The `Vision` dataclass:
    ```python
    @dataclass(frozen=True)
    class Vision:
        placeholder: tuple[int, ...]           # ids the gateway writes for one image
        soft_tokens: Callable[[int, int], int]  # (width, height) -> soft tokens vLLM puts in for it
        def expanded(self, image: Image) -> int: ...  # soft tokens + the 2 marks around them
        def added(self, image: Image) -> int: ...     # expanded(image) - len(placeholder)
    ```
  - `gemma_soft_tokens(width: int, height: int, patch: int, pool: int, max_soft: int) -> int`.
  - `qwen_soft_tokens(width: int, height: int, patch: int, merge: int, min_pixels: int, max_pixels: int) -> int`.
    It raises `ImageError("image aspect ratio over 200:1")` where the processor would raise.
  - `load_vision(s: Settings) -> Vision | None`. It returns None when `s.systemone_images` is off.
- Family table, read at startup from `AutoConfig.from_pretrained(s.hf_model, revision=s.hf_revision)`:

  | `model_type` | `placeholder` | soft-token settings |
  |---|---|---|
  | `gemma4` | `(image_token_id,)`, which is 258880; vLLM adds boi 255999 and eoi 258882 | `vision_config.patch_size`, `pooling_kernel_size`; `max_soft` from `mm_processor_kwargs["max_soft_tokens"]`, else `vision_config.default_output_length` |
  | `qwen3_5` | `(vision_start_token_id, image_token_id, vision_end_token_id)`, which is 248053, 248056, 248054 | `vision_config.patch_size`, `spatial_merge_size`; `min_pixels`/`max_pixels` from `preprocessor_config.json` `size.shortest_edge`/`longest_edge` (`hf_hub_download`, same revision), overridden by `mm_processor_kwargs` |

  Any other `model_type` with images on raises `ValueError` at startup.
- The two counts are ports, not guesses: vLLM 0.30 `Gemma4ProcessingInfo._compute_num_soft_tokens` and
  transformers' `qwen2_vl.image_processing_qwen2_vl.smart_resize`, with `factor = patch * merge`. Copy them as they
  are:

```python
def gemma_soft_tokens(width, height, patch, pool, max_soft):
    unit, max_patches = patch * pool, max_soft * pool**2
    scale = math.sqrt(max_patches / ((height / patch) * (width / patch)))
    h = max(unit, int(math.floor(height * scale / unit)) * unit)
    w = max(unit, int(math.floor(width * scale / unit)) * unit)
    return min((h // patch) * (w // patch) // pool**2, max_soft)

def qwen_soft_tokens(width, height, patch, merge, min_pixels, max_pixels):
    factor = patch * merge
    if max(height, width) / min(height, width) > 200:
        raise ImageError("image aspect ratio over 200:1")
    h, w = round(height / factor) * factor, round(width / factor) * factor
    if h * w > max_pixels:
        beta = math.sqrt(height * width / max_pixels)
        h, w = max(factor, math.floor(height / beta / factor) * factor), max(factor, math.floor(width / beta / factor) * factor)
    elif h * w < min_pixels:
        beta = math.sqrt(min_pixels / (height * width))
        h, w = math.ceil(height * beta / factor) * factor, math.ceil(width * beta / factor) * factor
    return (h // factor) * (w // factor)
```

- [ ] **Step 1: Write the failing tests.** The values come from the ports above. Task 8's live test checks the
  ports against vLLM.

```python
@pytest.mark.parametrize("w, h, n560, n280", [(1024, 1024, 529, 256), (1280, 1092, 525, 270), (10, 10, 529, 256),
                                              (3, 900, 409, 280), (4000, 3000, 540, 266)])
def test_gemma_soft_tokens(w, h, n560, n280):
    assert gemma_soft_tokens(w, h, 16, 3, 560) == n560 and gemma_soft_tokens(w, h, 16, 3, 280) == n280

@pytest.mark.parametrize("w, h, n", [(1024, 1024, 1024), (1280, 1092, 1360), (10, 10, 64), (1600, 1024, 1600), (4000, 3000, 1564)])
def test_qwen_soft_tokens(w, h, n):
    assert qwen_soft_tokens(w, h, 16, 2, 65536, 1_638_400) == n

def test_qwen_refuses_extreme_aspect_ratios():
    with pytest.raises(ImageError, match="200:1"):
        qwen_soft_tokens(3, 900, 16, 2, 65536, 1_638_400)

def test_gemma_profile_vision():
    s = replace(Settings.from_profile("gemma-4-31b"), systemone_images=True, mm_processor_kwargs={"max_soft_tokens": 560})
    v = load_vision(s)
    assert v.placeholder == (258880,) and v.expanded(image(1024, 1024)) == 531 and v.added(image(1024, 1024)) == 530

def test_qwen_profile_vision():
    s = replace(Settings.from_profile("qwen3.8-27b"), systemone_images=True, mm_processor_kwargs={"max_pixels": 1_638_400})
    v = load_vision(s)
    assert v.placeholder == (248053, 248056, 248054) and v.expanded(image(1024, 1024)) == 1026 and v.added(image(1024, 1024)) == 1023

def test_vision_is_off_unless_asked():
    assert load_vision(Settings.from_profile("gemma-4-31b")) is None

def test_unknown_model_types_refuse_images(monkeypatch):
    monkeypatch.setattr("gateway.vision.AutoConfig.from_pretrained", lambda *a, **k: SimpleNamespace(model_type="llama"))
    with pytest.raises(ValueError, match="llama"):
        load_vision(replace(Settings.from_profile("gemma-4-31b"), systemone_images=True))
```

`image(w, h)` builds an `Image` with those sizes; its bytes are not read.

- [ ] **Step 2: Run the tests and see them fail.** Run `uv run pytest tests/unit/test_vision.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement** `gateway/vision.py`.
- [ ] **Step 4: Run the tests and see them pass.** Run the same command. Expected: PASS. The HF cache is offline and
  read-only, as in the other tokenizer tests.
- [ ] **Step 5: Commit.** Stage both files. Message: `feat(vision): placeholders and image token counts`.

### Task 4: Image context in the prompt rows

**Files:**
- Modify: `gateway/prompts.py`
- Test: `tests/unit/test_prompts.py`

**Interfaces:**
- Consumes: `Image` (Task 2); `Vision` (Task 3).
- Produces:
  - The `ImageContext` dataclass:
    ```python
    @dataclass(frozen=True)
    class ImageContext:
        ids: list[int]               # the context part, one placeholder per image
        images: tuple[Image, ...]    # in placeholder order
        placeholder: tuple[int, ...]
        added: int                   # ids vLLM adds to a row when it expands every image
    ```
  - `image_context(tok, layout: Layout, items: list[str | Image], vision: Vision) -> ImageContext`.
  - `build_rows(..., pad_rows=None, images: ImageContext | None = None) -> Batch`: one new last parameter. With
    `images`, the `context` part is `images.ids`, not the encoded state.
  - New `Batch` fields and properties:
    - `images: ImageContext | None = None` and `images_shared: bool = False`. The second is
      `"context" in shared_parts(layout)`.
    - `shared_tokens` is `shared_len`, plus `added` when the images are shared.
    - `longest` adds `added`.
    - `input_tokens` adds `added` once when the images are shared, else once per row.
- How `image_context` builds `ids`:
  1. Format `layout.context` with `state = "\n".join(SENTINEL if image else text for each item)`.
  2. Split on `SENTINEL` and encode the pieces with `encode_each`.
  3. Put `vision.placeholder` between the pieces.
- Padding rules for image rows:
  - Padding uses expanded lengths: `pad = padding.size(len(before) + len(after) + added)` and
    `pays(rows, len(plain) + added, pad)` when the images are shared.
  - `middle` mode does not pad image rows, because its split needs the state text.
- Placeholder check: in an image request, every row must hold each placeholder id exactly
  `len(images) * placeholder.count(id)` times. Otherwise raise
  `ImageError("text must not contain image placeholder tokens")`.

- [ ] **Step 1: Write the failing tests.** `Vision` is built directly here:
  `Vision(placeholder=(258880,), soft_tokens=lambda w, h: 100)` for gemma, and the three-id placeholder for qwen.

```python
def test_image_context_keeps_item_order(gemma_tok):
    ctx = image_context(gemma_tok, LAYOUTS["header"], [img(), "Pick the red one", img()], GEMMA_VISION)
    assert ctx.ids == encode(gemma_tok, "Context:\n") + [258880] + encode(gemma_tok, "\nPick the red one\n") + [258880]
    assert ctx.added == 2 * 101 and len(ctx.images) == 2

def test_image_rows_count_expanded_tokens(gemma_tok):
    b = image_batch(gemma_tok, "header", questions=2)  # one image, added 101
    assert b.images_shared and b.shared_tokens == b.shared_len + 101
    assert b.longest == max(len(r.ids) for r in b.rows) + 101
    assert b.input_tokens == b.unpadded_len + sum(len(r.ids) - b.shared_len for r in b.rows) + 101

def test_images_after_the_question_count_per_row(gemma_tok):
    b = image_batch(gemma_tok, "question_first", questions=2)
    assert not b.images_shared and b.input_tokens == b.unpadded_len + sum(len(r.ids) - b.shared_len for r in b.rows) + 101 * len(b.rows)

def test_qwen_pads_on_expanded_lengths(qwen_tok):
    b = image_batch(qwen_tok, "header", questions=8, padding=Padding("front", 800, always=True, token=newline_token(qwen_tok)))
    assert (b.shared_len + b.images.added) % 800 == 0

def test_middle_padding_skips_image_rows(qwen_tok):
    b = image_batch(qwen_tok, "header", questions=8, padding=Padding("middle", 800, always=True, token=newline_token(qwen_tok)))
    assert b.shared_len == b.unpadded_len

def test_placeholder_text_in_an_image_request_is_refused(gemma_tok):
    with pytest.raises(ImageError, match="placeholder"):
        image_batch(gemma_tok, "header", questions=1, instructions="Is <|image|> blue?")

def test_the_same_image_twice_gets_two_placeholders(gemma_tok):
    ctx = image_context(gemma_tok, LAYOUTS["header"], [img(), img()], GEMMA_VISION)
    assert ctx.ids.count(258880) == 2
```

  `image_batch` is a small helper next to the existing `batch_for` in `tests/helpers.py`. Add a `gemma_tok`
  fixture if none exists.
- [ ] **Step 2: Run the tests and see them fail.** Run `uv run pytest tests/unit/test_prompts.py -q`. Expected: the
  new tests FAIL; the golden tests PASS.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run the tests and see them pass.** Run `uv run pytest -q`. Expected: all pass, with no golden file
  rewritten (`git status tests/unit/golden` is clean).
- [ ] **Step 5: Commit.** Stage `gateway/prompts.py`, `tests/unit/test_prompts.py` and `tests/helpers.py`.
  Message: `feat(prompts): image placeholders in the context`.

### Task 5: Read image rows through `/inference/v1/generate`

**Files:**
- Modify: `gateway/readout.py`
- Test: `tests/unit/test_readout.py`

**Interfaces:**
- Produces:
  ```python
  async def image_logprobs(self, prompts: list[list[int]], label_ids: list[list[int]], shared_len: int,
                           shared_tokens: int, parts: list[dict], prefix_parts: list[dict]) -> list[list[float]]
  ```
  `_post(payload, path="/v1/completions")` gains the path. The text methods are unchanged.
- Each row is one call per chunk of at most 127 label ids. The payload is exact:

```json
{"model": "<served>", "token_ids": [...], "content_parts": [...],
 "sampling_params": {"max_tokens": 1, "temperature": 0, "logprobs": N + 1, "logprob_token_ids": [...chunk, spare]}}
```

  - `N` is the chunk's size.
  - `spare` is the smallest non-negative id not in the chunk. vLLM cuts the last entry otherwise (spike).
  - `priority` goes at the top level, only when set.
  - The response gives `choices[0]["logprobs"]["content"][0]["top_logprobs"]` as `[{"token": "token_id:<id>",
    "logprob": x}]`.
  - A label missing from the response raises `RuntimeError` naming the id.
- Warm-up uses the text rule, measured on `shared_tokens` (expanded):
  - `prefix`: send `prompts[0][:shared_len]` with `prefix_parts` and
    `sampling_params = {"max_tokens": 1, "temperature": 0}`, then all rows.
  - `row`: row 1 first, then the rest.
  - `off`: all rows at once.
  - "All rows" means waves of `governor.wave_size() or len(rows)` rows, sent together. Each HTTP call goes through
    `governor.call`.

- [ ] **Step 1: Write the failing tests.** Add a `fake_generate(seen, drop=None)` handler. It records `(path, body)`
  and answers each label in `sampling_params.logprob_token_ids` with `-id`, skipping `drop`.

```python
async def test_image_rows_go_one_per_call_with_their_images():
    seen = []
    out = await readout(fake_generate(seen)).image_logprobs([[1, 2], [1, 3]], [[30, 10], [20]], 1, 1, PARTS, PARTS)
    assert out == [[-30.0, -10.0], [-20.0]]
    assert [p for p, _ in seen] == ["/inference/v1/generate"] * 2
    body = next(b for _, b in seen if b["token_ids"] == [1, 2])
    assert body["content_parts"] == PARTS and body["sampling_params"]["logprob_token_ids"] == [10, 30, 0]
    assert body["sampling_params"]["logprobs"] == 3 and body["sampling_params"]["max_tokens"] == 1

async def test_the_spare_id_is_never_a_label():
    seen = []
    await readout(fake_generate(seen)).image_logprobs([[1]], [[0, 1, 2]], 1, 1, PARTS, PARTS)
    assert seen[0][1]["sampling_params"]["logprob_token_ids"] == [0, 1, 2, 3]

async def test_prefix_warm_up_sends_the_shared_images_first():
    seen = []
    rows = [[5] * 20 + [k] for k in range(3)]
    await readout(fake_generate(seen), warm_up="prefix").image_logprobs(rows, [[10]] * 3, 20, 600, PARTS, PARTS)
    first = seen[0][1]
    assert first["token_ids"] == [5] * 20 and first["content_parts"] == PARTS and "logprob_token_ids" not in first["sampling_params"]
    assert len(seen) == 4

async def test_warm_up_threshold_counts_expanded_tokens():
    seen = []
    await readout(fake_generate(seen), warm_up="prefix").image_logprobs([[5, 1], [5, 2]], [[10]] * 2, 1, 100, PARTS, PARTS)
    assert len(seen) == 2  # 100 < 512: no warm-up

async def test_row_warm_up_reads_row_one_first():
    seen = []
    rows = [[5] * 20 + [k] for k in range(3)]
    await readout(fake_generate(seen), warm_up="row").image_logprobs(rows, [[10]] * 3, 20, 600, PARTS, PARTS)
    assert seen[0][1]["token_ids"] == rows[0]

async def test_more_than_127_labels_split_across_calls():
    seen = []
    labels = list(range(1, 201))
    out = await readout(fake_generate(seen)).image_logprobs([[1]], [labels], 1, 1, PARTS, PARTS)
    assert out == [[-float(i) for i in labels]] and len(seen) == 2
    assert all(len(b["sampling_params"]["logprob_token_ids"]) <= 128 for _, b in seen)

async def test_a_missing_label_is_an_error():
    with pytest.raises(RuntimeError, match="30"):
        await readout(fake_generate([], drop=30)).image_logprobs([[1]], [[30, 10]], 1, 1, PARTS, PARTS)

async def test_image_rows_carry_priority_only_when_set(): ...   # mirror test_priority_is_sent_only_when_set
async def test_image_calls_go_through_the_governor(): ...       # mirror test_prefix_warm_up_goes_through_the_governor
```

- [ ] **Step 2: Run the tests and see them fail.** Run `uv run pytest tests/unit/test_readout.py -q`. Expected: the
  new tests FAIL.
- [ ] **Step 3: Implement.** Add `image_logprobs` and `_generate_row`, and the `path` parameter on `_post`.
- [ ] **Step 4: Run the tests and see them pass.** Run `uv run pytest -q`. Expected: all pass.
- [ ] **Step 5: Commit.** Message: `feat(readout): image rows via token-in generate`.

### Task 6: Route image requests; 400s; body limit; README

**Files:**
- Create: `gateway/body_limit.py`
- Modify: `gateway/decide.py`, `gateway/app.py`, `README.md`
- Test: `tests/unit/test_decide.py`, `tests/unit/test_app.py`

**Interfaces:**
- Consumes: Tasks 2–5.
- Produces:
  - `Engine.vision: Vision | None = None`, set by `load_engine` from `load_vision(s)`.
  - `build_batch`:
    1. `items = context_items(request.state, request.images)`.
    2. With images and `engine.vision is None`, raise `ImageError("this profile serves text only")`.
    3. Otherwise build the `ImageContext` and pass it to `build_rows` on both its calls (padded, and the `OFF`
       retry).
  - When `batch.images` is set, `read_rows` builds `parts = [i.part() for i in batch.images.images]` and calls
    `readout.image_logprobs(ids, labels, batch.shared_len, batch.shared_tokens, parts,
    parts if batch.images_shared else [])`. Text calls `letter_logprobs` as today.
  - `body_limit.BodyLimit(app, path="/v1/systemone", limit=MAX_BODY_BYTES)` is a plain ASGI middleware. It does not
    use `BaseHTTPMiddleware`, which breaks disconnect detection. A POST whose `Content-Length` exceeds the limit
    gets 400 `{"error": {"message": "request body over 20 MB"}}`.
  - `app.py`:
    - an `ImageError` handler that returns 400;
    - `BodyLimit` added;
    - `/health` adds `"systemone_images"` and `"mm_processor_kwargs"`.

- [ ] **Step 1: Write the failing tests.**
  - `test_decide.py`, with the module's existing fakes:
    - `test_images_on_a_text_profile_are_refused`: an engine with `vision=None` and a request with `images` raises
      `ImageError` matching "text only".
    - `test_image_requests_read_through_the_image_path`: a fake readout records which method ran.
      `image_logprobs` gets `parts == [img.part()]` and `prefix_parts == parts` on `header`. A text request still
      calls `letter_logprobs`.
    - `test_expanded_image_prompts_over_the_cap_are_refused`: with `systemone_max_len` just above the text length,
      a `RequestError` matches "maximum context length".
    - `test_usage_counts_image_tokens`: `usage.input_tokens == batch.input_tokens`, which includes `added`.
  - `test_app.py`, with its existing TestClient setup:
    - `test_url_images_are_400`: `images=["https://x/a.png"]` gives 400 and the message contains `images[0]`.
    - `test_bodies_over_20_mb_are_400`: a body of 20,000,001 bytes gives 400.
    - `test_health_reports_images`: both new keys are present.
- [ ] **Step 2: Run the tests and see them fail.** Run
  `uv run pytest tests/unit/test_decide.py tests/unit/test_app.py -q`. Expected: the new tests FAIL.
- [ ] **Step 3: Implement.** Update the README section on `/v1/systemone`:
  - the two image formats;
  - the sources (`data:` and base64 only);
  - the limits (4 images, 20 MB, 1,638,400 px downscale);
  - the 400 and 422 cases;
  - which profiles serve images.
- [ ] **Step 4: Run the tests and see them pass.** Run `uv run pytest -q` and `uv run ruff check .`. Expected: all pass.
- [ ] **Step 5: Commit.** Message: `feat(decide): route image requests`.

### Task 7: Text baseline before the profile edits (GPU)

**Files:**
- Create: `scripts/index_agreement.py`, promoted from the spike's `agree.py`
- Test: `tests/unit/test_index_agreement.py`

**Interfaces:**
- Produces: `uv run python scripts/index_agreement.py BEFORE/merged/results.jsonl AFTER/merged/results.jsonl`.
  - It prints rows compared, top-answer flips, flips where the top-two gap > 0.10, and max and median |dp|.
  - It exits 1 when a flip with a gap > 0.10 exists.
  - It is a function `agreement(before: dict, after: dict) -> dict` plus a thin `main`.

- [ ] **Step 1: Write the failing test.** Two tiny result sets give `{"rows": 2, "flips": 1, "flips_over_gap": 0,
  "max_dp": ...}`. A noul answer counts as `{"true": p, "false": 1 - p}`.
- [ ] **Step 2: Run the test and see it fail.** Then implement the script. Then run the test and see it pass.
- [ ] **Step 3: Commit.** Message: `feat(scripts): Index answer agreement`.
- [ ] **Step 4: Ask the owner for an ok before the GPU runs.** Give an estimate per profile. Each profile runs
  JevBench-only (~5 min), the 3,120-row subset and latency-v1. Check the power limit is 600 W.
- [ ] **Step 5: Run the before set for gemma-4-31b and then qwen3.8-27b, both at today's profiles.**
  Run `docker compose --env-file profiles/P.env up -d`, then:
  - keep the line `GPU KV cache size: N tokens` (vLLM log);
  - `uv run python scripts/bench.py --profile P --gateway $G --jevbench-only`;
  - `uv run python scripts/evaluate.py index --profile P --gateway $G --ids .cache/submit-gemma/agree-ids.json`;
  - `uv run python scripts/latency.py --profile P --gateway $G`.
- [ ] **Step 6: Commit the result folders,** one per profile, staged explicitly. Message:
  `docs(results): text baselines before vision`.

### Task 8: Vision profiles and live tests (GPU)

**Files:**
- Modify: `profiles/gemma-4-31b.env`, `profiles/qwen3.8-27b.env`
- Create: `tests/live/test_images.py`

**Interfaces:**
- Profile changes:

  | Profile | Changes |
  |---|---|
  | gemma-4-31b | `SYSTEMONE_IMAGES=1`; `MM_PROCESSOR_KWARGS={"max_soft_tokens":560}`; `--limit-mm-per-prompt {"video":0,"image":4}` in `EXTRA_ARGS`; fix the comment "images (<=280)" to 560 |
  | qwen3.8-27b | `LANGUAGE_MODEL_ONLY=0`; `SYSTEMONE_IMAGES=1`; `MM_PROCESSOR_KWARGS={"max_pixels":1638400}`; add `--limit-mm-per-prompt {"video":0,"image":4}` to `EXTRA_ARGS` |

- Live tests, all `pytestmark = pytest.mark.live`, with images made by Pillow in the test. Use a unique image per
  test (a random pixel) so the cache is cold.
  - `test_one_image_several_questions`: 4 noul and choice questions give 200, and every answer is typed.
  - `test_image_parts_in_state`: `state=[{"image": data_url}, "text"]` gives 200.
  - `test_second_question_hits_the_image_cache`: the same image with one question, then another question. The
    `vllm:prefix_cache_hits` delta of the second call ≥ the image's expanded tokens.
  - `test_expanded_lengths_match_vllm`: for sizes (1024, 1024), (1280, 1092), (10, 10), (3, 900) on gemma only,
    (4000, 3000) after the gateway's downscale, and two images in one request:
    - load `load_vision(Settings.from_profile(P))` in the test process;
    - post one row's ids and parts straight to vLLM `/inference/v1/generate` with `return_token_ids: true`;
    - assert `len(prompt_token_ids) == len(ids) + sum(vision.added(i))`.
  - `test_text_requests_unchanged`: run the existing `test_prefix_cache.py` and `test_stability.py` unchanged
    (no new code).
- [ ] **Step 1: Write the live tests.**
- [ ] **Step 2: Edit the profiles.**
- [ ] **Step 3: Run the tests on each profile.**
  1. Bring the stack up on the profile and keep the KV line.
  2. Run `uv run pytest -m live tests/live -v` with the stack up and idle.
  3. Expected: all pass, including on qwen with MTP. MTP with image rows passing is the DS-004 sampler check.
  4. A failing count test means the port is wrong for that size. Fix `gateway/vision.py` and add the size to
     Task 3's tests.
- [ ] **Step 4: Commit.** Message: `feat(profiles): images on gemma and qwen3.8`.

### Task 9: Text regression after the profile edits (GPU)

- [ ] **Step 1: Run Task 7 Step 5's commands for both profiles at the edited profiles.** Get the owner's ok
  (same estimate) and check 600 W first.
- [ ] **Step 2: Compare.**
  - `uv run python scripts/compare_runs.py BEFORE AFTER` for JevBench.
  - `scripts/index_agreement.py` for the subset.
  - The latency summaries side by side.
  - The KV lines: before and after for both profiles. On qwen, that is the vision tower's cost.
- [ ] **Step 3: Gate.** Pass when no top answer flips where the top-two gap > 0.10 and latency is within
  run-to-run noise. A failure stops the plan: report the numbers to the owner.
- [ ] **Step 4: Commit the result folders and a short note.** Add a "Vision profiles" note to each profile's results
  README, or the nearest existing results index. Message: `docs(results): text unchanged with vision on`.

### Task 10: Image prompt-sharing check (GPU)

This task produces numbers for the owner. It does not change a threshold.

- [ ] **Step 1: Copy the probe.** Copy `share_probe.py` from the scratchpad to
  `.cache/share-spike/image_share_probe.py`. Build image requests: one image (1280×1092), a 200-token state,
  4 and 16 questions, 3 reps.
  - Arm `all`: all rows at once.
  - Arm `prefix`: the prefix with images first.
  - Record computed ÷ usage from `vllm:prompt_tokens_total` and `vllm:prompt_tokens_cached_total`, plus wall ms.
- [ ] **Step 2: Run it on gemma-4-31b and qwen3.8-27b** (a few minutes each, 600 W).
- [ ] **Step 3: Report the table to the owner,** with a recommendation on the image warm-up threshold
  (`WARM_MIN_PREFIX_TOKENS` is shared with text). Apply only what the owner picks.

### Task 11: Vision evaluation runner and runs (GPU)

**Files:**
- Create: `scripts/vision_run.py`, `scripts/vision_baseline.sh`, `scripts/vision_engines.py` (`NoThinkVl`,
  promoted from `.cache/decision-index-vision/spike-engines/`)
- Test: `tests/unit/test_vision_run.py`

**Interfaces:**
- `uv run python scripts/vision_run.py --profile P --gateway $G [--sample N] [--workers 8]`:
  1. `GET /health`; refuse unless `systemone_images` is true.
  2. With `--sample`, write a seeded sample stratified by benchmark (seed 24) to the run folder and pass it as
     `--rows`.
  3. Run `.cache/decision-index-vision/venv/bin/python -m decision_index vision run --dir <kit>/work/vision
     --engine decide --option base_url=$G --option path=/v1/systemone --option protocol=decisions
     --option model=<served_model> --workers W --compact --out <run>`. Use cwd = kit `src`, and pass
     `DECISION_INDEX_API_KEY` from `GATEWAY_API_KEY`.
  4. Run `vision score`.
  5. Write `docs/results/<profile>/<UTC>-vision[-sample]/`, holding `health.json`, `vision-scores.json`,
     `results.jsonl.gz`, `summary.json` and `summary.md`.
- Functions with tests:
  - `latency(rows) -> {"median", "mean", "p80"}` over `model_request_wall_ms` of ok rows;
  - `calibration(rows, expected) -> {"ece", "accuracy", "n"}`, which uses `scripts.metrics.ece_of` on the max
    probability against `expected.answer`;
  - `status_counts(rows)`.
- `scripts/vision_baseline.sh P` is the spike's `baselines.sh`, made reusable. It runs the kit `vllm-vl` engine in the
  pinned vLLM image on the full suite with the profile's `mm_processor_kwargs`. Qwen uses
  `vision_engines:NoThinkVl`. The stack must be down.

- [ ] **Step 1: Write the failing tests** for `latency`, `calibration` and `status_counts` on 4 hand-made rows, with
  exact expected numbers.
- [ ] **Step 2: Implement until the tests pass,** then commit. Message: `feat(scripts): vision suite runner`.
- [ ] **Step 3: Single-client latency.** For each profile, at 600 W, run
  `vision_run.py --sample 300 --workers 1`. The gate is median, mean and p80 each ≤ 1,000 ms. The timing gives the
  estimate for Step 4.
- [ ] **Step 4: Ask the owner for an ok with that estimate,** then run the full suite (12,210 rows) for both
  profiles. Then run `vision_baseline.sh` for both, with the stack down.
- [ ] **Step 5: Commit the result folders and scripts.** Message: `docs(results): vision suite, gateway vs stock`.

### Task 12: Docs and ticket

**Files:**
- Create: `docs/background/images.md`
- Modify: `docs/background/prompt-layouts.md`, `docs/background/prompt-sharing.md`, `README.md` (results table)

- [ ] **Step 1: Write `images.md`.** Cover:
  - request to rows;
  - where images sit;
  - placeholders and expanded lengths per model, with the ported formulas named;
  - the `uuid` cache key;
  - what is cached within and across requests;
  - the spike, live and Task 10 numbers;
  - the evaluation results next to the stock baselines.
- [ ] **Step 2: Add the short image notes.**
  - `prompt-layouts.md`: images inside `Context:`.
  - `prompt-sharing.md`: image prefixes and the cross-request caveat.
  - README: results.
- [ ] **Step 3: Commit.** Message: `docs: vision decisions`. Then move DS-024 to Verification and request
  completion (`dostuff-tickets`).
