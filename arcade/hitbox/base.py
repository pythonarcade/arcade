from __future__ import annotations

import gzip
import json
from math import cos, radians, sin
from pathlib import Path
from typing import Any, TypedDict

from PIL.Image import Image
from typing_extensions import Self

from arcade.types import EMPTY_POINT_LIST, Point2, Point2List

__all__ = ["HitBoxAlgorithm", "HitBox", "RawHitBox"]


class RawHitBox(TypedDict):
    """Typed dictionary representing the serialized form of a :py:class:`HitBox`."""

    version: int
    regions: dict[str, Point2List]


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
    A hit box with support for multiple named regions, scaling, and rotation.

    Each region is a named polygon (sequence of points). A hitbox with a
    single region can be constructed by passing a ``Point2List`` directly,
    which creates a region named ``"default"``. For multiple regions, pass
    a ``dict[str, Point2List]``.

    **Single-region construction** (backward compatible)::

        box = HitBox(
            [(-10, -10), (10, -10), (10, 10), (-10, 10)]
        )

    **Multi-region construction** with a dict::

        box = HitBox({
            "body": [(-10, -10), (10, -10), (10, 10), (-10, 10)],
            "head": [(-5, 10), (5, 10), (5, 20), (-5, 20)],
        })

    **Rotation** (replaces the former ``RotatableHitBox`` class)::

        box = HitBox(points, angle=45.0)
        # Angle can be updated later:
        box.angle = 90.0

    **Region management**::

        box.add_region("shield", shield_points)
        box.has_region("shield")   # True
        box.remove_region("shield")

    **Serialization** to and from JSON files::

        box.save("hitbox.json")       # plain JSON
        box.save("hitbox.json.gz")    # gzip-compressed

        loaded = HitBox.load("hitbox.json")

        # Dict round-trip (see RawHitBox for the schema)
        data = box.to_dict()
        copy = HitBox.from_dict(data)

    .. note::

        All points are normalized to tuples of tuples on construction.
        Any sequence type is accepted as input, but regions will always
        store tuples internally.

    Args:
        points:
            Either a single ``Point2List`` (creates a ``"default"`` region)
            or a ``dict[str, Point2List]`` mapping region names to point lists.
            Points are normalized to tuples on storage.
        position:
            The center around which the points will be offset.
        scale:
            The X and Y scaling factors.
        angle:
            The rotation angle in degrees (clockwise).
    """

    DEFAULT_REGION = "default"

    def __init__(
        self,
        points: Point2List | dict[str, Point2List],
        position: Point2 = (0.0, 0.0),
        scale: Point2 = (1.0, 1.0),
        angle: float = 0.0,
    ):
        if isinstance(points, dict):
            self._regions: dict[str, Point2List] = {
                name: tuple(tuple(p) for p in pts) for name, pts in points.items()
            }
        else:
            self._regions = {self.DEFAULT_REGION: tuple(tuple(p) for p in points)}

        self._position = position
        self._scale = scale
        self._angle: float = angle
        self._is_single_region: bool = len(self._regions) == 1

        # Cached adjusted points per region
        self._adjusted_regions: dict[str, Point2List] = {}
        self._adjusted_cache_dirty = True

    @property
    def points(self) -> Point2List:
        """
        The raw, unadjusted points of the default region.

        This is provided for backward compatibility. For multi-region
        hitboxes, use :py:attr:`regions` instead.
        """
        return self._regions.get(self.DEFAULT_REGION, EMPTY_POINT_LIST)

    @property
    def regions(self) -> dict[str, Point2List]:
        """All raw, unadjusted regions as a dict mapping names to point lists."""
        return self._regions

    @property
    def region_names(self) -> tuple[str, ...]:
        """The names of all regions in this hit box."""
        return tuple(self._regions.keys())

    def has_region(self, name: str) -> bool:
        """Check if a region with the given name exists."""
        return name in self._regions

    def add_region(self, name: str, points: Point2List) -> None:
        """
        Add a named region to this hit box.

        Args:
            name: The name for the new region.
            points: The polygon points for the region.
        """
        self._regions[name] = tuple(tuple(p) for p in points)
        self._is_single_region = len(self._regions) == 1
        self._adjusted_cache_dirty = True

    def remove_region(self, name: str) -> None:
        """
        Remove a named region from this hit box.

        Args:
            name: The name of the region to remove.
        """
        del self._regions[name]
        self._is_single_region = len(self._regions) == 1
        self._adjusted_cache_dirty = True

    @property
    def position(self) -> Point2:
        """The center point used to offset the final adjusted positions."""
        return self._position

    @position.setter
    def position(self, position: Point2):
        self._position = position
        self._adjusted_cache_dirty = True

    @property
    def angle(self) -> float:
        """The angle to rotate the raw points by in degrees."""
        return self._angle

    @angle.setter
    def angle(self, angle: float):
        self._angle = angle
        self._adjusted_cache_dirty = True

    @property
    def left(self) -> float:
        """Calculates the leftmost adjusted x position across all regions."""
        self._recalculate_if_dirty()
        min_x = float("inf")
        for points in self._adjusted_regions.values():
            for point in points:
                if point[0] < min_x:
                    min_x = point[0]
        return min_x

    @property
    def right(self) -> float:
        """Calculates the rightmost adjusted x position across all regions."""
        self._recalculate_if_dirty()
        max_x = float("-inf")
        for points in self._adjusted_regions.values():
            for point in points:
                if point[0] > max_x:
                    max_x = point[0]
        return max_x

    @property
    def top(self) -> float:
        """Calculates the topmost adjusted y position across all regions."""
        self._recalculate_if_dirty()
        max_y = float("-inf")
        for points in self._adjusted_regions.values():
            for point in points:
                if point[1] > max_y:
                    max_y = point[1]
        return max_y

    @property
    def bottom(self) -> float:
        """Calculates the bottommost adjusted y position across all regions."""
        self._recalculate_if_dirty()
        min_y = float("inf")
        for points in self._adjusted_regions.values():
            for point in points:
                if point[1] < min_y:
                    min_y = point[1]
        return min_y

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

    def _recalculate_if_dirty(self) -> None:
        """Recalculate all adjusted regions if the cache is dirty."""
        if not self._adjusted_cache_dirty:
            return

        rad = radians(-self._angle)
        scale_x, scale_y = self._scale
        position_x, position_y = self._position
        rad_cos = cos(rad)
        rad_sin = sin(rad)
        do_rotate = bool(rad)

        def _adjust_point(point: Point2) -> Point2:
            x, y = point
            x *= scale_x
            y *= scale_y

            if do_rotate:
                rot_x = x * rad_cos - y * rad_sin
                rot_y = x * rad_sin + y * rad_cos
                x = rot_x
                y = rot_y

            return (x + position_x, y + position_y)

        self._adjusted_regions = {
            name: tuple(_adjust_point(p) for p in pts) for name, pts in self._regions.items()
        }
        self._adjusted_cache_dirty = False

    def get_adjusted_points(self, region: str | None = None) -> Point2List:
        """
        Return the positions of points, scaled, rotated, and offset.

        Args:
            region:
                The name of the region to get points for. If ``None``,
                returns the default region's points (backward compatible).
        """
        self._recalculate_if_dirty()
        name = region if region is not None else self.DEFAULT_REGION
        return self._adjusted_regions.get(name, EMPTY_POINT_LIST)

    def get_all_adjusted_polygons(self) -> list[Point2List]:
        """
        Return adjusted points for all regions as a list of polygons.

        This is used by collision detection to check all regions.
        """
        self._recalculate_if_dirty()
        return list(self._adjusted_regions.values())

    # --- Serialization ---

    def to_dict(self) -> RawHitBox:
        """
        Serialize the hitbox shape to a :py:class:`RawHitBox` dictionary.

        Only the region definitions (point data) are serialized.
        Position, scale, and angle are runtime state and are not included.
        """
        return {
            "version": 1,
            "regions": {name: pts for name, pts in self._regions.items()},
        }

    @classmethod
    def from_dict(
        cls,
        data: RawHitBox,
        position: Point2 = (0.0, 0.0),
        scale: Point2 = (1.0, 1.0),
        angle: float = 0.0,
    ) -> HitBox:
        """
        Create a HitBox from a :py:class:`RawHitBox` dictionary.

        Args:
            data: A :py:class:`RawHitBox` dictionary to deserialize from.
            position: The center offset.
            scale: The scaling factors.
            angle: The rotation angle in degrees.
        """
        return cls(points=data["regions"], position=position, scale=scale, angle=angle)

    def save(self, path: str | Path) -> None:
        """
        Save the hitbox shape definition to a JSON file.

        If the path ends with ``.gz``, the file will be gzip-compressed.

        Args:
            path: The file path to save to.
        """
        path = Path(path)
        data_str = json.dumps(self.to_dict())
        data_bytes = data_str.encode("utf-8")

        if path.suffix == ".gz":
            data_bytes = gzip.compress(data_bytes)

        with open(path, mode="wb") as fd:
            fd.write(data_bytes)

    @classmethod
    def load(
        cls,
        path: str | Path,
        position: Point2 = (0.0, 0.0),
        scale: Point2 = (1.0, 1.0),
        angle: float = 0.0,
    ) -> HitBox:
        """
        Load a hitbox shape definition from a JSON file.

        If the path ends with ``.gz``, the file is assumed to be gzip-compressed.

        Args:
            path: The file path to load from.
            position: The center offset.
            scale: The scaling factors.
            angle: The rotation angle in degrees.
        """
        path = Path(path)
        if path.suffix == ".gz":
            with gzip.open(path, mode="rb") as fd:
                data = json.loads(fd.read())
        else:
            with open(path) as fd:
                data = json.loads(fd.read())

        return cls.from_dict(data, position=position, scale=scale, angle=angle)
