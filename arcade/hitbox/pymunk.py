from typing import List, Optional
from PIL.Image import Image
import pymunk
from pymunk.autogeometry import (
    PolylineSet,
    march_soft,
    simplify_curves,
)
from pymunk import Vec2d
from arcade.types import Point, PointList
from .base import HitBoxAlgorithm


class PymunkHitBoxAlgorithm(HitBoxAlgorithm):
    """
    Hit box point algorithm that uses pymunk to calculate the points.

    This is a more accurate algorithm generating more points. The
    point count can be controlled with the ``detail`` parameter.
    """
    name = "pymunk"
    #: The default detail when creating a new instance.
    default_detail = 4.5

    def __init__(self, *, detail: Optional[float] = None):
        self.detail = detail or self.default_detail

    @property
    def param_str(self) -> str:
        """
        Return a string representation of the parameters used to create this algorithm.

        This is used in caching.
        """
        return f"detail={self.detail}"

    def __call__(self, *, detail: Optional[float] = None) -> "PymunkHitBoxAlgorithm":
        """Create a new instance with new default values"""
        return PymunkHitBoxAlgorithm(detail=detail or self.detail)

    def calculate(self, image: Image, detail: Optional[float] = None, **kwargs) -> PointList:
        """
        Given an RGBA image, this returns points that make up a hit box around it.

        :param Image image: Image get hit box from.
        :param int detail: How detailed to make the hit box. There's a
                           trade-off in number of points vs. accuracy.

        :Returns: List of points
        """
        hit_box_detail = detail or self.detail

        if image.mode != "RGBA":
            raise ValueError("Image mode is not RGBA. image.convert('RGBA') is needed.")

        # Trace the image finding all the outlines and holes
        line_sets = self.trace_image(image)
        if len(line_sets) == 0:
            return tuple()

        # Get the largest line set
        line_set = self.select_largest_line_set(line_sets)

        # Reduce number of vertices
        if len(line_set) > 4:
            line_set = simplify_curves(line_set, hit_box_detail)

        return self.to_points_list(image, line_set)

    def to_points_list(self, image: Image, line_set: List[Vec2d]) -> PointList:
        """
        Convert a line set to a list of points.

        Coordinates are offset so ``(0,0)`` is the center of the image.

        :param Image image: Image to trace.
        :param List[Vec2d] line_set: Line set to convert.
        """
        # Convert to normal points, offset fo 0,0 is center, flip the y
        hh = image.height / 2.0
        hw = image.width / 2.0
        points = []
        for vec2 in line_set:
            point_tuple = (
                float(round(vec2.x - hw)),
                float(round(image.height - (vec2.y - hh) - image.height)),
            )
            points.append(point_tuple)

        # Remove duplicate end point
        if len(points) > 1 and points[0] == points[-1]:
            points.pop()

        # Return immutable data
        return tuple(points)

    def trace_image(self, image: Image) -> PolylineSet:
        """
        Trace the image and return a list of line sets.

        These line sets represent the outline of the image or the outline of the
        holes in the image. If more than one line set is returned it's important
        to pick the one that covers the most of the image.

        :param Image image: Image to trace.
        :return: Line sets
        """
        def sample_func(sample_point: Point) -> int:
            """ Method used to sample image. """
            if sample_point[0] < 0 \
                    or sample_point[1] < 0 \
                    or sample_point[0] >= image.width \
                    or sample_point[1] >= image.height:
                return 0

            point_tuple = int(sample_point[0]), int(sample_point[1])
            color = image.getpixel(point_tuple)
            return 255 if color[3] > 0 else 0

        # Do a quick check if it is a full tile
        # Points are pixel coordinates
        px1 = 0, 0
        px2 = 0, image.height - 1
        px3 = image.width - 1, image.height - 1
        px4 = image.width - 1, 0
        if sample_func(px1) and sample_func(px2) and sample_func(px3) and sample_func(px4):
            # Actual points are in world coordinates
            p1 = 0.0, 0.0
            p2 = 0.0, float(image.height)
            p3 = float(image.width), float(image.height)
            p4 = float(image.width), 0.0
            # Manually create a line set
            points = PolylineSet()
            points.collect_segment(p2, p3)
            points.collect_segment(p3, p4)
            points.collect_segment(p4, p1)
            return points

        # Get the bounding box
        logo_bb = pymunk.BB(-1, -1, image.width, image.height)

        # How often to sample?
        down_res = 1
        horizontal_samples = int(image.width / down_res)
        vertical_samples = int(image.height / down_res)

        # Run the trace
        # Get back one or more sets of lines covering stuff.
        # We want the one that covers the most of the sprite
        # or the line set might just be a hole in the sprite.
        return march_soft(
            logo_bb,
            horizontal_samples, vertical_samples,
            99,
            sample_func)

    def select_largest_line_set(self, line_sets: PolylineSet) -> List[Vec2d]:
        """
        Given a list of line sets, return the one that covers the most of the image.

        :param PolylineSet line_sets: List of line sets.
        :return: List of points that make up the line set.
        """
        if len(line_sets) == 1:
            return line_sets[0]

        # We have more than one line set.
        # Try and find one that covers most of the sprite.
        selected_line_set = line_sets[0]
        largest_area = -1.0

        for line_set in line_sets:
            min_x = None
            min_y = None
            max_x = None
            max_y = None
            for point in line_set:
                if min_x is None or point.x < min_x:
                    min_x = point.x
                if max_x is None or point.x > max_x:
                    max_x = point.x
                if min_y is None or point.y < min_y:
                    min_y = point.y
                if max_y is None or point.y > max_y:
                    max_y = point.y

            if min_x is None or max_x is None or min_y is None or max_y is None:
                raise ValueError("No points in bounding box.")

            # Calculate the area of the bounding box
            area = (max_x - min_x) * (max_y - min_y)
            if area > largest_area:
                largest_area = area
                selected_line_set = line_set

        return selected_line_set
