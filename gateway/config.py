"""Settings from the environment (compose) or from a profile file (scripts, tests)."""

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_env_file(path: Path) -> dict[str, str]:
    """KEY=VALUE per line; blank lines and '#' comments skipped; single quotes stripped."""
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip("'")
    return env


@dataclass(frozen=True)
class Settings:
    profile: str
    hf_model: str
    hf_revision: str
    served_model: str
    max_model_len: int
    prompt_layout: str = "decider_chat"
    option_orders: str = "identity"
    vllm_url: str = "http://127.0.0.1:8000"
    api_key: str | None = field(default=None, repr=False)  # keys never show in logs or tracebacks
    vllm_api_key: str | None = field(default=None, repr=False)
    warm_min_prefix_tokens: int = 512
    prefix_pad: str = "off"  # where to pad the shared prefix: off | end | front | middle
    prefix_block: int = 0  # pad it to a multiple of this many tokens; 0 never pads
    prefix_pad_always: bool = False  # pad even when it does not pay (fidelity experiments)
    data_root: Path = ROOT / "data"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        e = dict(os.environ) if env is None else env
        return cls(
            profile=e["PROFILE"],
            hf_model=e["HF_MODEL"],
            hf_revision=e["HF_REVISION"],
            served_model=e["SERVED_MODEL"],
            max_model_len=int(e["MAX_MODEL_LEN"]),
            prompt_layout=e.get("PROMPT_LAYOUT") or "decider_chat",
            option_orders=e.get("OPTION_ORDERS") or "identity",
            vllm_url=e.get("VLLM_URL") or "http://127.0.0.1:8000",
            api_key=e.get("GATEWAY_API_KEY") or None,
            vllm_api_key=e.get("VLLM_API_KEY") or None,
            warm_min_prefix_tokens=int(e.get("WARM_MIN_PREFIX_TOKENS") or 512),
            prefix_pad=e.get("PREFIX_PAD") or "off",
            prefix_block=int(e.get("PREFIX_BLOCK") or 0),
            prefix_pad_always=e.get("PREFIX_PAD_ALWAYS") == "1",
            data_root=Path(e.get("DATA_ROOT") or ROOT / "data"),
        )

    @classmethod
    def from_profile(cls, name: str) -> "Settings":
        return cls.from_env(read_env_file(ROOT / "profiles" / f"{name}.env"))

    def data_dir(self, layout: str) -> Path:
        return self.data_root / self.profile / layout
