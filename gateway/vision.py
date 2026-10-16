"""Which ids stand for an image in a decision prompt, and how many ids vLLM expands each into."""

import json
import math
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from huggingface_hub import hf_hub_download
from transformers import AutoConfig

from gateway.config import Settings
from gateway.images import Image
from gateway.schema import ImageError

MARKS = 2  # the ids vLLM puts around an image's soft tokens


@dataclass(frozen=True)
class Vision:
    placeholder: tuple[int, ...]  # ids the gateway writes for one image
    soft_tokens: Callable[[int, int], int]  # (width, height) -> soft tokens vLLM puts in for it

    def expanded(self, image: Image) -> int:
        try:
            return self.soft_tokens(image.width, image.height) + MARKS
        except ImageError as e:
            raise ImageError(f"{image.where}: {e}") from e

    def added(self, image: Image) -> int:
        return self.expanded(image) - len(self.placeholder)


def gemma_soft_tokens(width: int, height: int, patch: int, pool: int, max_soft: int) -> int:
    """Port of vLLM 0.30 Gemma4ProcessingInfo._compute_num_soft_tokens."""
    unit, max_patches = patch * pool, max_soft * pool**2
    scale = math.sqrt(max_patches / ((height / patch) * (width / patch)))
    h = max(unit, math.floor(height * scale / unit) * unit)
    w = max(unit, math.floor(width * scale / unit) * unit)
    return min((h // patch) * (w // patch) // pool**2, max_soft)


def qwen_soft_tokens(width: int, height: int, patch: int, merge: int, min_pixels: int, max_pixels: int) -> int:
    """Port of transformers' qwen2_vl smart_resize, counted in merged patches."""
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


def gemma_vision(config, s: Settings) -> Vision:
    v = config.vision_config
    max_soft = s.mm_processor_kwargs.get("max_soft_tokens", v.default_output_length)
    return Vision((config.image_token_id,), partial(gemma_soft_tokens, patch=v.patch_size, pool=v.pooling_kernel_size, max_soft=max_soft))


def qwen_vision(config, s: Settings) -> Vision:
    v = config.vision_config
    path = hf_hub_download(s.hf_model, "preprocessor_config.json", revision=s.hf_revision)
    size = json.loads(Path(path).read_text())["size"]
    min_pixels = s.mm_processor_kwargs.get("min_pixels", size["shortest_edge"])
    max_pixels = s.mm_processor_kwargs.get("max_pixels", size["longest_edge"])
    count = partial(qwen_soft_tokens, patch=v.patch_size, merge=v.spatial_merge_size, min_pixels=min_pixels, max_pixels=max_pixels)
    return Vision((config.vision_start_token_id, config.image_token_id, config.vision_end_token_id), count)


FAMILIES = {"gemma4": gemma_vision, "qwen3_5": qwen_vision}


def load_vision(s: Settings) -> Vision | None:
    """The model's image placeholder and token counts; None when images are off."""
    if not s.systemone_images:
        return None
    config = AutoConfig.from_pretrained(s.hf_model, revision=s.hf_revision)
    if config.model_type not in FAMILIES:
        raise ValueError(f"images are on but model type {config.model_type!r} has no image support")
    return FAMILIES[config.model_type](config, s)
