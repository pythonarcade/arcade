"""Rects all act the same, but take four of the possible eight attributes and calculate the rest."""

from __future__ import annotations

from typing import NamedTuple, Optional
from pyglet.math import Vec2

AsFloat = float | int


class Rect(NamedTuple):
    """Rects define a rectangle, with several convenience properties and functions.

    This object is immutable by design. It provides no setters, and is a NamedTuple subclass.

    Attempts to implement all Rectangle functions used in the library, with the notable exception
    of `.scale()`, as that function was ill-defined and assumed a bottom-left anchor point, something
    that should be accounted for if `.scale()` is to be reimplemented."""
    left: float
    right: float
    bottom: float
    top: float
    width: float
    height: float
    x: float
    y: float

    @property
    def center_x(self) -> float:
        """Backwards-compatible alias."""
        return self.x

    @property
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

    def move(self, dx: AsFloat = 0.0, dy: AsFloat = 0.0) -> Rect:
        """Returns new Rect which is moved by dx and dy"""
        return Rect(self.left + dx, self.right + dx,
                    self.bottom + dy, self.top + dy,
                    self.width, self.height,
                    self.x + dx, self.y + dy)

    def collides_with_point(self, point: Vec2) -> bool:
        return (self.left <= point.x <= self.left + self.width and
                self.bottom <= point.y <= self.bottom + self.height)

    def resize(self, new_size: Vec2) -> Rect:
        return Rect(self.left, self.right + new_size.x,
                    self.bottom, self.top + new_size.y,
                    self.width + new_size.x, self.height + new_size.y,
                    self.left + (self.right + new_size.x) / 2,
                    self.bottom + (self.top + new_size.y) / 2)

    def align_top(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the top."""
        diff_y = value - self.top
        return self.move(dy=diff_y)

    def align_bottom(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the bottom."""
        diff_y = value - self.bottom
        return self.move(dy=diff_y)

    def align_left(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the left."""
        diff_x = value - self.left
        return self.move(dx=diff_x)

    def align_right(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the right."""
        diff_x = value - self.right
        return self.move(dx=diff_x)

    def align_center(self, value: Vec2) -> Rect:
        """Returns new Rect, which is aligned to the center x and y."""
        diff_x = value.x - self.center_x
        diff_y = value.y - self.center_y
        return self.move(dx=diff_x, dy=diff_y)

    def align_center_x(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the center_x."""
        diff_x = value - self.center_x
        return self.move(dx=diff_x)

    def align_center_y(self, value: AsFloat) -> Rect:
        """Returns new Rect, which is aligned to the center_y."""
        diff_y = value - self.center_y
        return self.move(dy=diff_y)

    def min_size(
            self,
            width: Optional[AsFloat] = None,
            height: Optional[AsFloat] = None
    ) -> Rect:
        """
        Sets the size to at least the given min values.
        """
        left = self.left
        bottom = self.bottom
        width = max(width or 0.0, self.width)
        height = max(height or 0.0, self.height)
        rect = LBWH.as_new_attrs(left, bottom, width, height)
        return Rect(*rect)

    def max_size(
            self,
            width: Optional[AsFloat] = None,
            height: Optional[AsFloat] = None
    ) -> "Rect":
        """
        Limits the size to the given max values.
        """
        left = self.left
        bottom = self.bottom
        width = min(width or float("inf"), self.width)
        height = min(height or float("inf"), self.height)
        rect = LBWH.as_new_attrs(left, bottom, width, height)
        return Rect(*rect)

    def union(self, other: Rect) -> Rect:
        """
        Returns a new Rect that is the union of this rect and another.
        The union is the smallest rectangle that contains these two rectangles.
        """
        left = min(self.left, other.left)
        right = max(self.right, other.right)
        bottom = min(self.bottom, other.bottom)
        top = max(self.top, other.top)
        rect = LRBT.as_new_attrs(left, right, bottom, top)
        return Rect(*rect)

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
        rect = LRBT.as_new_attrs(left, right, bottom, top)
        return Rect(*rect)

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

    # Subclass-only methods
    @staticmethod
    def tuple_from_rect(rect: Rect) -> tuple[float, ...]:
        raise NotImplementedError

    @staticmethod
    def as_new_attrs(*args: tuple[AsFloat]) -> tuple[AsFloat, ...]:
        """Takes an incomplete signature and returns all attributes needed to create a new Rect."""
        raise NotImplementedError


class LRBT(Rect):
    def __new__(cls, left: AsFloat, right: AsFloat, bottom: AsFloat, top: AsFloat):
        rect = cls.as_new_attrs(left, right, bottom, top)
        return Rect.__new__(cls, *rect)

    @staticmethod
    def tuple_from_rect(rect: Rect) -> tuple[float, float, float, float]:
        return (rect.left, rect.right, rect.bottom, rect.top)

    @staticmethod
    def as_new_attrs(left: AsFloat, right: AsFloat, bottom: AsFloat, top: AsFloat) -> tuple[AsFloat, ...]:
        width = right - left
        height = top - bottom
        x = left + (width / 2)
        y = bottom + (height / 2)
        return (left, right, bottom, top, width, height, x, y)


class LBWH(Rect):
    def __new__(cls, left: AsFloat, bottom: AsFloat, width: AsFloat, height: AsFloat):
        rect = cls.as_new_attrs(left, bottom, width, height)
        return Rect.__new__(cls, *rect)

    @staticmethod
    def tuple_from_rect(rect: Rect) -> tuple[float, float, float, float]:
        return (rect.left, rect.bottom, rect.width, rect.height)

    @staticmethod
    def as_new_attrs(left: AsFloat, bottom: AsFloat, width: AsFloat, height: AsFloat) -> tuple[AsFloat, ...]:
        right = left + width
        top = bottom + height
        x = left + (width / 2)
        y = bottom + (height / 2)
        return (left, right, bottom, top, width, height, x, y)


class XYWH(Rect):
    def __new__(cls, x: AsFloat, y: AsFloat, width: AsFloat, height: AsFloat):
        rect = cls.to_rect_attrs(x, y, width, height)
        return Rect.__new__(cls, *rect)

    @staticmethod
    def tuple_from_rect(rect: Rect) -> tuple[float, float, float, float]:
        return (rect.x, rect.y, rect.width, rect.height)

    @staticmethod
    def to_rect_attrs(x: AsFloat, y: AsFloat, width: AsFloat, height: AsFloat) -> tuple[AsFloat, ...]:
        left = x - (width / 2)
        right = x + (width / 2)
        bottom = y - (width / 2)
        top = y + (width / 2)
        return (left, right, bottom, top, width, height, x, y)


class XYRR(Rect):
    def __new__(cls, x: AsFloat, y: AsFloat, half_width: AsFloat, half_height: AsFloat):
        rect = cls.to_rect_attrs(x, y, half_width * 2, half_height * 2)
        return Rect.__new__(cls, *rect)

    @staticmethod
    def from_rect(rect: Rect) -> tuple[float, float, float, float]:
        return (rect.x, rect.y, rect.width / 2, rect.height / 2)

    @staticmethod
    def to_rect_attrs(x: AsFloat, y: AsFloat, half_width: AsFloat, half_height: AsFloat) -> tuple[AsFloat, ...]:
        left = x - half_width
        right = x + half_width
        bottom = y - half_width
        top = y + half_width
        return (left, right, bottom, top, half_width * 2, half_height * 2, x, y)
