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


QUICKSTART = {
    "department": {
        "type": "choice",
        "instructions": "Which team should handle this",
        "criteria": {
            "billing": "Payment or subscription issues",
            "technical": "Bugs or integration problems",
            "sales": "Pricing or account questions",
        },
    },
    "frustration": {
        "type": "score",
        "instructions": "How frustrated the customer appears",
        "criteria": ["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
    },
    "is_urgent": {"type": "noul", "instructions": "The message conveys urgency or time-sensitivity"},
}
STATE = "Hi, my Stripe integration keeps failing and I'm losing sales. Please help ASAP."
