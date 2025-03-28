"""Points, sizes, and other similar aliases.

This is a submodule of :py:mod:`arcade.types` to avoid issues with:

* Circular imports
* Partially initialized modules

"""

from typing import Sequence, Union

from pyglet.math import Vec2, Vec3

from arcade.types.numbers import AsFloat

#: Matches both :py:class:`~pyglet.math.Vec2` and tuples of two numbers.
Point2 = Union[tuple[AsFloat, AsFloat], Vec2]

#: Matches both :py:class:`~pyglet.math.Vec3` and tuples of three numbers.
Point3 = Union[tuple[AsFloat, AsFloat, AsFloat], Vec3]


#: Matches any 2D or 3D point, including:
#:
#: * :py:class:`pyglet.math.Vec2`
#: * :py:class:`pyglet.math.Vec3`
#: * An ordinary :py:class:`tuple` of 2 or 3 values, either:
#:
#:   * :py:class:`int`
#    * :py:class:`float`
#:
#: This works the same way as :py:attr:`arcade.types.RGBOrA255` to
#: annotate RGB tuples, RGBA tuples, and :py:class:`tuple` or a
#: :py:class:`Color` instances.
Point = Union[Point2, Point3]

PointList = Sequence[Point]
Point2List = Sequence[Point2]
Point3List = Sequence[Point3]


# Speed / typing workaround:
# 1. Eliminate extra allocations
# 2. Allows type annotation to be cleaner, primarily for HitBox & subclasses
EMPTY_POINT_LIST: Point2List = tuple()


class AnchorPoint:
    """Common anchor points as constants in UV space.

    Each is a :py:class:`~pyglet.math.Vec2` with axis values between
    ``0.0`` and ``1.0``. They can be used as arguments to
    :py:meth:`Rect.uv_to_position <arcade.types.Rect.uv_to_position>`
    to help calculate:

    * a pixel offset inside a :py:class:`~arcade.types.Rect`
    * an absolute screen positions in pixels

    Advanced users may also find them useful when working with
    shaders.
    """

    BOTTOM_LEFT = Vec2(0.0, 0.0)
    BOTTOM_CENTER = Vec2(0.5, 0.0)
    BOTTOM_RIGHT = Vec2(1.0, 0.0)
    CENTER_LEFT = Vec2(0.0, 0.5)
    CENTER = Vec2(0.5, 0.5)
    CENTER_RIGHT = Vec2(1.0, 0.5)
    TOP_LEFT = Vec2(0.0, 1.0)
    TOP_CENTER = Vec2(0.5, 1.0)
    TOP_RIGHT = Vec2(1.0, 1.0)


__all__ = [
    "Point2",
    "Point3",
    "Point",
    "Point2List",
    "Point3List",
    "PointList",
    "AnchorPoint",
    "EMPTY_POINT_LIST",
]
