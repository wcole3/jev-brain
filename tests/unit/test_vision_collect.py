import dataclasses
import gzip
import hashlib
import io
import json
import re

import httpx
import PIL.Image
import pytest

from gateway.config import Settings
from gateway.images import decode_image
from gateway.labels import build_labels, save_labels
from gateway.layouts import load_layouts
from gateway.readout import GENERATE_PATH
from gateway.vision import load_vision
from scripts import vision_collect as vc
from scripts import vision_splits as vs
from scripts.collect import records
from tests.helpers import fake_vllm as fake_text_vllm

PROFILE = "gemma-4-31b"


def png(path, colour, size=(32, 24)):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = io.BytesIO()
    PIL.Image.new("RGB", size, colour).save(out, format="PNG")
    path.write_bytes(out.getvalue())


def row(i: int, image: str, options: list[str], answer: str) -> dict:
    question = {"type": "choice", "instructions": f"Question {i}?", "criteria": {k: f"option {k}" for k in options}}
    return {
        "id": f"bench:{i}",
        "benchmark": "Bench",
        "images": [image],
        "state": "{}",
        "questions": {"answer": question},
        "expected": {"answer": answer},
    }


ROWS = [  # rows 0 and 1 share an image, so they are one group
    row(0, "img/a.png", ["A", "B"], "A"),
    row(1, "img/a.png", ["A", "B", "C"], "C"),
    row(2, "img/b.png", ["A", "B"], "B"),
    row(3, "img/c.png", ["A", "B", "C", "D"], "Z"),
]


class FakeVllm:
    """vLLM stand-in: letter logprobs -0.001 * id, and prompt lengths expanded by `vision` (plus `extra`)."""

    def __init__(self, vision, extra: int = 0):
        self.vision, self.extra, self.paths = vision, extra, []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.paths.append(request.url.path)
        if request.url.path != GENERATE_PATH:
            return fake_text_vllm(request)
        body = json.loads(request.content)
        if body.get("return_token_ids"):
            images = [decode_image(p["url"], "probe") for p in body["content_parts"]]
            n = len(body["token_ids"]) + sum(self.vision.added(i) for i in images) + self.extra
            return httpx.Response(200, json={"prompt_token_ids": list(range(n))})
        ids = body["sampling_params"].get("logprob_token_ids", [])
        top = [{"token": f"token_id:{t}", "logprob": -0.001 * t} for t in ids]
        return httpx.Response(200, json={"choices": [{"logprobs": {"content": [{"top_logprobs": top}]}}]})


@pytest.fixture
def suite(tmp_path, monkeypatch, gemma_tok):
    """A 4-row suite with its manifests, label tables in tmp, and every output path moved to tmp."""
    root = tmp_path / "suite"
    for name, colour in (("a", "red"), ("b", "green"), ("c", "blue")):
        png(root / "img" / f"{name}.png", colour)
    rows_file = root / "vision-rows.jsonl"
    rows_file.write_text("".join(json.dumps(r) + "\n" for r in ROWS))
    splits = tmp_path / "splits"
    splits.mkdir()
    meta = {"suite_sha256": hashlib.sha256(rows_file.read_bytes()).hexdigest()}
    for name, ids in (("vision-dev", [r["id"] for r in ROWS]), ("vision-holdout", ["bench:2"])):
        (splits / f"{name}.json").write_text(json.dumps({"meta": meta, "ids": ids}))
    monkeypatch.setattr(vs, "SUITE", rows_file)
    monkeypatch.setattr(vs, "SPLITS", splits)
    monkeypatch.setattr(vs, "HOLDOUT_LOG", tmp_path / "holdout-log.md")
    monkeypatch.setattr(vc, "COLLECT", tmp_path / "collect")
    monkeypatch.setattr("gateway.app.AutoTokenizer.from_pretrained", lambda *a, **k: gemma_tok)
    data = tmp_path / "data"
    for name, layout in load_layouts().items():
        save_labels(data / PROFILE / name / "labels.json", build_labels(gemma_tok, layout))
    return tmp_path


def vision_with(kwargs: dict):
    s = Settings.from_profile(PROFILE)
    return load_vision(dataclasses.replace(s, systemone_images=True, mm_processor_kwargs=kwargs))


def args_for(tmp_path, *extra: str):
    return vc.parse_args(["--profile", PROFILE, "--label", "base", "--env", f"DATA_ROOT={tmp_path / 'data'}", *extra])


async def run(tmp_path, *extra: str, fake: FakeVllm | None = None) -> tuple[int, FakeVllm]:
    fake = fake or FakeVllm(vision_with({"max_soft_tokens": 560}))
    n = await vc.run(args_for(tmp_path, *extra), httpx.MockTransport(fake))
    return n, fake


def out_file(tmp_path, split="dev"):
    return tmp_path / "collect" / PROFILE / "base" / f"{split}.jsonl.gz"


