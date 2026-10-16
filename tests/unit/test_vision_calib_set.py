import hashlib
import io
import json
import random

import PIL.Image

from gateway.images import decode_image
from gateway.layouts import load_layouts
from gateway.schema import Question
from scripts import vision_calib_set as cs
from scripts import vision_collect as vc


def noise(seed: int, fmt: str = "PNG", size=(64, 48), **save) -> bytes:
    """A distinct, detailed image: seeded random pixels."""
    rng = random.Random(seed)
    im = PIL.Image.new("RGB", size)
    im.putdata([(rng.randrange(256), rng.randrange(256), rng.randrange(256)) for _ in range(size[0] * size[1])])
    im = im.resize((size[0] * 4, size[1] * 4), PIL.Image.Resampling.BILINEAR)
    out = io.BytesIO()
    im.save(out, format=fmt, **save)
    return out.getvalue()


def reencode(data: bytes, fmt: str, **save) -> bytes:
    out = io.BytesIO()
    PIL.Image.open(io.BytesIO(data)).convert("RGB").save(out, format=fmt, **save)
    return out.getvalue()


def item(i: int, image: bytes, n_options: int = 4) -> cs.Item:
    return cs.Item(str(i), f"Question {i}?", [f"choice {k}" for k in range(n_options)], i % n_options, image)


def fake(name: str, items: list[cs.Item] | Exception) -> cs.Source:
    def read():
        if isinstance(items, Exception):
            raise items
        return iter(items)

    return cs.Source(name, f"fake/{name}", "rev", "train", "", read)


