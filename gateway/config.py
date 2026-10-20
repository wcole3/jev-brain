"""Settings from the environment (compose) or from a profile file (scripts, tests)."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from gateway.orders import gate

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


def json_object(env: dict[str, str], key: str) -> dict:
    """env[key] parsed as a JSON object; empty or missing gives {}; anything else raises ValueError naming key."""
    try:
        value = json.loads(env.get(key) or "{}")
    except json.JSONDecodeError:
        value = None
    if isinstance(value, dict):
        return value
    raise ValueError(f"{key} must be a JSON object, got {env[key]!r}")


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
    option_orders_images: str = ""  # the setting for requests with images; empty means option_orders
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
    systemone_images: bool = False  # accept images in decision requests; vision profiles only
    mm_processor_kwargs: dict = field(default_factory=dict)  # also passed to vLLM, so both count image tokens alike
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
            option_orders_images=e.get("OPTION_ORDERS_IMAGES") or "",
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
            systemone_images=e.get("SYSTEMONE_IMAGES") == "1",
            mm_processor_kwargs=json_object(e, "MM_PROCESSOR_KWARGS"),
            data_root=Path(e.get("DATA_ROOT") or ROOT / "data"),
        )

    @classmethod
    def from_profile(cls, name: str) -> "Settings":
        return cls.from_env(read_env_file(ROOT / "profiles" / f"{name}.env"))

    def data_dir(self, layout: str) -> Path:
        return self.data_root / self.profile / layout

    @property
    def image_orders(self) -> str:
        return self.option_orders_images or self.option_orders

    def orders_in_use(self) -> list[str]:
        """Text setting, then the image setting, then identity when any of them is gated."""
        used = [self.option_orders]
        if self.systemone_images:
            used.append(self.image_orders)
        if any(gate(x) is not None for x in used):
            used.append("identity")  # a gate reads its temperature from the identity fit
        return list(dict.fromkeys(used))

    def calibration_path(self, layout: str, orders: str | None = None) -> Path:
        """calibration-<slug of orders>.json for another setting when present; else the block-size rule."""
        if orders not in (None, self.option_orders):
            slug = orders.replace(":", "-").replace("+", "-")
            own = self.data_dir(layout) / f"calibration-{slug}.json"
            if own.exists():
                return own
        sized = self.data_dir(layout) / f"calibration-{self.prefix_block}.json"
        return sized if sized.exists() else self.data_dir(layout) / "calibration.json"
