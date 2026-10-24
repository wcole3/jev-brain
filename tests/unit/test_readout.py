import asyncio
import json

import httpx
import pytest

from gateway.governor import Governor
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


def readout(handler, warm_up: str = "row", governor: Governor | None = None) -> Readout:
    client = httpx.AsyncClient(base_url="http://vllm", transport=httpx.MockTransport(handler))
    return Readout(client, "m", warm_min_prefix_tokens=512, warm_up=warm_up, governor=governor)


def decoding(duty: float, wave: int = 2) -> Governor:
    governor = Governor(duty=duty, wave=wave)
    governor.chat_started()
    return governor


async def test_reads_label_logprobs_in_label_order():
    seen = []
    out = await readout(fake_vllm(seen)).letter_logprobs([[1, 2], [1, 3]], [[30, 10], [20]], shared_len=1)
    assert out == [[-30.0, -10.0], [-20.0]]
    assert seen[0]["max_tokens"] == 1
    assert seen[0]["logprob_token_ids"] == [10, 20, 30]
    assert seen[0]["prompt"] == [[1, 2], [1, 3]]


async def test_priority_is_sent_only_when_set():
    seen = []
    await readout(fake_vllm(seen)).letter_logprobs([[1]], [[10]], shared_len=1)
    assert "priority" not in seen[0]
    client = httpx.AsyncClient(base_url="http://vllm", transport=httpx.MockTransport(fake_vllm(seen)))
    await Readout(client, "m", priority=1).letter_logprobs([[1]], [[10]], shared_len=1)
    assert seen[1]["priority"] == 1


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


async def test_warm_up_off_sends_every_row_at_once():
    seen, prompts = [], [[7] * 600 + [1], [7] * 600 + [2], [7] * 600 + [3]]
    out = await readout(fake_vllm(seen), warm_up="off").letter_logprobs(prompts, [[5], [5], [5]], shared_len=600)
    assert [b["prompt"] for b in seen] == [prompts] and len(out) == 3


def test_unknown_warm_up_is_refused():
    with pytest.raises(ValueError, match="'row', 'prefix' or 'off'"):
        Readout(httpx.AsyncClient(), "m", warm_up="bogus")


async def test_prefix_warm_up_sends_the_shared_prefix_alone_then_all_rows():
    seen, prompts = [], [[7] * 600 + [1], [7] * 600 + [2], [7] * 600 + [3]]
    out = await readout(fake_vllm(seen, by_prompt), warm_up="prefix").letter_logprobs(
        prompts, [[5], [5], [5]], shared_len=600
    )
    warm, read = seen
    assert warm["prompt"] == [[7] * 600] and warm["max_tokens"] == 1 and warm["add_special_tokens"] is False
    assert "logprob_token_ids" not in warm and "logprobs" not in warm
    assert read["prompt"] == prompts and read["logprob_token_ids"] == [5]
    assert out == [[by_prompt(p, 5)] for p in prompts]


@pytest.mark.parametrize(("prompts", "shared_len"), [([[7] * 600 + [1], [7] * 600 + [2]], 511), ([[7] * 600], 600)])
async def test_prefix_warm_up_is_skipped_for_a_short_prefix_or_one_row(prompts, shared_len):
    seen = []
    await readout(fake_vllm(seen), warm_up="prefix").letter_logprobs(prompts, [[5]] * len(prompts), shared_len)
    assert [b["prompt"] for b in seen] == [prompts]


async def test_prefix_warm_up_carries_priority_only_when_set():
    seen, prompts = [], [[7] * 600 + [1], [7] * 600 + [2]]
    for priority in (0, 1):
        client = httpx.AsyncClient(base_url="http://vllm", transport=httpx.MockTransport(fake_vllm(seen)))
        r = Readout(client, "m", warm_min_prefix_tokens=512, warm_up="prefix", priority=priority)
        await r.letter_logprobs(prompts, [[5], [5]], shared_len=600)
    assert ["priority" in b for b in seen] == [False, False, True, True]


async def test_prefix_warm_up_goes_through_the_governor():
    seen, prompts = [], [[7] * 600 + [1], [7] * 600 + [2]]
    r = readout(fake_vllm(seen), warm_up="prefix", governor=decoding(0.5, wave=1))
    await r.letter_logprobs(prompts, [[5], [5]], shared_len=600)
    assert [len(b["prompt"]) for b in seen] == [1, 1, 1]  # warm-up, then one row per wave


