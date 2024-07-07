"""
Drawing text with pyglet label
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Union

import pyglet

import arcade
from arcade.resources import resolve
from arcade.texture_atlas import TextureAtlasBase
from arcade.types import Color, Point, RGBOrA255
from arcade.utils import PerformanceWarning, warning

__all__ = ["load_font", "Text", "create_text_sprite", "draw_text"]


def load_font(path: Union[str, Path]) -> None:
    """
    Load fonts in a file (usually .ttf) adding them to a global font registry.

    A file can contain one or multiple fonts. Each font has a name.
    Open the font file to find the actual name(s). These names
    are used to select font when drawing text.

    Examples::

        # Load a font in the current working directory
        # (absolute path is often better)
        arcade.load_font("Custom.ttf")
        # Load a font using a custom resource handle
        arcade.load_font(":font:Custom.ttf")

    :param path: A string, or an array of paths with fonts.
    :raises FileNotFoundError: if the font specified wasn't found
    :return:
    """
    file_path = resolve(path)
    pyglet.font.add_file(str(file_path))


FontNameOrNames = Union[str, tuple[str, ...]]


def _attempt_font_name_resolution(font_name: FontNameOrNames) -> str:
    """Attempt to resolve a font name.

    Preserves the original logic of this section, even though it
    doesn't seem to make sense entirely. Comments are an attempt
    to make sense of the original code.

    If it can't resolve a definite path, it will return the original
    argument for pyglet to attempt to resolve. This is consistent with
    the original behavior of this code before it was encapsulated.

    :param Union[str, tuple[str, ...]] font_name:
    :return: Either a resolved path or the original tuple
    """
    if font_name:
        # ensure
        if isinstance(font_name, str):
            font_list: tuple[str, ...] = (font_name,)
        elif isinstance(font_name, tuple):
            font_list = font_name
        else:
            raise TypeError(
                "font_name parameter must be a string, or a tuple of strings that specify a font name."
            )

        for font in font_list:
            try:
                path = resolve(font)
                # print(f"Font path: {path=}")

                # found a font successfully!
                return path.name

            except FileNotFoundError:
                pass

        # failed to find it ourselves, hope pyglet can make sense of it
        # Note this is the best approximation of what I unerstand the old
        # behavior to have been.
        return pyglet.font.load(font_list).name

    raise ValueError(f"Couldn't find a font for {font_name!r}")


def _draw_pyglet_label(label: pyglet.text.Label) -> None:
    """

    Helper for drawing pyglet labels with rotation within arcade.

    Originally part of draw_text in this module, now abstracted and improved
    so that both arcade.Text and arcade.draw_text can make use of it.

    :param label: a pyglet label to wrap and draw
    """
    assert isinstance(label, pyglet.text.Label)
    label.draw()


class Text:
    """
    An object-oriented way to draw text to the screen.

    .. tip:: Use this class when performance matters!

       Unlike :py:func:`~arcade.draw_text`, this class does not risk
       wasting time recalculating and re-setting any text each time
       :py:meth:`~arcade.Text.draw` is called. This makes it faster
       while:

       - requiring you to manage instances and drawing yourself
       - using negligible extra RAM

       The speed advantage scales as more text needs to be drawn
       to the screen.

    The constructor arguments work identically to those of
    :py:func:`~arcade.draw_text`. See its documentation for in-depth
    explanation for how to use each of them. For example code, see :ref:`drawing_text_objects`.

    :param text: Initial text to display. Can be an empty string
    :param x: x position to align the text's anchor point with
    :param y: y position to align the text's anchor point with
    :param z: z position to align the text's anchor point with
    :param color: Color of the text as an RGBA tuple or a
        :py:class:`~arcade.types.Color` instance.
    :param font_size: Size of the text in points
    :param width: A width limit in pixels
    :param align: Horizontal alignment; values other than "left" require width to be set
    :param Union[str, tuple[str, ...]] font_name: A font name, path to a font file, or list of names
    :param bold: Whether to draw the text as bold, and if a string,
        how bold. See :py:attr:`.bold` to learn more.
    :param italic: Whether to draw the text as italic
    :param anchor_x: How to calculate the anchor point's x coordinate.
                         Options: "left", "center", or "right"
    :param anchor_y: How to calculate the anchor point's y coordinate.
                         Options: "top", "bottom", "center", or "baseline".
    :param multiline: Requires width to be set; enables word wrap rather than clipping
    :param rotation: rotation in degrees, counter-clockwise from horizontal

    All constructor arguments other than ``text`` have a corresponding
    property. To access the current text, use the ``value`` property
    instead.

    By default, the text is placed so that:

    - the left edge of its bounding box is at ``x``
    - its baseline is at ``y``

    The baseline is located along the line the bottom of the text would
    be written on, excluding letters with tails such as y:

        .. figure:: ../images/text_anchor_y.png
           :width: 40%

           The blue line is the baseline for the string ``"Python"``

    ``rotation`` allows for the text to be rotated around the anchor
    point by the passed number of degrees. Positive values rotate
    counter-clockwise from horizontal, while negative values rotate
    clockwise:

        .. figure:: ../images/text_rotation_degrees.png
           :width: 55%

           Rotation around the default anchor (
           ``anchor_y="baseline"`` and ``anchor_x="left"``)

    """

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        color: RGBOrA255 = arcade.color.WHITE,
        font_size: float = 12,
        width: int | None = None,
        align: str = "left",
        font_name: FontNameOrNames = ("calibri", "arial"),
        bold: bool | str = False,
        italic: bool = False,
        anchor_x: str = "left",
        anchor_y: str = "baseline",
        multiline: bool = False,
        rotation: float = 0,
        batch: pyglet.graphics.Batch | None = None,
        group: pyglet.graphics.Group | None = None,
        z: float = 0,
    ):
        # Raises a RuntimeError if no window for better user feedback
        arcade.get_window()

        if align not in ("left", "center", "right"):
            raise ValueError("The 'align' parameter must be equal to 'left', 'right', or 'center'.")

        if multiline and not width:
            raise ValueError(
                f"The 'width' parameter must be set to a non-zero value when 'multiline' is True, "
                f"but got {width!r}."
            )

        adjusted_font = _attempt_font_name_resolution(font_name)

        self._label = pyglet.text.Label(
            text=text,
            # pyglet is lying about what it takes here and float is entirely valid
            x=x,  # type: ignore
            y=y,  # type: ignore
            z=z,  # type: ignore
            font_name=adjusted_font,
            # TODO: Fix this upstream (Mac & Linux seem to allow float)
            font_size=font_size,  # type: ignore
            # use type: ignore since cast is slow & pyglet used Literal
            anchor_x=anchor_x,  # type: ignore
            anchor_y=anchor_y,  # type: ignore
            color=Color.from_iterable(color),
            width=width,
            align=align,  # type: ignore
            bold=bold,
            italic=italic,
            multiline=multiline,
            rotation=rotation,  # type: ignore  # pending https://github.com/pyglet/pyglet/issues/843
            batch=batch,
            group=group,
        )

    def __enter__(self):
        """
        Update multiple attributes of this text,
        using efficient update mechanism of the underlying ``pyglet.Label``
        """
        self._label.begin_update()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._label.end_update()

    @property
    def batch(self) -> pyglet.graphics.Batch:
        return self._label.batch

    @batch.setter
    def batch(self, batch: pyglet.graphics.Batch):
        self._label.batch = batch

    @property
    def group(self) -> pyglet.graphics.Group | None:
        return self._label.group

    @group.setter
    def group(self, group: pyglet.graphics.Group):
        self._label.group = group

    @property
    def value(self) -> str:
        """
        Get or set the current text string to display.

        The value assigned will be converted to a string.
        """
        return self._label.text

    @value.setter
    def value(self, value: Any):
        value = str(value)
        if self._label.text == value:
            return
        self._label.text = value

    @property
    def text(self) -> str:
        """
        Get or set the current text string to display.

        The value assigned will be converted to a string.

        This is an alias for :py:attr:`~arcade.Text.value`
        """
        return self._label.text

    @text.setter
    def text(self, value: Any):
        value = str(value)
        if self._label.text == value:
            return
        self._label.text = value

    @property
    def x(self) -> float:
        """
        Get or set the x position of the label
        """
        return self._label.x

    @x.setter
    def x(self, x: float) -> None:
        if self._label.x == x:
            return
        self._label.x = x

    @property
    def y(self) -> float:
        """
        Get or set the y position of the label
        """
        return self._label.y

    @y.setter
    def y(self, y: float):
        if self._label.y == y:
            return
        self._label.y = y

    @property
    def z(self) -> float:
        """
        Get or set the z position of the label
        """
        return self._label.z

    @z.setter
    def z(self, z: float):
        if self._label.z == z:
            return
        self._label.z = z

    @property
    def font_name(self) -> FontNameOrNames:
        """
        Get or set the font name(s) for the label
        """
        return self._label.font_name

    @font_name.setter
    def font_name(self, font_name: FontNameOrNames) -> None:
        self._label.font_name = font_name

    @property
    def font_size(self) -> float:
        """
        Get or set the font size of the label
        """
        return self._label.font_size

    @font_size.setter
    def font_size(self, font_size: float):
        self._label.font_size = font_size

    @property
    def anchor_x(self) -> str:
        """
        Get or set the horizontal anchor.

        Options: "left", "center", or "right"
        """
        return self._label.anchor_x

    @anchor_x.setter
    def anchor_x(self, anchor_x: str):
        self._label.anchor_x = anchor_x  # type: ignore

    @property
    def anchor_y(self) -> str:
        """
        Get or set the vertical anchor.

        Options : "top", "bottom", "center", or "baseline"
        """
        return self._label.anchor_y

    @anchor_y.setter
    def anchor_y(self, anchor_y: str):
        self._label.anchor_y = anchor_y  # type: ignore

    @property
    def rotation(self) -> float:
        return self._label.rotation

    @rotation.setter
    def rotation(self, rotation: float):
        self._label.rotation = rotation

    @property
    def color(self) -> Color:
        """
        Get or set the text color for the label
        """
        return Color.from_iterable(self._label.color)

    @color.setter
    def color(self, color: RGBOrA255):
        self._label.color = Color.from_iterable(color)

    @property
    def width(self) -> int | None:
        """
        Get or set the width of the label in pixels.
        This value affects text flow when multiline text is used.
        If you are looking for the physical size if the text, see
        :py:attr:`~arcade.Text.content_width`
        """
        return self._label.width

    @width.setter
    def width(self, width: int):
        self._label.width = width

    @property
    def height(self) -> int | None:
        """
        Get or set the height of the label in pixels
        This value affects text flow when multiline text is used.
        If you are looking for the physical size if the text, see
        :py:attr:`~arcade.Text.content_height`
        """
        return self._label.height

    @height.setter
    def height(self, value: int):
        self._label.height = value

    @property
    def size(self):
        """
        Get the size of the label
        """
        return self._label.width, self._label.height

    @property
    def content_width(self) -> int:
        """
        Get the pixel width of the text contents
        """
        return self._label.content_width

    @property
    def content_height(self) -> int:
        """
        Get the pixel height of the text content.
        """
        return self._label.content_height

    @property
    def left(self) -> float:
        """
        Pixel location of the left content border.
        """
        return self._label.left

    @property
    def right(self) -> float:
        """
        Pixel location of the right content border.
        """
        return self._label.right

    @property
    def top(self) -> float:
        """
        Pixel location of the top content border.
        """
        return self._label.top

    @property
    def bottom(self) -> float:
        """
        Pixel location of the bottom content border.
        """
        return self._label.bottom

    @property
    def content_size(self) -> tuple[int, int]:
        """
        Get the pixel width and height of the text contents.
        """
        return self._label.content_width, self._label.content_height

    @property
    def align(self) -> str:
        return self._label.get_style("align")  # type: ignore

    @align.setter
    def align(self, align: str):
        self._label.set_style("align", align)

    @property
    def bold(self) -> bool | str:
        """
        Get or set bold state of the label.

        The supported values include:

        * ``"black"``
        * ``"bold" (same as ``True``)
        * ``"semibold"``
        * ``"semilight"``
        * ``"light"``

        """
        return self._label.bold

    @bold.setter
    def bold(self, bold: bool | str):
        self._label.bold = bold

    @property
    def italic(self) -> bool:
        """
        Get or set the italic state of the label
        """
        return self._label.italic

    @italic.setter
    def italic(self, italic: bool):
        self._label.italic = italic

    @property
    def multiline(self) -> bool:
        """
        Get or set the multiline flag of the label.
        """
        return self._label.multiline

    @multiline.setter
    def multiline(self, multiline: bool):
        self._label.multiline = multiline

    def draw(self) -> None:
        """
        Draw the label to the screen at its current ``x`` and ``y`` position.

        .. warning: Cameras affect text drawing!
            If you want to draw a custom GUI that doesn't move with the
            game world, you will need a second :py:class:`~arcade.Camera`
            instance. For information on how to do this, see
            :ref:`sprite_move_scrolling`.

        """
        _draw_pyglet_label(self._label)

    def draw_debug(
        self,
        anchor_color: RGBOrA255 = arcade.color.RED,
        background_color: RGBOrA255 = arcade.color.DARK_BLUE,
        outline_color: RGBOrA255 = arcade.color.WHITE,
    ) -> None:
        """
        Draw test with debug geometry showing the content
        area, outline and the anchor point.

        :param anchor_color: Color of the anchor point
        :param background_color: Color the content background
        :param outline_color: Color of the content outline
        """
        left = self.left
        right = self.right
        top = self.top
        bottom = self.bottom

        # Draw background
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color=background_color)

        # Draw outline
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, color=outline_color)

        # Draw anchor
        arcade.draw_point(self.x, self.y, color=anchor_color, size=6)

        _draw_pyglet_label(self._label)

    @property
    def position(self) -> Point:
        """
        The current x, y position as a tuple.

        This is faster than setting x and y position separately
        because the underlying geometry only needs to change position once.
        """
        return self._label.x, self._label.y

    @position.setter
    def position(self, point: Point):
        # Starting with Pyglet 2.0b2 label positions take a z parameter.
        x, y, *z = point

        if z:
            self._label.position = x, y, z[0]
        else:
            self._label.position = x, y, self._label.z


def create_text_sprite(
    text: str,
    color: RGBOrA255 = arcade.color.WHITE,
    font_size: float = 12.0,
    width: int | None = None,
    align: str = "left",
    font_name: FontNameOrNames = ("calibri", "arial"),
    bold: bool | str = False,
    italic: bool = False,
    anchor_x: str = "left",
    multiline: bool = False,
    texture_atlas: TextureAtlasBase | None = None,
    background_color: RGBOrA255 | None = None,
) -> arcade.Sprite:
    """
    Creates a sprite containing text based off of :py:class:`~arcade.Text`.

    Internally this creates a Text object and an empty texture. It then uses either the
    provided texture atlas, or gets the default one, and draws the Text object into the
    texture atlas.

    It then creates a sprite referencing the newly created texture, and positions it
    accordingly, and that is final result that is returned from the function.

    If you are providing a custom texture atlas, something important to keep in mind is
    that the resulting Sprite can only be added to SpriteLists which use that atlas. If
    it is added to a SpriteList which uses a different atlas, you will likely just see
    a black box drawn in its place.

    :param text: Initial text to display. Can be an empty string
    :param color: Color of the text as a tuple or list of 3 (RGB) or 4 (RGBA) integers
    :param font_size: Size of the text in points
    :param width: A width limit in pixels
    :param align: Horizontal alignment; values other than "left" require width to be set
    :param font_name: A font name, path to a font file, or list of names
    :param bold: Whether to draw the text as bold
    :param italic: Whether to draw the text as italic
    :param anchor_x: How to calculate the anchor point's x coordinate.
                         Options: "left", "center", or "right"
    :param multiline: Requires width to be set; enables word wrap rather than clipping
    :param texture_atlas: The texture atlas to use for the
        newly created texture. The default global atlas will be used if this is None.
    :param background_color: The background color of the text. If None, the background
        will be transparent.
    """
    text_object = Text(
        text,
        x=0,
        y=0,
        color=color,
        font_size=font_size,
        width=width,
        align=align,
        font_name=font_name,
        bold=bold,
        italic=italic,
        anchor_x=anchor_x,
        anchor_y="baseline",
        multiline=multiline,
    )

    size = (
        int(text_object.right - text_object.left),
        int(text_object.top - text_object.bottom),
    )
    text_object.y = -text_object.bottom
    texture = arcade.Texture.create_empty(text, size)

    if not texture_atlas:
        texture_atlas = arcade.get_window().ctx.default_atlas
    texture_atlas.add(texture)
    with texture_atlas.render_into(texture) as fbo:
        fbo.clear(color=background_color or arcade.color.TRANSPARENT_BLACK)
        text_object.draw()

    return arcade.Sprite(
        texture,
        center_x=text_object.right - (size[0] / 2),
        center_y=text_object.top,
    )


@warning(
    message="draw_text is an extremely slow function for displaying text. Consider using Text objects instead.",
    warning_type=PerformanceWarning,
)
def draw_text(
    text: Any,
    x: int,
    y: int,
    color: RGBOrA255 = arcade.color.WHITE,
    font_size: float = 12.0,
    width: int | None = None,
    align: str = "left",
    font_name: FontNameOrNames = ("calibri", "arial"),
    bold: bool | str = False,
    italic: bool = False,
    anchor_x: str = "left",
    anchor_y: str = "baseline",
    multiline: bool = False,
    rotation: float = 0,
    z: int = 0,
):
    """
    A simple way for beginners to draw text.

    .. warning:: Use :py:class:`arcade.Text` objects instead.

        This method of drawing text is very slow
        and might be removed in the near future.
        Text objects can be 10-100 times faster
        depending on the use case.

    .. warning:: Cameras affect text drawing!

        If you want to draw a custom GUI that doesn't move with the
        game world, you will need a second camera. For information on
        how to do this, see :ref:`sprite_move_scrolling`.

    This function lets you start draw text easily with better
    performance than the old pillow-based text. If you need even higher
    performance, consider using :py:class:`~arcade.Text`.

    Example code can be found at :ref:`drawing_text`.

    :param text: Text to display. The object passed in will be converted to a string
    :param x: x position to align the text's anchor point with
    :param y: y position to align the text's anchor point with
    :param z: z position to align the text's anchor point with
    :param color: Color of the text as an RGBA tuple or
        :py:class:`~arcade.types.Color` instance.
    :param font_size: Size of the text in points
    :param width: A width limit in pixels
    :param align: Horizontal alignment; values other than "left" require width to be set
    :param Union[str, tuple[str, ...]] font_name: A font name, path to a font file, or list of names
    :param bold: Whether to draw the text as bold, and if a :py:class:`str`,
        how bold to draw it. See :py:attr:`.Text.bold` to learn more.
    :param italic: Whether to draw the text as italic
    :param anchor_x: How to calculate the anchor point's x coordinate
    :param anchor_y: How to calculate the anchor point's y coordinate
    :param multiline: Requires width to be set; enables word wrap rather than clipping
    :param rotation: rotation in degrees, counter-clockwise from horizontal

    By default, the text is placed so that:

    - the left edge of its bounding box is at ``x``
    - its baseline is at ``y``

    The baseline of text is the line it would be written on:

        .. figure:: ../images/text_anchor_y.png
           :width: 40%

           The blue line is the baseline for the string ``"Python"``

    ``font_name`` can be any of the following:

    - a built-in font in the :ref:`Resources`
    - the name of a system font
    - a path to a font on the system
    - a `tuple` containing any mix of the previous three

    Each entry provided will be tried in order until one is found. If
    none of the fonts are found, a default font will be chosen (usually
    Arial).

    ``anchor_x`` and ``anchor_y`` specify how to calculate the anchor point,
    which affects how the text is:

    - Placed relative to ``x`` and ``y``
    - Rotated

    By default, the text is drawn so that ``x`` is at the left of
    the text's bounding box and ``y`` is at the baseline.

    You can set a custom anchor point by passing combinations of the
    following values for ``anchor_x`` and ``anchor_y``:

    .. list-table:: Values allowed by ``anchor_x``
        :widths: 20 40 40
        :header-rows: 1

        * - String value
          - Practical Effect
          - Anchor Position

        * - ``"left"`` `(default)`
          - Text drawn with its left side at ``x``
          - Anchor point on the left side of the text's bounding box

        * - ``"center"``
          - Text drawn horizontally centered on ``x``
          - Anchor point at horizontal center of text's bounding box

        * - ``"right"``
          - Text drawn with its right side at ``x``
          - Anchor placed on the right side of the text's bounding box


    .. list-table:: Values allowed by ``anchor_y``
        :widths: 20 40 40
        :header-rows: 1

        * - String value
          - Practical Effect
          - Anchor Position

        * - ``"baseline"`` `(default)`
          - Text drawn with baseline on ``y``.
          - Anchor placed at the text rendering baseline

        * - ``"top"``
          - Text drawn with its top aligned with ``y``
          - Anchor point placed at the top of the text

        * - ``"bottom"``
          - Text drawn with its absolute bottom aligned with ``y``,
            including the space for tails on letters such as y and g
          - Anchor point placed at the bottom of the text after the
            space allotted for letters such as y and g

        * - ``"center"``
          - Text drawn with its vertical center on ``y``
          - Anchor placed at the vertical center of the text


    ``rotation`` allows for the text to be rotated around the anchor
    point by the passed number of degrees. Positive values rotate
    counter-clockwise from horizontal, while negative values rotate
    clockwise:

        .. figure:: ../images/text_rotation_degrees.png
           :width: 55%

           Rotation around the default anchor point (
           ``anchor_y="baseline"`` and ``anchor_x="left"``)


    It can be helpful to think of this function working as follows:

    1. Text layout and alignment are calculated:

        1. The text's characters are laid out within a bounding box
           according to the current styling options

        2. The anchor point on the text is calculated based on
           the text value, styling, as well as values for ``anchor_x``
           and ``anchor_y``

    2. The text is placed so its anchor point is at ``(x,
       y))``

    3. The text is rotated around its anchor point before finally
       being drawn

    This function is less efficient than using :py:class:`~arcade.Text`
    because some steps above can be repeated each time a call is
    made rather than fully cached as with the class.

    """
    # See : https://github.com/pyglet/pyglet/blob/ff30eadc2942553c9de96d6ce564ad1bc3128fb4/pyglet/text/__init__.py#L401

    color = Color.from_iterable(color)
    # Cache the states that are expensive to change
    key = f"{font_size}{font_name}{bold}{italic}{anchor_x}{anchor_y}{align}{width}{rotation}"
    ctx = arcade.get_window().ctx
    label = ctx.label_cache.get(key)

    if align not in ("left", "center", "right"):
        raise ValueError("The 'align' parameter must be equal to 'left', 'right', or 'center'.")

    if multiline and not width:
        raise ValueError(
            f"The 'width' parameter must be set to a non-zero value when 'multiline' is True, "
            f"but got {width!r}."
        )

    if not label:
        adjusted_font = _attempt_font_name_resolution(font_name)

        label = arcade.Text(
            text=str(text),
            x=x,
            y=y,
            z=z,
            font_name=adjusted_font,
            font_size=font_size,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            color=color,
            width=width,
            align=align,
            bold=bold,
            italic=italic,
            multiline=multiline,
            rotation=rotation,
        )
        ctx.label_cache[key] = label

    # These updates are quite expensive
    if label.text != text:
        label.text = str(text)
    if label.x != x or label.y != y or label.z != z:
        label.position = x, y, z  # type: ignore
    if label.color != color:
        label.color = color
    if label.rotation != rotation:
        label.rotation = rotation

    label.draw()
    # This is absolutely necessary to prevent the vertex buffers
    # to be altered while another one is drawing. If the same cached
    # label is used multiple times in a single frame it's a disaster.
    ctx.flush()
