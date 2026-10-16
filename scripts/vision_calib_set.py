"""A non-suite image calibration set: seeded multiple-choice rows from public train splits, suite images dropped.

usage: uv run python scripts/vision_calib_set.py build
Writes .cache/vision-calib/rows.jsonl and img/ (suite row format) and the manifest data/splits/vision-calib.json.
"""

import hashlib
import io
import json
import shutil
import sys
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import PIL.Image

from gateway.config import ROOT
from gateway.images import ALLOWED_FORMATS, MAX_DECODE_PIXELS
from scripts import vision_splits
from scripts.vision_calib_sources import SOURCES, Item, Source, Unavailable

OUT = ROOT / ".cache/vision-calib"
FINGERPRINTS = OUT / "suite-fingerprints.json"
MANIFEST = vision_splits.SPLITS / "vision-calib.json"
SEED = vision_splits.SEED
TOTAL = 1800
LETTERS = "ABCDEFGHIJ"  # at most 10 options
THUMB = (16, 16)
NEAR = 2.0  # mean |gray difference| of the 16x16 thumbs under which a lossy copy counts as the suite image
DEDUPE = ("dropped when the image matches a suite image by byte sha256, by 16x16 gray thumb sha256, or by thumb "
          "mean |difference| <= near_mean_abs (exact thumbs miss JPEG re-encodes)")
EXTENSIONS = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp", "GIF": "gif"}
assert set(EXTENSIONS) == set(ALLOWED_FORMATS)


def thumb(im: PIL.Image.Image) -> bytes:
    return im.convert("L").resize(THUMB, PIL.Image.Resampling.BOX).tobytes()


def fingerprint(image_bytes: bytes) -> str:
    """SHA-256 of the image as 16x16 grayscale, so a lossless re-encode matches."""
    return hashlib.sha256(thumb(PIL.Image.open(io.BytesIO(image_bytes)))).hexdigest()


@dataclass
class SuiteIndex:
    suite_sha256: str
    sha256: set[str]
    fingerprints: set[str]
    thumbs: np.ndarray  # one 256-value row per suite image

    def matches(self, sha: str, small: bytes) -> bool:
        """Same bytes, same thumb, or a thumb within NEAR: exact thumbs miss JPEG re-encodes (off by 1 gray level)."""
        if sha in self.sha256 or hashlib.sha256(small).hexdigest() in self.fingerprints:
            return True
        diff = np.abs(self.thumbs - np.frombuffer(small, np.uint8).astype(np.int16))
        return bool(len(diff) and diff.mean(axis=1).min() <= NEAR)


def suite_images(rows_path: Path) -> dict[str, list[str]]:
    """Suite image path -> [byte sha256, thumb hex]; an undecodable image keeps only its byte hash."""
    paths = sorted({p for line in rows_path.read_text().splitlines() if line for p in json.loads(line)["images"]})
    out = {}
    for p in paths:
        data = (rows_path.parent / p).read_bytes()
        try:
            small = thumb(PIL.Image.open(io.BytesIO(data))).hex()
        except (OSError, ValueError, PIL.Image.DecompressionBombError):
            small = ""
        out[p] = [hashlib.sha256(data).hexdigest(), small]
    return out


def suite_index(rows_path: Path = vision_splits.SUITE, cache: Path = FINGERPRINTS) -> SuiteIndex:
    """The suite's image hashes and thumbs, computed once per suite file hash."""
    key = hashlib.sha256(rows_path.read_bytes()).hexdigest()
    stored = json.loads(cache.read_text()) if cache.exists() else {}
    if stored.get("suite_sha256") != key:
        stored = {"suite_sha256": key, "images": suite_images(rows_path)}
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(stored))
    smalls = [bytes.fromhex(t) for _, t in stored["images"].values() if t]
    return SuiteIndex(
        key,
        {s for s, _ in stored["images"].values()},
        {hashlib.sha256(t).hexdigest() for t in smalls},
        np.array([np.frombuffer(t, np.uint8) for t in smalls], np.int16).reshape(len(smalls), -1),
    )


@dataclass
class Taken:
    row: dict
    data: bytes
    sha: str


