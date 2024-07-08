from arcade import gl
from arcade.types import RGBOrA255

from .helpers import _generic_draw_line_strip
from .polygon import draw_polygon_outline


def draw_triangle_filled(
    x1: float, y1: float, x2: float, y2: float, x3: float, y3: float, color: RGBOrA255
) -> None:
    """
    Draw a filled in triangle.

    :param x1: x value of first coordinate.
    :param y1: y value of first coordinate.
    :param x2: x value of second coordinate.
    :param y2: y value of second coordinate.
    :param x3: x value of third coordinate.
    :param y3: y value of third coordinate.
    :param color: Color of the triangle as an RGBA :py:class:`tuple` or
        :py:class:`~arcade.types.Color` instance.
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

    :param x1: x value of first coordinate.
    :param y1: y value of first coordinate.
    :param x2: x value of second coordinate.
    :param y2: y value of second coordinate.
    :param x3: x value of third coordinate.
    :param y3: y value of third coordinate.
    :param color: RGBOrA255 of triangle as an RGBA
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    :param border_width: Width of the border in pixels. Defaults to 1.
    """
    point_list = (
        (x1, y1),
        (x2, y2),
        (x3, y3),
    )
    draw_polygon_outline(point_list, color, border_width)
