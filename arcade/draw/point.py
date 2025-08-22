import array

from arcade.types import Color, Point2List, RGBOrA255
from arcade.types.rect import XYWH
from arcade.window_commands import get_window

from .rect import draw_rect_filled


def draw_point(x: float, y: float, color: RGBOrA255, size: float = 1.0) -> None:
    """Draw a 2D point at ``(x, y)`` as a square ``size`` pixels wide.

    The square will be centered on ``(x, y)`` with the given ``color``
    as its fill value.

    To draw more rounded shapes, please see:

    * :py:func:`arcade.draw.circle.draw_circle_filled`
    * :py:func:`pyglet.shapes.Circle`

    Args:
        x:
            The center of the square along the x axis.
        y:
            The center of the square along the y axis.
        color:
            The fill color of the square as an RGBA :py:class:`tuple`,
            RGB py:class:`tuple`, or a :py:class:`.Color` instance.
        size:
             The width and height of the square in pixels.
    """
    draw_rect_filled(XYWH(x, y, size, size), color)


def draw_points(point_list: Point2List, color: RGBOrA255, size: float = 1.0) -> None:
    """Draw 2D points as squares ``size`` pixels  wide.

    Each point in ``point_list`` will be drawn centered on its x and y
    value with the same ``color`` and square ``size`` in pixels.

    To draw more rounded shapes, please see:

    * :py:func:`arcade.draw.circle.draw_circle_filled`
    * :py:func:`pyglet.shapes.Circle`

    Args:
        point_list:
            A :py:class:`list` or :py:class:`tuple` of 2D points.
        color:
            The fill color for the points as an RGBA :py:class:`tuple`,
            RGB :py:class:`tuple`, or :py:class:`.Color` instance.
        size:
            The width and height of each point's square in pixels.
    """
    # Fails immediately if we don't have a window or context
    window = get_window()
    ctx = window.ctx
    program = ctx.shape_rectangle_filled_unbuffered_program  # type: ignore
    geometry = ctx.shape_rectangle_filled_unbuffered_geometry
    buffer = ctx.shape_rectangle_filled_unbuffered_buffer  # type: ignore

    # Validate & normalize to a pass the shader an RGBA float uniform
    color_normalized = Color.from_iterable(color).normalized

    # Get # of points and translate Python tuples to a C-style array
    num_points = len(point_list)
    if num_points == 0:
        return
    point_array = array.array("f", (v for point in point_list for v in point))

    # Resize buffer
    data_size = num_points * 8
    buffer.orphan(size=data_size)

    ctx.enable(ctx.BLEND)

    # Pass data to shader
    program["color"] = color_normalized
    program["shape"] = size, size, 0
    buffer.write(data=point_array)

    # Only render the # of points we have complete data for
    geometry.render(program, instances=num_points)

    ctx.disable(ctx.BLEND)
