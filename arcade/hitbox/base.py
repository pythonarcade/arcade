from __future__ import annotations

from math import cos, radians, sin
from typing import Any, Tuple

from PIL.Image import Image

from arcade.types import Point, PointList


__all__ = ["HitBoxAlgorithm", "HitBox", "RotatableHitBox"]


class HitBoxAlgorithm:
    """
    The base class for hit box algorithms.

    Hit box algorithms are intended to calculate the points which make up
    a hit box for a given :py:class:`~PIL.Image.Image`. However, advanced
    users can also repurpose them for other tasks.
    """

    #: The name of the algorithm
    name = "base"

    #: Whether points for this algorithm should be cached
    cache = True

    @property
    def param_str(self) -> str:
        """
        A string representation of the parameters used to create this algorithm.

        This is used when caching :py:class:`~arcade.Texture` instances.
        """
        return ""

    def calculate(self, image: Image, **kwargs) -> PointList:
        """
        Calculate hit box points for a given image.

        .. warning:: This method should not be made into a class method!

                     Although this base class does not take arguments
                     when initialized, subclasses use them to alter how
                     a specific instance handles image data by default.

        :param image: The image to calculate hitbox points for
        :param kwargs: keyword arguments
        :return: A list of hit box points.
        """
        raise NotImplementedError

    def __call__(self, *args: Any, **kwds: Any) -> "HitBoxAlgorithm":
        """
        Shorthand allowing any instance to be used identically to the base type.

        :param args: The same positional arguments as `__init__`
        :param kwds: The same keyword arguments as `__init__`
        :return: A new HitBoxAlgorithm instance
        """
        return self.__class__(*args, **kwds)


class HitBox:
    def __init__(
        self,
        points: PointList,
        position: Point = (0.0, 0.0),
        scale: Tuple[float, float] = (1.0, 1.0),
    ):
        self._points = points
        self._position = position
        self._scale = scale

        self._left = None
        self._right = None
        self._bottom = None
        self._top = None

        self._adjusted_points = None
        self._adjusted_cache_dirty = True

    @property
    def points(self):
        return self._points

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position: Point):
        self._position = position
        self._adjusted_cache_dirty = True

    @property
    def left(self):
        points = self.get_adjusted_points()
        x_points = [point[0] for point in points]
        return min(x_points)

    @property
    def right(self):
        points = self.get_adjusted_points()
        x_points = [point[0] for point in points]
        return max(x_points)

    @property
    def top(self):
        points = self.get_adjusted_points()
        y_points = [point[1] for point in points]
        return max(y_points)

    @property
    def bottom(self):
        points = self.get_adjusted_points()
        y_points = [point[1] for point in points]
        return min(y_points)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale: Tuple[float, float]):
        self._scale = scale
        self._adjusted_cache_dirty = True

    def create_rotatable(
        self,
        angle: float = 0.0,
    ) -> RotatableHitBox:
        return RotatableHitBox(
            self._points, position=self._position, scale=self._scale, angle=angle
        )

    def get_adjusted_points(self):
        if not self._adjusted_cache_dirty:
            return self._adjusted_points

        def _adjust_point(point) -> Point:
            x, y = point

            x *= self.scale[0]
            y *= self.scale[1]

            return (x + self.position[0], y + self.position[1])

        self._adjusted_points = [_adjust_point(point) for point in self.points]
        self._adjusted_cache_dirty = False
        return self._adjusted_points


class RotatableHitBox(HitBox):
    def __init__(
        self,
        points: PointList,
        *,
        position: Tuple[float, float] = (0.0, 0.0),
        angle: float = 0.0,
        scale: Tuple[float, float] = (1.0, 1.0),
    ):
        super().__init__(points, position=position, scale=scale)
        self._angle = angle

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle: float):
        self._angle = angle
        self._adjusted_cache_dirty = True

    def get_adjusted_points(self):
        if not self._adjusted_cache_dirty:
            return self._adjusted_points

        rad = radians(self._angle)
        rad_cos = cos(rad)
        rad_sin = sin(rad)

        def _adjust_point(point) -> Point:
            x, y = point

            x *= self.scale[0]
            y *= self.scale[1]

            if rad:
                rot_x = x * rad_cos - y * rad_sin
                rot_y = x * rad_sin + y * rad_cos
                x = rot_x
                y = rot_y

            return (
                x + self.position[0],
                y + self.position[1],
            )

        self._adjusted_points = [_adjust_point(point) for point in self.points]
        self._adjusted_cache_dirty = False
        return self._adjusted_points
