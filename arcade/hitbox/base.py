from __future__ import annotations

from math import cos, hypot, radians, sin
from typing import Any

from PIL.Image import Image
from typing_extensions import Self

from arcade.types import EMPTY_POINT_LIST, Point2, Point2List

__all__ = ["HitBoxAlgorithm", "HitBox", "RotatableHitBox"]

#: Maps a rounded unit normal to an edge normal with that direction. See _add_axis().
Axes = dict[tuple[float, float], tuple[float, float]]

# Unit vectors are rounded to this many decimal places when checking
# whether two edges are parallel.
_AXIS_DECIMALS = 9

# Cosine and sine for 0, 90, 180 and 270 degrees clockwise
_RIGHT_ANGLE_ROTATIONS = ((1.0, 0.0), (0.0, -1.0), (-1.0, 0.0), (0.0, 1.0))


def _get_rotation(angle: float) -> tuple[float, float]:
    """
    Get the cosine and sine used to rotate points clockwise by ``angle`` degrees.

    Right angles give exact values. Otherwise ``sin(radians(180))`` is
    about 1.2e-16 instead of 0, and rotated hit boxes pick up tiny errors
    that can decide whether exactly touching sprites collide.
    """
    quarter_turns, remainder = divmod(angle, 90)
    if remainder == 0:
        return _RIGHT_ANGLE_ROTATIONS[int(quarter_turns) % 4]
    rad = radians(-angle)
    return cos(rad), sin(rad)


def _add_axis(axes: Axes, normal_x: float, normal_y: float) -> None:
    """
    Add an edge normal to a set of separating axes.

    Normals are keyed by their rounded unit vector, with the sign chosen so
    parallel edges facing either way share a key. The stored normal is not
    normalized: projecting onto it keeps exact arithmetic where possible,
    so exactly touching edges stay exactly touching. Zero-length edges and
    axis-aligned normals are skipped: the bounding box check done before
    the separating axis test already covers the x and y axes.
    """
    # Only skip exactly axis-aligned normals. Nearly axis-aligned ones
    # still matter for exactly touching edges.
    if normal_x == 0 or normal_y == 0:
        return
    length = hypot(normal_x, normal_y)
    key_x = round(normal_x / length, _AXIS_DECIMALS)
    key_y = round(normal_y / length, _AXIS_DECIMALS)
    if key_x < 0 or (key_x == 0 and key_y < 0):
        key_x, key_y = -key_x, -key_y
    axes[(key_x, key_y)] = (normal_x, normal_y)


def _axes_from_points(points: Point2List) -> Axes:
    """Get the distinct, non axis-aligned edge normals of a polygon."""
    axes: Axes = {}
    if not points:
        return axes
    prev_x, prev_y = points[-1]
    for x, y in points:
        _add_axis(axes, y - prev_y, prev_x - x)
        prev_x, prev_y = x, y
    return axes


def _edge_directions(points: Point2List) -> list[Point2]:
    """Get one edge vector for each distinct edge direction of a polygon."""
    directions: dict[tuple[float, float], Point2] = {}
    if not points:
        return []
    prev_x, prev_y = points[-1]
    for x, y in points:
        edge_x, edge_y = x - prev_x, y - prev_y
        prev_x, prev_y = x, y
        length = hypot(edge_x, edge_y)
        if length == 0:
            continue
        key_x = round(edge_x / length, _AXIS_DECIMALS)
        key_y = round(edge_y / length, _AXIS_DECIMALS)
        if key_x < 0 or (key_x == 0 and key_y < 0):
            key_x, key_y = -key_x, -key_y
        directions.setdefault((key_x, key_y), (edge_x, edge_y))
    return list(directions.values())


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

    def calculate(self, image: Image, **kwargs) -> Point2List:
        """
        Calculate hit box points for a given image.

        .. warning:: This method should not be made into a class method!

                     Although this base class does not take arguments
                     when initialized, subclasses use them to alter how
                     a specific instance handles image data by default.

        Args:
            image:
                The image to calculate hitbox points for
            kwargs:
                keyword arguments
        """
        raise NotImplementedError

    def __call__(self, *args: Any, **kwds: Any) -> Self:
        """
        Shorthand allowing any instance to be used identically to the base type.

        Args:
            args:
                The same positional arguments as `__init__`
           kwds:
                The same keyword arguments as `__init__`
        Returns:
            A new HitBoxAlgorithm instance
        """
        return self.__class__(*args, **kwds)  # type: ignore

    def create_bounding_box(self, image: Image) -> Point2List:
        """
        Create points for a simple bounding box around an image.
        This is often used as a fallback if a hit box algorithm
        doesn't manage to figure out any reasonable points for
        an image.

        Args:
            image: The image to create a bounding box for.
        """
        size = image.size
        return (
            (-size[0] / 2, -size[1] / 2),
            (size[0] / 2, -size[1] / 2),
            (size[0] / 2, size[1] / 2),
            (-size[0] / 2, size[1] / 2),
        )