def suite_of(tmp_path, images: list[bytes]) -> cs.SuiteIndex:
    folder = tmp_path / "suite"
    rows = []
    for n, data in enumerate(images):
        (folder / "img").mkdir(parents=True, exist_ok=True)
        (folder / f"img/{n}.png").write_bytes(data)
        rows.append({"id": f"s:{n}", "images": [f"img/{n}.png"]})
    (folder / "rows.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    return cs.suite_index(folder / "rows.jsonl", tmp_path / "fingerprints.json")


def build(tmp_path, sources, suite, total):
    out, manifest = tmp_path / "out", tmp_path / "vision-calib.json"
    cs.build(sources, suite, out, manifest, total=total)
    rows = [json.loads(line) for line in (out / "rows.jsonl").read_text().splitlines()]
    return rows, json.loads(manifest.read_text())


def by_name(manifest: dict) -> dict:
    return {s["name"]: s for s in manifest["meta"]["sources"]}


def test_rows_are_in_suite_format_and_load_in_collect(tmp_path):
    suite = suite_of(tmp_path, [noise(99)])
    rows, manifest = build(tmp_path, [fake("aokvqa", [item(i, noise(i)) for i in range(4)])], suite, total=3)
    source = vc.file_source(tmp_path / "out/rows.jsonl")
    assert [r["id"] for r in source.rows] == manifest["ids"] and len(rows) == manifest["meta"]["count"] == 3
    layout = load_layouts()["header"]
    for row in source.rows:
        assert row["benchmark"] == "aokvqa" and row["state"] == {} and row["id"].startswith("aokvqa:")
        Question.model_validate(row["questions"]["answer"])
        assert vc.option_names(row, layout) == ["A", "B", "C", "D"]
        assert row["expected"]["answer"] in "ABCD"
        path = source.image_dir / row["images"][0]
        decode_image(vc.data_url(path), "images[0]")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["image_sha256"][row["id"]]
    assert manifest["meta"]["seed"] == 20261016 and manifest["meta"]["suite_sha256"] == suite.suite_sha256


def test_a_hint_is_the_row_state_and_the_question_stays_alone(tmp_path):
    suite = suite_of(tmp_path, [noise(99)])
    hinted = cs.Item("0", "Which is north?", ["a", "b"], 0, noise(0), "Look at the map.")
    rows, _ = build(tmp_path, [fake("scienceqa", [hinted, item(1, noise(1))])], suite, total=2)
    assert [(r["state"], r["questions"]["answer"]["instructions"]) for r in rows] == [
        ("Look at the map.", "Which is north?"),
        ({}, "Question 1?"),
    ]


def test_byte_identical_suite_image_is_dropped(tmp_path):
    copy = noise(1)
    suite = suite_of(tmp_path, [copy])
    rows, manifest = build(tmp_path, [fake("ai2d", [item(0, copy), item(1, noise(2))])], suite, total=2)
    assert [r["id"] for r in rows] == ["ai2d:1"]
    assert by_name(manifest)["ai2d"]["dropped_suite"] == 1


def test_reencoded_suite_image_is_dropped_by_fingerprint(tmp_path):
    original = noise(1)
    suite = suite_of(tmp_path, [original])
    jpeg = reencode(original, "JPEG", quality=90)
    assert jpeg != original
    rows, manifest = build(tmp_path, [fake("ai2d", [item(0, jpeg), item(1, noise(2))])], suite, total=2)
    assert [r["id"] for r in rows] == ["ai2d:1"]
    assert by_name(manifest)["ai2d"]["dropped_suite"] == 1


def test_lossless_copy_has_the_same_fingerprint():
    original = noise(3)
    assert cs.fingerprint(reencode(original, "WEBP", lossless=True)) == cs.fingerprint(original)
    assert cs.fingerprint(noise(4)) != cs.fingerprint(original)


def test_unavailable_source_shifts_its_share_and_is_recorded(tmp_path):
    suite = suite_of(tmp_path, [noise(99)])
    sources = [
        fake("scienceqa", [item(i, noise(i)) for i in range(10)]),
        fake("ai2d", cs.Unavailable("gated")),
        fake("aokvqa", [item(i, noise(100 + i)) for i in range(10)]),
    ]
    rows, manifest = build(tmp_path, sources, suite, total=9)
    meta = by_name(manifest)
    assert len(rows) == 9 and meta["ai2d"]["taken"] == 0 and "gated" in meta["ai2d"]["note"]
    assert sorted([meta["scienceqa"]["taken"], meta["aokvqa"]["taken"]]) == [4, 5]


def test_short_source_gives_its_deficit_to_the_others(tmp_path):
    suite = suite_of(tmp_path, [noise(99)])
    sources = [fake("a", [item(i, noise(i)) for i in range(2)]), fake("b", [item(i, noise(50 + i)) for i in range(10)])]
    _, manifest = build(tmp_path, sources, suite, total=8)
    assert {s["name"]: s["taken"] for s in manifest["meta"]["sources"]} == {"a": 2, "b": 6}


def test_more_than_10_options_are_skipped(tmp_path):
    suite = suite_of(tmp_path, [noise(99)])
    items = [item(0, noise(0), n_options=11), item(1, noise(1), n_options=10)]
    rows, manifest = build(tmp_path, [fake("scienceqa", items)], suite, total=2)
    assert [r["id"] for r in rows] == ["scienceqa:1"]
    assert list(rows[0]["questions"]["answer"]["criteria"]) == list("ABCDEFGHIJ")
    assert by_name(manifest)["scienceqa"]["skipped"]["choices"] == 1


def test_undecodable_and_repeated_images_are_skipped(tmp_path):
    suite = suite_of(tmp_path, [noise(99)])
    same = noise(5)
    items = [item(0, b"not an image"), item(1, same), item(2, same)]
    rows, manifest = build(tmp_path, [fake("aokvqa", items)], suite, total=3)
    assert len(rows) == 1
    assert by_name(manifest)["aokvqa"]["skipped"] == {"undecodable": 1, "repeat_image": 1}


def test_non_passthrough_format_is_reencoded_png(tmp_path):
    suite = suite_of(tmp_path, [noise(99)])
    rows, _ = build(tmp_path, [fake("ai2d", [item(0, noise(6, fmt="BMP"))])], suite, total=1)
    path = tmp_path / "out" / rows[0]["images"][0]
    assert path.suffix == ".png" and PIL.Image.open(path).format == "PNG"


def test_suite_fingerprints_are_cached_by_suite_hash(tmp_path):
    first = suite_of(tmp_path, [noise(1)])
    cache = json.loads((tmp_path / "fingerprints.json").read_text())
    assert cache["suite_sha256"] and len(cache["images"]) == 1
    (tmp_path / "suite/img/0.png").unlink()  # a cache hit must not reread the images
    again = cs.suite_index(tmp_path / "suite/rows.jsonl", tmp_path / "fingerprints.json")
    assert again.sha256 == first.sha256 and again.fingerprints == first.fingerprints
