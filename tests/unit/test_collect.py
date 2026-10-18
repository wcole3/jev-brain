import dataclasses
import hashlib

import httpx
import pytest

from gateway.config import ROOT, Settings
from gateway.labels import save_labels
from gateway.layouts import load_layout
from gateway.orders import option_orders
from scripts import collect
from scripts.build_labels import table_for
from tests.helpers import QUICKSTART, STATE, FavourFirstLabel, fake_vllm

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
    assert rec["stamp"]["warm_up"] == "row" and rec["stamp"]["prefix_pad_always"] is False


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


async def test_resume_repairs_a_truncated_file(engine, tmp_path):
    path = tmp_path / "out.jsonl.gz"
    await collect.collect(engine, [ROW | {"id": "a"}, ROW | {"id": "b"}], ["decider_chat"], path)
    path.write_bytes(path.read_bytes()[:-8])  # killed before the gzip trailer was written
    assert await collect.collect(engine, [ROW | {"id": "c"}], ["decider_chat"], path) == 1
    assert [r["id"] for r in collect.records(path)] == ["a", "b", "c"]


async def test_resume_refuses_a_file_from_other_settings(engine, tmp_path):
    path = tmp_path / "out.jsonl.gz"
    await collect.collect(engine, [ROW], ["decider_chat"], path)
    other = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, warm_up="off"))
    with pytest.raises(SystemExit, match="warm_up"):
        await collect.collect(other, [ROW | {"id": "r2"}], ["decider_chat"], path)
    assert collect.done_keys(path) == {("r1", "decider_chat")}


class FlakyReadout(FavourFirstLabel):
    """Fails the first `failures` calls with a vLLM 503, then answers."""

    def __init__(self, failures):
        super().__init__()
        self.failures = failures

    async def letter_logprobs(self, prompts, label_ids, shared_len):
        if self.failures:
            self.failures -= 1
            request = httpx.Request("POST", "http://vllm/v1/completions")
            raise httpx.HTTPStatusError("503", request=request, response=httpx.Response(503, request=request))
        return await super().letter_logprobs(prompts, label_ids, shared_len)


async def test_vllm_hiccups_are_retried(engine, monkeypatch):
    monkeypatch.setattr(collect, "BACKOFF", 0)
    flaky = dataclasses.replace(engine, readout=FlakyReadout(failures=2))
    assert (await collect.collect_retrying(flaky, ROW, "decider_chat"))["status"] == "ok"


async def test_a_lasting_failure_is_raised_not_recorded(engine, monkeypatch, tmp_path):
    monkeypatch.setattr(collect, "BACKOFF", 0)
    down = dataclasses.replace(engine, readout=FlakyReadout(failures=collect.ATTEMPTS))
    with pytest.raises(httpx.HTTPStatusError):
        await collect.collect(down, [ROW], ["decider_chat"], tmp_path / "out.jsonl.gz")
    assert collect.done_keys(tmp_path / "out.jsonl.gz") == set()


async def test_collect_refuses_a_non_identity_profile(engine, tmp_path):
    other = dataclasses.replace(engine, settings=dataclasses.replace(engine.settings, option_orders="identity+reversed"))
    with pytest.raises(SystemExit, match="option_orders"):
        await collect.collect(other, [ROW], ["decider_chat"], tmp_path / "out.jsonl.gz")


PROFILE = "qwen3.6-27b"
EXPERIMENTS = ROOT / "prompts" / "experiments"
STAMP_KEYS = {"tokenizer_sha256", "layout_sha256", "hf_revision", "prefix_pad", "prefix_block", "profile",
              "prefix_pad_always", "warm_up", "systemone_max_len"}


@pytest.fixture
def cli(tmp_path, monkeypatch, qwen_tok):
    """collect.main on two rows against a fake vLLM, output under tmp_path."""
    monkeypatch.setattr(collect, "COLLECT", tmp_path)
    monkeypatch.setattr(collect, "rows_for", lambda split: [ROW, ROW | {"id": "r2"}])
    monkeypatch.setattr("gateway.app.AutoTokenizer.from_pretrained", lambda *a, **k: qwen_tok)
    return tmp_path


async def run_cli(*argv: str) -> None:
    args = collect.parse_args(["--profile", PROFILE, "--split", "calib", *argv])
    await collect.main(args, httpx.MockTransport(fake_vllm))


async def test_layout_file_collect_records_tags_and_stamp(cli, qwen_tok):
    path = EXPERIMENTS / "labels-digits.toml"
    await run_cli("--layout-file", str(path), "--orders", "identity+reversed", "--label", "digits")
    recs = list(collect.records(cli / PROFILE / "calib-digits.jsonl.gz"))
    assert [r["id"] for r in recs] == ["r1", "r2"] and {r["layout"] for r in recs} == {"labels-digits"}
    on_disk = cli / "labels.json"  # the bytes build_labels.py would write for this layout
    save_labels(on_disk, table_for(qwen_tok, load_layout(path), Settings.from_profile(PROFILE)))
    for r in recs:
        assert r["status"] == "ok" and r["label_tags"] == dict.fromkeys(QUICKSTART, "set")
        assert [q["perm"] for q in r["questions"]["department"]] == [[0, 1, 2], [2, 1, 0]]
        assert all(len(reads) == 2 for reads in r["questions"].values())
        assert r["stamp"]["layout_file"] == "prompts/experiments/labels-digits.toml"
        assert r["stamp"]["orders"] == "identity+reversed"
        assert r["stamp"]["labels_sha256"] == hashlib.sha256(on_disk.read_bytes()).hexdigest()


async def test_resume_refuses_other_layout_file(cli):
    await run_cli("--layout-file", str(EXPERIMENTS / "labels-digits.toml"), "--label", "x")
    with pytest.raises(SystemExit, match=r"other \[.*'labels_sha256', 'layout_file'"):
        await run_cli("--layout-file", str(EXPERIMENTS / "labels-lower.toml"), "--label", "x")


async def test_default_collect_unchanged(cli):
    await run_cli()
    recs = list(collect.records(cli / PROFILE / "calib.jsonl.gz"))
    assert sorted({r["layout"] for r in recs}) == ["decider_chat", "header", "question_first"] and len(recs) == 6
    for r in recs:
        assert set(r) == {"id", "layout", "stamp", "status", "input_tokens", "questions"}
        assert set(r["stamp"]) == STAMP_KEYS
        assert [q["perm"] for q in r["questions"]["department"]] == collect.all_orders(3)


def test_layout_file_needs_a_label(capsys):
    with pytest.raises(SystemExit):
        collect.parse_args(["--profile", PROFILE, "--split", "calib", "--layout-file", "x.toml"])
    assert "--label" in capsys.readouterr().err
