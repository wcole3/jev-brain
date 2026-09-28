import httpx


def post(url: str, body: dict) -> httpx.Response:
    return httpx.post(f"{url}/v1/systemone", json=body, timeout=600)
