"""Rects all act the same, but take four of the possible eight attributes and calculate the rest."""

from __future__ import annotations

from typing import NamedTuple, Optional, TypedDict

from pyglet.math import Vec2

from arcade.types.numbers import AsFloat
from arcade.types.vector_like import AnchorPoint

from arcade.utils import ReplacementWarning, warning

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

    def resize(self, width: AsFloat, height: AsFloat, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        anchor_x = self.left + anchor.x * self.width
        anchor_y = self.bottom + anchor.y * self.height

        ratio_x = width / (self.width or 1.0)
        ratio_y = height / (self.height or 1.0)

        adjusted_left = anchor_x + (self.left - anchor_x) * ratio_x
        adjusted_right = anchor_x + (self.right - anchor_x) * ratio_x
        adjusted_top = anchor_y + (self.top - anchor_y) * ratio_y
        adjusted_bottom = anchor_y + (self.bottom - anchor_y) * ratio_y

        return LRBT(adjusted_left, adjusted_right, adjusted_top, adjusted_bottom)

    def scale(self, new_scale: AsFloat, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        anchor_x = self.left + anchor.x * self.width
        anchor_y = self.bottom + anchor.y * self.height

        adjusted_left = anchor_x + (self.left - anchor_x) * new_scale
        adjusted_right = anchor_x + (self.right - anchor_x) * new_scale
        adjusted_top = anchor_y + (self.top - anchor_y) * new_scale
        adjusted_bottom = anchor_y + (self.bottom - anchor_y) * new_scale

        return LRBT(adjusted_left, adjusted_right, adjusted_bottom, adjusted_top)

    def scale_axes(self, new_scale: Vec2, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        anchor_x = self.left + anchor.x * self.width
        anchor_y = self.bottom + anchor.y * self.height

        adjusted_left = anchor_x + (self.left - anchor_x) * new_scale.x
        adjusted_right = anchor_x + (self.right - anchor_x) * new_scale.x
        adjusted_top = anchor_y + (self.top - anchor_y) * new_scale.y
        adjusted_bottom = anchor_y + (self.bottom - anchor_y) * new_scale.y

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
        return self.resize(width, height, anchor)

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
        return self.resize(width, height, anchor)

    def clamp_height(self, min_height: Optional[AsFloat] = None, max_height: Optional[AsFloat] = None,
                     anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        height = min(max_height or float("inf"), max(min_height or 0.0, self.height))
        return self.resize(self.width, height, anchor)

    def clamp_width(self, min_width: Optional[AsFloat] = None, max_width: Optional[AsFloat] = None,
                    anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        width = min(max_width or float("inf"), max(min_width or 0.0, self.width))
        return self.resize(width, self.height, anchor)

    def clamp_size(self,
                   min_width: Optional[AsFloat] = None, max_width: Optional[AsFloat] = None,
                   min_height: Optional[AsFloat] = None, max_height: Optional[AsFloat] = None,
                   anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        width = min(max_width or float("inf"), max(min_width or 0.0, self.width))
        height = min(max_height or float("inf"), max(min_height or 0.0, self.height))
        return self.resize(width, height, anchor)

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

    def point_on_bounds(self, point: Vec2, tolerance: float) -> bool:
        if tolerance > self.width / 2:
            return XYWH(self.x, self.y, self.width + tolerance, self.height + tolerance).point_in_rect(point)

        return (XYWH(self.x, self.top, self.width + tolerance, tolerance).point_in_rect(point) or
                XYWH(self.x, self.bottom, self.width + tolerance, tolerance).point_in_rect(point) or
                XYWH(self.left, self.y, tolerance, self.height + tolerance).point_in_rect(point) or
                XYWH(self.right, self.y, tolerance, self.height + tolerance).point_in_rect(point))

    def to_points(self) -> tuple[Vec2, Vec2, Vec2, Vec2]:
        """Returns a tuple of the four corners of this Rect."""
        left = self.left
        bottom = self.bottom
        right = self.right
        top = self.top
        return (
            Vec2(left, bottom),
            Vec2(left, top),
            Vec2(right, top),
            Vec2(right, bottom)
        )

    @property
    def lbwh(self) -> RectParams:
        """Provides a view into the Rect in the form of a tuple of (left, bottom, width, height)."""
        return (self.left, self.bottom, self.width, self.height)

    @property
    def lrbt(self) -> RectParams:
        """Provides a view into the Rect in the form of a tuple of (left, right, bottom, top)."""
        return (self.left, self.right, self.bottom, self.top)

    @property
    def xywh(self) -> RectParams:
        """Provides a view into the Rect in the form of a tuple of (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)

    @property
    def xyrr(self) -> RectParams:
        """Provides a view into the Rect in the form of a tuple of (x, y, width / 2, height / 2)."""
        return (self.x, self.y, self.width / 2, self.height / 2)

    @property
    def viewport(self) -> ViewportParams:
        """Provides a view into the Rect in the form of a tuple of (left, right, bottom, top), coerced to integers."""
        return (int(self.left), int(self.right), int(self.bottom), int(self.top))

    @classmethod
    def from_kwargs(cls, **kwargs: AsFloat) -> Rect:
        """Creates a new Rect from keyword arguments. Throws ValueError if not enough are provided.

        Expected forms are:
        - LRBT (providing `left`, `right`, `bottom`, and `top`)
        - LBWH (providing `left`, `bottom`, `width`, and `height`)
        - XYWH (providing `x`, `y`, `width`, and `height`)
        """
        # Perform iteration only once and store it as a set literal
        specified: set[str] = {k for k, v in kwargs.items() if v is not None}
        have_lb = 'left' in specified and 'bottom' in specified

        # LRBT
        if have_lb and 'top' in specified and 'right' in specified:
            return LRBT(kwargs["left"], kwargs["right"], kwargs["bottom"], kwargs["top"])  # type: ignore

        # LBWH
        have_wh = 'width' in specified and 'height' in specified
        if have_wh and have_lb:
            return LBWH(kwargs["left"], kwargs["bottom"], kwargs["width"], kwargs["height"])  # type: ignore

        # XYWH
        if have_wh and 'x' in specified and 'y' in specified:
            return XYWH(kwargs["x"], kwargs["y"], kwargs["width"], kwargs["height"])  # type: ignore

        raise ValueError("Not enough attributes defined for a valid rectangle!")

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

    # Since __repr__ is handled automatically by NamedTuple, we focus on
    # human-readable spot-check values for __str__ instead.
    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__} LRBT({self.left}, {self.right}, {self.bottom}, {self.top})"
            f" XYWH({self.x}, {self.y}, {self.width}, {self.height})>")


# Shorthand creation helpers

def LRBT(left: AsFloat, right: AsFloat, bottom: AsFloat, top: AsFloat) -> Rect:
    """Creates a new Rect from left, right, bottom, and top parameters."""
    width = right - left
    height = top - bottom
    x = left + (width / 2)
    y = bottom + (height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def LBWH(left: AsFloat, bottom: AsFloat, width: AsFloat, height: AsFloat) -> Rect:
    """Creates a new Rect from left, bottom, width, and height parameters."""
    right = left + width
    top = bottom + height
    x = left + (width / 2)
    y = bottom + (height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def XYWH(x: AsFloat, y: AsFloat, width: AsFloat, height: AsFloat) -> Rect:
    """Creates a new Rect from center x, center y, width, and height parameters."""
    left = x - (width / 2)
    right = x + (width / 2)
    bottom = y - (width / 2)
    top = y + (width / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def XYRR(x: AsFloat, y: AsFloat, half_width: AsFloat, half_height: AsFloat) -> Rect:
    """Creates a new Rect from center x, center y, half width, and half height parameters. This is mainly used by OpenGL."""
    left = x - half_width
    right = x + half_width
    bottom = y - half_width
    top = y + half_width
    return Rect(left, right, bottom, top, half_width * 2, half_height * 2, x, y)


def XYWHAnchored(x: AsFloat, y: AsFloat, width: AsFloat, height: AsFloat, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
    """Creates a new Rect from x, y, width, and height parameters, anchored at a relative point."""
    left = x - anchor.x * width
    right = left + width
    bottom = y - anchor.y * height
    top = bottom + height
    c_x = left + width / 2.0
    c_y = bottom + height / 2.0
    return Rect(left, right, bottom, top, width, height, c_x, c_y)


def Viewport(left: int, bottom: int, width: int, height: int) -> Rect:
    """Creates a new Rect from left, bottom, width, and height parameters, restricted to integers."""
    right = left + width
    top = bottom + height
    x = left + int(width / 2)
    y = bottom + int(height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)
