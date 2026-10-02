"""Print a profile's settings as shell `export` lines, with K=V overrides.

usage: python scripts/profile_env.py PROFILE [K=V ...]   (eval "$(...)" in a shell)
"""

import shlex
import sys

from gateway.config import ROOT, read_env_file

PROFILES = ROOT / "profiles"


def exports(profile: str, overrides: list[str]) -> str:
    env = read_env_file(PROFILES / f"{profile}.env")
    env |= dict(item.split("=", 1) for item in overrides)
    return "\n".join(f"export {key}={shlex.quote(value)}" for key, value in env.items())


if __name__ == "__main__":
    print(exports(sys.argv[1], sys.argv[2:]))
