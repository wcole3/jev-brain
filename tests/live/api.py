import os

import httpx


def auth() -> dict:
    key = os.environ.get("GATEWAY_API_KEY")
    return {"Authorization": f"Bearer {key}"} if key else {}


def post(url: str, body: dict) -> httpx.Response:
    return httpx.post(f"{url}/v1/systemone", json=body, headers=auth(), timeout=600)
