import json

import httpx
import pytest

from gateway.labels import label_table
from gateway.readout import MAX_LABEL_IDS, Readout
from gateway.schema import RequestError


def same_for_every_prompt(prompt: list[int], token: int) -> float:
    return -float(token)


def fake_vllm(seen: list, logprob=same_for_every_prompt):
    """Choices come back in reverse index order, like a server that may reorder them."""

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        seen.append(body)
        ids = body.get("logprob_token_ids", [])  # the warm-up call reads no labels
        assert len(ids) <= MAX_LABEL_IDS
        tops = [{f"token_id:{t}": logprob(p, t) for t in ids} for p in body["prompt"]]
        choices = [{"index": i, "logprobs": {"top_logprobs": [top]}} for i, top in enumerate(tops)]
        return httpx.Response(200, json={"choices": choices[::-1]})

    return handler


def readout(handler) -> Readout:
    client = httpx.AsyncClient(base_url="http://vllm", transport=httpx.MockTransport(handler))
    return Readout(client, "m", warm_min_prefix_tokens=512)


async def test_reads_label_logprobs_in_label_order():
    seen = []
    out = await readout(fake_vllm(seen)).letter_logprobs([[1, 2], [1, 3]], [[30, 10], [20]], shared_len=1)
    assert out == [[-30.0, -10.0], [-20.0]]
    assert seen[0]["max_tokens"] == 1
    assert seen[0]["logprob_token_ids"] == [10, 20, 30]
    assert seen[0]["prompt"] == [[1, 2], [1, 3]]


async def test_more_than_128_labels_are_split_across_calls():
    seen = []
    ids = list(range(200))
    out = await readout(fake_vllm(seen)).letter_logprobs([[1]], [ids], shared_len=0)
    assert [len(b["logprob_token_ids"]) for b in seen] == [128, 72]
    assert out == [[-float(i) for i in ids]]


async def test_wide_label_chunks_go_only_to_the_rows_that_read_them(qwen_tok):
    """A 200-option choice between two small questions: its second chunk of 72 ids is sent with its row alone."""
    ids = label_table(qwen_tok).ids

    def by_prompt(prompt, token):
        return -float(token) - 1000.0 * prompt[0]

    seen = []
    prompts, label_ids = [[1], [2], [3]], [ids[:3], ids[:200], ids[:2]]
    out = await readout(fake_vllm(seen, by_prompt)).letter_logprobs(prompts, label_ids, shared_len=0)
    assert [(b["prompt"], len(b["logprob_token_ids"])) for b in seen] == [(prompts, 128), ([[2]], 72)]
    unrouted = [[by_prompt(p, t) for t in row] for p, row in zip(prompts, label_ids)]  # every chunk with every row
    assert out == unrouted


async def test_long_shared_prefix_warms_the_first_row_alone():
    seen = []
    await readout(fake_vllm(seen)).letter_logprobs([[1], [2], [3]], [[5], [5], [5]], shared_len=600)
    assert [len(b["prompt"]) for b in seen] == [1, 2]


async def test_context_too_long_becomes_a_refusal():
    def handler(request):
        return httpx.Response(400, text="This model's maximum context length is 32768 tokens.")

    with pytest.raises(RequestError, match="maximum context length"):
        await readout(handler).letter_logprobs([[1]], [[5]], shared_len=0)


async def test_unreachable_vllm_raises_transport_error():
    def handler(request):
        raise httpx.ConnectError("down")

    with pytest.raises(httpx.TransportError):
        await readout(handler).letter_logprobs([[1]], [[5]], shared_len=0)
