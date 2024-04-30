import math
from copy import deepcopy
from itertools import product
from typing import Iterable, Callable, Tuple
from unittest.mock import Mock

import pytest

import arcade.color as colors
from arcade.types import Color

# This seems better as fixtures, but it's added here for consistency
# with  the rest of the framework's beginner-accessible test styling.
OK_NORMALIZED = (0.0, 1.0)
BAD_NORMALIZED = (-0.01, 1.01)
MIXED_NORMALIZED = OK_NORMALIZED + BAD_NORMALIZED


class ColorSubclass(Color):
    pass


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


def test_color_from_iterable_inheritance():
    color = ColorSubclass.from_iterable(colors.AO)
    assert isinstance(color, ColorSubclass)


def test_color_from_uint24():
    assert Color.from_uint24(0xFFFFFF) == (255, 255, 255, 255)
    assert Color.from_uint24((1 << 16) + (2 << 8) + 3) == (1, 2, 3, 255)

    # Ensure alpha arg works
    assert Color.from_uint24(0xFFFFFF, a=128) == (255, 255, 255, 128)

    with pytest.raises(TypeError):
        Color.from_uint24("moo")


def test_color_from_uint24_inheritance():
    color = ColorSubclass.from_uint24(0xFFFFFF)
    assert isinstance(color, ColorSubclass)


def test_color_from_uint32():
    assert Color.from_uint32(4294967295) == (255, 255, 255, 255)
    assert Color.from_uint32((1 << 24) + (2 << 16) + (3 << 8) + 4) == (1, 2, 3, 4)
    assert Color.from_uint32(0xFF) == (0, 0, 0, 255)
    assert Color.from_uint32(128) == (0, 0, 0, 128)

    with pytest.raises(TypeError):
        Color.from_uint32("bad")


def test_color_from_uint32_inheritance():
    color = ColorSubclass.from_uint32(0xFFFFFFFF)
    assert isinstance(color, ColorSubclass)


def test_color_from_normalized():
    # spot check conversion of acceptable human-ish values
    float_steps = (1 / 255, 2 / 255, 3 / 255, 4 / 255)
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


def test_from_normalized_inheritance():
    color = ColorSubclass.from_normalized((1.0, 1.0, 1.0, 1.0))
    assert isinstance(color, ColorSubclass)


def test_color_from_gray():
    OK_255 = (0, 255)
    BAD_255 = (-1, 256)
    MIXED_255 = OK_255 + BAD_255

    for brightness in OK_255:
        color = Color.from_gray(brightness)
        assert color == (brightness, brightness, brightness, 255)

    for brightness, alpha in product(OK_255, repeat=2):
        color = Color.from_gray(brightness, alpha)
        assert color == (brightness, brightness, brightness, alpha)

    at_least_one_bad = at_least_one_in(BAD_255)
    for bad_args in filter(at_least_one_bad, product(MIXED_255, repeat=2)):
        with pytest.raises(ValueError):
            Color.from_gray(*bad_args)

    for bad_arg in BAD_255:
        with pytest.raises(ValueError):
            Color.from_gray(bad_arg)


def test_color_from_gray_inheritance():
    color = ColorSubclass.from_gray(255, a=255)
    assert isinstance(color, ColorSubclass)


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


def test_color_from_hex_string_inheritance():
    color = ColorSubclass.from_hex_string("#fff")
    assert isinstance(color, ColorSubclass)


def test_color_normalized_property():
    assert colors.BLACK.normalized == (0.0, 0.0, 0.0, 1.0)
    assert colors.WHITE.normalized == (1.0, 1.0, 1.0, 1.0)
    assert colors.TRANSPARENT_BLACK.normalized == (0.0, 0.0, 0.0, 0.0)
    assert colors.GRAY.normalized == (128 / 255, 128 / 255, 128 / 255, 1.0)


def test_color_rgb_property():
    # Try some bounds
    assert colors.WHITE.rgb == (255, 255, 255)
    assert colors.BLACK.rgb == (0, 0, 0)

    # Spot check unique colors
    assert colors.COBALT.rgb == (0, 71, 171)
    assert Color(1,3,5,7).rgb == (1, 3, 5)


def test_deepcopy_color_values():
    expected_color = Color(255, 255, 255, 255)
    assert deepcopy(expected_color) == expected_color


def test_deepcopy_color_inheritance():
    color_subclass_instance = ColorSubclass(255, 255, 255, a=255)
    deep = deepcopy(color_subclass_instance)
    assert isinstance(deep, ColorSubclass)


@pytest.mark.parametrize("klass", [Color, ColorSubclass])
def test_swizzle(klass):
    color_instance = klass(1, 2, 3, a=4)

    # Edge case
    assert color_instance.swizzle("") == tuple()

    assert color_instance.swizzle("r") == (1,)
    assert color_instance.swizzle("g") == (2,)
    assert color_instance.swizzle("b") == (3,)
    assert color_instance.swizzle("a") == (4,)
    assert color_instance.swizzle("R") == (1,)
    assert color_instance.swizzle("G") == (2,)
    assert color_instance.swizzle("B") == (3,)
    assert color_instance.swizzle("A") == (4,)

    assert color_instance.swizzle("ra") == (1, 4)
    assert color_instance.swizzle("RA") == (1, 4)

    assert color_instance.swizzle("aabbggrr") == (4, 4, 3, 3, 2, 2, 1, 1)
    assert color_instance.swizzle("AABBGGRR") == (4, 4, 3, 3, 2, 2, 1, 1)


RANDINT_RETURN_RESULT = 128


@pytest.fixture
def randint_is_constant(monkeypatch):
    """
    Replace the randomized color uint32 with a known signal value.

    Since the color randomization masks out channels, we use a known
    repeated value (128, or 0x80 in hex) to represent a channel fetched
    from random rather than taken from user input.
    """
    monkeypatch.setattr('random.randint', Mock(return_value=0x80808080))


def test_color_random(randint_is_constant):

    for combo in product((None, 0), repeat=4):
        color = Color.random(*combo)
        for channel_value, channel_arg in zip(color, combo):
            if channel_arg is None:
                expected = RANDINT_RETURN_RESULT
            else:
                expected = 0

            assert channel_value == expected


def test_color_random_inheritance(randint_is_constant):
    color = ColorSubclass.random()
    assert isinstance(color, ColorSubclass)
