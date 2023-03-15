import pytest

import arcade.color as colors
from arcade.types import Color


def test_color_from_uint24():
    assert Color.from_uint24(0xFFFFFF) == (255, 255, 255, 255)
    assert Color.from_uint24((1 << 16) + (2 << 8) + 3) == (1, 2, 3, 255)

    # Ensure alpha arg works
    assert Color.from_uint24(0xFFFFFF, a=128) == (255, 255, 255, 128)

    with pytest.raises(TypeError):
        Color.from_uint24("moo")


def test_color_from_uint32():
    assert Color.from_uint32(4294967295) == (255, 255, 255, 255)
    assert Color.from_uint32((1 << 24) + (2 << 16) + (3 << 8) + 4) == (1, 2, 3, 4)
    assert Color.from_uint32(0xFF) == (0, 0, 0, 255)
    assert Color.from_uint32(128) == (0, 0, 0, 128)

    with pytest.raises(TypeError):
        Color.from_uint32("bad")


def test_color_normalized_property():
    assert colors.BLACK.normalized == (0.0, 0.0, 0.0, 1.0)
    assert colors.WHITE.normalized == (1.0, 1.0, 1.0, 1.0)
    assert colors.TRANSPARENT_BLACK.normalized == (0.0, 0.0, 0.0, 0.0)
    assert colors.GRAY.normalized == (128 / 255, 128 / 255, 128 / 255, 1.0)
