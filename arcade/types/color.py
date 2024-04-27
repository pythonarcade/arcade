"""Color-related types, aliases, and constants.

This module does not contain pre-defined color values. For pre-made
named color values, please see the following:

.. list-table::
   :header-rows: 1

   * - Module
     - Contents

   * - :py:mod:`arcade.color`
     - A set of pre-defined :py:class`.Color` constants.

   * - :py:mod:`arcade.csscolor`
     - The `CSS named colors <https://developer.mozilla.org/en-US/docs/Web/CSS/named-color>`_
       as :py:class:`.Color` constants.

"""
from __future__ import annotations

import random
from typing import Tuple, Iterable, Optional, Union, TypeVar

from typing_extensions import Self, Final

from arcade.utils import ByteRangeError, IntOutsideRangeError, NormalizedRangeError


__all__ = (
    'Color',
    'RGB',
    'RGBA',
    'RGB255',
    'RGBA255',
    'RGBNormalized',
    'RGBANormalized',
    'RGBOrA',
    'RGBOrA255',
    'RGBOrANormalized',
    'MASK_RGBA_R',
    'MASK_RGBA_G',
    'MASK_RGBA_B',
    'MASK_RGBA_A',
    'MASK_RGB_R',
    'MASK_RGB_G',
    'MASK_RGB_B',
    'MAX_UINT24',
    'MAX_UINT32',
)


# Helpful color-related constants for bit masking
MAX_UINT24: Final[int] = 0xFFFFFF
MAX_UINT32: Final[int] = 0xFFFFFFFF
MASK_RGBA_R: Final[int] = 0xFF000000
MASK_RGBA_G: Final[int] = 0x00FF0000
MASK_RGBA_B: Final[int] = 0x0000FF00
MASK_RGBA_A: Final[int] = 0x000000FF
MASK_RGB_R: Final[int] = 0xFF0000
MASK_RGB_G: Final[int] = 0x00FF00
MASK_RGB_B: Final[int] = 0x0000FF


# Color type aliases.
ChannelType = TypeVar('ChannelType')

# Generic color aliases
RGB = Tuple[ChannelType, ChannelType, ChannelType]
RGBA = Tuple[ChannelType, ChannelType, ChannelType, ChannelType]
RGBOrA = Union[RGB[ChannelType], RGBA[ChannelType]]

# Specific color aliases
RGB255 = RGB[int]
RGBA255 = RGBA[int]
RGBNormalized = RGB[float]
RGBANormalized = RGBA[float]
RGBOrA255 = RGBOrA[int]
RGBOrANormalized = RGBOrA[float]


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

    __slots__ = ()

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

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """Return only a color's RGB components.

        This is syntactic sugar for slice indexing as below:

        .. code-block:: python

            >>> from arcade.color import WHITE
            >>> WHITE[:3]
            (255, 255, 255)
            # Equivalent but slower than the above
            >>> (WHITE.r, WHITE.g, WHITE.b)
            (255, 255, 255)

        To reorder the channels as you retrieve them, see
        :meth:`.swizzle`.
        """
        return self[:3]

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

        :param color: An int between 0 and 4294967295 (``0xFFFFFFFF``)
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

        :param color_normalized: The color as normalized (0.0 to 1.0) RGBA values.
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

        :param r: Fixed value for red channel
        :param g: Fixed value for green channel
        :param b: Fixed value for blue channel
        :param a: Fixed value for alpha channel
        """
        rand = random.randint(0, MAX_UINT32)
        if r is None:
            r = (rand & MASK_RGBA_R) >> 24
        if g is None:
            g = (rand & MASK_RGBA_G) >> 16
        if b is None:
            b = (rand & MASK_RGBA_B) >> 8
        if a is None:
            a = (rand & MASK_RGBA_A)

        return cls(r, g, b, a)

    def swizzle(self, swizzle_string: str) -> Tuple[int, ...]:
        """
        Get a tuple of channel values in the same order as the passed string.

        This imitates swizzling `as implemented in GLSL <https://www.khronos.org/opengl/wiki/Data_Type_(GLSL)#Swizzling>`_

        .. code-block:: python

           >>> from arcade.types import Color
           >>> color = Color(180, 90, 0, 255)
           >>> color.swizzle("abgr")
           (255, 0, 90, 180)

        You can also use any length of swizzle string and use capital
        letters. Any capitals will be treated as lower case equivalents.

        .. code-block: python

           >>> from arcade.types import Color
           >>> color = Color(180, 90, 0, 255)
           >>> color.swizzle("ABGR")
           (255, 0, 90, 180)


        :param swizzle_string:
            A string of channel names as letters in ``"RGBArgba"``.
        :return:
            A tuple in the same order as the input string.
        """
        ret = []
        for c in swizzle_string.lower():
            if c not in 'rgba':
                raise ValueError(f"Swizzle string must only contain characters in [RGBArgba], not {c}.")
            ret.append(getattr(self, c))
        return tuple(ret)
