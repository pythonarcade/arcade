"""
Module for handling common texture transforms
such as rotation, translation, flipping etc.

We don't actually transform pixel data, we simply
transform the texture coordinates and hit box points.
"""
from typing import Iterable, Tuple
from enum import Enum
import arcade
from arcade.arcade_types import PointList


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
        """Change texture coordinates order."""
        uvs = texture_coordinates
        return (
            uvs[order[0]],
            uvs[order[0]],
            uvs[order[1]],
            uvs[order[1]],
            uvs[order[2]],
            uvs[order[2]],
            uvs[order[3]],
            uvs[order[3]],
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
        return tuple(arcade.rotate_point(point[0], point[1], 0, 0, 90) for point in points)


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
        return tuple(arcade.rotate_point(point[0], point[1], 0, 0, 180) for point in points)


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
        return tuple(arcade.rotate_point(point[0], point[1], 0, 0, 270) for point in points)


class FlipLeftToRightTransform(Transform):
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


class FlipTopToBottomTransform(Transform):
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
        VertexOrder.LOWER_RIGHT.value,
        VertexOrder.UPPER_RIGHT.value,
        VertexOrder.LOWER_LEFT.value,
        VertexOrder.UPPER_LEFT.value,
    )

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
    ) -> PointList:
        return tuple((point[1], point[0]) for point in points)


class TransverseTransform(Transform):
    """
    Transverse texture.
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
        return tuple((-point[1], -point[0]) for point in points)


def normalize(transforms: Iterable[Transform]):
    """
    Normalize a list of transforms.

    This will remove redundant transforms and
    combine transforms where possible.

    :param transforms: List of transforms
    :return: Normalized list of transforms
    """
    return []