async def test_prefix_warm_up_too_long_becomes_a_refusal():
    def handler(request):
        return httpx.Response(400, text="This model's maximum context length is 32768 tokens.")

    with pytest.raises(RequestError, match="maximum context length"):
        await readout(handler, warm_up="prefix").letter_logprobs([[7] * 600, [7] * 600], [[5], [5]], shared_len=600)


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


PROMPTS = [[1], [2], [3], [4], [5]]


def by_prompt(prompt, token):
    return -float(token) - 1000.0 * prompt[0]


async def test_duty_one_sends_exactly_todays_calls():
    plain, governed = [], []
    labels = [[5], [5, 6], [5], [6], [5]]
    want = await readout(fake_vllm(plain, by_prompt), warm_up="off").letter_logprobs(PROMPTS, labels, shared_len=0)
    out = await readout(fake_vllm(governed, by_prompt), warm_up="off", governor=decoding(1.0)).letter_logprobs(
        PROMPTS, labels, shared_len=0
    )
    assert governed == plain and out == want


async def test_waves_split_rows_while_chat_decodes():
    seen = []
    labels = [[5]] * 5
    want = await readout(fake_vllm([], by_prompt), warm_up="off").letter_logprobs(PROMPTS, labels, shared_len=0)
    r = readout(fake_vllm(seen, by_prompt), warm_up="off", governor=decoding(0.5))
    out = await r.letter_logprobs(PROMPTS, labels, shared_len=0)
    assert [len(b["prompt"]) for b in seen] == [2, 2, 1]
    assert out == want


async def test_waves_and_label_chunks_keep_row_order(qwen_tok):
    ids = label_table(qwen_tok).ids
    labels = [ids[:3], ids[:200], ids[:2], ids[100:200], ids[:130]]
    want = await readout(fake_vllm([], by_prompt), warm_up="off").letter_logprobs(PROMPTS, labels, shared_len=0)
    r = readout(fake_vllm([], by_prompt), warm_up="off", governor=decoding(0.5))
    assert await r.letter_logprobs(PROMPTS, labels, shared_len=0) == want


async def test_no_waves_when_no_chat():
    seen = []
    r = readout(fake_vllm(seen, by_prompt), warm_up="off", governor=Governor(duty=0.5, wave=2))
    await r.letter_logprobs(PROMPTS, [[5]] * 5, shared_len=0)
    assert [len(b["prompt"]) for b in seen] == [5]


PARTS = [{"type": "image_url", "url": "data:image/png;base64,AAAA", "uuid": "abc"}]


def fake_generate(seen: list, drop: int | None = None):
    """Answers each label id in the request with its negated id; `drop` is left out of the answer."""

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        seen.append((request.url.path, body))
        ids = body["sampling_params"].get("logprob_token_ids", [])  # the warm-up call reads no labels
        assert len(ids) <= MAX_LABEL_IDS
        top = [{"token_id": t, "logprob": -float(t)} for t in ids if t != drop]
        return httpx.Response(200, json={"choices": [{"logprobs": {"content": [{"top_logprobs": top}]}}]})

    return handler


async def test_image_rows_go_one_per_call_with_their_images():
    seen = []
    out = await readout(fake_generate(seen)).image_logprobs([[1, 2], [1, 3]], [[30, 10], [20]], 1, 1, PARTS, PARTS)
    assert out == [[-30.0, -10.0], [-20.0]]
    assert [p for p, _ in seen] == ["/inference/v1/generate"] * 2
    body = next(b for _, b in seen if b["token_ids"] == [1, 2])
    assert body["content_parts"] == PARTS and body["sampling_params"]["logprob_token_ids"] == [10, 30, 0]
    assert body["sampling_params"]["logprobs"] == 3 and body["sampling_params"]["max_tokens"] == 1


async def test_the_spare_id_is_never_a_label():
    seen = []
    await readout(fake_generate(seen)).image_logprobs([[1]], [[0, 1, 2]], 1, 1, PARTS, PARTS)
    assert seen[0][1]["sampling_params"]["logprob_token_ids"] == [0, 1, 2, 3]


