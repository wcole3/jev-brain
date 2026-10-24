"""Refuse to publish vLLM beyond loopback, or the gateway beyond loopback without GATEWAY_API_KEY.

usage: docker compose ... config --format json | python scripts/check_bind.py
"""

import json
import sys

LOOPBACK = {"127.0.0.1", "::1", "localhost"}


def published(service: dict) -> set[str]:
    """The host addresses a service's ports bind; no address means every interface."""
    return {port.get("host_ip") or "0.0.0.0" for port in service.get("ports", [])}


def exposure_error(config: dict) -> str | None:
    # vLLM's /health, /metrics, /version and /tokenize skip VLLM_API_KEY (DS-012).
    if exposed := published(config["services"]["vllm"]) - LOOPBACK:
        return f"vllm binds {', '.join(sorted(exposed))}: keep port 8000 on loopback"
    gateway = config["services"]["gateway"]
    exposed = published(gateway) - LOOPBACK
    if not exposed or gateway.get("environment", {}).get("GATEWAY_API_KEY"):
        return None
    return f"gateway binds {', '.join(sorted(exposed))}: set GATEWAY_API_KEY first"


if __name__ == "__main__":
    error = exposure_error(json.load(sys.stdin))
    if error:
        raise SystemExit(error)
