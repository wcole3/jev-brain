import base64
import io
import struct
import zlib

import PIL.Image
import pytest

import gateway.images
from gateway.images import Image, context_items, decode_image
from gateway.questions import render_state
from gateway.schema import ImageError


def encoded(w, h, fmt, mode="RGB"):
    real = "P" if mode == "P+transparency" else mode
    extra = {"transparency": 0} if mode == "P+transparency" else {}
    buf = io.BytesIO()
    PIL.Image.new(real, (w, h)).save(buf, format=fmt, **extra)
    return buf.getvalue()


def png(w, h, mode="RGB"):
    return encoded(w, h, "PNG", mode)


def b64(raw):
    return base64.b64encode(raw).decode()


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def png_header(w, h):
    """A PNG whose IHDR claims w x h, with a stub IDAT: Pillow reads the size without decoding pixels."""
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    stub = zlib.compress(b"\0")
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", stub) + chunk(b"IEND", b"")


def test_both_wire_formats_give_the_same_context():
    a = context_items("Pick", [b64(png(64, 32))])
    b = context_items([{"image": "data:image/png;base64," + b64(png(64, 32))}, "Pick"], None)
    assert [type(x) for x in a] == [Image, str] and a[1] == "Pick"
    assert a[0].sha256 == b[0].sha256 and b[1] == "Pick"


@pytest.mark.parametrize("state", ["x", {"a": 1}, [1, 2], [{"a": 1}] * 9, {}, None])
def test_text_only_context_is_todays_state(state):
    assert context_items(state, None) == [render_state(state)]


@pytest.mark.parametrize("state", [None, "", {}, []])
def test_empty_state_adds_no_text_next_to_images(state):
    assert [type(x) for x in context_items(state, [b64(png(8, 8))])] == [Image]


def test_list_state_without_image_items_stays_whole():
    items = context_items([{"a": 1}], [b64(png(8, 8))])
    assert items[1] == render_state([{"a": 1}])


def test_a_dict_with_an_image_field_and_other_keys_is_text():
    state = ["Pick", {"image": "photo.jpg", "price": 10}]
    assert context_items(state, None) == [render_state(state)]


@pytest.mark.parametrize("src", ["https://x/a.png", "http://x/a.png", "file:///etc/passwd", "a.png", 7])
def test_url_and_path_sources_are_refused(src):
    with pytest.raises(ImageError, match=r"images\[0\]"):
        context_items("", [src])


def test_more_than_four_images_are_refused():
    with pytest.raises(ImageError, match="at most 4"):
        context_items([{"image": b64(png(8, 8))}] * 2, [b64(png(8, 8))] * 3)


def test_undecodable_image_is_refused():
    with pytest.raises(ImageError, match="not a decodable PNG, JPEG, WEBP or GIF image"):
        decode_image(b64(b"not an image"), "images[0]")


@pytest.mark.parametrize("fmt", ["BMP", "TIFF"])
def test_formats_outside_the_allowlist_are_refused(fmt):
    with pytest.raises(ImageError, match=r"images\[0\]: not a decodable PNG, JPEG, WEBP or GIF image"):
        decode_image(b64(encoded(8, 8, fmt)), "images[0]")


def test_images_carry_their_request_label():
    a = context_items([{"image": b64(png(8, 8))}], [b64(png(8, 8))])
    assert [i.where for i in a] == ["images[0]", "state[0].image"]


def test_small_images_pass_through_unchanged():
    raw = png(640, 480)
    assert decode_image(b64(raw), "images[0]").data == raw


@pytest.mark.parametrize("fmt, mime", [("PNG", "image/png"), ("JPEG", "image/jpeg")])
def test_large_images_are_downscaled_keeping_aspect(fmt, mime):
    img = decode_image(b64(encoded(2000, 1000, fmt)), "images[0]")
    assert img.width * img.height <= 1_638_400 and abs(img.width / img.height - 2) < 0.01 and img.mime == mime


def test_decompression_bombs_are_refused_before_decoding(monkeypatch):
    monkeypatch.setattr(PIL.Image, "MAX_IMAGE_PIXELS", 1000)
    with pytest.raises(ImageError, match="over 50 MP"):
        decode_image(b64(png(100, 100)), "images[0]")


@pytest.mark.parametrize(
    "mode, fmt, out_mode", [("RGBA", "PNG", "RGBA"), ("P+transparency", "PNG", "RGBA"), ("CMYK", "JPEG", "RGB")]
)
def test_downscale_handles_image_modes(mode, fmt, out_mode):
    img = decode_image(b64(encoded(2000, 1000, fmt, mode)), "images[0]")
    assert PIL.Image.open(io.BytesIO(img.data)).mode == out_mode


def test_an_image_over_50_mp_is_refused_from_its_header():
    with pytest.raises(ImageError, match=r"images\[0\]: image over 50 MP"):
        context_items("", [b64(png_header(8000, 8000))])


def test_images_over_100_mp_in_total_are_refused():
    with pytest.raises(ImageError, match="images over 100 MP in total"):
        context_items("", [b64(png_header(6000, 5000))] * 4)


def test_a_one_pixel_image_still_passes():
    assert context_items("", [b64(png(1, 1))])[0].width == 1


@pytest.mark.parametrize("prefix", ["", "data:image/png;base64,"])
@pytest.mark.parametrize("newline", ["\n", "\r\n\t "])
def test_wrapped_base64_is_accepted(prefix, newline):
    raw = png(64, 32)
    wrapped = base64.encodebytes(raw).decode()  # a newline every 76 characters
    assert "\n" in wrapped.strip()
    assert decode_image(prefix + wrapped.replace("\n", newline), "images[0]").data == raw


@pytest.mark.parametrize("w, h", [(10_000, 10_000), (20_000, 10_000)])  # Pillow warns over 89 MP, raises over 179 MP
def test_pillow_bomb_sizes_get_our_message_and_no_warning(w, h, recwarn):
    with pytest.raises(ImageError, match=r"images\[0\]: image over 50 MP"):
        context_items("", [b64(png_header(w, h))])
    assert not [x for x in recwarn if issubclass(x.category, PIL.Image.DecompressionBombWarning)]


def test_each_pillow_image_is_closed_once_decoded(monkeypatch):
    opened, real = [], gateway.images.open_image
    monkeypatch.setattr(gateway.images, "open_image", lambda *a: opened.append(real(*a)) or opened[-1])
    context_items([{"image": b64(png(8, 8))}], [b64(png(2000, 1000))])
    assert len(opened) == 2
    for item in opened:
        with pytest.raises(ValueError, match="closed image"):
            item.im.getpixel((0, 0))