async def test_record_shape_and_config_json(suite, gemma_tok):
    n, _ = await run(suite)
    recs = list(records(out_file(suite)))
    assert n == 4 and [r["id"] for r in recs] == [r["id"] for r in ROWS]
    first = recs[0]
    keys = {"id", "benchmark", "group", "layout", "status", "names", "gold", "input_tokens", "reads", "stamp"}
    assert set(first) == keys
    assert first["status"] == "ok" and first["benchmark"] == "Bench" and first["input_tokens"] > 0
    assert [r["group"] for r in recs] == ["bench:0", "bench:0", "bench:2", "bench:3"]
    assert [r["names"] for r in recs] == [["A", "B"], ["A", "B", "C"], ["A", "B"], ["A", "B", "C", "D"]]
    assert [r["gold"] for r in recs] == [0, 2, 1, None]
    label_ids = json.loads((suite / "data" / PROFILE / "header" / "labels.json").read_text())["ids"]
    want = [-0.001 * t for t in label_ids[:3]]
    assert recs[1]["reads"] == [{"perm": [0, 1, 2], "logprobs": want}, {"perm": [2, 1, 0], "logprobs": want}]
    config = json.loads((out_file(suite).parent / "config.json").read_text())
    assert config == {
        "profile": PROFILE,
        "label": "base",
        "layout": "header",
        "orders": "identity+reversed",
        "env": {"DATA_ROOT": str(suite / "data")},
        "split": "dev",
        "commit": vs.commit(),
    }


async def test_resume_skips_done_ids_and_a_truncated_tail(suite):
    await run(suite)
    path = out_file(suite)
    done = list(records(path))[:2]
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.write("".join(json.dumps(r) + "\n" for r in done) + json.dumps(done[0])[:40])
    path.write_bytes(path.read_bytes()[:-8])  # killed mid-write: half a line and no gzip trailer
    n, _ = await run(suite)
    assert n == 2
    assert [r["id"] for r in records(path)] == [r["id"] for r in ROWS]
    assert (await run(suite))[0] == 0


async def test_resume_refuses_another_config(suite):
    await run(suite)
    with pytest.raises(SystemExit, match="orders"):
        await run(suite, "--orders", "identity")


async def test_stamp_has_layout_labels_model_mm_kwargs_commit(suite):
    kwargs = {"max_soft_tokens": 280}
    await run(suite, "--env", f"MM_PROCESSOR_KWARGS={json.dumps(kwargs)}", fake=FakeVllm(vision_with(kwargs)))
    stamp = next(records(out_file(suite)))["stamp"]
    labels = suite / "data" / PROFILE / "header" / "labels.json"
    s = Settings.from_profile(PROFILE)
    assert stamp["layout_sha256"] == load_layouts()["header"].sha256
    assert stamp["labels_sha256"] == hashlib.sha256(labels.read_bytes()).hexdigest()
    assert stamp["hf_model"] == s.hf_model and stamp["hf_revision"] == s.hf_revision
    assert stamp["mm_processor_kwargs"] == kwargs
    assert stamp["commit"] == vs.commit()


async def test_self_check_refuses_a_count_mismatch(suite):
    fake = FakeVllm(vision_with({"max_soft_tokens": 560}), extra=1)
    with pytest.raises(SystemExit) as e:
        await run(suite, fake=fake)
    got, want = map(int, re.search(r"to (\d+) tokens, the gateway counts (\d+)", str(e.value)).groups())
    assert got == want + 1
    assert fake.paths == [GENERATE_PATH] and not out_file(suite).exists()


async def test_missing_label_table_is_refused(suite):
    (suite / "data" / PROFILE / "header" / "labels.json").unlink()
    fake = FakeVllm(vision_with({"max_soft_tokens": 560}))
    with pytest.raises(SystemExit, match="labels.json"):
        await run(suite, fake=fake)
    assert fake.paths == []


async def test_unreadable_image_is_recorded_unsupported_and_run_continues(suite):
    (suite / "suite" / "img" / "b.png").unlink()
    (suite / "suite" / "img" / "c.png").write_bytes(b"not an image")
    await run(suite)
    recs = {r["id"]: r for r in records(out_file(suite))}
    assert [recs[i]["status"] for i in ("bench:0", "bench:1")] == ["ok", "ok"]
    for i in ("bench:2", "bench:3"):
        assert recs[i]["status"] == "unsupported" and recs[i]["reads"] == []
    assert "b.png" in recs["bench:2"]["error"] and "not a decodable" in recs["bench:3"]["error"]
    assert recs["bench:2"]["names"] == ["A", "B"] and recs["bench:2"]["gold"] == 1


async def test_invalid_question_is_recorded_invalid(suite):
    rows = [ROWS[0] | {"questions": {"answer": {"type": "maybe"}}}]
    (suite / "suite" / "vision-rows.jsonl").write_text(json.dumps(rows[0]) + "\n")
    meta = {"suite_sha256": vs.suite_hash()}
    (suite / "splits" / "vision-dev.json").write_text(json.dumps({"meta": meta, "ids": ["bench:0"]}))
    await run(suite)
    rec = next(records(out_file(suite)))
    assert rec["status"] == "invalid" and rec["names"] == [] and rec["gold"] is None


async def test_holdout_needs_the_flag(suite):
    fake = FakeVllm(vision_with({"max_soft_tokens": 560}))
    with pytest.raises(SystemExit, match="--holdout"):
        await run(suite, "--split", "holdout", fake=fake)
    assert fake.paths == [] and not (suite / "holdout-log.md").exists()
    await run(suite, "--split", "holdout", "--holdout")
    assert [r["id"] for r in records(out_file(suite, "holdout"))] == ["bench:2"]
    assert "vision_collect" in (suite / "holdout-log.md").read_text()
