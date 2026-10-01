import dataclasses

from gateway.orders import option_orders
from scripts import collect
from tests.helpers import QUICKSTART, STATE

ROW = {"id": "r1", "source": "jevbench", "family": "f", "state": STATE, "questions": QUICKSTART, "gold": {}, "meta": {}}


def test_all_orders_cover_every_arm_without_repeats():
    for n in range(2, 12):
        orders = collect.all_orders(n)
        assert len({tuple(p) for p in orders}) == len(orders) <= 7
        for arm in collect.ARMS:
            assert all(p in orders for p in option_orders(n, arm))
    assert collect.all_orders(3) == [[0, 1, 2], [2, 1, 0], [2, 0, 1], [1, 2, 0]]


async def test_collect_one_reads_every_order(engine):
    rec = await collect.collect_one(engine, ROW, "decider_chat")
    assert rec["status"] == "ok" and rec["layout"] == "decider_chat"
    assert [r["perm"] for r in rec["questions"]["department"]] == collect.all_orders(3)
    assert rec["questions"]["is_urgent"][0]["logprobs"] == [0.0, -1.0]
    assert rec["stamp"]["profile"] == "qwen3.6-27b" and rec["input_tokens"] > 0


async def test_refusals_are_recorded_not_raised(engine):
    small = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, systemone_max_len=10))
    rec = await collect.collect_one(small, ROW, "decider_chat")
    assert rec["status"] == "unsupported" and "maximum context length" in rec["error"]
    bad = ROW | {"questions": {"q": {"type": "choice", "instructions": "x", "criteria": {"only": None}}}}
    assert (await collect.collect_one(engine, bad, "decider_chat"))["status"] == "unsupported"
    broken = ROW | {"questions": {"q": {"type": "maybe"}}}
    assert (await collect.collect_one(engine, broken, "decider_chat"))["status"] == "invalid"


async def test_collect_resumes(engine, tmp_path):
    path = tmp_path / "out.jsonl.gz"
    assert await collect.collect(engine, [ROW], ["decider_chat", "header"], path) == 2
    assert await collect.collect(engine, [ROW], ["decider_chat", "header"], path) == 0
    assert collect.done_keys(path) == {("r1", "decider_chat"), ("r1", "header")}
