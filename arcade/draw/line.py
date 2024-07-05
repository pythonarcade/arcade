import array

from arcade import gl
from arcade.types import RGBA255, Color, Point2List
from arcade.window_commands import get_window

from .helpers import _generic_draw_line_strip, get_points_for_thick_line


def draw_line_strip(point_list: Point2List, color: RGBA255, line_width: float = 1) -> None:
    """
    Draw a multi-point line.

    :param point_list: List of x, y points that make up this strip
    :param color: A color, specified as an RGBA tuple or a
        :py:class:`~arcade.types.Color` instance.
    :param line_width: Width of the line
    """
    if line_width == 1:
        _generic_draw_line_strip(point_list, color, gl.LINE_STRIP)
    else:
        triangle_point_list: Point2List = []
        # This needs a lot of improvement
        last_point = None
        for point in point_list:
            if last_point is not None:
                points = get_points_for_thick_line(
                    last_point[0], last_point[1], point[0], point[1], line_width
                )
                reordered_points = points[1], points[0], points[2], points[3]
                triangle_point_list.extend(reordered_points)
            last_point = point
        _generic_draw_line_strip(triangle_point_list, color, gl.TRIANGLE_STRIP)


def draw_line(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    color: RGBA255,
    line_width: float = 1,
) -> None:
    """
    Draw a line.

    :param start_x: x position of line starting point.
    :param start_y: y position of line starting point.
    :param end_x: x position of line ending point.
    :param end_y: y position of line ending point.
    :param color: A color, specified as an RGBA tuple or a
        :py:class:`~arcade.types.Color` instance.
    :param line_width: Width of the line in pixels.
    """
    # Fail if we don't have a window, context, or right GL abstractions
    window = get_window()
    ctx = window.ctx
    program = ctx.shape_line_program
    geometry = ctx.shape_line_geometry  # type: ignore
    line_pos_buffer = ctx.shape_line_buffer_pos  # type: ignore

    # Validate & normalize to a pass the shader an RGBA float uniform
    color_normalized = Color.from_iterable(color).normalized

    # Pass data to the shader
    program["color"] = color_normalized
    program["line_width"] = line_width
    line_pos_buffer.orphan()  # Allocate new buffer internally
    line_pos_buffer.write(data=array.array("f", (start_x, start_y, end_x, end_y)))

    ctx.enable(ctx.BLEND)
    geometry.render(program, mode=gl.LINES, vertices=2)
    ctx.disable(ctx.BLEND)


def draw_lines(point_list: Point2List, color: RGBA255, line_width: float = 1) -> None:
    """
    Draw a set of lines.

    Draw a line between each pair of points specified.

    :param point_list: List of points making up the lines. Each point is
         in a list. So it is a list of lists.
    :param color: A color, specified as an RGBA tuple or a
        :py:class:`~arcade.types.Color` instance.
    :param line_width: Width of the line in pixels.
    """
    # Fail if we don't have a window, context, or right GL abstractions
    window = get_window()
    ctx = window.ctx
    program = ctx.shape_line_program
    geometry = ctx.shape_line_geometry  # type: ignore
    line_buffer_pos = ctx.shape_line_buffer_pos  # type: ignore

    # Validate & normalize to a pass the shader an RGBA float uniform
    color_normalized = Color.from_iterable(color).normalized

    line_pos_array = array.array("f", (v for point in point_list for v in point))
    num_points = len(point_list)

    # Grow buffer until large enough to hold all our data
    goal_buffer_size = num_points * 3 * 4
    while goal_buffer_size > line_buffer_pos.size:
        ctx.shape_line_buffer_pos.orphan(line_buffer_pos.size * 2)  # type: ignore
    else:
        ctx.shape_line_buffer_pos.orphan()  # type: ignore

    ctx.enable(ctx.BLEND)

    # Pass data to shader
    program["line_width"] = line_width
    program["color"] = color_normalized
    line_buffer_pos.write(data=line_pos_array)

    geometry.render(program, mode=gl.LINES, vertices=num_points)

    ctx.disable(ctx.BLEND)
