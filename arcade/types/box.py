"""
Box is a stub named tuples which acts as the 3D partner to arcade.Rect
"""

from typing import NamedTuple

from arcade.types.vector_like import Point3


class Box(NamedTuple):
    """
    An immutable Axis-Aligned 3D Box
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

    def point_in_box(self, point: Point3) -> bool:
        x, y, z = point
        return (
            (self.left <= x <= self.right)
            and (self.bottom <= y <= self.top)
            and (self.near <= z <= self.far)
        )


def XYZWHD(x: float, y: float, z: float, width: float, height: float, depth: float) -> Box:
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


def LRBTNF(left: float, right: float, bottom: float, top: float, near: float, far: float) -> Box:
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
