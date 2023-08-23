"""
Module specifying data custom types used for type hinting.
"""
from __future__ import annotations

from __future__ import annotations

from array import array
import ctypes
import random
from collections import namedtuple
from collections.abc import ByteString
from pathlib import Path
from typing import (
    Iterable,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Union,
    TYPE_CHECKING, TypeVar
)
from typing_extensions import Self

from pytiled_parser import Properties

from arcade.utils import (
    IntOutsideRangeError,
    ByteRangeError,
    NormalizedRangeError
)

if TYPE_CHECKING:
    from arcade.texture import Texture

MAX_UINT24 = 0xFFFFFF
MAX_UINT32 = 0xFFFFFFFF

ChannelType = TypeVar('ChannelType')

RGB = Tuple[ChannelType, ChannelType, ChannelType]
RGBA = Tuple[ChannelType, ChannelType, ChannelType, ChannelType]
RGBOrA = Union[RGB[ChannelType], RGBA[ChannelType]]

RGBOrA255 = RGBOrA[int]
RGBOrANormalized = RGBOrA[float]

RGBA255 = RGBA[int]
RGBANormalized = RGBA[float]

RGBA255OrNormalized = Union[RGBA255, RGBANormalized]


__all__ = [
    "BufferProtocol",
    "Color",
    "ColorLike",
    "IPoint",
    "PathOrTexture",
    "Point",
    "PointList",
    "EMPTY_POINT_LIST",
    "NamedPoint",
    "Rect",
    "RectList",
    "RGB",
    "RGBA255",
    "RGBANormalized",
    "RGBA255OrNormalized",
    "TiledObject",
    "Vector"
]


