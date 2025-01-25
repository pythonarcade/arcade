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
from typing import Iterable, TypeVar, Union

from typing_extensions import Final, Self

from arcade.exceptions import ByteRangeError, IntOutsideRangeError, NormalizedRangeError

__all__ = (
    "Color",
    "RGB",
    "RGBA",
    "RGB255",
    "RGBA255",
    "RGBNormalized",
    "RGBANormalized",
    "RGBOrA",
    "RGBOrA255",
    "RGBOrANormalized",
    "MASK_RGBA_R",
    "MASK_RGBA_G",
    "MASK_RGBA_B",
    "MASK_RGBA_A",
    "MASK_RGB_R",
    "MASK_RGB_G",
    "MASK_RGB_B",
    "MAX_UINT24",
    "MAX_UINT32",
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
ChannelType = TypeVar("ChannelType")

# Generic color aliases
RGB = tuple[ChannelType, ChannelType, ChannelType]
RGBA = tuple[ChannelType, ChannelType, ChannelType, ChannelType]
RGBOrA = Union[RGB[ChannelType], RGBA[ChannelType]]

# Specific color aliases
RGB255 = RGB[int]
RGBA255 = RGBA[int]
RGBNormalized = RGB[float]
RGBANormalized = RGBA[float]
RGBOrA255 = RGBOrA[int]
RGBOrANormalized = RGBOrA[float]


class Color(RGBA255):
    """An RGBA color as a :py:class:`tuple` subclass.

    .. code-block:: python

        # The alpha channel value defaults to 255
        >>> from arcade.types import Color
        >>> Color(255, 0, 0)
        Color(r=255, g=0, b=0, a=255)

    If you prefer specifying color with another format, the class also
    provides number of helper methods for the most common RGB and RGBA
    formats:

    * :py:meth:`.from_hex_string`
    * :py:meth:`.from_normalized`
    * :py:meth:`.from_uint24`
    * :py:meth:`.from_uint32`
    * :py:meth:`.from_iterable`

    Regardless of the source format, all color channels must be between
    0 and 255, inclusive. If any channel is outside this range, creation
    will fail with a :py:class:`~arcade.utils.ByteRangeError`, which is a
    type of :py:class:`ValueError`.

    .. _colour: https://pypi.org/project/colour/

    .. note:: This class does not currently support HSV or other color spaces.

              If you need these, you may want to try the following:

              * Python's built-in :py:mod:`colorsys` module
              * The `colour`_ package

    Args:
        r: the red channel of the color, between 0 and 255, inclusive
        g: the green channel of the color, between 0 and 255, inclusive
        b: the blue channel of the color, between 0 and 255, inclusive
        a: the alpha or transparency channel of the color, between 0 and 255, inclusive
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

    def __getnewargs__(self) -> tuple[int, int, int, int]:
        return self.r, self.g, self.b, self.a

    def __deepcopy__(self, _) -> Self:
        """Allow :py:func:`~copy.deepcopy` to be used with Color"""
        return self.__class__(r=self.r, g=self.g, b=self.b, a=self.a)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

    @property
    def r(self) -> int:
        """Get the red value of the :py:class:`Color`.

        It will be between ``0`` and ``255``, inclusive.
        """
        return self[0]

    @property
    def g(self) -> int:
        """Get the green value of the :py:class:`Color`.

        It will be between ``0`` and ``255``, inclusive.
        """
        return self[1]

    @property
    def b(self) -> int:
        """Get the blue value of the :py:class:`Color`.

        It will be between ``0`` and ``255``, inclusive.
        """
        return self[2]

    @property
    def a(self) -> int:
        """Get the alpha value of the :py:class:`Color`.

        It will be between ``0`` and ``255``, inclusive.
        """
        return self[3]

    @property
    def rgb(self) -> tuple[int, int, int]:
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
        """Create a :py:class:`Color` from an iterable of 3 or 4 channel values.

        If an iterable is already a :py:class:`Color` instance,
        it will be returned unchanged. Otherwise, it must unpack as
        3 or 4 :py:class:`int` values between ``0`` and ``255``, inclusive.

        If an iterable has no less than 3 or more than 4 elements,
        this method raises a :py:class:`ValueError`. The function will
        attempt to create a new Color instance. The usual rules apply,
        i.e.: all values must be between 0 and 255, inclusive.

        .. note:: This is a more readable alternative to ``*`` unpacking.

                  If you are an advanced user who needs brevity or
                  higher performance, you can unpack directly into
                  :py:class:`Color`:

                  .. code-block:: python

                     >>> rgb_green_tuple = (0, 255, 0)
                     >>> Color(*rgb_green_tuple, 127)
                     Color(r=0, g=255, b=0, a=127)

        Args:
            iterable: An iterable which unpacks to 3 or 4 elements,
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
        """Convert the :py:class:`Color` to a tuple of 4 normalized floats.

        .. code-block:: python

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
        """Create a gray :py:class:`Color` of the given ``brightness``.

        .. code-block:: python

            >>> off_white = Color.from_gray(220)
            >>> print(off_white)
            Color(r=220, g=220, b=220, a=255)

            >>> half_opacity_gray = Color.from_gray(128, 128)
            >>> print(half_opacity_gray)
            Color(r=128, g=128, b=128, a=128)

        Args:
            brightness: How bright the new gray should be
            a: a transparency value, fully opaque by default
        """

        if not 0 <= brightness <= 255:
            raise ByteRangeError("brightness", brightness)

        if not 0 <= a <= 255:
            raise ByteRangeError("a", a)

        return cls(brightness, brightness, brightness, a=a)

    @classmethod
    def from_uint24(cls, color: int, a: int = 255) -> Self:
        """Convert an unsigned 24-bit integer to a :py:class:`Color`.

        .. code-block:: python

            # The alpha channel is assumed to be 255
            >>> Color.from_uint24(0x010203)
            Color(r=1, g=2, b=3, a=255)

            # Specify alpha via the a keyword argument
            >>> Color.from_uint24(0x010203, a=127)
            Color(r=1, g=2, b=3, a=127)

            # The maximum value as decimal
            >>> Color.from_uint24(16777215)
            Color(r=255, g=255, b=255, a=255)

        To convert from an RGBA value as a 32-bit integer, see
        :py:meth:`.from_uint32`.

        Args:
            color:
                a 3-byte :py:class:`int` between ``0`` and ``16777215`` (``0xFFFFFF``)
            a:
                An alpha value to use between 0 and 255, inclusive.
        """

        if not 0 <= color <= MAX_UINT24:
            raise IntOutsideRangeError("color", color, 0, MAX_UINT24)

        if not 0 <= a <= 255:
            raise ByteRangeError("a", a)

        return cls((color & 0xFF0000) >> 16, (color & 0xFF00) >> 8, color & 0xFF, a=a)

    @classmethod
    def from_uint32(cls, color: int) -> Self:
        """Convert an unsigned 32-bit integer to a :py:class:`Color`.

        The four bytes are interpreted as R, G, B, A:

        .. code-block:: python

            >>> Color.from_uint32(0x01020304)
            Color(r=1, g=2, b=3, a=4)

            # The maximum value as a decimal integer
            >>> Color.from_uint32(4294967295)
            Color(r=255, g=255, b=255, a=255)

        To convert from an RGB value as a 24-bit integer, see
        :py:meth:`.from_uint24`.

        Args:
            color:
                An :py:class:`int` between ``0`` and ``4294967295`` (``0xFFFFFFFF``)
        """
        if not 0 <= color <= MAX_UINT32:
            raise IntOutsideRangeError("color", color, 0, MAX_UINT32)

        return cls(
            (color & 0xFF000000) >> 24,
            (color & 0xFF0000) >> 16,
            (color & 0xFF00) >> 8,
            a=(color & 0xFF),
        )

    @classmethod
    def from_normalized(cls, color_normalized: RGBANormalized) -> Self:
        """Convert normalized float RGBA to an RGBA :py:class:`Color`.

        If any input channels aren't normalized (between ``0.0`` and
        ``1.0``), this method will raise a
        :py:class:`~arcade.utils.NormalizedRangeError` you can handle as
        a :py:class:`ValueError`.

        Examples::

            >>> Color.from_normalized((1.0, 0.0, 0.0, 1.0))
            Color(r=255, g=0, b=0, a=255)

            >>> normalized_half_opacity_green = (0.0, 1.0, 0.0, 0.5)
            >>> Color.from_normalized(normalized_half_opacity_green)
            Color(r=0, g=255, b=0, a=127)

        Args:
            color_normalized: A tuple of 4 normalized (``0.0`` to ``1.0``) RGBA values.
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
        """Create a :py:class:`Color` from a hex code of 3, 4, 6, or 8 digits.

        .. code-block:: python

            # RGB color codes are assumed to have an alpha value of 255
            >>> Color.from_hex_string("#FF00FF")
            Color(r=255, g=0, b=255, a=255)

            # You can use eight-digit RGBA codes to specify alpha
            >>> Color.from_hex_string("#FF007F")
            Color(r=255, g=0, b=255, a=127)

            # For brevity, you can omit the # and use RGB shorthand
            >>> Color.from_hex_string("FFF")
            Color(r=255, g=255, b=255, a=255)

            # Lower case and four-digit RGBA shorthand are also allowed
            >>> Color.from_hex_string("ff0a")
            Color(r=255, g=255, b=0, a=170)

        Aside from the optional leading ``#``, the ``code`` must otherwise
        be a valid CSS hexadecimal color code. It will be processed as
        follows:

        * Any leading ``'#'`` characters will be stripped
        * 3 and 4 digit shorthands are expanded by multiplying each
          digit's value by 16
        * 6 digit RGB hex codes assume 255 as their alpha values
        * 8 digit RGBA hex codes are converted to byte values
          and passed directly to a new :py:class:`Color`
        * All other lengths will raise a :py:class:`ValueError`

        .. _CSS hex color: https://www.w3.org/TR/css-color-4/#hex-notation
        .. _Simple Wiki's Hexadecimal Page: https://simple.wikipedia.org/wiki/Hexadecimal

        To learn more, please see:

        * Python's :py:func:`hex` function and :py:class:`int` type
        * `Simple Wiki's Hexadecimal Page`_
        * The `CSS hex color`_ specification

        Args:
            code:
                A `CSS hex color`_ string which may omit the leading ``#`` character.
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
            return cls(
                int(code[:2], 16), int(code[2:4], 16), int(code[4:6], 16), int(code[6:8], 16)
            )

        raise ValueError(f"Improperly formatted color: '{code}'")

    @classmethod
    def random(
        cls,
        r: int | None = None,
        g: int | None = None,
        b: int | None = None,
        a: int | None = None,
    ) -> Self:
        """Create a :py:class:`Color` by randomizing all unspecified channels.

        All arguments are optional. If you specify a channel's value, it
        will be used in the new color instead of randomizing:

        .. code-block:: python

            # Randomize all channels
            >>> Color.random()
            Color(r=35, g=145, b=4, a=200)

            # Create a random opaque color
            >>> Color.random(a=255)
            Color(r=25, g=99, b=234, a=255)

        Args:
            r: Specify a value for the red channel
            g: Specify a value for the green channel
            b: Specify a value for the blue channel
            a: Specify a value for the alpha channel
        """
        rand = random.randint(0, MAX_UINT32)
        if r is None:
            r = (rand & MASK_RGBA_R) >> 24
        if g is None:
            g = (rand & MASK_RGBA_G) >> 16
        if b is None:
            b = (rand & MASK_RGBA_B) >> 8
        if a is None:
            a = rand & MASK_RGBA_A

        return cls(r, g, b, a)

    def replace(
        self,
        r: int | None = None,
        g: int | None = None,
        b: int | None = None,
        a: int | None = None,
    ) -> Color:
        """Create a :py:class:`Color` with specified values replaced in a predefined color.

        .. code-block:: python

            # Color with alpha with a predefined constant
            >>> arcade.color.BLUE.replace(a = 100)
            Color(r = 0, g = 0, b = 255, a = 100)

        Args:
            r: Specify a value for the red channel
            g: Specify a value for the green channel
            b: Specify a value for the blue channel
            a: Specify a value for the alpha channel
        """
        return Color(
            self.r if r is None else r,
            self.g if g is None else g,
            self.b if b is None else b,
            self.a if a is None else a,
        )

    def swizzle(self, order: str) -> tuple[int, ...]:
        """Get a :py:class:`tuple` of channel values in the given ``order``.

        .. _GLSL's swizzling: https://www.khronos.org/opengl/wiki/Data_Type_(GLSL)#Swizzling

        This imitates `GLSL's swizzling`_, a way to reorder vector values:

        .. code-block:: python

           >>> from arcade.types import Color
           >>> color = Color(180, 90, 0, 255)
           >>> color.swizzle("abgr")
           (255, 0, 90, 180)

        Unlike GLSL, this function allows upper case.

        .. code-block:: python

           >>> from arcade.types import Color
           >>> color = Color(180, 90, 0, 255)
           # You can repeat channels and use upper case
           >>> color.swizzle("ABGRa")
           (255, 0, 90, 180, 255)

        .. note:: The ``order`` is case-insensitive.

                  If you were hoping ``order`` would also specify how to
                  convert data, you may instead be looking for Python's
                  built-in :py:mod:`struct` and :py:mod:`array` modules.

        Args:
            order:
                A string of channel names as letters in ``"RGBArgba"`` with repeats allowed.
        Returns:
            A tuple of channel values in the given ``order``.
        """
        ret = []
        for c in order.lower():
            if c not in "rgba":
                raise ValueError(
                    f"Swizzle string must only contain characters in [RGBArgba], not {c}."
                )
            ret.append(getattr(self, c))
        return tuple(ret)
