"""
Module for handling common texture transforms
such as rotation, translation, flipping etc.

We don't actually transform pixel data, we simply
transform the texture coordinates and hit box points.
"""
from typing import Tuple
import arcade
from arcade.arcade_types import Point, PointList


class Transform:
    """
    Base class for all texture transforms.

    Transforms are responsible for transforming the texture
    coordinates and hit box points.
    """
    @staticmethod
    def transform_hit_box_points(points: PointList) -> PointList:
        raise NotImplementedError

    @staticmethod
    def transform_texture_coordinate(
        uv_1: Point,
        uv_2: Point,
        uv_3: Point,
        uv_4: Point,
    ) -> Tuple[Point, Point, Point, Point]:
        raise NotImplementedError


class RotateTransform(Transform):
    """
    Rotate 90 degrees clockwise.
    """
    @staticmethod
    def transform_hit_box_points(points: PointList) -> PointList:
        return [arcade.rotate_point(point[0], point[1], 0, 0, 90) for point in points]

    @staticmethod
    def transform_texture_coordinate(
        uv_1: Point,
        uv_2: Point,
        uv_3: Point,
        uv_4: Point,
    ) -> Tuple[Point, Point, Point, Point]:
        return uv_4, uv_1, uv_2, uv_3


class FlipLeftToRightTransform(Transform):
    """
    Flip texture horizontally / left to right.
    """
    @staticmethod
    def transform_hit_box_points(points: PointList) -> PointList:
        raise NotImplementedError

    @staticmethod
    def transform_texture_coordinate(
        uv_1: Point,
        uv_2: Point,
        uv_3: Point,
        uv_4: Point,
    ) -> Tuple[Point, Point, Point, Point]:
        return uv_3, uv_4, uv_1, uv_2 


class FlipTopToBottomTransform(Transform):
    """
    Flip texture vertically / top to bottom.
    """
    @staticmethod
    def transform_hit_box_points(points: PointList) -> PointList:
        raise NotImplementedError

    @staticmethod
    def transform_texture_coordinate(
        uv_1: Point,
        uv_2: Point,
        uv_3: Point,
        uv_4: Point,
    ) -> Tuple[Point, Point, Point, Point]:
        return uv_2, uv_3, uv_4, uv_1