class Color(RGBA255):
    """
    A :py:class:`tuple` subclass representing an RGBA Color.

    This class provides helpful utility methods and properties. When
    performance or brevity matters, arcade will usually allow you to
    use an ordinary :py:class:`tuple` of RGBA values instead.

    All channels are byte values from 0 to 255, inclusive. If any are
    outside this range, a :py:class:`~arcade.utils.ByteRangeError` will
    be raised, which can be handled as a :py:class:`ValueError`.

    Examples::

        >>> from arcade.types import Color
        >>> Color(255, 0, 0)
        Color(r=255, g=0, b=0, a=0)

        >>> Color(*rgb_green_tuple, 127)
        Color(r=0, g=255, b=0, a=127)

    :param r: the red channel of the color, between 0 and 255
    :param g: the green channel of the color, between 0 and 255
    :param b: the blue channel of the color, between 0 and 255
    :param a: the alpha or transparency channel of the color, between
        0 and 255
    """

    def __new__(cls, r: int, g: int, b: int, a: int = 255):

        if not 0 <= r <= 255:
            raise ByteRangeError("r", r)

        if not 0 <= g <= 255:
            raise ByteRangeError("g", g)

        if not 0 <= g <= 255:
            raise ByteRangeError("b", b)

        if not 0 <= a <= 255:
            raise ByteRangeError("a", a)

        # Typechecking is ignored because of a mypy bug involving
        # tuples & super:
        # https://github.com/python/mypy/issues/8541
        return super().__new__(cls, (r, g, b, a))  # type: ignore

    def __deepcopy__(self, _) -> Self:
        """Allow :py:func:`~copy.deepcopy` to be used with Color"""
        return self.__class__(r=self.r, g=self.g, b=self.b, a=self.a)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

    @property
    def r(self) -> int:
        return self[0]

    @property
    def g(self) -> int:
        return self[1]

    @property
    def b(self) -> int:
        return self[2]

    @property
    def a(self) -> int:
        return self[3]

    @classmethod
    def from_iterable(cls, iterable: Iterable[int]) -> Self:
        """
        Create a color from an :py:class`Iterable` with 3-4 elements

        If the passed iterable is already a Color instance, it will be
        returned unchanged. If the iterable has less than 3 or more than
        4 elements, a ValueError will be raised.

        Otherwise, the function will attempt to create a new Color
        instance. The usual rules apply, ie all values must be between
        0 and 255, inclusive.

        :param iterable: An iterable which unpacks to 3 or 4 elements,
            each between 0 and 255, inclusive.
        """
        if isinstance(iterable, cls):
            return iterable

        # We use unpacking because there isn't a good way of specifying
        # lengths for sequences as of 3.8, our minimum Python version as
        # of March 2023: https://github.com/python/typing/issues/786
        r, g, b, *_a = iterable

        if _a:
            if len(_a) > 1:
                raise ValueError("iterable must unpack to 3 or 4 values")
            a = _a[0]
        else:
            a = 255

        return cls(r, g, b, a=a)

    @property
    def normalized(self) -> RGBANormalized:
        """
        Return this color as a tuple of 4 normalized floats.

        Examples::

            >>> arcade.color.WHITE.normalized
            (1.0, 1.0, 1.0, 1.0)

            >>> arcade.color.BLACK.normalized
            (0.0, 0.0, 0.0, 1.0)

            >>> arcade.color.TRANSPARENT_BLACK.normalized
            (0.0, 0.0, 0.0, 0.0)

        """
        return self[0] / 255, self[1] / 255, self[2] / 255, self[3] / 255

    @classmethod
    def from_gray(cls, brightness: int, a: int = 255) -> Self:
        """
        Return a shade of gray of the given brightness.

        Example::

            >>> custom_white = Color.from_gray(255)
            >>> print(custom_white)
            Color(r=255, g=255, b=255, a=255)

            >>> half_opacity_gray = Color.from_gray(128, 128)
            >>> print(half_opacity_gray)
            Color(r=128, g=128, b=128, a=128)

        :param brightness: How bright the shade should be
        :param a: a transparency value, fully opaque by default
        :return:
        """

        if not 0 <= brightness <= 255:
            raise ByteRangeError("brightness", brightness)

        if not 0 <= a <= 255:
            raise ByteRangeError("a", a)

        return cls(brightness, brightness, brightness, a=a)

    @classmethod
    def from_uint24(cls, color: int, a: int = 255) -> Self:
        """
        Return a Color from an unsigned 3-byte (24 bit) integer.

        These ints may be between 0 and 16777215 (``0xFFFFFF``), inclusive.

        Example::

            >>> Color.from_uint24(16777215)
            Color(r=255, g=255, b=255, a=255)

            >>> Color.from_uint24(0xFF0000)
            Color(r=255, g=0, b=0, a=255)

        :param color: a 3-byte int between 0 and 16777215 (``0xFFFFFF``)
        :param a: an alpha value to use between 0 and 255, inclusive.
        """

        if not 0 <= color <= MAX_UINT24:
            raise IntOutsideRangeError("color", color, 0, MAX_UINT24)

        if not 0 <= a <= 255:
            raise ByteRangeError("a", a)

        return cls(
            (color & 0xFF0000) >> 16,
            (color & 0xFF00) >> 8,
            color & 0xFF,
            a=a
        )

    @classmethod
    def from_uint32(cls, color: int) -> Self:
        """
        Return a Color tuple for a given unsigned 4-byte (32-bit) integer

        The bytes are interpreted as R, G, B, A.

        Examples::

            >>> Color.from_uint32(4294967295)
            Color(r=255, g=255, b=255, a=255)

            >>> Color.from_uint32(0xFF0000FF)
            Color(r=255, g=0, b=0, a=255)

        :param int color: An int between 0 and 4294967295 (``0xFFFFFFFF``)
        """
        if not 0 <= color <= MAX_UINT32:
            raise IntOutsideRangeError("color", color, 0, MAX_UINT32)

        return cls(
            (color & 0xFF000000) >> 24,
            (color & 0xFF0000) >> 16,
            (color & 0xFF00) >> 8,
            a=(color & 0xFF)
        )

    @classmethod
    def from_normalized(cls, color_normalized: RGBANormalized) -> Self:
        """
        Convert normalized (0.0 to 1.0) channels into an RGBA Color

        If the input channels aren't normalized, a
        :py:class:`arcade.utils.NormalizedRangeError` will be raised.
        This is a subclass of :py:class`ValueError` and can be handled
        as such.

        Examples::

            >>> Color.from_normalized((1.0, 0.0, 0.0, 1.0))
            Color(r=255, g=0, b=0, a=255)

            >>> normalized_half_opacity_green = (0.0, 1.0, 0.0, 0.5)
            >>> Color.from_normalized(normalized_half_opacity_green)
            Color(r=0, g=255, b=0, a=127)

        :param RGBANormalized color_normalized: The color as normalized (0.0 to 1.0) RGBA values.
        :return:
        """
        r, g, b, *_a = color_normalized

        if _a:
            if len(_a) > 1:
                raise ValueError("color_normalized must unpack to 3 or 4 values")
            a = _a[0]

            if not 0.0 <= a <= 1.0:
                raise NormalizedRangeError("a", a)

        else:
            a = 1.0

        if not 0.0 <= r <= 1.0:
            raise NormalizedRangeError("r", r)

        if not 0.0 <= g <= 1.0:
            raise NormalizedRangeError("g", g)

        if not 0.0 <= b <= 1.0:
            raise NormalizedRangeError("b", b)

        return cls(int(255 * r), int(255 * g), int(255 * b), a=int(255 * a))

    @classmethod
    def from_hex_string(cls, code: str) -> Self:
        """
        Make a color from a hex code that is 3, 4, 6, or 8 hex digits long

        Prefixing it with a pound sign (``#`` / hash symbol) is
        optional. It will be ignored if present.

        The capitalization of the hex digits (``'f'`` vs ``'F'``)
        does not matter.

        3 and 6 digit hex codes will be treated as if they have an opacity of
        255.

        3 and 4 digit hex codes will be expanded.

        Examples::

            >>> Color.from_hex_string("#ff00ff")
            Color(r=255, g=0, b=255, a=255)

            >>> Color.from_hex_string("#ff00ff00")
            Color(r=255, g=0, b=255, a=0)

            >>> Color.from_hex_string("#FFF")
            Color(r=255, g=255, b=255, a=255)

            >>> Color.from_hex_string("FF0A")
            Color(r=255, g=255, b=0, a=170)

        """
        code = code.lstrip("#")

        # This looks unusual, but it matches CSS color code expansion
        # behavior for 3 and 4 digit hex codes.
        if len(code) <= 4:
            code = "".join(char * 2 for char in code)

        if len(code) == 6:
            # full opacity if no alpha specified
            return cls(int(code[:2], 16), int(code[2:4], 16), int(code[4:6], 16), 255)
        elif len(code) == 8:
            return cls(int(code[:2], 16), int(code[2:4], 16), int(code[4:6], 16), int(code[6:8], 16))

        raise ValueError(f"Improperly formatted color: '{code}'")

    @classmethod
    def random(
        cls,
        r: Optional[int] = None,
        g: Optional[int] = None,
        b: Optional[int] = None,
        a: Optional[int] = None,
    ) -> Self:
        """
        Return a random color.

        The parameters are optional and can be used to fix the value of
        a particular channel. If a channel is not fixed, it will be
        randomly generated.

        Examples::

            # Randomize all channels
            >>> Color.random()
            Color(r=35, g=145, b=4, a=200)

            # Random color with fixed alpha
            >>> Color.random(a=255)
            Color(r=25, g=99, b=234, a=255)

        :param int r: Fixed value for red channel
        :param int g: Fixed value for green channel
        :param int b: Fixed value for blue channel
        :param int a: Fixed value for alpha channel
        """
        if r is None:
            r = random.randint(0, 255)
        if g is None:
            g = random.randint(0, 255)
        if b is None:
            b = random.randint(0, 255)
        if a is None:
            a = random.randint(0, 255)

        return cls(r, g, b, a)


