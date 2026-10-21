from dataclasses import replace
from functools import partial
from types import SimpleNamespace

import pytest

from gateway.config import Settings
from gateway.images import Image
from gateway.schema import ImageError
from gateway.vision import Vision, gemma_soft_tokens, load_vision, qwen_soft_tokens


def image(w, h):
    return Image(b"", "image/png", w, h, "")


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


def test_aspect_refusal_names_the_image():
    v = Vision((1,), partial(qwen_soft_tokens, patch=16, merge=2, min_pixels=65536, max_pixels=1_638_400))
    with pytest.raises(ImageError, match=r"^state\[2\]\.image: image aspect ratio over 200:1"):
        v.added(replace(image(3, 900), where="state[2].image"))


def test_gemma_profile_vision():
    s = replace(Settings.from_profile("gemma-4-31b"), systemone_images=True, mm_processor_kwargs={"max_soft_tokens": 560})
    v = load_vision(s)
    assert v.placeholder == (258880,) and v.expanded(image(1024, 1024)) == 531 and v.added(image(1024, 1024)) == 530


def test_qwen_profile_vision():
    s = replace(Settings.from_profile("qwen3.8-27b"), systemone_images=True, mm_processor_kwargs={"max_pixels": 1_638_400})
    v = load_vision(s)
    assert v.placeholder == (248053, 248056, 248054) and v.expanded(image(1024, 1024)) == 1026 and v.added(image(1024, 1024)) == 1023


def test_vision_is_off_unless_asked():
    assert load_vision(Settings.from_profile("qwen3.6-27b")) is None  # a text-only profile


def test_unknown_model_types_refuse_images(monkeypatch):
    monkeypatch.setattr("gateway.vision.AutoConfig.from_pretrained", lambda *a, **k: SimpleNamespace(model_type="llama"))
    with pytest.raises(ValueError, match="llama"):
        load_vision(replace(Settings.from_profile("gemma-4-31b"), systemone_images=True))


UNIFIED = SimpleNamespace(model_type="gemma4_unified", image_token_id=258880,
                          vision_config=SimpleNamespace(patch_size=16, pooling_kernel_size=3, num_soft_tokens=280))


@pytest.mark.parametrize("w, h, n", [(640, 480, 542), (800, 600, 542), (100, 100, 531), (4000, 3000, 542),
                                     (3, 900, 411), (1920, 1080, 529), (300, 2000, 551)])
def test_gemma_unified_matches_vllm_expansion(monkeypatch, w, h, n):
    monkeypatch.setattr("gateway.vision.AutoConfig.from_pretrained", lambda *a, **k: UNIFIED)
    s = replace(Settings.from_profile("gemma-4-12b"), systemone_images=True, mm_processor_kwargs={"max_soft_tokens": 560})
    assert load_vision(s).expanded(image(w, h)) == n


def test_gemma_unified_defaults_to_num_soft_tokens(monkeypatch):
    monkeypatch.setattr("gateway.vision.AutoConfig.from_pretrained", lambda *a, **k: UNIFIED)
    s = replace(Settings.from_profile("gemma-4-12b"), systemone_images=True, mm_processor_kwargs={})
    assert load_vision(s).expanded(image(4000, 3000)) == gemma_soft_tokens(4000, 3000, 16, 3, 280) + 2
