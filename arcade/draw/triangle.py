from arcade import gl
from arcade.types import RGBOrA255

from .helpers import _generic_draw_line_strip
from .polygon import draw_polygon_outline


def draw_triangle_filled(
    x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, color: RGBOrA255
) -> None:
    """
    Draw a filled in triangle.

    Args:
        x1: x value of first coordinate.
        y1: y value of first coordinate.
        x2: x value of second coordinate.
        y2: y value of second coordinate.
        x3: x value of third coordinate.
        y3: y value of third coordinate.
        color: Color of the triangle as an RGBA :py:class:`tuple` or
            :py:class:`.Color` instance.
    """
    point_list = (
        (x1, y1),
        (x2, y2),
        (x3, y3),
    )
    _generic_draw_line_strip(point_list, color, gl.TRIANGLES)


def draw_triangle_outline(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    x3: float,
    y3: float,
    color: RGBOrA255,
    border_width: float = 1,
) -> None:
    """
    Draw a the outline of a triangle.

    Args:
        x1: x value of first coordinate.
        y1: y value of first coordinate.
        x2: x value of second coordinate.
        y2: y value of second coordinate.
        x3: x value of third coordinate.
        y3: y value of third coordinate.
        color: RGBOrA255 of triangle as an RGBA
            :py:class:`tuple` or :py:class:`.Color` instance.
        border_width: Width of the border in pixels. Defaults to 1.
    """
    point_list = (
        (x1, y1),
        (x2, y2),
        (x3, y3),
    )
    draw_polygon_outline(point_list, color, border_width)
