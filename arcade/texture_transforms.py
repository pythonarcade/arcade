"""
Module for handling common texture transforms
such as rotation, translation, flipping etc.

We don't actually transform pixel data, we simply
transform the texture coordinates and hit box points.
"""
from typing import Iterable, Tuple
import arcade
from arcade.arcade_types import Point, PointList


class Transform:
    """
    Base class for all texture transforms.

    Transforms are responsible for transforming the texture
    coordinates and hit box points.
    """
    #: How texture coordinates order should be changed
    #: for this transform.
    order = 0, 1, 2, 3

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
        center: Tuple[float, float] = (0, 0),
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
    ) -> Iterable[Point]:
        """Change texture coordinates order."""
        uvs = texture_coordinates
        return (
            uvs[cls.order[0]],
            uvs[cls.order[0]],
            uvs[cls.order[1]],
            uvs[cls.order[1]],
            uvs[cls.order[2]],
            uvs[cls.order[2]],
            uvs[cls.order[3]],
            uvs[cls.order[3]],
        )


class RotateTransform(Transform):
    """
    Rotate 90 degrees clockwise.
    """
    order = 3, 0, 1, 2

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
        center: Tuple[float, float] = (0, 0),
    ) -> PointList:
        return tuple(arcade.rotate_point(point[0], point[1], 0, 0, 90) for point in points)


class FlipLeftToRightTransform(Transform):
    """
    Flip texture horizontally / left to right.
    """
    order = 2, 3, 0, 1

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
        center: Tuple[float, float] = (0, 0),
    ) -> PointList:
        return tuple((-point[0], point[1]) for point in points)



class FlipTopToBottomTransform(Transform):
    """
    Flip texture vertically / top to bottom.
    """
    oder = 1, 2, 3, 0

    @staticmethod
    def transform_hit_box_points(
        points: PointList,
        center: Tuple[float, float] = (0, 0),
    ) -> PointList:
        return tuple((point[0], -point[1]) for point in points)


def normalize(transforms: Iterable[Transform]):
    """
    Normalize a list of transforms.

    This will remove redundant transforms and
    combine transforms where possible.

    :param transforms: List of transforms
    :return: Normalized list of transforms
    """
    return []
