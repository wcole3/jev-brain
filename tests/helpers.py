"""Values shared by tests. Import from here, not from conftest or other test modules."""
import functools

from transformers import AutoTokenizer

from gateway.config import Settings

PROFILES = ["qwen3.8-27b", "qwen3.6-27b", "gemma-4-31b"]


@functools.cache
def tokenizer_for(profile: str):
    """The pinned tokenizer of a profile (downloads a few MB into the HF cache once)."""
    s = Settings.from_profile(profile)
    return AutoTokenizer.from_pretrained(s.hf_model, revision=s.hf_revision)
