from PIL.Image import Image
import pymunk
from pymunk import autogeometry
from arcade import Point, PointList
from .base import HitBoxAlgorithm


class DetailedHitBoxAlgorithm(HitBoxAlgorithm):
    name = "detailed"

    @classmethod
    def calculate(cls, image: Image, **kwargs) -> PointList:
        """
        Given an RGBA image, this returns points that make up a hit box around it. Attempts
        to trim out transparent pixels.

        :param Image image: Image get hit box from.
        :param int hit_box_detail: How detailed to make the hit box. There's a
                                   trade-off in number of points vs. accuracy.

        :Returns: List of points
        """
        hit_box_detail = kwargs.get("hit_box_detail", 4.5)

        if image.mode != "RGBA":
            raise ValueError("Image mode is not RGBA. image.convert('RGBA') is needed.")

        def sample_func(sample_point: Point) -> int:
            """ Method used to sample image. """
            if sample_point[0] < 0 \
                    or sample_point[1] < 0 \
                    or sample_point[0] >= image.width \
                    or sample_point[1] >= image.height:
                return 0

            point_tuple = sample_point[0], sample_point[1]
            color = image.getpixel(point_tuple)
            return 255 if color[3] > 0 else 0

        # Do a quick check if it is a full tile
        p1 = 0, 0
        p2 = 0, image.height - 1
        p3 = image.width - 1, image.height - 1
        p4 = image.width - 1, 0

        if sample_func(p1) and sample_func(p2) and sample_func(p3) and sample_func(p4):
            # Do a quick check if it is a full tile
            p1 = (-image.width / 2, -image.height / 2)
            p2 = (image.width / 2, -image.height / 2)
            p3 = (image.width / 2, image.height / 2)
            p4 = (-image.width / 2, image.height / 2)

            return p1, p2, p3, p4

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
        line_sets = autogeometry.march_soft(
            logo_bb,
            horizontal_samples, vertical_samples,
            99,
            sample_func)

        if len(line_sets) == 0:
            return []

        selected_line_set = line_sets[0]
        selected_area = None
        if len(line_sets) > 1:
            # We have more than one line set. Try and find one that covers most of
            # the sprite.
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

                area = (max_x - min_x) * (max_y - min_y)
                # print(f"Area: {area} = ({max_x} - {min_x}) * ({max_y} - {min_y})")
                if selected_area is None or area > selected_area:
                    selected_area = area
                    selected_line_set = line_set

        # Reduce number of vertices
        selected_line_set = autogeometry.simplify_curves(
            selected_line_set,
            hit_box_detail,
        )

        # Convert to normal points, offset fo 0,0 is center, flip the y
        hh = image.height / 2
        hw = image.width / 2
        points = []
        for vec2 in selected_line_set:
            point_tuple = round(vec2.x - hw), round(image.height - (vec2.y - hh) - image.height)
            points.append(point_tuple)

        # Remove duplicate end point
        if len(points) > 1 and points[0] == points[-1]:
            points.pop()

        # Return immutable data
        return tuple(points)