async def test_prefix_warm_up_sends_the_shared_images_first():
    seen = []
    rows = [[5] * 20 + [k] for k in range(3)]
    await readout(fake_generate(seen), warm_up="prefix").image_logprobs(rows, [[10]] * 3, 20, 600, PARTS, PARTS)
    first = seen[0][1]
    assert first["token_ids"] == [5] * 20 and first["content_parts"] == PARTS
    assert "logprob_token_ids" not in first["sampling_params"] and first["sampling_params"]["max_tokens"] == 1
    assert len(seen) == 4


async def test_warm_up_threshold_counts_expanded_tokens():
    seen = []
    rows = [[5, 1], [5, 2]]
    await readout(fake_generate(seen), warm_up="prefix").image_logprobs(rows, [[10]] * 2, 1, 100, PARTS, PARTS)
    assert len(seen) == 2  # 100 < 512: no warm-up


async def test_row_warm_up_reads_row_one_first():
    log, answer = [], fake_generate([])

    async def handler(request: httpx.Request) -> httpx.Response:
        k = json.loads(request.content)["token_ids"][-1]  # the row number
        log.append(("start", k))
        await asyncio.sleep(0)  # lets rows sent together overlap
        log.append(("end", k))
        return answer(request)

    rows = [[5] * 20 + [k] for k in range(3)]
    await readout(handler, warm_up="row").image_logprobs(rows, [[10]] * 3, 20, 600, PARTS, PARTS)
    assert log.index(("end", 0)) < min(log.index(("start", k)) for k in (1, 2))


async def test_more_than_127_labels_split_across_calls():
    seen = []
    labels = list(range(1, 201))
    out = await readout(fake_generate(seen)).image_logprobs([[1]], [labels], 1, 1, PARTS, PARTS)
    assert out == [[-float(i) for i in labels]] and len(seen) == 2
    assert all(len(b["sampling_params"]["logprob_token_ids"]) <= MAX_LABEL_IDS for _, b in seen)


async def test_a_later_chunks_spare_id_does_not_overwrite_an_earlier_label():
    def handler(request: httpx.Request) -> httpx.Response:
        ids = json.loads(request.content)["sampling_params"]["logprob_token_ids"]
        top = [{"token_id": t, "logprob": -float(t)} for t in ids[:-1]]
        top.append({"token_id": ids[-1], "logprob": 999.0})  # the spare answers differently
        return httpx.Response(200, json={"choices": [{"logprobs": {"content": [{"top_logprobs": top}]}}]})

    labels = list(range(201))  # chunk 2 holds 127..200 and its spare is 0, a label of chunk 1
    out = await readout(handler).image_logprobs([[1]], [labels], 1, 1, PARTS, PARTS)
    assert out == [[-float(i) for i in labels]]


async def test_a_missing_label_is_an_error():
    with pytest.raises(RuntimeError, match="30"):
        await readout(fake_generate([], drop=30)).image_logprobs([[1]], [[30, 10]], 1, 1, PARTS, PARTS)


async def test_image_rows_carry_priority_only_when_set():
    seen = []
    await readout(fake_generate(seen)).image_logprobs([[1]], [[10]], 1, 1, PARTS, PARTS)
    assert "priority" not in seen[0][1]
    client = httpx.AsyncClient(base_url="http://vllm", transport=httpx.MockTransport(fake_generate(seen)))
    await Readout(client, "m", priority=1).image_logprobs([[1]], [[10]], 1, 1, PARTS, PARTS)
    assert seen[1][1]["priority"] == 1


class CountingGovernor(Governor):
    calls = 0

    async def call(self, fn):
        self.calls += 1
        return await super().call(fn)


async def test_image_calls_go_through_the_governor():
    seen, governor = [], CountingGovernor(duty=0.5, wave=1)
    governor.chat_started()
    rows = [[5] * 20 + [k] for k in range(2)]
    r = readout(fake_generate(seen), warm_up="prefix", governor=governor)
    await r.image_logprobs(rows, [[10]] * 2, 20, 600, PARTS, PARTS)
    assert len(seen) == 3 and governor.calls == 3  # warm-up, then one call per row
