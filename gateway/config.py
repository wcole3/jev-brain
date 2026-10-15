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


def number(env: dict[str, str], key: str, kind: type, default):
    """env[key] as kind; empty or missing gives default; junk raises ValueError naming key."""
    try:
        return kind(env.get(key) or default)
    except ValueError:
        raise ValueError(f"{key} must be a number, got {env[key]!r}") from None


@dataclass(frozen=True)
class Settings:
    profile: str
    hf_model: str
    hf_revision: str
    served_model: str
    max_model_len: int
    systemone_max_len: int = 32768  # decisions refuse prompts this long; <= max_model_len (DS-018)
    prompt_layout: str = "decider_chat"
    option_orders: str = "identity"
    vllm_url: str = "http://127.0.0.1:8000"
    api_key: str | None = field(default=None, repr=False)  # keys never show in logs or tracebacks
    vllm_api_key: str | None = field(default=None, repr=False)
    warm_min_prefix_tokens: int = 512
    warm_up: str = "row"  # row: row 1 first (hybrid Qwen); prefix: shared prefix alone first (gemma); off: all at once
    prefix_pad: str = "off"  # where to pad the shared prefix: off | end | front | middle
    prefix_block: int = 0  # pad it to a multiple of this many tokens; 0 never pads
    prefix_pad_always: bool = False  # pad even when it does not pay (fidelity experiments)
    systemone_priority: int = 0  # vLLM priority for decision requests; >0 runs them after chat (needs --scheduling-policy priority)
    governor_duty: float = 1.0  # share of time decisions keep while chat decodes; 1.0 turns the governor off (DS-007)
    governor_wave: int = 4  # prompts per decision request while throttling
    data_root: Path = ROOT / "data"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        e = dict(os.environ) if env is None else env
        max_model_len = int(e["MAX_MODEL_LEN"])
        return cls(
            profile=e["PROFILE"],
            hf_model=e["HF_MODEL"],
            hf_revision=e["HF_REVISION"],
            served_model=e["SERVED_MODEL"],
            max_model_len=max_model_len,
            systemone_max_len=int(e.get("SYSTEMONE_MAX_LEN") or min(32768, max_model_len)),
            prompt_layout=e.get("PROMPT_LAYOUT") or "decider_chat",
            option_orders=e.get("OPTION_ORDERS") or "identity",
            vllm_url=e.get("VLLM_URL") or "http://127.0.0.1:8000",
            api_key=e.get("GATEWAY_API_KEY") or None,
            vllm_api_key=e.get("VLLM_API_KEY") or None,
            warm_min_prefix_tokens=int(e.get("WARM_MIN_PREFIX_TOKENS") or 512),
            warm_up=e.get("WARM_UP") or "row",
            prefix_pad=e.get("PREFIX_PAD") or "off",
            prefix_block=int(e.get("PREFIX_BLOCK") or 0),
            prefix_pad_always=e.get("PREFIX_PAD_ALWAYS") == "1",
            systemone_priority=int(e.get("SYSTEMONE_PRIORITY") or 0),
            governor_duty=number(e, "GOVERNOR_DUTY", float, 1.0),
            governor_wave=number(e, "GOVERNOR_WAVE", int, 4),
            data_root=Path(e.get("DATA_ROOT") or ROOT / "data"),
        )

    @classmethod
    def from_profile(cls, name: str) -> "Settings":
        return cls.from_env(read_env_file(ROOT / "profiles" / f"{name}.env"))

    def data_dir(self, layout: str) -> Path:
        return self.data_root / self.profile / layout

    def calibration_path(self, layout: str) -> Path:
        """calibration-<prefix_block>.json when the layout has one, else calibration.json."""
        sized = self.data_dir(layout) / f"calibration-{self.prefix_block}.json"
        return sized if sized.exists() else self.data_dir(layout) / "calibration.json"
