"""Rects all act the same, but take four of the possible eight attributes and calculate the rest."""

from __future__ import annotations

from typing import NamedTuple, Optional, TypedDict
from pyglet.math import Vec2

# Only used for the reference draw implementation
# from array import array
# from arcade.draw_commands import _generic_draw_line_strip
# from arcade.math import rotate_point
# from arcade.types.color import RGBA255, Color
# from arcade.color import WHITE
# import pyglet.gl as gl
# ###############################################

from arcade.types import AsFloat
from arcade.utils import ReplacementWarning, warning
# from arcade.window_commands import get_window

RectParams = tuple[AsFloat, AsFloat, AsFloat, AsFloat]
ViewportParams = tuple[int, int, int, int]


class RectKwargs(TypedDict):
    left: float
    right: float
    bottom: float
    top: float
    width: float
    height: float
    x: float
    y: float


class AnchorPoint:
    """Provides helper aliases for several Vec2s to be used as anchor points in UV space."""
    BOTTOM_LEFT = Vec2(0.0, 0.0)
    BOTTOM_CENTER = Vec2(0.5, 0.0)
    BOTTOM_RIGHT = Vec2(1.0, 0.0)
    CENTER_LEFT = Vec2(0.0, 0.5)
    CENTER = Vec2(0.5, 0.5)
    CENTER_RIGHT = Vec2(1.0, 0.5)
    TOP_LEFT = Vec2(0.0, 1.0)
    TOP_CENTER = Vec2(0.5, 1.0)
    TOP_RIGHT = Vec2(1.0, 1.0)


