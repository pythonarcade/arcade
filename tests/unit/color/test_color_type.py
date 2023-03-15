import math
from itertools import combinations_with_replacement
from typing import Iterable, Optional, Callable, Generator, TypeVar, Tuple

import pytest

import arcade.color as colors
from arcade.types import Color


# This seems better as fixtures, but it's added here for consistency
# with  the rest of the framework's beginner-accessible test styling.
OK_NORMALIZED = frozenset((0.0, 1.0))
BAD_NORMALIZED = frozenset((-0.01, 1.01))
MIXED_NORMALIZED = OK_NORMALIZED | BAD_NORMALIZED


_EltType = TypeVar('_EltType')


def gen_combos(
        i: Iterable[_EltType],
        r: Optional[int] = None,
        requirement: Callable = lambda e: True) -> Generator[Tuple[_EltType], None, None]:
    """
    A helper for boundary testing combinations in arcade's test style

    Combinations-with-replacement will be generated and filtered
    according to the passed requirement. If no requirement is given,
    a dummy always-true one will be used.

    :param i: An iterable to source possible values from
    :param r: How long each combo should be
    :param requirement: A requirement to meet (always true by default)
    :return:
    """
    for p in filter(requirement, combinations_with_replacement(i, r)):
        yield p


def at_least_one_bad(i: Iterable) -> bool:
    """Returns true when at least one value is bad"""
    return bool(set(i) & BAD_NORMALIZED)


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
    assert Color.from_normalized(r=1/255, g=2/255, b=3/255) == (1, 2, 3, 255)
    assert Color.from_normalized(r=1/255, g=2/255, b=3/255, a=4/255) == (1, 2, 3, 4)

    # make sure boundary values are accepted
    def local_convert(i: Iterable[float]) -> Tuple[int]:
        """
        Local conversion helper for normalized float -> byte ints
        :param i:
        :return:
        """
        return tuple(math.floor(c * 255) for c in i)

    for rgb_channels in gen_combos(OK_NORMALIZED, r=3):
        expected = local_convert(rgb_channels) + (255,)
        assert Color.from_normalized(*rgb_channels) == expected

    for rgba_channels in gen_combos(OK_NORMALIZED, r=4):
        expected = local_convert(rgba_channels)
        assert Color.from_normalized(*rgba_channels) == expected

    # make sure bad values raise appropriate exceptions
    for rgb_channels in gen_combos(MIXED_NORMALIZED, 3, at_least_one_bad):
        with pytest.raises(ValueError):
            Color.from_normalized(*rgb_channels)

    for rgba_channels in gen_combos(MIXED_NORMALIZED, 4, at_least_one_bad):
        with pytest.raises(ValueError):
            Color.from_normalized(*rgba_channels)


def test_color_normalized_property():
    assert colors.BLACK.normalized == (0.0, 0.0, 0.0, 1.0)
    assert colors.WHITE.normalized == (1.0, 1.0, 1.0, 1.0)
    assert colors.TRANSPARENT_BLACK.normalized == (0.0, 0.0, 0.0, 0.0)
    assert colors.GRAY.normalized == (128 / 255, 128 / 255, 128 / 255, 1.0)
