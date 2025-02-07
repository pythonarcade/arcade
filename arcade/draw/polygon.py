from arcade import gl
from arcade.earclip import earclip
from arcade.types import Point2, Point2List, RGBOrA255

from .helpers import _generic_draw_line_strip, get_points_for_thick_line


def draw_polygon_filled(point_list: Point2List, color: RGBOrA255) -> None:
    """
    Draw a polygon that is filled in.

    Args:
        point_list:
            List of points making up the lines. Each point is
            in a list. So it is a list of lists.
        color:
            The color, specified in RGB or RGBA format.
    """
    triangle_points = earclip(point_list)
    flattened_list = tuple(i for g in triangle_points for i in g)
    _generic_draw_line_strip(flattened_list, color, gl.TRIANGLES)


def draw_polygon_outline(point_list: Point2List, color: RGBOrA255, line_width: float = 1.0) -> None:
    """
    Draw a polygon outline. Also known as a "line loop."

    Args:
        point_list:
            List of points making up the lines. Each point is
            in a list. So it is a list of lists.
        color:
            The color of the outline as an RGBA :py:class:`tuple` or
            :py:class:`.Color` instance.
        line_width:
            Width of the line in pixels.
    """
    # Convert to modifiable list & close the loop
    new_point_list = list(point_list)
    new_point_list.append(point_list[0])

    # Create a place to store the triangles we'll use to thicken the line
    triangle_point_list: list[Point2] = []

    # This needs a lot of improvement
    last_point = None
    for point in new_point_list:
        if last_point is not None:
            # Calculate triangles, then re-order to link up the quad?
            points = get_points_for_thick_line(*last_point, *point, line_width)
            reordered_points = points[1], points[0], points[2], points[3]

            triangle_point_list.extend(reordered_points)
        last_point = point

    # Use first two points of new list to close the loop
    new_start, new_next = new_point_list[:2]
    s_x, s_y = new_start
    n_x, n_y = new_next
    points = get_points_for_thick_line(s_x, s_y, n_x, n_y, line_width)
    triangle_point_list.append(points[1])

    _generic_draw_line_strip(triangle_point_list, color, gl.TRIANGLE_STRIP)
