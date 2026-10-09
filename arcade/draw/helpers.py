import array
import math
from itertools import chain

from arcade import gl
from arcade.types import Color, Point2, Point2List, RGBOrA255
from arcade.window_commands import get_window


def _bad_point_error(point_list: Point2List) -> ValueError | None:
    """Return an error naming the first point that isn't 2 numbers, if any.

    Only called after something went wrong, so it can be slow.
    """
    for index, point in enumerate(point_list):
        try:
            x, y = point
            array.array("f", (x, y))
        except (TypeError, ValueError, OverflowError):
            return ValueError(
                f"point_list[{index}] is {point!r}, but each point must be 2 numbers, "
                "such as (x, y)"
            )
    return None


def _flatten_points(point_list: Point2List) -> array.array:
    """Flatten 2D points into an array of floats: x0, y0, x1, y1, ...

    Raises a ValueError naming the first point that isn't 2 numbers.
    Checking costs one length comparison, so it doesn't slow down drawing.
    """
    try:
        data = array.array("f", tuple(chain.from_iterable(point_list)))
    except (TypeError, ValueError, OverflowError) as error:
        raise (_bad_point_error(point_list) or error) from None
    # A point with 1 or 3 numbers would shift every number after it
    if len(data) != 2 * len(point_list):
        raise _bad_point_error(point_list) or ValueError("Each point must be 2 numbers")
    return data


def _check_points_after(error: Exception, point_list: Point2List) -> None:
    """Raise a clearer error than ``error`` if a point isn't 2 numbers."""
    clearer = _bad_point_error(point_list)
    if clearer is not None:
        raise clearer from None


def get_points_for_thick_line(
    start_x: float, start_y: float, end_x: float, end_y: float, line_width: float
) -> tuple[Point2, Point2, Point2, Point2]:
    """
    Function used internally for Arcade. OpenGL draws triangles only, so a thick
    line must be two triangles that make up a rectangle. This calculates and returns
    those points.
    """
    vector_x = start_x - end_x
    vector_y = start_y - end_y
    perpendicular_x = vector_y
    perpendicular_y = -vector_x
    length = math.sqrt(vector_x * vector_x + vector_y * vector_y)
    if length == 0:
        normal_x = 1.0
        normal_y = 1.0
    else:
        normal_x = perpendicular_x / length
        normal_y = perpendicular_y / length

    half_width = line_width / 2
    shift_x = normal_x * half_width
    shift_y = normal_y * half_width

    r1_x = start_x + shift_x
    r1_y = start_y + shift_y
    r2_x = start_x - shift_x
    r2_y = start_y - shift_y
    r3_x = end_x + shift_x
    r3_y = end_y + shift_y
    r4_x = end_x - shift_x
    r4_y = end_y - shift_y

    return (r1_x, r1_y), (r2_x, r2_y), (r4_x, r4_y), (r3_x, r3_y)


def _generic_draw_line_strip(
    point_list: Point2List, color: RGBOrA255, mode: int = gl.LINE_STRIP
) -> None:
    """
    Draw a line strip. A line strip is a set of continuously connected
    line segments.

    Args:
        point_list:
            List of points making up the line. Each point is in a list.
            So it is a list of lists.
        color:
            A color, specified as an RGBA tuple or a
            :py:class:`.Color` instance.
    """
    # Fail if we don't have a window, context, or right GL abstractions
    window = get_window()
    ctx = window.ctx
    geometry = ctx.generic_draw_line_strip_geometry  # type: ignore
    vertex_buffer = ctx.generic_draw_line_strip_vbo  # type: ignore
    color_buffer = ctx.generic_draw_line_strip_color  # type: ignore
    program = ctx.line_vertex_shader

    # Validate and alpha-pad color, then expand to multi-vertex form since
    # this shader normalizes internally as if made to draw multicolor lines.
    rgba = Color.from_iterable(color)
    num_vertices = len(point_list)  # Fail if it isn't a sized / sequence object

    # Translate Python objects into types Arcade's Buffer objects accept
    color_array = array.array("B", rgba * num_vertices)
    vertex_array = _flatten_points(point_list)
    geometry.num_vertices = num_vertices

    # Double buffer sizes until they can hold all our data
    goal_vertex_buffer_size = len(vertex_array) * 4
    while goal_vertex_buffer_size > vertex_buffer.size:
        vertex_buffer.orphan(color_buffer.size * 2)
        color_buffer.orphan(color_buffer.size * 2)
    else:
        vertex_buffer.orphan()
        color_buffer.orphan()

    ctx.enable(ctx.BLEND)

    # Write data & render
    vertex_buffer.write(vertex_array)
    color_buffer.write(color_array)
    geometry.render(program, mode=mode)

    ctx.disable(ctx.BLEND)