class Rect(NamedTuple):
    """Rects define a rectangle, with several convenience properties and functions.

    This object is immutable by design. It provides no setters, and is a NamedTuple subclass.

    Attempts to implement all Rectangle functions used in the library, and to be a helpful
    tool for developers storing/maniulating rectangle and rectangle-like constructs.

    Rectangles cannot rotate by design, since this complicates their implmentation a lot.

    You probably don't want to create one of these directly, and should instead use a helper method."""
    left: float
    right: float
    bottom: float
    top: float
    width: float
    height: float
    x: float
    y: float

    @property
    @warning(ReplacementWarning, message=".center_x is deprecated. Please use .x instead.")
    def center_x(self) -> float:
        """Backwards-compatible alias."""
        return self.x

    @property
    @warning(ReplacementWarning, message=".center_y is deprecated. Please use .y instead.")
    def center_y(self) -> float:
        """Backwards-compatible alias."""
        return self.y

    @property
    def center(self) -> Vec2:
        return Vec2(self.x, self.y)

    @property
    def bottom_left(self) -> Vec2:
        return Vec2(self.left, self.bottom)

    @property
    @warning(ReplacementWarning, message=".position is deprecated. Please use .bottom_left instead.")
    def position(self) -> Vec2:
        """Backwards-compatible alias."""
        return self.bottom_left

    @property
    def bottom_right(self) -> Vec2:
        return Vec2(self.right, self.bottom)

    @property
    def top_left(self) -> Vec2:
        return Vec2(self.left, self.top)

    @property
    def top_right(self) -> Vec2:
        return Vec2(self.right, self.top)

    @property
    def bottom_center(self) -> Vec2:
        return Vec2(self.x, self.bottom)

    @property
    def right_center(self) -> Vec2:
        return Vec2(self.right, self.y)

    @property
    def top_center(self) -> Vec2:
        return Vec2(self.x, self.top)

    @property
    def left_center(self) -> Vec2:
        return Vec2(self.left, self.y)

    @property
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    def at_position(self, position: Vec2) -> Rect:
        """Returns new Rect which is moved to put `position` at it's center."""
        return XYWH(position.x, position.y, self.width, self.height)

    def move(self, dx: AsFloat = 0.0, dy: AsFloat = 0.0) -> Rect:
        """Returns new Rect which is moved by `dx` and `dy`."""
        return XYWH(self.x + dx, self.y + dy, self.width, self.height)

    def resize(self, new_size: Vec2, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        anchor_x = self.left + anchor.x * self.width
        anchor_y = self.bottom + anchor.y * self.height

        ratio_x = new_size.x / (self.width or 1.0)
        ratio_y = new_size.y / (self.height or 1.0)

        adjusted_left = anchor_x + (self.left - anchor_x) * ratio_x
        adjusted_right = anchor_x + (self.right - anchor_x) * ratio_x
        adjusted_top = anchor_y + (self.top - anchor_y) * ratio_y
        adjusted_bottom = anchor_y + (self.bottom - anchor_y) * ratio_y

        return LRBT(adjusted_left, adjusted_right, adjusted_top, adjusted_bottom)

    def scale(self, new_scale: float, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        anchor_x = self.left + anchor.x * self.width
        anchor_y = self.bottom + anchor.y * self.height

        adjusted_left = anchor_x + (self.left - anchor_x) * new_scale
        adjusted_right = anchor_x + (self.right - anchor_x) * new_scale
        adjusted_top = anchor_y + (self.top - anchor_y) * new_scale
        adjusted_bottom = anchor_y + (self.bottom - anchor_y) * new_scale

        return LRBT(adjusted_left, adjusted_right, adjusted_bottom, adjusted_top)

    def align_top(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the top."""
        return LBWH(self.left, value - self.height, self.width, self.height)

    def align_bottom(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the bottom."""
        return LBWH(self.left, value, self.width, self.height)

    def align_left(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the left."""
        return LBWH(value, self.bottom, self.width, self.height)

    def align_right(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the right."""
        return LBWH(value - self.width, self.bottom, self.width, self.height)

    def align_center(self, value: Vec2) -> Rect:
        """Returns new Rect, which is aligned to the center x and y."""
        return XYWH(value.x, value.y, self.width, self.height)

    def align_center_x(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the center_x."""
        return XYWH(value, self.y, self.width, self.height)

    def align_center_y(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the center_y."""
        return XYWH(self.x, value, self.width, self.height)

    def min_size(
            self,
            width: Optional[AsFloat] = None,
            height: Optional[AsFloat] = None,
            anchor: Vec2 = AnchorPoint.CENTER
    ) -> Rect:
        """
        Sets the size to at least the given min values.
        """
        width = max(width or 0.0, self.width)
        height = max(height or 0.0, self.height)
        return self.resize(Vec2(width, height), anchor)

    def max_size(
            self,
            width: Optional[AsFloat] = None,
            height: Optional[AsFloat] = None,
            anchor: Vec2 = AnchorPoint.CENTER
    ) -> Rect:
        """
        Limits the size to the given max values.
        """
        width = min(width or float("inf"), self.width)
        height = min(height or float("inf"), self.height)
        return self.resize(Vec2(width, height), anchor)

    def clamp_height(self, min_height: Optional[AsFloat] = None, max_height: Optional[AsFloat] = None,
                     anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        height = min(max_height or float("inf"), max(min_height or 0.0, self.height))
        return self.resize(Vec2(self.width, height), anchor)

    def clamp_width(self, min_width: Optional[AsFloat] = None, max_width: Optional[AsFloat] = None,
                    anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        width = min(max_width or float("inf"), max(min_width or 0.0, self.width))
        return self.resize(Vec2(width, self.height), anchor)

    def clamp_size(self,
                   min_width: Optional[AsFloat] = None, max_width: Optional[AsFloat] = None,
                   min_height: Optional[AsFloat] = None, max_height: Optional[AsFloat] = None,
                   anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        width = min(max_width or float("inf"), max(min_width or 0.0, self.width))
        height = min(max_height or float("inf"), max(min_height or 0.0, self.height))
        return self.resize(Vec2(width, height), anchor)

    def union(self, other: Rect) -> Rect:
        """
        Returns a new Rect that is the union of this rect and another.
        The union is the smallest rectangle that contains these two rectangles.
        """
        left = min(self.left, other.left)
        right = max(self.right, other.right)
        bottom = min(self.bottom, other.bottom)
        top = max(self.top, other.top)
        return LRBT(left, right, bottom, top)

    def __or__(self, other: Rect) -> Rect:
        return self.union(other)

    def overlaps(self, other: Rect) -> bool:
        u = self | other
        return u.width > 0 or u.height > 0

    def intersect(self, other: Rect) -> Rect | None:
        """
        Returns a new Rect that is the overlaping portion of this Rect and another.
        This will return None if no such rectangle exists.
        """
        intersecting = self.collides(other)
        if not intersecting:
            return None
        left = max(self.left, other.left)
        right = min(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        top = min(self.top, other.top)
        return LRBT(left, right, bottom, top)

    def collides(self, other: Rect) -> bool:
        return (self.right >= other.left and other.right >= self.left) and \
            (self.top >= other.bottom and other.top >= self.bottom)

    def __and__(self, other: Rect) -> Rect | None:
        return self.intersect(other)

    def point_in_rect(self, point: Vec2) -> bool:
        return (self.left < point.x < self.right) and (self.bottom < point.y < self.top)

    def to_points(self) -> tuple[Vec2, Vec2, Vec2, Vec2]:
        return (
            Vec2(self.left, self.bottom),
            Vec2(self.left, self.top),
            Vec2(self.right, self.top),
            Vec2(self.right, self.bottom)
        )

    @property
    def lbwh(self) -> RectParams:
        return (self.left, self.bottom, self.width, self.height)

    @property
    def lrbt(self) -> RectParams:
        return (self.left, self.right, self.bottom, self.top)

    @property
    def xywh(self) -> RectParams:
        return (self.x, self.y, self.width, self.height)

    @property
    def xyrr(self) -> RectParams:
        return (self.x, self.y, self.width / 2, self.height / 2)

    @property
    def viewport(self) -> ViewportParams:
        return (int(self.left), int(self.right), int(self.bottom), int(self.top))

    @property
    def kwargs(self) -> RectKwargs:
        return {"left": self.left,
                "right": self.right,
                "bottom": self.bottom,
                "top": self.top,
                "x": self.x,
                "y": self.y,
                "width": self.width,
                "height": self.height}

    def __repr__(self) -> str:
        return (f"<Rect LRBT({self.left}, {self.right}, {self.bottom}, {self.top})"
                f" XYWH({self.x}, {self.y}, {self.width}, {self.height})>")

    def __str__(self) -> str:
        return repr(self)


# Convinience constructors

def LRBT(left: AsFloat, right: AsFloat, bottom: AsFloat, top: AsFloat) -> Rect:
    width = right - left
    height = top - bottom
    x = left + (width / 2)
    y = bottom + (height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def LBWH(left: AsFloat, bottom: AsFloat, width: AsFloat, height: AsFloat) -> Rect:
    right = left + width
    top = bottom + height
    x = left + (width / 2)
    y = bottom + (height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def XYWH(x: AsFloat, y: AsFloat, width: AsFloat, height: AsFloat) -> Rect:
    left = x - (width / 2)
    right = x + (width / 2)
    bottom = y - (width / 2)
    top = y + (width / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def XYRR(x: AsFloat, y: AsFloat, half_width: AsFloat, half_height: AsFloat) -> Rect:
    left = x - half_width
    right = x + half_width
    bottom = y - half_width
    top = y + half_width
    return Rect(left, right, bottom, top, half_width * 2, half_height * 2, x, y)


def AnchorXYWH(x: AsFloat, y: AsFloat, width: AsFloat, height: AsFloat, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
    left = x - anchor.x * width
    right = left + width
    bottom = y - anchor.y * height
    top = bottom + height
    c_x = left + width / 2.0
    c_y = bottom + height / 2.0
    return Rect(left, right, bottom, top, width, height, c_x, c_y)


def Viewport(left: int, bottom: int, width: int, height: int) -> Rect:
    right = left + width
    top = bottom + height
    x = left + int(width / 2)
    y = bottom + int(height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def Kwargtangle(**kwargs: AsFloat) -> Rect:
    # LRBT
    if all(kwargs.get(v, None) is not None for v in ["left", "right", "top", "bottom"]):
        return LRBT(kwargs["left"], kwargs["right"], kwargs["bottom"], kwargs["top"])
    # LBWH
    elif all(kwargs.get(v, None) is not None for v in ["left", "bottom", "width", "height"]):
        return LBWH(kwargs["left"], kwargs["bottom"], kwargs["width"], kwargs["height"])
    # XYWH
    elif all(kwargs.get(v, None) is not None for v in ["x", "y", "width", "height"]):
        return XYWH(kwargs["x"], kwargs["y"], kwargs["width"], kwargs["height"])
    else:
        raise ValueError("Not enough attributes defined for a valid rectangle!")


## Reference implementations: draw
#
#def draw_outline(rect: Rect, color: RGBA255, border_width: float = 1, tilt_angle: float = 0):
#    """
#    Draw a rectangle outline.
#
#    :param rect: The rectangle to draw.
#        a :py:class`~arcade.types.Rect` instance.
#    :param color: The color of the rectangle.
#        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
#    :param border_width: width of the lines, in pixels.
#    :param tilt_angle: rotation of the rectangle. Defaults to zero (clockwise).
#    """
#
#    HALF_BORDER = border_width / 2
#
#    i_lb = rect.bottom_left.x  + HALF_BORDER, rect.bottom_left.y   + HALF_BORDER
#    i_rb = rect.bottom_right.x - HALF_BORDER, rect.bottom_right.y  + HALF_BORDER
#    i_rt = rect.top_right.x    - HALF_BORDER, rect.top_right.y     - HALF_BORDER
#    i_lt = rect.top_left.x     + HALF_BORDER, rect.top_left.y      - HALF_BORDER
#    o_lb = rect.bottom_left.x  - HALF_BORDER, rect.bottom_left.y   - HALF_BORDER
#    o_rb = rect.bottom_right.x + HALF_BORDER, rect.bottom_right.y  - HALF_BORDER
#    o_rt = rect.top_right.x    + HALF_BORDER, rect.top_right.y     + HALF_BORDER
#    o_lt = rect.top_left.x     - HALF_BORDER, rect.top_right.y     + HALF_BORDER
#
#    point_list: PointList = (o_lt, i_lt, o_rt, i_rt, o_rb, i_rb, o_lb, i_lb, o_lt, i_lt)
#
#    if tilt_angle != 0:
#        point_list_2 = []
#        for point in point_list:
#            new_point = rotate_point(point[0], point[1], rect.x, rect.y, tilt_angle)
#            point_list_2.append(new_point)
#        point_list = point_list_2
#
#    _generic_draw_line_strip(point_list, color, gl.GL_TRIANGLE_STRIP)
#
#
#def draw_filled(rect: Rect, color: RGBA255, tilt_angle: float = 0):
#    """
#    Draw a filled-in rectangle.
#
#    :param rect: The rectangle to draw.
#        a :py:class`~arcade.types.Rect` instance.
#    :param color: The color of the rectangle as an RGBA
#        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
#    :param tilt_angle: rotation of the rectangle (clockwise). Defaults to zero.
#    """
#    # Fail if we don't have a window, context, or right GL abstractions
#    window = get_window()
#    ctx = window.ctx
#    program = ctx.shape_rectangle_filled_unbuffered_program
#    geometry = ctx.shape_rectangle_filled_unbuffered_geometry
#    buffer = ctx.shape_rectangle_filled_unbuffered_buffer
#
#    # Validate & normalize to a pass the shader an RGBA float uniform
#    color_normalized = Color.from_iterable(color).normalized
#
#    # Pass data to the shader
#    program['color'] = color_normalized
#    program['shape'] = rect.width, rect.height, tilt_angle
#    buffer.orphan()
#    buffer.write(data=array('f', (rect.x, rect.y)))
#
#    geometry.render(program, mode=ctx.POINTS, vertices=1)
#
#
#def draw_outline_kwargs(color: RGBA255 = WHITE, border_width: int = 1, tilt_angle: float = 0, **kwargs):
#    rect = Kwargtangle(**kwargs)
#    draw_outline(rect, color, border_width, tilt_angle)
#
#
#def draw_filled_kwargs(color: RGBA255 = WHITE, tilt_angle: float = 0, **kwargs):
#    rect = Kwargtangle(**kwargs)
#    draw_filled(rect, color, tilt_angle)
#