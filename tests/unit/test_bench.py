import datetime
import json

import httpx
import pytest

from scripts.bench import chat_once, parse_args, run_suffix


def sse(*chunks: dict) -> bytes:
    return "".join(f"data: {json.dumps(c)}\n\n" for c in chunks).encode() + b"data: [DONE]\n\n"


async def test_chat_once_counts_tokens_from_usage_not_chunks():
    body = sse(
        {"choices": [{"delta": {"role": "assistant", "content": ""}}]},
        {"choices": [{"delta": {"reasoning": "Hmm"}}]},
        {"choices": [{"delta": {"content": "2, 3, 5"}}]},
        {"choices": [], "usage": {"completion_tokens": 9}},
    )
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content))
        return httpx.Response(200, content=body)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://gw") as client:
        ttft, rate = await chat_once(client, "m", "primes")
    assert ttft >= 0 and rate > 0
    assert seen["stream_options"] == {"include_usage": True}


async def test_chat_once_refuses_a_stream_without_usage():
    body = sse({"choices": [{"delta": {"content": "2"}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, content=body)),
                                 base_url="http://gw") as client:
        with pytest.raises(ValueError, match="usage"):
            await chat_once(client, "m", "primes")


def test_parse_args_chat_defaults_off():
    assert parse_args(["--profile", "p"]).chat is False


def test_parse_args_chat_flag_turns_it_on():
    assert parse_args(["--profile", "p", "--chat"]).chat is True


def test_parse_args_gateway_needs_a_profile():
    with pytest.raises(SystemExit):
        parse_args([])


def test_parse_args_jev_needs_no_profile():
    assert parse_args(["--target", "jev"]).target == "jev"


def test_parse_args_jev_rejects_chat():
    with pytest.raises(SystemExit):
        parse_args(["--target", "jev", "--chat"])


def test_run_suffix_is_utc_time_plus_flags():
    started = datetime.datetime(2026, 9, 29, 21, 9, 57, tzinfo=datetime.UTC)
    assert run_suffix(started, quick=False, jevbench_only=False) == "2026-09-29T210957Z"
    assert run_suffix(started, quick=True, jevbench_only=False) == "2026-09-29T210957Z-quick"
    assert run_suffix(started, quick=True, jevbench_only=True) == "2026-09-29T210957Z-quick-jevbench"
