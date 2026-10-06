"""
Drawing text with pyglet label
"""

import math
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

import PIL.Image
import PIL.ImageChops
import pyglet
from pyglet.enums import Style, Weight

# Pyright can't figure out the dynamic backend imports in pyglet.graphics
# right now. Maybe can fix in future Pyglet version
from pyglet.graphics import Batch, Group  # type: ignore
from pyglet.text import LinearGradient

import arcade
from arcade.exceptions import NoArcadeWindowError, PerformanceWarning, warning
from arcade.resources import resolve
from arcade.texture_atlas import TextureAtlasBase
from arcade.types import RGBA255, Color, Point, RGBOrA255
from arcade.types.rect import LRBT, Rect

__all__ = ["load_font", "Text", "TextPool", "create_text_sprite", "draw_text"]


def load_font(path: str | Path) -> None:
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

    You can also pass the path to a font file as ``font_name``,
    which loads the file the first time it's used.

    Args:
        path: Path to the font file
    Raises:
        FileNotFoundError: if the font specified wasn't found
    """
    _load_font_file(resolve(path))


FontNameOrNames = str | tuple[str, ...]

# Family names of the font files loaded so far, so each file is only
# loaded once, and a path can be used as a font name
_font_file_families: dict[Path, str | None] = {}


def _load_font_file(path: Path) -> str | None:
    """
    Load a font file, if it isn't loaded yet, and return its family name.

    Returns ``None`` if the family name couldn't be found.
    """
    if path in _font_file_families:
        return _font_file_families[path]

    # pyglet reports the families it added with the name the platform
    # uses for them, which is the name to load the font with
    families: list[str] = []

    def on_font_loaded(family_name, weight, style, stretch):
        families.append(family_name)

    pyglet.font.manager.push_handlers(on_font_loaded=on_font_loaded)
    try:
        pyglet.font.add_file(str(path))
    finally:
        pyglet.font.manager.remove_handlers(on_font_loaded=on_font_loaded)

    family: str | None = families[0] if families else None
    if family is None:
        # The file was already loaded some other way, for example with
        # pyglet.font.add_file(), so read the name from the file itself
        from pyglet.font.ttf import TruetypeInfo

        try:
            info = TruetypeInfo(str(path))
        except Exception:
            pass
        else:
            try:
                family = info.get_name("family")
            finally:
                info.close()

    _font_file_families[path] = family
    return family


def _font_file_family(font_name: str) -> str | None:
    """
    If a font name is the path to a font file, load it and return its
    family name. Otherwise, return ``None``.
    """
    try:
        path = resolve(font_name)
    except FileNotFoundError:
        # Not a file, or a resource that doesn't exist
        return None
    except OSError:
        # Some font names aren't valid paths at all, but a resource
        # handle should still report what's wrong with it
        if font_name.strip().startswith(":"):
            raise
        return None
    if not path.is_file():
        return None
    return _load_font_file(path)


def _attempt_font_name_resolution(font_name: FontNameOrNames) -> str:
    """Resolve a font name, path, or list of them to the name of one font.

    Paths to font files are loaded and replaced by the font's family
    name. The first name pyglet finds is returned, or pyglet's default
    font if it finds none.

    Args:
        font_name: A font name, path to a font file, or a tuple or list
            of them.
    """
    if isinstance(font_name, str):
        font_list: tuple[str, ...] = (font_name,)
    elif isinstance(font_name, (tuple, list)):
        font_list = tuple(font_name)
    else:
        raise TypeError(
            "font_name parameter must be a string, or a tuple of strings that specify a font name."
        )
    if not font_list or not all(font_list):
        raise ValueError(f"Couldn't find a font for {font_name!r}")

    names = [_font_file_family(font) or font for font in font_list]
    return pyglet.font.load(names).name


def _draw_pyglet_label(label: pyglet.text.Label) -> None:
    """
    Helper for drawing pyglet labels with rotation within arcade.

    Args:
       label: The pyglet label to draw
    """
    assert isinstance(label, pyglet.text.Label)
    label.draw()


def _to_text_color(color: RGBOrA255 | LinearGradient) -> Color | LinearGradient:
    """Convert a text color to a Color, passing gradients through unchanged."""
    if isinstance(color, LinearGradient):
        return color
    return Color.from_iterable(color)


def _normalize_font_name(font_name: FontNameOrNames) -> FontNameOrNames:
    """Make font names comparable, since a list and a tuple are never equal."""
    if isinstance(font_name, str):
        return font_name
    return tuple(font_name)


def _to_weight(bold: bool | str) -> str:
    """Convert a ``bold`` value to a pyglet font weight name."""
    if isinstance(bold, Enum):
        return bold.value
    if isinstance(bold, str) and bold:
        return bold
    return (Weight.BOLD if bold else Weight.NORMAL).value


def _from_weight(weight: Any) -> bool | str:
    """Convert a pyglet font weight back to a ``bold`` value."""
    if weight == Weight.BOLD.value:
        return True
    if weight is None or weight == Weight.NORMAL.value:
        return False
    return str(weight)


def _to_style(italic: bool | str) -> str:
    """Convert an ``italic`` value to a pyglet font style name."""
    if isinstance(italic, Enum):
        return italic.value
    if isinstance(italic, str) and italic:
        return italic
    return (Style.ITALIC if italic else Style.NORMAL).value


def _from_style(style: Any) -> bool | str:
    """Convert a pyglet font style back to an ``italic`` value."""
    if style == Style.ITALIC.value:
        return True
    if style is None or style == Style.NORMAL.value:
        return False
    return str(style)


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

    .. tip:: Batch drawing larger amounts of text

       Text objects can also be assigned a pyglet batch for batch
       rendering small or large amounts of text instances. This
       is by far the most efficient way to draw text::

            from pyglet.graphics import Batch

            batch = Batch()
            text_1 = Text("Hello, World 1", 0, 50, batch=batch)
            text_2 = Text("Hello, World 2", 0, 100, batch=batch)
            text_3 = Text("Hello, World 2", 0, 150, batch=batch)
            # Draw the batch
            batch.draw()
            # Remove a text instance from the batch
            text_2.batch = None

       The text instances an also be modified while in the batch
       such as changing the text value, position, or color.

    The constructor arguments work identically to those of
    :py:func:`~arcade.draw_text`. See its documentation for in-depth
    explanation for how to use each of them. For example code, see :ref:`drawing_text_objects`.

    Args:
        text: Initial text to display. Can be an empty string
        x: x position to align the text's anchor point with
        y: y position to align the text's anchor point with
        z: z position to align the text's anchor point with
        color: Color of the text as an RGBA tuple or a
            :py:class:`~arcade.types.Color` instance, or a
            :py:class:`pyglet.text.LinearGradient` for a left-to-right gradient.
        font_size: Size of the text in points
        width: A width limit in pixels
        align: Horizontal alignment; values other than "left" require width to be set.
            Valid options: ``"left"``, ``"center"``, ``"right"``.
        font_name: A font name, path to a font file, or list of names
        bold: Whether to draw the text as bold, and if a string,
              how bold. See :py:attr:`.bold` to learn more.
        italic: Whether to draw the text as italic
        anchor_x: How to calculate the anchor point's x coordinate.
                  Options: "left", "center", or "right"
        anchor_y: How to calculate the anchor point's y coordinate.
                  Options: "top", "bottom", "center", or "baseline".
        multiline: Requires width to be set; enables word wrap rather than clipping
        rotation: rotation in degrees, clockwise from horizontal
        batch: The batch to add the text to (for batch rendering text)
        group: The specific group in a a batch to add the text to
            (for batch rendering text)

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
    clockwise from horizontal, while negative values rotate
    counter-clockwise:

        .. figure:: ../images/text_rotation_degrees.png
           :width: 55%

           Rotation around the default anchor (
           ``anchor_y="baseline"`` and ``anchor_x="left"``)

    This class is a wrapper around pyglet's :py:class:`pyglet.text.Label`.
    More advanced users can use pyglet's label directly if preferred.
    """

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        color: RGBOrA255 | LinearGradient = arcade.color.WHITE,
        font_size: float = 12,
        width: int | None = None,
        align: str = "left",
        font_name: FontNameOrNames = ("calibri", "arial"),
        bold: bool | str = False,
        italic: bool | str = False,
        anchor_x: str = "left",
        anchor_y: str = "baseline",
        multiline: bool = False,
        rotation: float = 0,
        batch: Batch | None = None,
        group: Group | None = None,
        z: float = 0,
        **kwargs,
    ):
        self._arguments = dict(
            text=text,
            x=x,
            y=y,
            color=_to_text_color(color),
            font_size=font_size,
            width=width,
            align=align,
            font_name=font_name,
            weight=_to_weight(bold),
            style=_to_style(italic),
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            multiline=multiline,
            rotation=rotation,
            batch=batch,
            group=group,
            z=z,
            **kwargs,
        )

        if align not in ("left", "center", "right"):
            raise ValueError("The 'align' parameter must be equal to 'left', 'right', or 'center'.")

        if multiline and not width:
            raise ValueError(
                f"The 'width' parameter must be set to a non-zero value when 'multiline' is True, "
                f"but got {width!r}."
            )

        # Nesting depth of ``with text:`` blocks, and whether a pyglet
        # update was begun for a change inside them
        self._update_depth = 0
        self._update_begun = False
        # The font name as last requested, since the label holds the
        # resolved name (e.g. "arial" for ("calibri", "arial"))
        self._requested_font_name = _normalize_font_name(font_name)
        self._resolved_font_name: str | None = None

        self._initialized = False
        try:
            self._init_deferred()
        except NoArcadeWindowError:
            # No window yet, so create the label when it's first used
            pass

    @property
    def label(self) -> pyglet.text.Label:
        """
        The underlying pyglet.Label instance.
        """
        if not self._initialized:
            self._init_deferred()
        return self._label

    def initialize(self) -> None:
        """
        Manually initialize the Text if it was lazy loaded.
        This has no effect if the Text was already initialized.
        """
        if self._initialized:
            return
        self._init_deferred()

    def _init_deferred(self):
        """
        Deferred initialization when lazy loaded
        """
        # NOTE: Give the user a clear error message stating that the window is not created yet
        arcade.get_window()

        self._arguments["font_name"] = _attempt_font_name_resolution(self._arguments["font_name"])  # type: ignore
        self._label = pyglet.text.Label(**self._arguments)  # type: ignore
        self._resolved_font_name = self._label.font_name
        self._initialized = True

    def __enter__(self):
        """
        Update multiple attributes of this text, laying out the text
        only once at the end of the block.

        Changes that need a new layout, such as the text, font, or
        width, are laid out together when the block ends. Changes that
        don't, such as the position, color, or rotation, apply right
        away. If nothing that needs a new layout changes, the block
        costs nothing.
        """
        self._update_depth += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._update_depth -= 1
        if self._update_depth == 0 and self._update_begun:
            self._update_begun = False
            self.label.end_update()

    def _layout_label(self) -> pyglet.text.Label:
        """
        Get the label, to make a change that needs a new layout.

        Inside ``with text:``, the first such change begins a pyglet
        update, so all of them are laid out once when the block ends.
        """
        label = self.label
        if self._update_depth and not self._update_begun:
            label.begin_update()
            self._update_begun = True
        return label

    @property
    def batch(self) -> Batch | None:
        """The batch this text is in, if any.

        Can be unset by setting to ``None``.
        """
        return self.label.batch

    @batch.setter
    def batch(self, batch: Batch):
        self.label.batch = batch

    @property
    def group(self) -> Group | None:
        """
        The specific group in a batch the text should belong to.

        This is normally not necessary to specify unless you are
        batching very large sets of text needing to separate into
        groups or even mix with other pyglet batch content.
        """
        return self.label.group

    @group.setter
    def group(self, group: Group):
        if self.label.group is group:
            return
        self._layout_label().group = group

    @property
    def value(self) -> str:
        """
        Get or set the current text string to display.

        The value assigned will be converted to a string.
        """
        return self.label.text

    @value.setter
    def value(self, value: Any):
        value = str(value)
        if self.label.text == value:
            return
        self._layout_label().text = value

    @property
    def text(self) -> str:
        """
        Get or set the current text string to display.

        The value assigned will be converted to a string.

        This is an alias for :py:attr:`~arcade.Text.value`
        """
        return self.label.text

    @text.setter
    def text(self, value: Any):
        value = str(value)
        if self.label.text == value:
            return
        self._layout_label().text = value

    @property
    def x(self) -> float:
        """Get or set the x position of the label."""
        return self.label.x

    @x.setter
    def x(self, x: float) -> None:
        if self.label.x == x:
            return
        self.label.x = x

    @property
    def y(self) -> float:
        """Get or set the y position of the label."""
        return self.label.y

    @y.setter
    def y(self, y: float):
        if self.label.y == y:
            return
        self.label.y = y

    @property
    def z(self) -> float:
        """Get or set the z position of the label."""
        return self.label.z

    @z.setter
    def z(self, z: float):
        if self.label.z == z:
            return
        self.label.z = z

    @property
    def font_name(self) -> FontNameOrNames:
        """Get or set the font name(s) for the label."""
        if not isinstance(self.label.font_name, str):
            return tuple(self.label.font_name)
        else:
            return self.label.font_name

    @font_name.setter
    def font_name(self, font_name: FontNameOrNames) -> None:
        font_name = _normalize_font_name(font_name)
        label = self.label
        # Compare with the requested name, since the label holds the
        # resolved one, and check the label wasn't changed directly
        if font_name == self._requested_font_name and label.font_name == self._resolved_font_name:
            return
        label = self._layout_label()
        label.font_name = _attempt_font_name_resolution(font_name)
        self._requested_font_name = font_name
        self._resolved_font_name = label.font_name

    @property
    def font_size(self) -> float:
        """Get or set the font size of the label."""
        return self.label.font_size

    @font_size.setter
    def font_size(self, font_size: float):
        if self.label.font_size == font_size:
            return
        self._layout_label().font_size = font_size

    @property
    def anchor_x(self) -> str:
        """
        Get or set the horizontal anchor.

        Options: ``"left"``, ``"center"``, or ``"right"``
        """
        return self.label.anchor_x

    @anchor_x.setter
    def anchor_x(self, anchor_x: str):
        if self.label.anchor_x == anchor_x:
            return
        self.label.anchor_x = anchor_x  # type: ignore

    @property
    def anchor_y(self) -> str:
        """
        Get or set the vertical anchor.

        Options : ``"top"``, ``"bottom"``, ``"center"``, or ``"baseline"``
        """
        return self.label.anchor_y

    @anchor_y.setter
    def anchor_y(self, anchor_y: str):
        if self.label.anchor_y == anchor_y:
            return
        self.label.anchor_y = anchor_y  # type: ignore

    @property
    def rotation(self) -> float:
        """Get or set the clockwise rotation"""
        return self.label.rotation

    @rotation.setter
    def rotation(self, rotation: float):
        if self.label.rotation == rotation:
            return
        self.label.rotation = rotation

    @property
    def color(self) -> Color | LinearGradient:
        """
        Get or set the text color for the label.

        This is a :py:class:`~arcade.types.Color`, or a
        :py:class:`pyglet.text.LinearGradient` if one was set.
        """
        color = self.label.color
        if isinstance(color, LinearGradient):
            return color
        return Color.from_iterable(color)

    @color.setter
    def color(self, color: RGBOrA255 | LinearGradient):
        color = _to_text_color(color)
        label = self.label
        old_color = label.color
        if old_color == color:
            return
        # Solid colors are updated in place, but gradients need a new layout
        if isinstance(color, LinearGradient) or isinstance(old_color, LinearGradient):
            label = self._layout_label()
        label.color = color

    @property
    def width(self) -> int | None:
        """
        Get or set the width of the label in pixels.

        This value affects text flow when multiline text is used.
        If you are looking for the physical size if the text, see
        :py:attr:`~arcade.Text.content_width`
        """
        return self.label.width

    @width.setter
    def width(self, width: int):
        if self.label.width == width:
            return
        self._layout_label().width = width

    @property
    def height(self) -> int | None:
        """
        Get or set the height of the label in pixels.

        This value affects text flow when multiline text is used.
        If you are looking for the physical size if the text, see
        :py:attr:`~arcade.Text.content_height`
        """
        return self.label.height

    @height.setter
    def height(self, value: int):
        if self.label.height == value:
            return
        self._layout_label().height = value

    @property
    def size(self):
        """Get the size of the label."""
        return self.label.width, self.label.height

    @property
    def content_width(self) -> int:
        """Get the pixel width of the text contents."""
        return self.label.content_width

    @property
    def content_height(self) -> int:
        """Get the pixel height of the text content."""
        return self.label.content_height

    @property
    def left(self) -> float:
        """Pixel location of the left content border."""
        return self.label.left

    @property
    def right(self) -> float:
        """Pixel location of the right content border."""
        return self.label.right

    @property
    def top(self) -> float:
        """Pixel location of the top content border."""
        return self.label.top

    @property
    def bottom(self) -> float:
        """Pixel location of the bottom content border."""
        return self.label.bottom

    @property
    def rect(self) -> Rect:
        """Rect representing the bounds of the text.

        .. tip:: Don't worry about `width` being `None`.

            Although a label can be created with a `width=None`:
            * The underlying :py:mod:`pyglet` label will have bounding dimensions
            * This rect is for on-screen click and layout purposes, not maximum possible width
        """
        return LRBT(self.left, self.right, self.bottom, self.top)

    @property
    def content_size(self) -> tuple[int, int]:
        """Get the pixel width and height of the text contents."""
        return self.label.content_width, self.label.content_height

    @property
    def align(self) -> str:
        """Horizontal alignment; values other than ``"left"`` require width to be set.

        Valid options: ``"left"``, ``"center"``, ``"right"``.
        """
        return self.label.get_style("align")  # type: ignore

    @align.setter
    def align(self, align: str):
        if self.label.get_style("align") == align:
            return
        self._layout_label().set_style("align", align)

    @property
    def bold(self) -> bool | str:
        """
        Get or set bold state of the label.

        ``True`` is the same as ``"bold"``, and ``False`` the same as
        ``"normal"``. Other values are font weight names from
        :py:class:`pyglet.enums.Weight`, such as ``"thin"``,
        ``"light"``, ``"medium"``, ``"semibold"``, ``"extrabold"``
        or ``"black"``. Not every font has every weight.

        Returns ``True`` for bold, ``False`` for normal, and the weight
        name for any other weight.
        """
        return _from_weight(self.label.weight)

    @bold.setter
    def bold(self, bold: bool | str):
        weight = _to_weight(bold)
        if self.label.weight == weight:
            return
        self._layout_label().weight = weight

    @property
    def italic(self) -> bool | str:
        """
        Get or set the italic state of the label.

        ``True`` is the same as ``"italic"``, and ``False`` the same as
        ``"normal"``. ``"oblique"`` is also accepted.

        Returns ``True`` for italic, ``False`` for normal, and the style
        name for any other style.
        """
        return _from_style(self.label.document.get_style("style"))

    @italic.setter
    def italic(self, italic: bool | str):
        # Set the "style" document style, which pyglet uses to pick the
        # font. pyglet's own Label.italic sets an "italic" style, which
        # doesn't change the font: https://github.com/pyglet/pyglet/issues/1508
        style = _to_style(italic)
        if self.label.document.get_style("style") == style:
            return
        label = self._layout_label()
        label.document.set_style(0, len(label.document.text), {"style": style})

    @property
    def multiline(self) -> bool:
        """Get or set the multiline flag of the label."""
        return self.label.multiline

    @multiline.setter
    def multiline(self, multiline: bool):
        if self.label.multiline == multiline:
            return
        self._layout_label().multiline = multiline

    @property
    def visible(self) -> bool:
        """
        Whether the text is visible or not.

        This is a property of the underlying pyglet.Label.
        """
        return self.label.visible

    @visible.setter
    def visible(self, visible: bool):
        """
        Set the visibility of the text.

        This is a property of the underlying pyglet.Label.
        """
        self.label.visible = visible

    def draw(self) -> None:
        """
        Draw the label to the screen at its current ``x`` and ``y`` position.

        .. warning:: Cameras affect text drawing!

            If you want to draw a custom GUI that doesn't move with the
            game world, you will need a second :py:class:`~arcade.Camera`
            instance. For information on how to do this, see
            :ref:`sprite_move_scrolling`.
        """
        _draw_pyglet_label(self.label)

    def draw_debug(
        self,
        anchor_color: RGBOrA255 = arcade.color.RED,
        background_color: RGBOrA255 = arcade.color.DARK_BLUE,
        outline_color: RGBOrA255 = arcade.color.WHITE,
    ) -> None:
        """
        Draw test with debug geometry showing the content
        area, outline and the anchor point.

        Args:
            anchor_color: Color of the anchor point
            background_color: Color the content background
            outline_color: Color of the content outline
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

        _draw_pyglet_label(self.label)

    @property
    def position(self) -> Point:
        """
        The current x, y position as a tuple.

        This is faster than setting x and y position separately
        because the underlying geometry only needs to change position once.
        """
        return self.label.x, self.label.y

    @position.setter
    def position(self, point: Point):
        # Starting with Pyglet 2.0b2 label positions take a z parameter.
        x, y, *z = point
        label = self.label
        position = (x, y, z[0] if z else label.z)
        if label.position == position:
            return
        label.position = position

    @property
    def tracking(self) -> float | None:
        """
        Get/set the tracking amount for this text object, or rather,
        the added space between each character.

        The value is an amount in pixels and can be negative.
        To convert from the em unit, use Text.em_to_px().

        Returns:
            a pixel amount, or None if the tracking is inconsistent.
        """
        kerning = self.label.get_style("kerning")
        return kerning if kerning != pyglet.text.document.STYLE_INDETERMINATE else None

    @tracking.setter
    def tracking(self, value: float):
        if self.label.get_style("kerning") == value:
            return
        self._layout_label().set_style("kerning", value)

    def em_to_px(self, em: float) -> float:
        """Convert from an em value to a pixel amount.

        1em is defined as ``font_size`` pt.
        """
        return (em * self.font_size) * (4 / 3)

    def px_to_em(self, px: float) -> float:
        """Convert from a pixel amount to a value in ems.

        1em is defined as ``font_size`` pt.
        """
        return px / (4 / 3) / self.font_size


class TextPool:
    """A keyed cache of reusable Text objects.

    Avoids the cost of creating new :py:class:`arcade.Text` objects every
    frame for dynamic text that changes position, content, or color
    frequently.

    Any keyword arguments passed to the constructor become defaults for
    every ``Text`` created by this pool. Per-call keyword arguments
    override these defaults.

    Example::

        pool = arcade.TextPool(font_name="Arial")

        def on_draw(self):
            pool.draw("score", f"Score: {self.score}", 10, 580,
                       color=arcade.color.WHITE, font_size=16)
            pool.draw("fps", f"FPS: {arcade.get_fps():.0f}", 10, 560,
                       color=arcade.color.GRAY, font_size=12)

    Args:
        font_name: Default font for all text created by this pool.
        **defaults: Default keyword arguments passed to
            :py:class:`arcade.Text` on creation (e.g. ``bold``,
            ``anchor_x``).
    """

    def __init__(self, font_name: FontNameOrNames = ("calibri", "arial"), **defaults):
        self._font_name = font_name
        self._defaults = defaults
        self._cache: dict[str, Text] = {}

    def draw(
        self,
        key: str,
        text: str,
        x: float,
        y: float,
        color: RGBOrA255 | LinearGradient = arcade.color.WHITE,
        font_size: float = 12,
        **kwargs,
    ) -> Text:
        """Get or create a cached Text object, update it, and draw it.

        The first call with a given *key* creates the
        :py:class:`arcade.Text` object.  Subsequent calls update the
        existing object's properties and draw it, avoiding
        reconstruction costs.

        Args:
            key: Unique string identifier for this text slot.
            text: The string to display.
            x: X position in pixels.
            y: Y position in pixels.
            color: Text color (any format accepted by arcade).
            font_size: Font size in points.
            **kwargs: Additional :py:class:`arcade.Text` properties
                such as ``bold``, ``anchor_x``, ``rotation``, etc.

        Returns:
            The :py:class:`arcade.Text` object, useful for measuring
            ``content_width`` / ``content_height`` after drawing.
        """
        cached_text = self.get(key, text, x, y, color, font_size, **kwargs)
        cached_text.draw()
        return cached_text

    def get(
        self,
        key: str,
        text: str,
        x: float,
        y: float,
        color: RGBOrA255 | LinearGradient = arcade.color.WHITE,
        font_size: float = 12,
        **kwargs,
    ) -> Text:
        """Get or create a cached Text object and update its properties.

        Like :py:meth:`draw` but does **not** draw the text.  Useful
        when you need to measure the text (e.g. ``content_width``) or
        draw it later as part of a batch.

        Args:
            key: Unique string identifier for this text slot.
            text: The string to display.
            x: X position in pixels.
            y: Y position in pixels.
            color: Text color (any format accepted by arcade).
            font_size: Font size in points.
            **kwargs: Additional :py:class:`arcade.Text` properties
                such as ``bold``, ``anchor_x``, ``rotation``, etc.

        Returns:
            The :py:class:`arcade.Text` object.
        """
        if key in self._cache:
            cached_text = self._cache[key]
            with cached_text:
                cached_text.text = text
                cached_text.x = x
                cached_text.y = y
                cached_text.color = color
                cached_text.font_size = font_size
                for attr_name, attr_value in kwargs.items():
                    setattr(cached_text, attr_name, attr_value)
            return cached_text

        merged_kwargs = {**self._defaults, **kwargs}
        new_text = Text(
            text,
            x,
            y,
            color,
            font_size=font_size,
            font_name=self._font_name,
            **merged_kwargs,
        )
        self._cache[key] = new_text
        return new_text

    def clear(self) -> None:
        """Remove all cached Text objects from the pool."""
        self._cache.clear()

    def remove(self, key: str) -> None:
        """Remove a specific cached Text object by key.

        Args:
            key: The identifier of the text slot to remove.

        Raises:
            KeyError: If *key* is not in the pool.
        """
        del self._cache[key]


def create_text_sprite(
    text: str,
    color: RGBOrA255 | LinearGradient = arcade.color.WHITE,
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
    texture atlas. The texture has the same colors and transparency as the text, so the
    sprite looks the same as the text drawn directly.

    It then creates a sprite referencing the newly created texture, and positions it
    accordingly, and that is final result that is returned from the function.

    If you are providing a custom texture atlas, something important to keep in mind is
    that the resulting Sprite can only be added to SpriteLists which use that atlas. If
    it is added to a SpriteList which uses a different atlas, you will likely just see
    a black box drawn in its place.

    Args:
        text: Initial text to display. Can be an empty string
        color: Color of the text as an RGBA tuple or a
            :py:class:`~arcade.types.Color` instance, or a
            :py:class:`pyglet.text.LinearGradient` for a left-to-right gradient.
        font_size: Size of the text in points
        width: A width limit in pixels
        align: Horizontal alignment; values other than "left" require width to be set.
            Valid options: ``"left"``, ``"center"``, ``"right"``.
        font_name: A font name, path to a font file, or list of names
        bold: Whether to draw the text as bold, and if a string,
              how bold. See :py:attr:`arcade.gui.widgets.text.bold` to learn more.
        italic: Whether to draw the text as italic
        anchor_x: How to calculate the anchor point's x coordinate.
                  Options: "left", "center", or "right"
        multiline: Requires width to be set; enables word wrap rather than clipping
        background_color: The background color of the text. If None, the background
            will be transparent.
        texture_atlas: The texture atlas to use for the
            newly created texture. The default global atlas will be used if this is None.
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

    # Where the text is with its anchor at (0, 0), as a Text object would be
    left = text_object.left
    bottom = text_object.bottom
    # At least 1 pixel, so an empty string still makes a (transparent) texture
    size = (
        max(1, math.ceil(text_object.right - left)),
        max(1, math.ceil(text_object.top - bottom)),
    )

    # Draw it into the texture with its bottom left corner at (0, 0)
    text_object.x = -left
    text_object.y = -bottom

    # Each sprite needs its own image in the atlas. A name based on the text
    # would make sprites with the same text, but different colors or sizes,
    # share one.
    texture = arcade.Texture.create_empty(f"create_text_sprite_{uuid4().hex}", size)

    if not texture_atlas:
        texture_atlas = arcade.get_window().ctx.default_atlas
    texture_atlas.add(texture)

    # Drawing text over a transparent background would multiply the color
    # by the text's alpha and square the alpha, since pyglet blends alpha
    # like color, so the sprite would be drawn too faint. Instead, draw it
    # over black and over white: over black each pixel is the color times
    # the alpha, and over white it's lighter by (1 - alpha).
    def draw_over(background: RGBA255) -> PIL.Image.Image:
        with texture_atlas.render_into(texture) as fbo:
            fbo.clear(color=background)
            text_object.draw()
        return texture_atlas.read_texture_image_from_atlas(texture).convert("RGB")

    over_black = draw_over(arcade.color.BLACK)
    over_white = draw_over(arcade.color.WHITE)
    alpha = PIL.ImageChops.invert(PIL.ImageChops.subtract(over_white, over_black).convert("L"))
    # "RGBa" is premultiplied RGBA, so converting it divides out the alpha
    image = PIL.Image.merge("RGBa", (*over_black.split(), alpha)).convert("RGBA")
    if background_color:
        background = PIL.Image.new("RGBA", size, Color.from_iterable(background_color))
        image = PIL.Image.alpha_composite(background, image)

    # Store the result in the texture's image too. The atlas redraws
    # textures from their images when it rebuilds itself, which would
    # otherwise leave the sprite blank.
    texture.image_data.image = image
    texture_atlas.update_texture_image(texture)

    # Place the sprite where the Text object was drawn
    return arcade.Sprite(
        texture,
        center_x=left + size[0] / 2,
        center_y=bottom + size[1] / 2,
    )


# How many labels draw_text keeps for reuse, in total and per style
_DRAW_TEXT_CACHE_SIZE = 256
_DRAW_TEXT_LABELS_PER_STYLE = 8


def _get_draw_text_label(label_cache, style: tuple, text: str) -> "Text | None":
    """
    Find a label in draw_text's cache for drawing ``text`` in a style.

    Returns the label already showing this text, or the style's least
    recently used label (changed to show this text) if the style already
    has the most labels it may. Returns None if a new label should be made.
    Labels used every frame stay recent, so a line whose text keeps
    changing reuses its own previous label rather than another line's.
    """
    key = (style, text)
    label = label_cache.get(key)
    if label is not None:
        label_cache.move_to_end(key)
        return label

    count = 0
    oldest = None
    for cached_style, cached_text in label_cache:
        if cached_style == style:
            if oldest is None:
                oldest = (cached_style, cached_text)
            count += 1
    if oldest is None or count < _DRAW_TEXT_LABELS_PER_STYLE:
        return None

    label = label_cache.pop(oldest)
    label.text = text
    label_cache[key] = label
    return label


@warning(
    message=(
        "draw_text is much slower than drawing arcade.Text objects, especially "
        "for many lines or changing text. Consider using Text objects instead."
    ),
    warning_type=PerformanceWarning,
)
def draw_text(
    text: Any,
    x: float,
    y: float,
    color: RGBOrA255 | LinearGradient = arcade.color.WHITE,
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
    z: float = 0,
):
    """
    A simple way for beginners to draw text.

    .. warning:: Use :py:class:`arcade.Text` objects instead.

        This method of drawing text is slower than ``Text`` objects
        and might be removed in the near future. Each call has some
        overhead, text that changes is laid out again on every call,
        and many ``Text`` objects can be drawn at once in a batch.
        See :ref:`text_guide`.

    .. warning:: Cameras affect text drawing!

        If you want to draw a custom GUI that doesn't move with the
        game world, you will need a second camera. For information on
        how to do this, see :ref:`sprite_move_scrolling`.

    This function lets you start draw text easily with better
    performance than the old pillow-based text. If you need even higher
    performance, consider using :py:class:`~arcade.Text`.

    Example code can be found at :ref:`drawing_text`.

    Args:
        text: Initial text to display. Can be an empty string
        x: x position to align the text's anchor point with
        y: y position to align the text's anchor point with
        z: z position to align the text's anchor point with
        color: Color of the text as an RGBA tuple or a
            :py:class:`~arcade.types.Color` instance, or a
            :py:class:`pyglet.text.LinearGradient` for a left-to-right gradient.
        font_size: Size of the text in points
        width: A width limit in pixels
        align: Horizontal alignment; values other than "left" require width to be set.
            Valid options: ``"left"``, ``"center"``, ``"right"``.
        font_name: A font name, path to a font file, or list of names
        bold: Whether to draw the text as bold, and if a string,
              how bold. See :py:attr:`arcade.gui.widgets.text.bold` to learn more.
        italic: Whether to draw the text as italic
        anchor_x: How to calculate the anchor point's x coordinate.
                  Options: "left", "center", or "right"
        anchor_y: How to calculate the anchor point's y coordinate.
                  Options: "top", "bottom", "center", or "baseline".
        multiline: Requires width to be set; enables word wrap rather than clipping
        rotation: rotation in degrees, clockwise from horizontal

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
    clockwise from horizontal, while negative values rotate
    counter-clockwise:

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

    if align not in ("left", "center", "right"):
        raise ValueError("The 'align' parameter must be equal to 'left', 'right', or 'center'.")

    if multiline and not width:
        raise ValueError(
            f"The 'width' parameter must be set to a non-zero value when 'multiline' is True, "
            f"but got {width!r}."
        )

    color = _to_text_color(color)
    text = str(text)
    # Reuse labels, keyed by the settings that are expensive to change and
    # the text. Position, color, and rotation are cheap to update.
    style = (
        font_size,
        tuple(font_name) if isinstance(font_name, list) else font_name,
        bold,
        italic,
        anchor_x,
        anchor_y,
        align,
        width,
        multiline,
    )
    ctx = arcade.get_window().ctx
    label_cache = ctx.label_cache
    label = _get_draw_text_label(label_cache, style, text)

    if label is None:
        adjusted_font = _attempt_font_name_resolution(font_name)

        label = arcade.Text(
            text=text,
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
        label_cache[style, text] = label
        # Forget the least recently used label, so the cache can't grow
        # forever, for example when animating font_size or the text
        if len(label_cache) > _DRAW_TEXT_CACHE_SIZE:
            label_cache.popitem(last=False)

    if label.x != x or label.y != y or label.z != z:
        label.position = x, y, z  # type: ignore
    if label.color != color:
        label.color = color
    if label.rotation != rotation:
        label.rotation = rotation

    label.draw()