class HitBox:
    """
    A basic hit box class supporting scaling.

    It includes support for rescaling as well as shorthand properties
    for boundary values along the X and Y axes. For rotation support,
    use :py:meth:`.create_rotatable` to create an instance of
    :py:class:`RotatableHitBox`.

    Args:
        points:
            The unmodified points bounding the hit box
        position:
            The center around which the points will be offset
        scale:
            The X and Y scaling factors to use when offsetting the points
    """

    def __init__(
        self,
        points: Point2List,
        position: Point2 = (0.0, 0.0),
        scale: Point2 = (1.0, 1.0),
    ):
        self._points = points
        self._position = position
        self._scale = scale

        # This empty tuple will be replaced the first time
        # get_adjusted_points is called
        self._adjusted_points: Point2List = EMPTY_POINT_LIST
        self._adjusted_cache_dirty = True

        # Bounds of the adjusted points and the point list they came from
        self._adjusted_bounds: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        self._adjusted_bounds_points: Point2List | None = None

        # Separating axes, see _get_axes()
        self._edge_directions: list[Point2] = []
        self._edge_directions_points: Point2List | None = None
        self._axes: Axes = {}
        self._axes_key: tuple[Any, ...] | None = None

    @property
    def points(self) -> Point2List:
        """
        The raw, unadjusted points of this hit box.

        These are the points as originally passed before offsetting, scaling,
        and any operations subclasses may perform, such as rotation.
        """
        return self._points

    @property
    def position(self) -> Point2:
        """
        The center point used to offset the final adjusted positions.
        """
        return self._position

    @position.setter
    def position(self, position: Point2):
        self._position = position
        self._adjusted_cache_dirty = True

    # Per Clepto's testing as of around May 2023, these are better
    # left uncached because caching them is somehow slower than what
    # we currently do. Any readers should feel free to retest /
    # investigate further.
    # Retested in 2026: using get_adjusted_bounds() here makes reading all
    # four after a move a bit faster, but reading just one is ~50% slower.
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

    def get_adjusted_bounds(self) -> tuple[float, float, float, float]:
        """
        Return the ``(left, right, bottom, top)`` bounds of the adjusted points.

        The bounds are cached and only recalculated when the adjusted
        points change, which makes this faster than reading
        :py:attr:`left`, :py:attr:`right`, :py:attr:`bottom` and
        :py:attr:`top` when more than one of them is needed.
        """
        points = self.get_adjusted_points()
        # Keyed on the point list itself so subclasses overriding
        # get_adjusted_points() can't leave stale bounds behind.
        if points is not self._adjusted_bounds_points:
            x_points, y_points = zip(*points)
            self._adjusted_bounds = (
                min(x_points),
                max(x_points),
                min(y_points),
                max(y_points),
            )
            self._adjusted_bounds_points = points
        return self._adjusted_bounds

    def _get_axes(self) -> Axes:
        """
        Get the separating axes to test this hit box against another.

        These are the distinct edge normals of the adjusted points, without
        the x and y axes. They are cached, and since the directions don't
        depend on position, moving the hit box doesn't recalculate them.
        """
        if type(self).get_adjusted_points is not HitBox.get_adjusted_points:
            return self._get_axes_from_adjusted_points()
        return self._get_transformed_axes(0.0)

    def _get_transformed_axes(self, angle: float) -> Axes:
        """
        Get the axes by scaling and rotating the raw edge directions.

        This must apply the same transform as get_adjusted_points(),
        without the offset.
        """
        points = self._points
        scale = self._scale
        key = self._axes_key
        if key is not None and key[0] is points and key[1] == scale and key[2] == angle:
            return self._axes

        # Scaling and rotation keep parallel edges parallel, so duplicate
        # directions only need removing once for the raw points.
        if self._edge_directions_points is not points:
            self._edge_directions = _edge_directions(points)
            self._edge_directions_points = points

        scale_x, scale_y = scale
        axes: Axes = {}
        if angle:
            rad_cos, rad_sin = _get_rotation(angle)
            for edge_x, edge_y in self._edge_directions:
                x = edge_x * scale_x
                y = edge_y * scale_y
                _add_axis(axes, x * rad_sin + y * rad_cos, y * rad_sin - x * rad_cos)
        else:
            for edge_x, edge_y in self._edge_directions:
                _add_axis(axes, edge_y * scale_y, -edge_x * scale_x)

        self._axes = axes
        self._axes_key = (points, scale, angle)
        return axes

    def _get_axes_from_adjusted_points(self) -> Axes:
        """
        Get the axes from the adjusted points.

        Used for subclasses that override get_adjusted_points(), since they
        may transform the points differently.
        """
        points = self.get_adjusted_points()
        key = self._axes_key
        if key is not None and key[0] is points and key[1] is None:
            return self._axes
        self._axes = _axes_from_points(points)
        self._axes_key = (points, None, None)
        return self._axes

    @property
    def scale(self) -> tuple[float, float]:
        """
        The X & Y scaling factors for the points in this hit box.

        These are used to calculate the final adjusted positions of points.
        """
        return self._scale

    @scale.setter
    def scale(self, scale: tuple[float, float]):
        self._scale = scale
        self._adjusted_cache_dirty = True

    def create_rotatable(
        self,
        angle: float = 0.0,
    ) -> RotatableHitBox:
        """
        Create a rotatable instance of this hit box.

        The internal ``PointList`` is transferred directly instead of
        deep copied, so care should be taken if using a mutable internal
        representation.

        Args:
            angle: The angle to rotate points by (0 by default)
        """
        return RotatableHitBox(
            self._points, position=self._position, scale=self._scale, angle=angle
        )

    def get_adjusted_points(self) -> Point2List:
        """
        Return the positions of points, scaled and offset from the center.

        Unlike the boundary helper properties (left, etc), this method will
        only recalculate the values when necessary:

        * The first time this method is called
        * After properties affecting adjusted position were changed
        """
        if not self._adjusted_cache_dirty:
            return self._adjusted_points  # type: ignore

        position_x, position_y = self._position
        scale_x, scale_y = self._scale

        def _adjust_point(point) -> Point2:
            x, y = point

            x *= scale_x
            y *= scale_y

            return (x + position_x, y + position_y)

        self._adjusted_points = [_adjust_point(point) for point in self._points]
        self._adjusted_cache_dirty = False
        return self._adjusted_points


