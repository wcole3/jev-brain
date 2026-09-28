import httpx
import pytest

pytestmark = pytest.mark.live


def test_chat_streams_with_thinking_on(gateway_url, served_model):
    body = {
        "model": served_model,
        "messages": [{"role": "user", "content": "What is 17 * 23?"}],
        "stream": True,
        "max_tokens": 512,
    }
    with httpx.stream("POST", f"{gateway_url}/v1/chat/completions", json=body, timeout=600) as r:
        assert r.status_code == 200
        lines = [line for line in r.iter_lines() if line.startswith("data: ")]
    assert lines[-1] == "data: [DONE]"
    assert len(lines) > 3
