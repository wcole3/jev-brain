"""Request images → checked, size-capped Image items that sit inside the decision context."""

import base64
import binascii
import hashlib
import io
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

import PIL.Image

from gateway.questions import render_state
from gateway.schema import ImageError

MAX_IMAGES = 4
MAX_PIXELS = 1_638_400  # 1600 × 32 × 32, the vision profiles' image budget
MAX_BODY_BYTES = 20_000_000  # request body cap, checked by the app
MAX_DECODE_PIXELS = 50_000_000  # per image, read from the header before any pixel is decoded
MAX_REQUEST_PIXELS = 100_000_000  # all images of one request, also from their headers

ALLOWED_FORMATS = ["PNG", "JPEG", "WEBP", "GIF"]  # the decision-index kit's pass-through set
EMPTY_STATES = (None, "", {}, [])
WRAPPING = str.maketrans("", "", " \t\r\n")  # line-wrapped base64 (MIME, encodebytes) decodes once these go


@dataclass(frozen=True)
class Image:
    data: bytes
    mime: str
    width: int
    height: int
    sha256: str
    where: str = ""  # its place in the request, e.g. "images[0]", for error messages

    def part(self) -> dict:
        """The vLLM chat content part. vLLM uses uuid as the image's cache key."""
        url = f"data:{self.mime};base64,{base64.b64encode(self.data).decode()}"
        return {"type": "image_url", "url": url, "uuid": self.sha256}


def fit(w: int, h: int, max_pixels: int) -> tuple[int, int]:
    """Largest size with the same aspect ratio inside max_pixels (the decision-index kit's rule)."""
    if w * h <= max_pixels:
        return w, h
    s = (max_pixels / (w * h)) ** 0.5
    w2, h2 = max(1, int(w * s)), max(1, int(h * s))
    while w2 * h2 > max_pixels:
        if w2 >= h2:
            w2 -= 1
        else:
            h2 -= 1
    return w2, h2


def raw_bytes(source: Any, where: str) -> bytes:
    """The image bytes from a base64 data: URL or raw base64. Never fetches anything."""
    if isinstance(source, str):
        head, _, payload = source.partition(",")
        if source.startswith("data:") and head.endswith(";base64"):
            source = payload
        try:
            return base64.b64decode(source.translate(WRAPPING), validate=True)
        except (binascii.Error, ValueError):
            pass
    raise ImageError(f"{where}: images must be data: URLs or base64; URLs are not fetched")


@dataclass(frozen=True)
class Opened:
    """An image whose header is read but whose pixels are not decoded yet."""

    raw: bytes
    im: PIL.Image.Image
    where: str

    @property
    def pixels(self) -> int:
        return self.im.size[0] * self.im.size[1]


@contextmanager
def pillow_errors(where: str):
    try:
        yield
    except PIL.Image.DecompressionBombError as e:
        raise ImageError(f"{where}: image too large") from e
    except (OSError, SyntaxError, ValueError) as e:
        raise ImageError(f"{where}: not a decodable PNG, JPEG, WEBP or GIF image") from e


def open_image(source: Any, where: str) -> Opened:
    """Open source as PNG, JPEG, WEBP or GIF only, reading the header but no pixels, and refuse it over 50 MP."""
    raw = raw_bytes(source, where)
    with pillow_errors(where):
        im = PIL.Image.open(io.BytesIO(raw), formats=ALLOWED_FORMATS)
    opened = Opened(raw, im, where)
    if opened.pixels > MAX_DECODE_PIXELS:
        raise ImageError(f"{where}: image over {MAX_DECODE_PIXELS // 1_000_000} MP")
    return opened


def downscale(im: PIL.Image.Image, size: tuple[int, int]) -> tuple[str, bytes]:
    """PNG stays PNG (keeping alpha); everything else becomes JPEG quality 95."""
    is_png = im.format == "PNG"
    alpha = is_png and ("A" in im.mode or "transparency" in im.info)
    small = im.convert("RGBA" if alpha else "RGB").resize(size, PIL.Image.Resampling.LANCZOS)
    out = io.BytesIO()
    if is_png:
        small.save(out, format="PNG")
    else:
        small.save(out, format="JPEG", quality=95)
    return ("PNG" if is_png else "JPEG"), out.getvalue()


def decode(opened: Opened) -> Image:
    """Decode the pixels, downscaling the image when it is over the image budget."""
    raw, im = opened.raw, opened.im
    with pillow_errors(opened.where):
        im.load()
    fmt, size = im.format, im.size
    if size[0] * size[1] > MAX_PIXELS:
        size = fit(*size, MAX_PIXELS)
        fmt, raw = downscale(im, size)
    return Image(raw, PIL.Image.MIME[fmt], size[0], size[1], hashlib.sha256(raw).hexdigest(), opened.where)


def decode_image(source: Any, where: str) -> Image:
    return decode(open_image(source, where))


def is_image_item(item: Any) -> bool:
    return isinstance(item, dict) and list(item) == ["image"]


def image_items(state: Any) -> list[Any]:
    return [i for i in state if is_image_item(i)] if isinstance(state, list) else []


def state_items(state: Any) -> list[str | Opened]:
    if image_items(state):
        return [
            open_image(item["image"], f"state[{i}].image") if is_image_item(item) else render_state(item)
            for i, item in enumerate(state)
        ]
    return [] if state in EMPTY_STATES else [render_state(state)]


def context_items(state: Any, images: list[str] | None) -> list[str | Image]:
    """The context in order: top-level images, then the state, with state images inline.
    Every header is read and the request's total checked before any image is decoded."""
    images = images or []
    if not images and not image_items(state):
        return [render_state(state)]
    if len(images) + len(image_items(state)) > MAX_IMAGES:
        raise ImageError(f"at most {MAX_IMAGES} images per request")
    items = [open_image(src, f"images[{i}]") for i, src in enumerate(images)] + state_items(state)
    if sum(item.pixels for item in items if isinstance(item, Opened)) > MAX_REQUEST_PIXELS:
        raise ImageError(f"images over {MAX_REQUEST_PIXELS // 1_000_000} MP in total")
    return [decode(item) if isinstance(item, Opened) else item for item in items]
