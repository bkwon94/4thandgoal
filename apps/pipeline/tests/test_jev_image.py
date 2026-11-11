"""
Tests for the image of the Jev port: a state holds PNG bytes in a JevImage, FakeJev keeps it in its requests,
and the TypeSafe adapter wraps each JevImage in the SDK image type. No test calls TypeSafe.
"""
import struct
import zlib

from fakes import FakeJev
from typesafe_sdk import Image

from league.jev import has_image, sdk_state
from league.jev_port import JevImage, NoulQuestion


def _png(width: int = 300, height: int = 300) -> bytes:
    """A real solid-grey PNG of the given size."""
    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    rows = b"".join(b"\x00" + b"\x80" * width for _ in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


QUESTION = NoulQuestion(instructions="Is text cut off in `shot`?", yes="text is cut off", no="no text is cut off")


def test_fake_jev_keeps_the_image_of_a_state_in_its_request():
    image = JevImage(_png())
    jev = FakeJev()
    jev.ask({"shot": image, "name": "banner"}, {"cut": QUESTION})
    assert jev.requests[0].state["shot"] is image
    assert jev.requests[0].state["shot"].png == image.png


def test_the_adapter_wraps_each_image_of_a_state_in_the_sdk_image():
    state = {"shot": JevImage(_png()), "shots": [JevImage(_png(280, 400))], "name": "banner", "n": 3}
    wrapped = sdk_state(state)
    assert isinstance(wrapped["shot"], Image)
    assert isinstance(wrapped["shots"][0], Image)
    assert wrapped["name"] == "banner"
    assert wrapped["n"] == 3


def test_has_image_finds_an_image_at_any_depth():
    assert has_image({"a": [{"b": JevImage(_png())}]})
    assert not has_image({"a": ["text", 3]})
