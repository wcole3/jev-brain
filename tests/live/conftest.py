import os

import httpx
import pytest


@pytest.fixture(scope="session")
def gateway_url() -> str:
    url = os.environ.get("GATEWAY_URL", "http://127.0.0.1:9000")
    try:
        httpx.get(f"{url}/health", timeout=5).raise_for_status()
    except httpx.HTTPError:
        pytest.skip("stack not running: docker compose --env-file profiles/<profile>.env up -d")
    return url


@pytest.fixture(scope="session")
def vllm_url() -> str:
    return os.environ.get("VLLM_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def served_model(gateway_url) -> str:
    return httpx.get(f"{gateway_url}/health", timeout=5).json()["served_model"]