@dataclass
class Pool:
    """One source's items in seeded order, accepted lazily; counts what it drops and skips."""

    items: Iterator[Item]
    name: str
    suite: SuiteIndex
    seen_images: set[str]
    taken: list[Taken] = field(default_factory=list)
    dropped_suite: int = 0
    skipped: Counter = field(default_factory=Counter)
    exhausted: bool = False

    def take(self, k: int) -> None:
        goal = len(self.taken) + k
        while len(self.taken) < goal:
            if (it := next(self.items, None)) is None:
                self.exhausted = True
                return
            self.consider(it)

    def consider(self, it: Item) -> None:
        if not 2 <= len(it.choices) <= len(LETTERS) or not 0 <= it.answer < len(it.choices) or not it.question:
            self.skipped["choices"] += 1
            return
        try:
            im = PIL.Image.open(io.BytesIO(it.image))
            if im.width * im.height > MAX_DECODE_PIXELS:
                raise PIL.Image.DecompressionBombError
            im.load()
        except PIL.Image.DecompressionBombError:
            self.skipped["too_large"] += 1
            return
        except (OSError, ValueError, SyntaxError):
            self.skipped["undecodable"] += 1
            return
        sha = hashlib.sha256(it.image).hexdigest()
        if self.suite.matches(sha, thumb(im)):
            self.dropped_suite += 1
        elif sha in self.seen_images:
            self.skipped["repeat_image"] += 1
        else:
            self.seen_images.add(sha)
            data, ext = image_file(im, it.image)
            written = hashlib.sha256(data).hexdigest()
            self.taken.append(Taken(row(self.name, it, f"img/{written}.{ext}"), data, written))


def image_file(im: PIL.Image.Image, original: bytes) -> tuple[bytes, str]:
    """The original bytes for a pass-through format, else a PNG re-encode."""
    if im.format in EXTENSIONS:
        return original, EXTENSIONS[im.format]
    out = io.BytesIO()
    im.save(out, format="PNG")
    return out.getvalue(), "png"


def row(name: str, it: Item, image: str) -> dict:
    criteria = dict(zip(LETTERS, it.choices, strict=False))
    question = {"type": "choice", "instructions": it.question, "criteria": criteria}
    return {"id": f"{name}:{it.source_id}", "benchmark": name, "images": [image], "state": it.state,
            "questions": {"answer": question}, "expected": {"answer": LETTERS[it.answer]}}


def seeded(name: str, items: Iterable[Item], seed: int) -> Iterator[Item]:
    return iter(sorted(items, key=lambda it: vision_splits.digest(seed, f"{name}:{it.source_id}")))


def allocate(pools: dict[str, Pool], total: int) -> None:
    """Equal shares; a source that runs short passes its deficit to the others."""
    live = list(pools)
    while live and (want := total - sum(len(p.taken) for p in pools.values())) > 0:
        for name, k in vision_splits.quotas(dict.fromkeys(live, 1), want).items():
            pools[name].take(k)
        live = [n for n in live if not pools[n].exhausted]


def write_rows(out: Path, taken: list[Taken]) -> bytes:
    shutil.rmtree(out / "img", ignore_errors=True)
    (out / "img").mkdir(parents=True)
    for t in taken:
        (out / t.row["images"][0]).write_bytes(t.data)
    text = "".join(json.dumps(t.row) + "\n" for t in taken).encode()
    (out / "rows.jsonl").write_bytes(text)
    return text


def build(sources: list[Source], suite: SuiteIndex, out: Path = OUT, manifest: Path = MANIFEST,
          total: int = TOTAL, seed: int = SEED) -> dict:
    pools, notes, seen = {}, {}, set()
    for s in sources:
        try:
            pools[s.name] = Pool(seeded(s.name, s.read(), seed), s.name, suite, seen)
            notes[s.name] = s.note
        except Unavailable as e:
            notes[s.name] = f"unavailable: {e}; its share went to the others"
    allocate(pools, total)
    taken = sorted((t for p in pools.values() for t in p.taken), key=lambda t: t.row["id"])
    text = write_rows(out, taken)
    meta = {"seed": seed, "suite_sha256": suite.suite_sha256, "near_mean_abs": NEAR, "dedupe": DEDUPE,
            "sources": [source_meta(s, pools.get(s.name), notes[s.name]) for s in sources],
            "rows_sha256": hashlib.sha256(text).hexdigest(), "count": len(taken)}
    doc = {"meta": meta, "ids": [t.row["id"] for t in taken], "image_sha256": {t.row["id"]: t.sha for t in taken}}
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(doc, indent=0) + "\n")
    return doc


def source_meta(s: Source, pool: Pool | None, note: str) -> dict:
    counts = {"taken": len(pool.taken), "dropped_suite": pool.dropped_suite,
              "skipped": dict(sorted(pool.skipped.items()))} if pool else {"taken": 0, "dropped_suite": 0, "skipped": {}}
    return {"name": s.name, "repo": s.repo, "revision": s.revision, "split": s.split} | counts | {"note": note}


if __name__ == "__main__":
    if sys.argv[1:] != ["build"]:
        raise SystemExit(__doc__)
    doc = build(SOURCES, suite_index())
    for s in doc["meta"]["sources"]:
        print(s["name"], "taken", s["taken"], "dropped_suite", s["dropped_suite"], "skipped", s["skipped"], s["note"])
    print("total", doc["meta"]["count"])
