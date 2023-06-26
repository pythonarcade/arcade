"""
Module for handling common texture transforms
such as rotation, translation, flipping etc.

We don't actually transform pixel data, we simply
transform the texture coordinates and hit box points.
"""
from typing import Dict, Tuple
from enum import Enum
from arcade.math import rotate_point
from arcade.types import PointList


class VertexOrder(Enum):
    """
    Order for texture coordinates.
    """
    UPPER_LEFT = 0
    UPPER_RIGHT = 1
    LOWER_LEFT = 2
    LOWER_RIGHT = 3


class Transform:
    """
    Base class for all texture transforms.

    Transforms are responsible for transforming the texture
    coordinates and hit box points.
    """
    #: How texture coordinates order should be changed
    #: for this transform.
    #: upper_left, upper_right, lower_left, lower_right
    order = (
        VertexOrder.UPPER_LEFT.value,
        VertexOrder.UPPER_RIGHT.value,
        VertexOrder.LOWER_LEFT.value,
        VertexOrder.LOWER_RIGHT.value,
    )

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        """Transforms hit box points."""
        return points

    @classmethod
    def transform_vertex_order(cls, order: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """
        Transforms and exiting vertex order with this transform.
        This gives us important metadata on how to quickly transform
        the texture coordinates without iterating all applied transforms.
        """
        return (
            order[cls.order[0]],
            order[cls.order[1]],
            order[cls.order[2]],
            order[cls.order[3]],
        )

    @classmethod
    def transform_texture_coordinates_order(
        cls,
        texture_coordinates: Tuple[float, float, float, float, float, float, float, float],
        order: Tuple[int, int, int, int],
    ) -> Tuple[float, float, float, float, float, float, float, float]:
        """
        Change texture coordinates order.

        :param texture_coordinates: Texture coordinates to transform
        :param order: The new order
        """
        uvs = texture_coordinates
        return (
            uvs[order[0] * 2],
            uvs[order[0] * 2 + 1],
            uvs[order[1] * 2],
            uvs[order[1] * 2 + 1],
            uvs[order[2] * 2],
            uvs[order[2] * 2 + 1],
            uvs[order[3] * 2],
            uvs[order[3] * 2 + 1],
        )


class Rotate90Transform(Transform):
    """
    Rotate 90 degrees clockwise.
    """
    order = (
        VertexOrder.LOWER_LEFT.value,
        VertexOrder.UPPER_LEFT.value,
        VertexOrder.LOWER_RIGHT.value,
        VertexOrder.UPPER_RIGHT.value,
    )

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        return tuple(rotate_point(point[0], point[1], 0, 0, -90) for point in points)


class Rotate180Transform(Transform):
    """
    Rotate 180 degrees clockwise.
    """
    order = (
        VertexOrder.LOWER_RIGHT.value,
        VertexOrder.LOWER_LEFT.value,
        VertexOrder.UPPER_RIGHT.value,
        VertexOrder.UPPER_LEFT.value,
    )

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        return tuple(rotate_point(point[0], point[1], 0, 0, -180) for point in points)


class Rotate270Transform(Transform):
    """
    Rotate 270 degrees clockwise.
    """
    order = (
        VertexOrder.UPPER_RIGHT.value,
        VertexOrder.LOWER_RIGHT.value,
        VertexOrder.UPPER_LEFT.value,
        VertexOrder.LOWER_LEFT.value,
    )
    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        return tuple(rotate_point(point[0], point[1], 0, 0, -270) for point in points)


class FlipLeftRightTransform(Transform):
    """
    Flip texture horizontally / left to right.
    """
    order = (
        VertexOrder.UPPER_RIGHT.value,
        VertexOrder.UPPER_LEFT.value,
        VertexOrder.LOWER_RIGHT.value,
        VertexOrder.LOWER_LEFT.value,
    )

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        return tuple((-point[0], point[1]) for point in points)


class FlipTopBottomTransform(Transform):
    """
    Flip texture vertically / top to bottom.
    """
    order = (
        VertexOrder.LOWER_LEFT.value,
        VertexOrder.LOWER_RIGHT.value,
        VertexOrder.UPPER_LEFT.value,
        VertexOrder.UPPER_RIGHT.value,
    )

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        return tuple((point[0], -point[1]) for point in points)


class TransposeTransform(Transform):
    """
    Transpose texture.
    """
    order = (
        VertexOrder.UPPER_LEFT.value,
        VertexOrder.LOWER_LEFT.value,
        VertexOrder.UPPER_RIGHT.value,
        VertexOrder.LOWER_RIGHT.value,
    )

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        points = FlipLeftRightTransform.transform_hit_box_points(points)
        points = Rotate90Transform.transform_hit_box_points(points)
        return points


class TransverseTransform(Transform):
    """
    Transverse texture.
    """
    order = (
        VertexOrder.LOWER_RIGHT.value,
        VertexOrder.UPPER_RIGHT.value,
        VertexOrder.LOWER_LEFT.value,
        VertexOrder.UPPER_LEFT.value,
    )

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        points = FlipLeftRightTransform.transform_hit_box_points(points)
        points = Rotate270Transform.transform_hit_box_points(points)
        return points


# Pre-calculated orientations. This can be calculated at runtime,
# but it's faster to just pre-calculate it.
# Key is the vertex order
# Value is the orientation (flip_left_right, flip_top_down, rotation)
ORIENTATIONS: Dict[Tuple[int, int, int, int], Tuple[int, bool, bool]] = {
    (0, 1, 2, 3): (0, False, False),  # Default
    (2, 0, 3, 1): (90, False, False),  # Rotate 90
    (3, 2, 1, 0): (180, False, False),  # Rotate 180
    (1, 3, 0, 2): (270, False, False),  # Rotate 270
    (1, 0, 3, 2): (0, True, False),  # Flip left to right
    (2, 3, 0, 1): (0, False, True),  # Flip top to bottom
    (0, 2, 1, 3): (-90, True, False),  # Transpose
    (3, 1, 2, 0): (90, True, False),  # Transverse
}


def get_orientation(order: Tuple[int, int, int, int]) -> int:
    """
    Get orientation info from the vertex order
    """
    return 0
