"""Refuse to publish the gateway beyond loopback without GATEWAY_API_KEY.

usage: docker compose ... config --format json | python scripts/check_bind.py
"""

import json
import sys

LOOPBACK = {"127.0.0.1", "::1", "localhost"}


def exposure_error(config: dict) -> str | None:
    gateway = config["services"]["gateway"]
    hosts = {port.get("host_ip") or "0.0.0.0" for port in gateway.get("ports", [])}
    if hosts <= LOOPBACK or gateway.get("environment", {}).get("GATEWAY_API_KEY"):
        return None
    return f"gateway binds {', '.join(sorted(hosts - LOOPBACK))}: set GATEWAY_API_KEY first"


if __name__ == "__main__":
    error = exposure_error(json.load(sys.stdin))
    if error:
        raise SystemExit(error)
