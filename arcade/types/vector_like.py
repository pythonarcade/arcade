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


__all__ = [
    'AnchorPoint',
    'Point2',
    'Point3'
]
