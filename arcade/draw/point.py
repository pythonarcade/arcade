import array

from arcade.types import Color, RGBA255, PointList
from arcade.types.rect import XYWH
from arcade.window_commands import get_window

from .rect import draw_rect_filled


def draw_point(x: float, y: float, color: RGBA255, size: float) -> None:
    """
    Draw a point.

    :param x: x position of point.
    :param y: y position of point.
    :param color: A color, specified as an RGBA tuple or a
        :py:class:`~arcade.types.Color` instance.
    :param size: Size of the point in pixels.
    """
    draw_rect_filled(XYWH(x, y, size, size), color)


def draw_points(point_list: PointList, color: RGBA255, size: float = 1) -> None:
    """
    Draw a set of points.

    :param point_list: List of points Each point is
         in a list. So it is a list of lists.
    :param color: A color, specified as an RGBA tuple or a
        :py:class:`~arcade.types.Color` instance.
    :param size: Size of the point in pixels.
    """
    # Fails immediately if we don't have a window or context
    window = get_window()
    ctx = window.ctx
    program = ctx.shape_rectangle_filled_unbuffered_program
    geometry = ctx.shape_rectangle_filled_unbuffered_geometry
    buffer = ctx.shape_rectangle_filled_unbuffered_buffer

    # Validate & normalize to a pass the shader an RGBA float uniform
    color_normalized = Color.from_iterable(color).normalized

    # Get # of points and translate Python tuples to a C-style array
    num_points = len(point_list)
    point_array = array.array("f", (v for point in point_list for v in point))

    # Resize buffer
    data_size = num_points * 8
    # if data_size > buffer.size:
    buffer.orphan(size=data_size)

    ctx.enable(ctx.BLEND)

    # Pass data to shader
    program["color"] = color_normalized
    program["shape"] = size, size, 0
    buffer.write(data=point_array)

    # Only render the # of points we have complete data for
    geometry.render(program, mode=ctx.POINTS, vertices=data_size // 8)

    ctx.disable(ctx.BLEND)
