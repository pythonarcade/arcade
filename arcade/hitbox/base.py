from __future__ import annotations

from math import cos, radians, sin
from typing import Any, Sequence, Tuple
from typing_extensions import Self

from PIL.Image import Image

from arcade.types import Point, PointList, EMPTY_POINT_LIST

__all__ = ["HitBoxAlgorithm", "HitBox", "RotatableHitBox"]


class HitBoxAlgorithm:
    """
    The base class for hit box algorithms.

    Hit box algorithms are intended to calculate the points which make up
    a hit box for a given :py:class:`~PIL.Image.Image`. However, advanced
    users can also repurpose them for other tasks.
    """

    #: Whether points for this algorithm should be cached
    cache = True

    def __init__(self):
        self._cache_name = self.__class__.__name__

    @property
    def cache_name(self) -> str:
        """
        A string representation of the parameters used to create this algorithm.

        It will be incorporated at the end of the string returned by
        :py:meth:`Texture.create_cache_name <arcade.Texture.create_cache_name>`.
        Subclasses should override this method to return a value which allows
        distinguishing different configurations of a particular hit box
        algorithm.
        """
        return self._cache_name

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

    def __call__(self, *args: Any, **kwds: Any) -> Self:
        """
        Shorthand allowing any instance to be used identically to the base type.

        :param args: The same positional arguments as `__init__`
        :param kwds: The same keyword arguments as `__init__`
        :return: A new HitBoxAlgorithm instance
        """
        return self.__class__(*args, **kwds)  # type: ignore


class HitBox:
    """
    A basic hit box class supporting scaling.

    It includes support for rescaling as well as shorthand properties
    for boundary values along the X and Y axes. For rotation support,
    use :py:meth:`.create_rotatable` to create an instance of
    :py:class:`RotatableHitBox`.

    :param points: The unmodified points bounding the hit box
    :param position: The center around which the points will be offset
    :param scale: The X and Y scaling factors to use when offsetting the
        points
    """
    def __init__(
        self,
        points: PointList,
        position: Point = (0.0, 0.0),
        scale: Tuple[float, float] = (1.0, 1.0),
    ):
        self._points = points
        self._position = position
        self._scale = scale

        # This empty tuple will be replaced the first time
        # get_adjusted_points is called
        self._adjusted_points: PointList = EMPTY_POINT_LIST
        self._adjusted_cache_dirty = True

    @property
    def points(self) -> PointList:
        """
        The raw, unadjusted points of this hit box.

        These are the points as originally passed before offsetting, scaling,
        and any operations subclasses may perform, such as rotation.
        """
        return self._points

    @property
    def position(self) -> Point:
        """
        The center point used to offset the final adjusted positions.
        :return:
        """
        return self._position

    @position.setter
    def position(self, position: Point):
        self._position = position
        self._adjusted_cache_dirty = True

    # Per Clepto's testing as of around May 2023, these are better
    # left uncached because caching them is somehow slower than what
    # we currently do. Any readers should feel free to retest /
    # investigate further.
    @property
    def left(self) -> float:
        """
        Calculates the leftmost adjusted x position of this hit box
        """
        points = self.get_adjusted_points()
        x_points = [point[0] for point in points]
        return min(x_points)

    @property
    def right(self) -> float:
        """
        Calculates the rightmost adjusted x position of this hit box
        """
        points = self.get_adjusted_points()
        x_points = [point[0] for point in points]
        return max(x_points)

    @property
    def top(self) -> float:
        """
        Calculates the topmost adjusted y position of this hit box
        """
        points = self.get_adjusted_points()
        y_points = [point[1] for point in points]
        return max(y_points)

    @property
    def bottom(self) -> float:
        """
        Calculates the bottommost adjusted y position of this hit box
        """
        points = self.get_adjusted_points()
        y_points = [point[1] for point in points]
        return min(y_points)

    @property
    def scale(self) -> Tuple[float, float]:
        """
        The X & Y scaling factors for the points in this hit box.

        These are used to calculate the final adjusted positions of points.
        """
        return self._scale

    @scale.setter
    def scale(self, scale: Tuple[float, float]):
        self._scale = scale
        self._adjusted_cache_dirty = True

    def create_rotatable(
        self,
        angle: float = 0.0,
    ) -> RotatableHitBox:
        """
        Create a rotatable instance of this hit box.

        The internal ``PointList`` is transferred directly instead of
        deepcopied, so care should be taken if using a mutable internal
        representation.

        :param angle: The angle to rotate points by (0 by default)
        :return:
        """
        return RotatableHitBox(
            self._points, position=self._position, scale=self._scale, angle=angle
        )

    def get_adjusted_points(self) -> Sequence[Point]:
        """
        Return the positions of points, scaled and offset from the center.

        Unlike the boundary helper properties (left, etc), this method will
        only recalculate the values when necessary:

        * The first time this method is called
        * After properties affecting adjusted position were changed
        """
        if not self._adjusted_cache_dirty:
            return self._adjusted_points # type: ignore

        def _adjust_point(point) -> Point:
            x, y = point

            x *= self.scale[0]
            y *= self.scale[1]

            return (x + self.position[0], y + self.position[1])

        self._adjusted_points = [_adjust_point(point) for point in self.points]
        self._adjusted_cache_dirty = False
        return self._adjusted_points # type: ignore [return-value]


class RotatableHitBox(HitBox):
    """
    A hit box with support for rotation.

    Rotation is separated from the basic hitbox because it is much
    slower than offsetting and scaling.
    """
    def __init__(
        self,
        points: PointList,
        *,
        position: Tuple[float, float] = (0.0, 0.0),
        angle: float = 0.0,
        scale: Tuple[float, float] = (1.0, 1.0),
    ):
        super().__init__(points, position=position, scale=scale)
        self._angle: float = angle

    @property
    def angle(self) -> float:
        """
        The angle to rotate the raw points by in degrees
        """
        return self._angle

    @angle.setter
    def angle(self, angle: float):
        self._angle = angle
        self._adjusted_cache_dirty = True

    def get_adjusted_points(self) -> PointList:
        """
        Return the offset, scaled, & rotated points of this hitbox.

        As with :py:meth:`.HitBox.get_adjusted_points`, this method only
        recalculates the adjusted values when necessary.
        :return:
        """
        if not self._adjusted_cache_dirty:
            return self._adjusted_points

        rad = radians(-self._angle)
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
