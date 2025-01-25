"""Rects all act the same, but take four of the possible eight attributes and calculate the rest."""

from __future__ import annotations

import math
from typing import Any, NamedTuple, TypedDict

from pyglet.math import Vec2

from arcade.types.numbers import AsFloat
from arcade.types.vector_like import AnchorPoint, Point2

RectParams = tuple[AsFloat, AsFloat, AsFloat, AsFloat]
IntRectParams = tuple[int, int, int, int]


class RectKwargs(TypedDict):
    """Annotates a plain :py:class:`dict` of :py:class:`Rect` arguments.

    This is only meaningful as a type annotation during type checking.
    For example, the :py:meth:`Rect.kwargs <arcade.types.Rect.kwargs>`
    property returns an ordinary will actually be a :py:class:`dict`
    of :py:class:`Rect` field names to :py:class:`float` values.

    To learn more, please see:

    * :py:class:`.Rect`
    * :py:class:`typing.TypedDict`

    """

    left: float
    right: float
    bottom: float
    top: float
    width: float
    height: float
    x: float
    y: float


class Rect(NamedTuple):
    """A rectangle, with several convenience properties and functions.

    This object is immutable by design. It provides no setters, and is a NamedTuple
    subclass.

    Attempts to implement all Rectangle functions used in the library, and to be a
    helpful tool for developers storing/manipulating rectangle and rectangle-like
    constructs.

    Rectangles cannot rotate by design, since this complicates their implementation
    a lot.

    You probably don't want to create one of these directly, and should instead use
    a helper method, like :py:func:`.LBWH`, :py:func:`.LRBT`, :py:func:`.XYWH`, or
    :py:func:`.Viewport`.

    You can also use :py:meth:`.from_kwargs` to create a Rect from keyword arguments.
    """

    #: The X position of the rectangle's left edge.
    left: float
    #: The X position of the rectangle's right edge.
    right: float
    #: The Y position of the rectangle's bottom edge.
    bottom: float
    #: The Y position of the rectangle's top edge.
    top: float
    #: The total width of the rectangle along the X axis.
    #: To get the rectangle's :py:attr:`.height` well, use
    #: :py:attr:`.size`
    width: float
    #: The total height of the rectangle along the Y axis.
    #: To get the rectangle's :py:attr:`.width` as well, use
    #: :py:attr:`.size`.
    height: float
    #: The center of the rectangle along the X axis. To get its
    #: center :py:attr:`.y` as well, use :py:attr:`.center`.
    x: float
    #: The center of the rectangle along the Y axis. To get its
    #: center :py:attr:`.x` as well, use :py:attr:`.center`.
    y: float

    @property
    def center_x(self) -> float:
        """Backwards-compatible alias for :py:attr:`.x`."""
        return self.x

    @property
    def center_y(self) -> float:
        """Backwards-compatible alias for :py:attr:`.y`."""
        return self.y

    @property
    def center(self) -> Vec2:
        """Returns a :py:class:`~pyglet.math.Vec2` representing the center of the rectangle."""
        return Vec2(self.x, self.y)

    @property
    def bottom_left(self) -> Vec2:
        """
        Returns a :py:class:`~pyglet.math.Vec2` representing the
        bottom-left of the rectangle.
        """
        return Vec2(self.left, self.bottom)

    @property
    def bottom_right(self) -> Vec2:
        """
        Returns a :py:class:`~pyglet.math.Vec2` representing the
        bottom-right of the rectangle.
        """
        return Vec2(self.right, self.bottom)

    @property
    def top_left(self) -> Vec2:
        """
        Returns a :py:class:`~pyglet.math.Vec2` representing the
        top-left of the rectangle.
        """
        return Vec2(self.left, self.top)

    @property
    def top_right(self) -> Vec2:
        """
        Returns a :py:class:`~pyglet.math.Vec2` representing the
        top-right of the rectangle.
        """
        return Vec2(self.right, self.top)

    @property
    def bottom_center(self) -> Vec2:
        """
        Returns a :py:class:`~pyglet.math.Vec2` representing the
        bottom-center of the rectangle.
        """
        return Vec2(self.x, self.bottom)

    @property
    def center_right(self) -> Vec2:
        """
        Returns a :py:class:`~pyglet.math.Vec2` representing the
        center-right of the rectangle.
        """
        return Vec2(self.right, self.y)

    @property
    def top_center(self) -> Vec2:
        """
        Returns a :py:class:`~pyglet.math.Vec2` representing the
        top-center of the rectangle.
        """
        return Vec2(self.x, self.top)

    @property
    def center_left(self) -> Vec2:
        """Returns a :py:class:`~pyglet.math.Vec2` representing the center-left of the rectangle."""
        return Vec2(self.left, self.y)

    @property
    def size(self) -> Vec2:
        """Returns a :py:class:`~pyglet.math.Vec2` representing the size of the rectangle."""
        return Vec2(self.width, self.height)

    @property
    def area(self) -> float:
        """The area of the rectangle in square pixels."""
        return self.width * self.height

    @property
    def aspect_ratio(self) -> float:
        """Returns the ratio between the width and the height."""
        return self.width / self.height

    def at_position(self, position: Point2) -> Rect:
        """Returns a new :py:class:`Rect` which is moved to put `position` at its center."""
        x, y = position
        return XYWH(x, y, self.width, self.height)

    def move(self, dx: AsFloat = 0.0, dy: AsFloat = 0.0) -> Rect:
        """
        Returns a new :py:class:`Rect` which is moved by `dx` in the
        x-direction and `dy` in the y-direction.
        """
        return XYWH(self.x + dx, self.y + dy, self.width, self.height)

    def resize(
        self,
        width: AsFloat | None = None,
        height: AsFloat | None = None,
        anchor: Vec2 = AnchorPoint.CENTER,
    ) -> Rect:
        """
        Returns a new :py:class:`Rect` at the current Rect's position,
        but with a new width and height, anchored at a point (default center.)
        """
        width = width if width is not None else self.width
        height = height if height is not None else self.height

        anchor_x = self.left + anchor.x * self.width
        anchor_y = self.bottom + anchor.y * self.height

        # ratio_x = width / (self.width or 1.0)
        # ratio_y = height / (self.height or 1.0)

        # adjusted_left = anchor_x - (self.left - anchor_x) * ratio_x
        # adjusted_bottom = anchor_y + (self.bottom - anchor_y) * ratio_y
        # return LBWH(adjusted_left, adjusted_bottom, width, height)

        return XYWH(anchor_x, anchor_y, width, height, anchor)

    def scale(self, new_scale: AsFloat, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        """
        Returns a new :py:class:`Rect` scaled by a factor of ``new_scale``,
        anchored at a point (default center.)
        """
        anchor_x = self.left + anchor.x * self.width
        anchor_y = self.bottom + anchor.y * self.height

        adjusted_left = anchor_x + (self.left - anchor_x) * new_scale
        adjusted_right = anchor_x + (self.right - anchor_x) * new_scale
        adjusted_top = anchor_y + (self.top - anchor_y) * new_scale
        adjusted_bottom = anchor_y + (self.bottom - anchor_y) * new_scale

        return LRBT(adjusted_left, adjusted_right, adjusted_bottom, adjusted_top)

    def scale_axes(self, new_scale: Point2, anchor: Vec2 = AnchorPoint.CENTER) -> Rect:
        """
        Return a new :py:class:`Rect`
        scaled by a factor of `new_scale.x` in the width
        and `new_scale.y` in the height, anchored at a point (default center.)
        """
        anchor_x = self.left + anchor.x * self.width
        anchor_y = self.bottom + anchor.y * self.height

        nsx, nsy = new_scale
        adjusted_left = anchor_x + (self.left - anchor_x) * nsx
        adjusted_right = anchor_x + (self.right - anchor_x) * nsx
        adjusted_top = anchor_y + (self.top - anchor_y) * nsy
        adjusted_bottom = anchor_y + (self.bottom - anchor_y) * nsy

        return LRBT(adjusted_left, adjusted_right, adjusted_bottom, adjusted_top)

    def __mul__(self, scale: AsFloat) -> Rect:  # type: ignore[override]
        """Scale the Rect by ``scale`` relative to ``(0, 0)``."""
        return Rect(
            self.left * scale,
            self.right * scale,
            self.bottom * scale,
            self.top * scale,
            self.width * scale,
            self.height * scale,
            self.x * scale,
            self.y * scale,
        )

    def __truediv__(self, scale: AsFloat) -> Rect:
        """Scale the rectangle by 1/``scale`` relative to ``(0, 0)``."""
        return Rect(
            self.left / scale,
            self.right / scale,
            self.bottom / scale,
            self.top / scale,
            self.width / scale,
            self.height / scale,
            self.x / scale,
            self.y / scale,
        )

    def align_top(self, value: AsFloat) -> Rect:
        """Returns a new :py:class:`Rect`, which is aligned to the top at `value`."""
        return LBWH(self.left, value - self.height, self.width, self.height)

    def align_bottom(self, value: AsFloat) -> Rect:
        """Returns a new :py:class:`Rect`, which is aligned to the bottom at `value`."""
        return LBWH(self.left, value, self.width, self.height)

    def align_left(self, value: AsFloat) -> Rect:
        """Returns a new :py:class:`Rect`, which is aligned to the left at `value`."""
        return LBWH(value, self.bottom, self.width, self.height)

    def align_right(self, value: AsFloat) -> Rect:
        """Returns a new :py:class:`Rect`, which is aligned to the right at `value`."""
        return LBWH(value - self.width, self.bottom, self.width, self.height)

    def align_center(self, value: Point2) -> Rect:
        """Returns a new :py:class:`Rect`, which is aligned to the center x and y at `value`."""
        cx, cy = value
        return XYWH(cx, cy, self.width, self.height)

    def align_x(self, value: AsFloat) -> Rect:
        """Returns a new :py:class:`Rect`, which is aligned to the x at `value`."""
        return XYWH(value, self.y, self.width, self.height)

    def align_center_x(self, value: AsFloat) -> Rect:
        """Backwards-compatible alias for `Rect.x`."""
        return self.align_x(value)

    def align_y(self, value: AsFloat) -> Rect:
        """Get a new :py:class:`Rect`, which is aligned to the y at `value`."""
        return XYWH(self.x, value, self.width, self.height)

    def align_center_y(self, value: AsFloat) -> Rect:
        """Backwards-compatible alias for `Rect.x`."""
        return self.align_y(value)

    def min_size(
        self,
        width: AsFloat | None = None,
        height: AsFloat | None = None,
        anchor: Vec2 = AnchorPoint.CENTER,
    ) -> Rect:
        """
        Return a :py:class:`Rect` that is at least size `width` by `height`, positioned at
        the current position and anchored to a point (default center.)
        """
        width = max(width or 0.0, self.width)
        height = max(height or 0.0, self.height)
        return self.resize(width, height, anchor)

    def max_size(
        self,
        width: AsFloat | None = None,
        height: AsFloat | None = None,
        anchor: Vec2 = AnchorPoint.CENTER,
    ) -> Rect:
        """
        Return a :py:class:`Rect` that is at most size `width` by `height`, positioned at
        the current position and anchored to a point (default center.)
        """
        width = min(width or float("inf"), self.width)
        height = min(height or float("inf"), self.height)
        return self.resize(width, height, anchor)

    def clamp_height(
        self,
        min_height: AsFloat | None = None,
        max_height: AsFloat | None = None,
        anchor: Vec2 = AnchorPoint.CENTER,
    ) -> Rect:
        """
        Return a :py:class:`Rect` that has a height between `min_height` and `max_height`,
        positioned at the current position and anchored to a point (default center.)
        """
        height = min(max_height or float("inf"), max(min_height or 0.0, self.height))
        return self.resize(self.width, height, anchor)

    def clamp_width(
        self,
        min_width: AsFloat | None = None,
        max_width: AsFloat | None = None,
        anchor: Vec2 = AnchorPoint.CENTER,
    ) -> Rect:
        """Return a :py:class:`.Rect` constrained to the passed dimension.

        It will be created as follows:

        * Its :py:attr:`.width` will be between any provided ``min_width``
          and ``max_width``
        * It will be positioned at the current position using the passed
          ``anchor``

        Args:
            min_width:
                An optional minimum width.
            max_width:
                An optional maximum width.
            anchor:
                A :py:class:`~pyglet.math.Vec2` of the fractional
                percentage of the rectangle's total :py:attr:`.size` along
                both axes. It defaults to the center.
        """
        width = min(max_width or float("inf"), max(min_width or 0.0, self.width))
        return self.resize(width, self.height, anchor)

    def clamp_size(
        self,
        min_width: AsFloat | None = None,
        max_width: AsFloat | None = None,
        min_height: AsFloat | None = None,
        max_height: AsFloat | None = None,
        anchor: Vec2 = AnchorPoint.CENTER,
    ) -> Rect:
        """Get a new clamped-size rectangle at the same position and anchored at ``anchor_point``.

        This combines the effects of :py:meth:`clamp_width` and :py:meth:`clamp_height` into
        one call.
        """
        width = min(max_width or float("inf"), max(min_width or 0.0, self.width))
        height = min(max_height or float("inf"), max(min_height or 0.0, self.height))
        return self.resize(width, height, anchor)

    def union(self, other: Rect) -> Rect:
        """Get the smallest rectangle covering both this one and ``other``."""
        left = min(self.left, other.left)
        right = max(self.right, other.right)
        bottom = min(self.bottom, other.bottom)
        top = max(self.top, other.top)
        return LRBT(left, right, bottom, top)

    def __or__(self, other: Rect) -> Rect:
        """Shorthand for :py:meth:`rect.union(other) <union>`.

        Args:
            other: Another :py:class:`Rect` instance.
        """
        return self.union(other)

    def intersection(self, other: Rect) -> Rect | None:
        """Return a :py:class:`Rect` of the overlap if any exists.

        If the two :py:class:`Rect` instances do not intersect, this
        method will return ``None`` instead.

        Args:
            other: Another :py:class:`Rect` instance.
        """
        intersecting = self.overlaps(other)
        if not intersecting:
            return None
        left = max(self.left, other.left)
        right = min(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        top = min(self.top, other.top)
        return LRBT(left, right, bottom, top)

    def __and__(self, other: Rect) -> Rect | None:
        """Shorthand for :py:meth:`rect.intersection(other) <interesection>`.

        Args:
            other: Another :py:class:`Rect` instance.
        """
        return self.intersection(other)

    def overlaps(self, other: Rect) -> bool:
        """Returns ``True`` if `other` overlaps with ``self``.

        Args:
            other: Another :py:class:`Rect` instance.
        """

        return (other.width + self.width) / 2.0 > abs(self.x - other.x) and (
            other.height + self.height
        ) / 2.0 > abs(self.y - other.y)

    def point_in_rect(self, point: Point2) -> bool:
        """Returns ``True`` if ``point`` is inside this rectangle.

        Args:
            point: A tuple of :py:class:`int` or :py:class:`float` values.
        """
        px, py = point
        return (self.left <= px <= self.right) and (self.bottom <= py <= self.top)

    def point_in_bounds(self, point: Point2) -> bool:
        """Returns ``True`` if ``point`` is inside this rectangle excluding the boundaries.

        Args:
            point: A tuple of :py:class:`int` or :py:class:`float` values.
        """
        px, py = point
        return (self.left < px < self.right) and (self.bottom < py < self.top)

    def __contains__(self, point: Point2 | Any) -> bool:
        """Shorthand for :py:meth:`rect.point_in_rect(point) <point_in_rect>`.

        Args:
            point: A tuple of :py:class:`int` or :py:class:`float` values.
        """
        from arcade.utils import is_iterable

        if not is_iterable(point):
            return False

        return self.point_in_rect(point)

    def distance_from_bounds(self, point: Point2) -> float:
        """Returns the point's distance from the boundary of this rectangle."""
        px, py = point
        diff = Vec2(px - self.x, py - self.y)
        dx = abs(diff.x) - self.width / 2.0
        dy = abs(diff.y) - self.height / 2.0
        d = (max(dx, 0.0) ** 2 + max(dy, 0.0) ** 2) ** 0.5 + min(max(dx, dy), 0.0)
        return d

    def point_on_bounds(self, point: Point2, tolerance: float) -> bool:
        """Returns ``True`` if ``point`` is within ``tolerance`` of the bounds.

        The ``point``'s distance from the bounds is computed by through
        :py:meth:`distance_from_bounds`.

        Args:
            point: The point to check.
            tolerance: The maximum distance the point can be from the bounds.
        """
        return abs(self.distance_from_bounds(point)) < tolerance

    def position_to_uv(self, point: Point2) -> Vec2:
        """Convert a point to UV space values inside the rectangle.

        This is like a pair of ratios which measure how far the ``point``
        is from the rectangle's :py:meth:`bottom_left` up toward its
        :py:meth:`top_right` along each axis.

        .. warning:: This method does not clamp output!

                     Since ``point`` is absolute pixels, one or both axes
                     of the returned :py:class:`~pyglet.math.Vec2` can be:

                     * less than ``0.0``
                     * greater than ``1.0``


        Each axis of the return value measures how far into
        the rectangle's ``size`` the ``point`` is relative
        to the :py:meth:`bottom_left`:

        .. code-block:: python

           # consult the diagram below
           Vec2(
             (point.x - rect.left)   / rect.width,
             (point.y - rect.bottom) / rect.height
           )

        .. code-block::

              |------- rect.width ------|

                     The rectangle      (rect.top_right)
              +-------------------------T    ---
              |                         |     |
           - - - - - - - P  (Point x, y)|     |
           |  |                         | rect.height
           |  |          |              |     |
           y  |                         |     |
           |  B----------|--------------+    ---
           |  (rect.bottom_right)
           |
           O----- x -----|

        Args:
            point: A point relative to the rectangle's :py:meth:`bottom_left` corner.
        """
        x, y = point
        return Vec2(
            (x - self.left) / self.width,
            (y - self.bottom) / self.height,
        )

    def uv_to_position(self, uv: Point2) -> Vec2:
        """Convert a point in UV-space to a point within the rectangle.

        The ``uv`` is a pair of ratios which describe how far a point
        extends across the rectangle's :py:attr:`width` and
        :py:attr:`height` from the :py:attr:`bottom_left` toward its
        :py:attr:`top_right`.

        .. warning:: This method does not clamp output!

                     Since one or both of ``uv``'s components can be
                     less than ``0.0`` or greater than ``1.0``, the
                     returned point can fall outside the rectangle.

        The following can be used as arguments to this function:

        #. Values in :py:class:`~arcade.types.AnchorPoint`
        #. Returned values from :py:meth:`position_to_uv`
        #. Rescaled input data from controllers

        Args:
            uv:
                A pair of ratio values describing how far a
                a point falls from a rectangle's :py:attr:`bottom_left`
                toward its :py:attr:`top_right`.
        """
        x, y = uv
        return Vec2(self.left + x * self.width, self.bottom + y * self.height)

    def get_relative_to_anchor(self, point: Point2, anchor: Vec2 = AnchorPoint.CENTER) -> Vec2:
        """Convert a point to a relative offset from the anchor point.

        Args:
            point:
                The point to make relative.
            anchor:
                The anchor point to make the point relative to.
        """
        x, y = point
        rx = x - (self.left + (self.width * anchor.x))
        ry = y - (self.bottom + (self.height * anchor.y))
        return Vec2(rx, ry)

    def to_points(self) -> tuple[Vec2, Vec2, Vec2, Vec2]:
        """Return a new :py:class:`tuple` of this rectangle's corner points.

        The points will be ordered as follows:

        #. :py:meth:`bottom_left`
        #. :py:meth:`top_left`
        #. :py:meth:`top_right`
        #. :py:meth:`bottom_right`

        """
        left = self.left
        bottom = self.bottom
        right = self.right
        top = self.top
        return (Vec2(left, bottom), Vec2(left, top), Vec2(right, top), Vec2(right, bottom))

    @property
    def lbwh(self) -> RectParams:
        """Provides a tuple in the format of (left, bottom, width, height)."""
        return (self.left, self.bottom, self.width, self.height)

    @property
    def lrbt(self) -> RectParams:
        """Provides a tuple in the format of (left, right, bottom, top)."""
        return (self.left, self.right, self.bottom, self.top)

    @property
    def xywh(self) -> RectParams:
        """Provides a tuple in the format of (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)

    @property
    def xyrr(self) -> RectParams:
        """Provides a tuple in the format of (x, y, width / 2, height / 2)."""
        return (self.x, self.y, self.width / 2, self.height / 2)

    @property
    def lbwh_int(self) -> IntRectParams:
        """Provides a tuple in the format of (left, bottom, width, height), casted to ints."""
        return (int(self.left), int(self.bottom), int(self.width), int(self.height))

    @property
    def lrbt_int(self) -> IntRectParams:
        """Provides a tuple in the format of (left, right, bottom, top), casted to ints."""
        return (int(self.left), int(self.right), int(self.bottom), int(self.top))

    @property
    def xywh_int(self) -> IntRectParams:
        """Provides a tuple in the format of (x, y, width, height), casted to ints."""
        return (int(self.x), int(self.y), int(self.width), int(self.height))

    @property
    def xyrr_int(self) -> RectParams:
        """Provides a tuple in the format of (x, y, width / 2, height / 2), casted to ints."""
        return (int(self.x), int(self.y), int(self.width) / 2, int(self.height) / 2)

    @classmethod
    def from_kwargs(cls, **kwargs: AsFloat) -> Rect:
        """Creates a new Rect from keyword arguments. Throws ValueError if not enough are provided.

        Expected forms are:

        * LRBT (providing ``left``, ``right``, ``bottom``, and ``top``)
        * LBWH (providing ``left``, ``bottom``, ``width``, and ``height``)
        * XYWH (providing ``x``, ``y``, ``width``, and ``height``)
        """
        # Perform iteration only once and store it as a set literal
        specified: set[str] = {k for k, v in kwargs.items() if v is not None}
        have_lb = "left" in specified and "bottom" in specified

        # LRBT
        if have_lb and "top" in specified and "right" in specified:
            return LRBT(kwargs["left"], kwargs["right"], kwargs["bottom"], kwargs["top"])  # type: ignore

        # LBWH
        have_wh = "width" in specified and "height" in specified
        if have_wh and have_lb:
            return LBWH(kwargs["left"], kwargs["bottom"], kwargs["width"], kwargs["height"])  # type: ignore

        # XYWH
        if have_wh and "x" in specified and "y" in specified:
            return XYWH(kwargs["x"], kwargs["y"], kwargs["width"], kwargs["height"])  # type: ignore

        raise ValueError("Not enough attributes defined for a valid rectangle!")

    @property
    def kwargs(self) -> RectKwargs:
        """Get this rectangle as a :py:class:`dict` of field names to values.

        .. _tomli: https://github.com/hukkin/tomli

        Many data formats have corresponding Python modules with write
        support. Such modules often one or more functions which convert
        a passed :py:class:`dict` to a :py:class:`str` or write the result
        of such a conversion to a file.

        For example, the built-in :py:mod:`json` module offers the
        following functions on all Python versions currently supported
        by Arcade:

        .. list-table::
           :header-rows: 1

           * - Function
             - Summary
             - Useful For

           * - :py:func:`json.dump`
             - Write a :py:class:`dict` to a file
             - Saving game progress or edited levels

           * - :py:func:`json.dumps`
             - Get a :py:class:`dict` as a :py:class:`str` of JSON
             - Calls to a Web API

        .. note::

           The return value is an ordinary :py:class:`dict`.

           Although the return type is annotated as a
           :py:class:`.RectKwargs`, it is only meaningful when type
           checking. See :py:class:`typing.TypedDict` to learn more.

        """
        return {
            "left": self.left,
            "right": self.right,
            "bottom": self.bottom,
            "top": self.top,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }

    # Since __repr__ is handled automatically by NamedTuple, we focus on
    # human-readable spot-check values for __str__ instead.
    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__} LRBT({self.left}, {self.right}, {self.bottom}, {self.top})"
            f" XYWH({self.x}, {self.y}, {self.width}, {self.height})>"
        )

    def __bool__(self) -> bool:
        """Returns True if area is not 0, else False."""
        return self.width != 0 and self.height != 0

    def __round__(self, n: int) -> Rect:
        """Rounds the left, right, bottom, and top to `n` decimals."""
        return LRBT(
            round(self.left, n), round(self.right, n), round(self.bottom, n), round(self.top, n)
        )

    def __floor__(self) -> Rect:
        """Floors the left, right, bottom, and top."""
        return LRBT(
            math.floor(self.left),
            math.floor(self.right),
            math.floor(self.bottom),
            math.floor(self.top),
        )

    def __ceil__(self) -> Rect:
        """Floors the left, right, bottom, and top."""
        return LRBT(
            math.ceil(self.left), math.ceil(self.right), math.ceil(self.bottom), math.ceil(self.top)
        )


# Shorthand creation helpers


def LRBT(left: AsFloat, right: AsFloat, bottom: AsFloat, top: AsFloat) -> Rect:
    """Creates a new :py:class:`.Rect` from left, right, bottom, and top parameters."""
    width = right - left
    height = top - bottom
    x = left + (width / 2)
    y = bottom + (height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def LBWH(left: AsFloat, bottom: AsFloat, width: AsFloat, height: AsFloat) -> Rect:
    """Creates a new :py:class:`.Rect` from left, bottom, width, and height parameters."""
    right = left + width
    top = bottom + height
    x = left + (width / 2)
    y = bottom + (height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


def XYWH(
    x: AsFloat, y: AsFloat, width: AsFloat, height: AsFloat, anchor: Vec2 = AnchorPoint.CENTER
) -> Rect:
    """
    Creates a new :py:class:`.Rect` from x, y, width, and height parameters,
    anchored at a relative point (default center).
    """
    left = x - anchor.x * width
    right = left + width
    bottom = y - anchor.y * height
    top = bottom + height
    c_x = left + width / 2.0
    c_y = bottom + height / 2.0
    return Rect(left, right, bottom, top, width, height, c_x, c_y)


def XYRR(x: AsFloat, y: AsFloat, half_width: AsFloat, half_height: AsFloat) -> Rect:
    """
    Creates a new :py:class:`.Rect` from center x, center y, half width, and half height parameters.
    This is mainly used by OpenGL.
    """
    left = x - half_width
    right = x + half_width
    bottom = y - half_height
    top = y + half_height
    return Rect(left, right, bottom, top, half_width * 2, half_height * 2, x, y)


def Viewport(left: int, bottom: int, width: int, height: int) -> Rect:
    """
    Creates a new :py:class:`.Rect` from left, bottom, width, and height parameters,
    restricted to integers.
    """
    right = left + width
    top = bottom + height
    x = left + int(width / 2)
    y = bottom + int(height / 2)
    return Rect(left, right, bottom, top, width, height, x, y)


__all__ = [
    "IntRectParams",
    "RectParams",
    "RectKwargs",
    "Rect",
    "AnchorPoint",
    "LBWH",
    "LRBT",
    "XYWH",
    "XYRR",
    "Viewport",
]
