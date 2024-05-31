"""This will hold point, size, and other similar aliases.

This is a submodule of :py:mod:`arcade.types` to avoid issues with:

* Circular imports
* Partially initialized modules

"""
from __future__ import annotations

from typing import Union, Tuple

from pyglet.math import Vec2, Vec3

from arcade.types.numbers import AsFloat

Point2 = Union[Tuple[AsFloat, AsFloat], Vec2]
Point3 = Union[Tuple[AsFloat, AsFloat, AsFloat], Vec3]


class AnchorPoint:
    """Common anchor points as constants in UV space.

    Each is a :py:class:`~pyglet.math.Vec2` with axis values between
    ``0.0`` and ``1.0``. They can be used as arguments to
    :py:meth:`Rect.uv_to_position <arcade.types.Rect.uv_to_position>`
    to help calculate:

    * a pixel offset inside a :py:class:`~arcade.types.Rect`
    * an absolute screen positions in pixels

    Advanced users may also find them useful when working with
    :ref:`tutorials_shaders`.
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
    'AnchorPoint',
    'Point2',
    'Point3'
]