class RotatableHitBox(HitBox):
    """
    A hit box with support for rotation.

    Rotation is separated from the basic hitbox because it is much
    slower than offsetting and scaling.

    Args:
        points:
            The unmodified points bounding the hit box
        position:
            The translation to apply to the points
        angle:
            The angle to rotate the points by
        scale:
            The X and Y scaling factors
    """

    def __init__(
        self,
        points: Point2List,
        *,
        position: tuple[float, float] = (0.0, 0.0),
        angle: float = 0.0,
        scale: Point2 = (1.0, 1.0),
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

    def _get_axes(self) -> Axes:
        if type(self).get_adjusted_points is not RotatableHitBox.get_adjusted_points:
            return self._get_axes_from_adjusted_points()
        return self._get_transformed_axes(self._angle)

    def get_adjusted_points(self) -> Point2List:
        """
        Return the offset, scaled, & rotated points of this hitbox.

        As with :py:meth:`.HitBox.get_adjusted_points`, this method only
        recalculates the adjusted values when necessary.
        """
        if not self._adjusted_cache_dirty:
            return self._adjusted_points

        angle = self._angle
        scale_x, scale_y = self._scale
        position_x, position_y = self._position
        rad_cos, rad_sin = _get_rotation(angle) if angle else (1.0, 0.0)

        def _adjust_point(point) -> Point2:
            x, y = point

            x *= scale_x
            y *= scale_y

            if angle:
                rot_x = x * rad_cos - y * rad_sin
                rot_y = x * rad_sin + y * rad_cos
                x = rot_x
                y = rot_y

            return (
                x + position_x,
                y + position_y,
            )

        self._adjusted_points = [_adjust_point(point) for point in self._points]
        self._adjusted_cache_dirty = False
        return self._adjusted_points
