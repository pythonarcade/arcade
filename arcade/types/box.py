"""
Box is the 3D counterpart to :py:class:`~arcade.types.rect.Rect`.
"""

from __future__ import annotations

from typing import Any, NamedTuple, TypedDict

from pyglet.math import Vec3

from arcade.types.numbers import AsFloat
from arcade.types.rect import LBWH, Rect
from arcade.types.vector_like import Point3


class BoxKwargs(TypedDict):
    """Annotates a plain :py:class:`dict` of :py:class:`Box` arguments.

    This is only meaningful as a type annotation during type checking.
    For example, the :py:meth:`Box.kwargs <arcade.types.Box.kwargs>`
    property returns an ordinary will actually be a :py:class:`dict`
    of :py:class:`Box` field names to :py:class:`float` values.

    To learn more, please see:

    * :py:class:`.Box`
    * :py:class:`typing.TypedDict`

    """

    left: float
    right: float
    bottom: float
    top: float
    near: float
    far: float
    width: float
    height: float
    depth: float
    x: float
    y: float
    z: float


class Box(NamedTuple):
    """A 3D box, with several convenience properties and functions.

    .. important:: Boxes are immutable and axis-aligned bounding prisms!

    As :py:class:`~typing.NamedTuple` subclasses, they cannot rotate and
    have no setters. This keeps their design simple and efficient. To
    rotate a box's points in 3D, use :py:meth:`to_points` with a 3D math
    library of your choice.

    To create a box, the helper class methods are usually the best choice:

    * :py:func:`.XYZWHD`
    * :py:func:`.LRBTNF`
    * :py:func:`.LBNWHD`
    * :py:meth:`.from_kwargs`

    """

    left: float
    right: float
    bottom: float

    top: float

    near: float
    far: float

    width: float
    height: float
    depth: float

    x: float
    y: float
    z: float

    @property
    def center_x(self) -> float:
        """Backwards-compatible alias for :py:attr:`.x`."""
        return self.x

    @property
    def center_y(self) -> float:
        """Backwards-compatible alias for :py:attr:`.y`."""
        return self.y

    @property
    def center_z(self) -> float:
        """Backwards-compatible alias for :py:attr:`.z`."""
        return self.z

    @property
    def center(self) -> Vec3:
        """Returns a :py:class:`~pyglet.math.Vec3` representing the center of the box."""
        return Vec3(self.x, self.y, self.z)

    @property
    def bottom_left_near(self) -> Vec3:
        """
        Returns a :py:class:`~pyglet.math.Vec3` representing the
        bottom-left-near corner of the box.
        """
        return Vec3(self.left, self.bottom, self.near)

    @property
    def bottom_left_far(self) -> Vec3:
        """
        Returns a :py:class:`~pyglet.math.Vec3` representing the
        bottom-left-far corner of the box.
        """
        return Vec3(self.left, self.bottom, self.far)

    @property
    def bottom_right_near(self) -> Vec3:
        """
        Returns a :py:class:`~pyglet.math.Vec3` representing the
        bottom-right-near corner of the box.
        """
        return Vec3(self.right, self.bottom, self.near)

    @property
    def bottom_right_far(self) -> Vec3:
        """
        Returns a :py:class:`~pyglet.math.Vec3` representing the
        bottom-right-far corner of the box.
        """
        return Vec3(self.right, self.bottom, self.far)

    @property
    def top_left_near(self) -> Vec3:
        """
        Returns a :py:class:`~pyglet.math.Vec3` representing the
        top-left-near corner of the box.
        """
        return Vec3(self.left, self.top, self.near)

    @property
    def top_left_far(self) -> Vec3:
        """
        Returns a :py:class:`~pyglet.math.Vec3` representing the
        top-left-far corner of the box.
        """
        return Vec3(self.left, self.top, self.far)

    @property
    def top_right_near(self) -> Vec3:
        """
        Returns a :py:class:`~pyglet.math.Vec3` representing the
        top-right-near corner of the box.
        """
        return Vec3(self.right, self.top, self.near)

    @property
    def top_right_far(self) -> Vec3:
        """
        Returns a :py:class:`~pyglet.math.Vec3` representing the
        top-right-far corner of the box.
        """
        return Vec3(self.right, self.top, self.far)

    @property
    def near_face(self) -> Rect:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        near face of the box.
        """
        return LBWH(self.left, self.bottom, self.width, self.height)

    @property
    def far_face(self) -> Rect:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        far face of the box.
        """
        return LBWH(self.left, self.bottom, self.width, self.height)

    @property
    def left_face(self) -> Rect:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        left face of the box.
        """
        return LBWH(self.near, self.bottom, self.depth, self.height)

    @property
    def right_face(self) -> Rect:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        right face of the box.
        """
        return LBWH(self.near, self.bottom, self.depth, self.height)

    @property
    def top_face(self) -> Rect:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        top face of the box.
        """
        return LBWH(self.left, self.near, self.width, self.depth)

    @property
    def bottom_face(self) -> Rect:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        bottom face of the box.
        """
        return LBWH(self.left, self.near, self.width, self.depth)

    @property
    def near_face_center(self) -> Vec3:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        center of the near face of the box.
        """
        return Vec3(self.x, self.y, self.near)

    @property
    def far_face_center(self) -> Vec3:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        center of the far face of the box.
        """
        return Vec3(self.x, self.y, self.far)

    @property
    def left_face_center(self) -> Vec3:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        center of the left face of the box.
        """
        return Vec3(self.left, self.y, self.z)

    @property
    def right_face_center(self) -> Vec3:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        center of the right face of the box.
        """
        return Vec3(self.right, self.y, self.z)

    @property
    def top_face_center(self) -> Vec3:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        center of the top face of the box.
        """
        return Vec3(self.x, self.top, self.z)

    @property
    def bottom_face_center(self) -> Vec3:
        """
        Returns a :py:class:`~arcade.Rect` representing the
        center of the bottom face of the box.
        """
        return Vec3(self.x, self.top, self.z)

    @property
    def size(self) -> Vec3:
        """Returns a :py:class:`~pyglet.math.Vec3` representing the size of the box."""
        return Vec3(self.width, self.height, self.depth)

    @property
    def volume(self) -> float:
        """The volume of the box in cubic pixels."""
        return self.width * self.height * self.depth

    def at_position(self, position: Point3) -> Box:
        """Returns a new :py:class:`Box` which is moved to put `position` at its center."""
        x, y, z = position
        return XYZWHD(x, y, z, self.width, self.height, self.depth)

    def move(self, dx: AsFloat = 0.0, dy: AsFloat = 0.0, dz: AsFloat = 0.0) -> Box:
        """
        Returns a new :py:class:`Box` which is moved by `dx` in the
        x-direction,`dy` in the y-direction, and `dz` in the z-direction.
        """
        return XYZWHD(self.x + dx, self.y + dy, self.z + dz, self.width, self.height, self.depth)

    def union(self, other: Box) -> Box:
        """Get the smallest Box encapsulating both this one and ``other``."""
        left = min(self.left, other.left)
        right = max(self.right, other.right)
        bottom = min(self.bottom, other.bottom)
        top = max(self.top, other.top)
        near = min(self.near, other.near)
        far = max(self.far, other.far)
        return LRBTNF(left, right, bottom, top, near, far)

    def __or__(self, other: Box) -> Box:
        """Shorthand for :py:meth:`Box.union(other) <union>`.

        Args:
            other: Another :py:class:`Box` instance.
        """
        return self.union(other)

    def intersection(self, other: Box) -> Box | None:
        """Return a :py:class:`Box` of the overlap if any exists.

        If the two :py:class:`Box` instances do not intersect, this
        method will return ``None`` instead.

        Args:
            other: Another :py:class:`Box` instance.
        """
        intersecting = self.overlaps(other)
        if not intersecting:
            return None
        left = max(self.left, other.left)
        right = min(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        top = min(self.top, other.top)
        near = max(self.near, other.near)
        far = min(self.far, other.far)
        return LRBTNF(left, right, bottom, top, near, far)

    def overlaps(self, other: Box) -> bool:
        """Returns ``True`` if `other` overlaps with ``self``.

        Args:
            other: Another :py:class:`Box` instance.
        """

        return (
            (other.width + self.width) / 2.0 > abs(self.x - other.x)
            and (other.height + self.height) / 2.0 > abs(self.y - other.y)
            and (other.depth + self.depth) / 2.0 > abs(self.z - other.z)
        )

    def __and__(self, other: Box) -> Box | None:
        """Shorthand for :py:meth:`Box.intersection(other) <interesection>`.

        Args:
            other: Another :py:class:`Box` instance.
        """
        return self.intersection(other)

    def point_in_box(self, point: Point3) -> bool:
        """``True`` if the point is in or touching the box, otherwise ``False``.

        Args:
             point: A 3D point.
        """
        x, y, z = point
        return (
            (self.left <= x <= self.right)
            and (self.bottom <= y <= self.top)
            and (self.near <= z <= self.far)
        )

    def __contains__(self, point: Point3 | Any) -> bool:
        """Shorthand for :py:meth:`Box.point_in_box(point) <point_in_box>`.

        Args:
            point: A tuple of :py:class:`int` or :py:class:`float` values.
        """
        from arcade.utils import is_iterable

        if not is_iterable(point):
            return False

        return self.point_in_box(point)

    def to_points(self) -> tuple[Vec3, Vec3, Vec3, Vec3, Vec3, Vec3, Vec3, Vec3]:
        """Return a new :py:class:`tuple` of this box's corners as 3D points.

        The points will be ordered as follows:

        #. :py:meth:`bottom_left_near`
        #. :py:meth:`top_left_near`
        #. :py:meth:`top_right_near`
        #. :py:meth:`bottom_right_near`
        #. :py:meth:`bottom_left_far`
        #. :py:meth:`top_left_far`
        #. :py:meth:`top_right_far`
        #. :py:meth:`bottom_right_far`

        """
        left = self.left
        bottom = self.bottom
        right = self.right
        top = self.top
        near = self.near
        far = self.far
        return (
            Vec3(left, bottom, near),
            Vec3(left, top, near),
            Vec3(right, top, near),
            Vec3(right, bottom, near),
            Vec3(left, bottom, far),
            Vec3(left, top, far),
            Vec3(right, top, far),
            Vec3(right, bottom, far),
        )

    @property
    def xyzwhd(self) -> tuple[AsFloat, AsFloat, AsFloat, AsFloat, AsFloat, AsFloat]:
        """Provides a tuple in the form (x, y, z, width, height, depth)."""
        return (self.x, self.y, self.z, self.width, self.height, self.depth)

    @property
    def lrbtnf(self) -> tuple[AsFloat, AsFloat, AsFloat, AsFloat, AsFloat, AsFloat]:
        """Provides a tuple in the form (left, right, bottom, top, near, far)."""
        return (self.left, self.right, self.bottom, self.top, self.near, self.far)

    @property
    def lbnwhd(self) -> tuple[AsFloat, AsFloat, AsFloat, AsFloat, AsFloat, AsFloat]:
        """Provides a tuple in the form (left, bottom, near, width, height, depth)."""
        return (self.left, self.bottom, self.near, self.width, self.height, self.depth)

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__} LRBTNF({self.left}, {self.right},"
            f"{self.bottom}, {self.top}, {self.near}, {self.far})"
            f" XYZWHD({self.x}, {self.y}, {self.z} {self.width}, {self.height}, {self.depth})>"
        )

    def __bool__(self) -> bool:
        """Returns ``True`` if volume is not ``0``, else ``False``."""
        return self.width != 0 and self.height != 0 and self.depth != 0


def XYZWHD(x: float, y: float, z: float, width: float, height: float, depth: float) -> Box:
    """Creates a new :py:class:`.Box` from center x, center y, center z,
    width, height, and depth parameters."""
    h_width = width / 2
    h_height = height / 2
    h_depth = depth / 2
    return Box(
        x - h_width,
        x + h_width,
        y - h_height,
        y + h_height,
        z - h_depth,
        z + h_depth,
        width,
        height,
        depth,
        x,
        y,
        z,
    )


def LBNWHD(
    left: float, bottom: float, near: float, width: float, height: float, depth: float
) -> Box:
    """Creates a new :py:class:`.Box` from left, bottom, near,
    width, height, and depth parameters."""
    return Box(
        left,
        left + width,
        bottom,
        bottom + height,
        near,
        near + depth,
        width,
        height,
        depth,
        left + (width / 2),
        bottom + (height / 2),
        near + (depth / 2),
    )


def LRBTNF(left: float, right: float, bottom: float, top: float, near: float, far: float) -> Box:
    """Creates a new :py:class:`.Box` from left, right, bottom, top, near, and far parameters."""
    width = right - left
    height = top - bottom
    depth = far - near
    return Box(
        left,
        right,
        bottom,
        top,
        near,
        far,
        width,
        height,
        depth,
        left + width / 2.0,
        bottom + height / 2.0,
        near + depth / 2.0,
    )
