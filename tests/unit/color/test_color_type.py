import math
from itertools import product
from typing import Iterable, Callable, Tuple, TypeVar

import pytest

import arcade.color as colors
from arcade.types import Color


# This seems better as fixtures, but it's added here for consistency
# with  the rest of the framework's beginner-accessible test styling.
OK_NORMALIZED = (0.0, 1.0)
BAD_NORMALIZED = (-0.01, 1.01)
MIXED_NORMALIZED = OK_NORMALIZED + BAD_NORMALIZED


def at_least_one_in(i: Iterable) -> Callable[[Iterable], bool]:
    """Return a callable which returns true when at least one elt is in iterable i"""
    def _at_least_one_in(checked: Iterable):
        return bool(set(checked) & frozenset(i))

    return _at_least_one_in


def test_color_from_iterable_noncolor_iterables():

    for length, type_converter in product((3, 4), (list, tuple, lambda a: a)):
        iterable = type_converter(range(length))
        color = Color.from_iterable(iterable)

        assert isinstance(color, Color)
        assert color[:3] == (0, 1, 2)
        if length == 4:
            assert color.a == 3
            assert color[3] == 3
        else:
            assert color.a == 255
            assert color[3] == 255


def test_color_from_iterable_returns_same_color():
    for color in (Color(1, 2, 3), Color(0, 0, 0, 255)):
        assert Color.from_iterable(color) is color


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


def test_color_from_normalized():

    # spot check conversion of acceptable human-ish values
    float_steps = (1/255, 2/255, 3/255, 4/255)
    assert Color.from_normalized(float_steps[:3]) == (1, 2, 3, 255)
    assert Color.from_normalized(float_steps) == (1, 2, 3, 4)

    # some helper callables
    at_least_one_bad = at_least_one_in(BAD_NORMALIZED)
    def local_convert(i: Iterable[float]) -> Tuple[int]:
        """Local helper converter, normalized float to byte ints"""
        return tuple(math.floor(c * 255) for c in i)

    for good_rgb_channels in product(OK_NORMALIZED, repeat=3):
        expected = local_convert(good_rgb_channels) + (255,)
        assert Color.from_normalized(good_rgb_channels) == expected

    for good_rgba_channels in product(OK_NORMALIZED, repeat=4):
        expected = local_convert(good_rgba_channels)
        assert Color.from_normalized(good_rgba_channels) == expected

    for bad_rgb_channels in filter(at_least_one_bad, product(MIXED_NORMALIZED, repeat=3)):
        with pytest.raises(ValueError):
            Color.from_normalized(bad_rgb_channels)

    for bad_rgba_channels in filter(at_least_one_bad, product(MIXED_NORMALIZED, repeat=4)):
        with pytest.raises(ValueError):
            Color.from_normalized(bad_rgba_channels)


def test_color_from_hex_string():
    with pytest.raises(ValueError):
        Color.from_hex_string("#ff0000ff0")

    # Hash symbol RGBA variants
    assert Color.from_hex_string("#ffffffff") == (255, 255, 255, 255)
    assert Color.from_hex_string("#ffffff00") == (255, 255, 255, 0)
    assert Color.from_hex_string("#ffff00ff") == (255, 255, 0, 255)
    assert Color.from_hex_string("#ff00ffff") == (255, 0, 255, 255)
    assert Color.from_hex_string("#00ffffff") == (0, 255, 255, 255)

    # RGB with hash
    assert Color.from_hex_string("#ffffff") == (255, 255, 255, 255)
    assert Color.from_hex_string("#ffff00") == (255, 255, 0, 255)
    assert Color.from_hex_string("#ff0000") == (255, 0, 0, 255)

    # RGB without hash
    assert Color.from_hex_string("FFFFFF") == (255, 255, 255, 255)
    assert Color.from_hex_string("ffff00") == (255, 255, 0, 255)
    assert Color.from_hex_string("ff0000") == (255, 0, 0, 255)

    # Short form
    assert Color.from_hex_string("#fff") == (255, 255, 255, 255)
    assert Color.from_hex_string("FFF") == (255, 255, 255, 255)

    for bad_value in ("ppp", 'ff', "e"):
        with pytest.raises(ValueError):
            Color.from_hex_string(bad_value)


def test_color_normalized_property():
    assert colors.BLACK.normalized == (0.0, 0.0, 0.0, 1.0)
    assert colors.WHITE.normalized == (1.0, 1.0, 1.0, 1.0)
    assert colors.TRANSPARENT_BLACK.normalized == (0.0, 0.0, 0.0, 0.0)
    assert colors.GRAY.normalized == (128 / 255, 128 / 255, 128 / 255, 1.0)
