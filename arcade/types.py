"""
Module specifying data custom types used for type hinting.
"""
from array import array
from pathlib import Path
from collections import namedtuple
from collections.abc import ByteString
from typing import (
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Union,
    TYPE_CHECKING
)
from arcade.utils import (
    IntOutsideRangeError,
    ByteRangeError,
    NormalizedRangeError
)
from pytiled_parser import Properties

if TYPE_CHECKING:
    from arcade.texture import Texture


MAX_UINT24 = 0xFFFFFF
MAX_UINT32 = 0xFFFFFFFF


RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]


class Color(tuple[int, int, int, int]):
    """
    A :py:class:`tuple` subclass representing an RGBA Color.

    Although arcade will accept RGBA tuples instead of instances
    of this class, you may find the utility methods and properties
    it provides to be helpful.

    All channels are byte values from 0 to 255, inclusive. If any are
    outside this range, a :py:class:`~arcade.utils.ByteRangeError` will
    be raised, which can be handled as a :py:class:`ValueError`.

    Examples::

        >>> from arcade.types import Color
        >>> Color(255, 0, 0)
        Color(255, 0, 0, 0)

        >>> Color(*rgb_green_tuple, 127)
        Color(0, 255, 0, 127)

    :param r: the red channel of the color, between 0 and 255
    :param g: the green channel of the color, between 0 and 255
    :param b: the blue channel of the color, between 0 and 255
    :param a: the alpha or transparency channel of the color, between
        0 and 255
    """
    def __new__(cls, r: int = 0, g: int = 0, b: int = 0, a: int = 255):

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

    @property
    def normalized(self) -> Tuple[float, float, float, float]:
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
    def from_intensity(cls, intensity: int, a: int = 255) -> "Color":
        """
        Return a shade of gray of the given intensity.

        Example::

            >>> Color.from_intensity(255)
            Color(255, 255, 255, 255)

            >>> Color.from_intensity(128)
            Color(128, 128, 128, 255)

        :param intensity: How bright the shade should be
        :param a: a transparency value, fully opaque by default
        :return:
        """

        if not 0 <= intensity <= 255:
            raise ByteRangeError("intensity", intensity)

        if not 0 <= a <= 255:
            raise ByteRangeError("a", a)

        return Color(intensity, intensity, intensity, a)

    @classmethod
    def from_uint24(cls, color: int, a: int = 255) -> "Color":
        """
        Return a Color from an unsigned 3-byte (24 bit) integer.

        These ints may be between 0 and 16777215 (``0xFFFFFF``), inclusive.

        Example::

            >>> Color.from_uint24(16777215)
            (255, 255, 255, 255)

            >>> Color.from_uint24(0xFF0000)
            (255, 0, 0, 255)

        :param color: a 3-byte int between 0 and 16777215 (``0xFFFFFF``)
        :param a: an alpha value to use between 0 and 255, inclusive.
        """

        if not 0 <= color <= MAX_UINT24:
            raise IntOutsideRangeError("color", color, 0, MAX_UINT24)

        if not 0 <= a <= 255:
            raise ByteRangeError("a", a)

        return cls(
            r=(color & 0xFF0000) >> 16,
            g=(color & 0xFF00) >> 8,
            b=color & 0xFF,
            a=a
        )

    @classmethod
    def from_uint32(cls, color: int) -> "Color":
        """
        Return a Color tuple for a given unsigned 4-byte (32-bit) integer

        The bytes are interpreted as R, G, B, A.

        Examples::

            >>> Color.from_uint32(4294967295)
            (255, 255, 255, 255)

            >>> Color.from_uint32(0xFF0000FF)
            (255, 0, 0, 255)

        :param int color: An int between 0 and 4294967295 (``0xFFFFFFFF``)
        """
        if not 0 <= color <= MAX_UINT32:
            raise IntOutsideRangeError("color", color, 0, MAX_UINT32)

        return cls(
            r=(color & 0xFF000000) >> 24,
            g=(color & 0xFF0000) >> 16,
            b=(color & 0xFF00) >> 8,
            a=(color & 0xFF)
        )

    @classmethod
    def from_normalized(cls, r: float = 1.0, g: float = 1.0, b: float = 1.0, a: float = 1.0) -> "Color":
        """
        Convert normalized float channels into an RGBA Color

        Input channels must be normalized, ie between 0.0 and 1.0. If
        they are not, a :py:class:`arcade.utils.NormalizedRangeError`
        will be raised. This is a subclass of :py:class`ValueError` and
        can be handled as such.

        Examples::

            >>> Color.from_normalized(1.0, 0.0, 0.0)
            Color(255, 0, 0, 255)

            >>> normalized_half_opacity_green = (0.0, 1.0, 0.0, 0.5)
            >>> Color.from_normalized(*normalized_half_opacity_green)
            Color(0, 255, 0, 127)

        :param r: Red channel value between 0.0 and 1.0
        :param g: Green channel value between 0.0 and 1.0
        :param b: Blue channel value between 0.0 and 1.0
        :param a: Alpha channel value between 0.0 and 1.0
        :return:
        """

        if not 0 <= r <= 1.0:
            raise NormalizedRangeError("r", r)

        if not 0 <= g <= 1.0:
            raise NormalizedRangeError("g", g)

        if not 0 <= b <= 1.0:
            raise NormalizedRangeError("b", b)

        if not 0 <= a <= 1.0:
            raise NormalizedRangeError("a", a)

        return cls(r=int(255 * r), g=int(255 * g), b=int(255 * b), a=int(255 * a))

    @classmethod
    def from_hex_string(cls, code: str) -> "Color":
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
            (255, 0, 255, 255)
            >>> Color.from_hex_string("#ff00ff00")
            (255, 0, 255, 0)
            >>> Color.from_hex_string("#FFF")
            (255, 255, 255, 255)
            >>> Color.from_hex_string("FF0A")
            (255, 255, 0, 170)

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


RGBALike = Union[Color, RGBA]
ColorLike = Union[Color, RGB, RGBA]


# Point = Union[Tuple[float, float], List[float]]
# Vector = Point
Point = Tuple[float, float]
IPoint = Tuple[int, int]
Vector = Point
NamedPoint = namedtuple("NamedPoint", ["x", "y"])

PointList = Sequence[Point]
Rect = Union[Tuple[int, int, int, int], List[int]]  # x, y, width, height
RectList = Union[Tuple[Rect, ...], List[Rect]]

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
BufferProtocol = Union[ByteString, memoryview, array]