ColorLike = Union[RGB, RGBA255]

# Point = Union[Tuple[float, float], List[float]]
# Vector = Point
Point = Tuple[float, float]
Point3 = Tuple[float, float, float]
IPoint = Tuple[int, int]
Vector = Point
NamedPoint = namedtuple("NamedPoint", ["x", "y"])


PointList = Sequence[Point]
# Speed / typing workaround:
# 1. Eliminate extra allocations
# 2. Allows type annotation to be cleaner, primarily for HitBox & subclasses
EMPTY_POINT_LIST: PointList = tuple()


Rect = Union[Tuple[int, int, int, int], List[int]]  # x, y, width, height
RectList = Union[Tuple[Rect, ...], List[Rect]]
FloatRect = Union[Tuple[float, float, float, float], List[float]]  # x, y, width, height

PathOrTexture = Optional[Union[str, Path, "Texture"]]


class TiledObject(NamedTuple):
    shape: Union[Point, PointList, Rect]
    properties: Optional[Properties] = None
    name: Optional[str] = None
    type: Optional[str] = None


# This is a temporary workaround for the lack of a way to type annotate
# objects implementing the buffer protocol. Although there is a PEP to
# add typing, it is scheduled for 3.12. Since that is years away from
# being our minimum Python version, we have to use a workaround. See
# the PEP and Python doc for more information:
# https://peps.python.org/pep-0688/
# https://docs.python.org/3/c-api/buffer.html
BufferProtocol = Union[ByteString, memoryview, array, ctypes.Array]
