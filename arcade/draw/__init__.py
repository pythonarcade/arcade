"""
This module contains commands for basic graphics drawing commands.
(Drawing primitives.)

Many of these commands are slow, because they load everything to the
graphics card each time a shape is drawn. For faster drawing, see the
Buffered Draw Commands.
"""

from .arc import draw_arc_filled, draw_arc_outline
from .parabola import draw_parabola_filled, draw_parabola_outline
from .circle import (
    draw_circle_filled,
    draw_circle_outline,
    draw_ellipse_filled,
    draw_ellipse_outline,
)
from .line import draw_line_strip, draw_line, draw_lines
from .point import draw_point, draw_points
from .polygon import draw_polygon_filled, draw_polygon_outline
from .triangle import draw_triangle_filled, draw_triangle_outline
from .rect import (
    draw_lrbt_rectangle_outline,
    draw_lbwh_rectangle_outline,
    draw_rect_outline,
    draw_lrbt_rectangle_filled,
    draw_lbwh_rectangle_filled,
    draw_rect_filled,
    draw_texture_rect,
    draw_sprite,
    draw_sprite_rect,
)
from .helpers import get_points_for_thick_line

__all__ = [
    # arc
    "draw_arc_filled",
    "draw_arc_outline",
    # parabola
    "draw_parabola_filled",
    "draw_parabola_outline",
    # circle
    "draw_circle_filled",
    "draw_circle_outline",
    "draw_ellipse_filled",
    "draw_ellipse_outline",
    # line
    "draw_line_strip",
    "draw_line",
    "draw_lines",
    # point
    "draw_point",
    "draw_points",
    # polygon
    "draw_polygon_filled",
    "draw_polygon_outline",
    # triangle
    "draw_triangle_filled",
    "draw_triangle_outline",
    # rectangle
    "draw_lrbt_rectangle_outline",
    "draw_lbwh_rectangle_outline",
    "draw_rect_outline",
    "draw_lrbt_rectangle_filled",
    "draw_lbwh_rectangle_filled",
    "draw_rect_filled",
    "draw_texture_rect",
    "draw_sprite",
    "draw_sprite_rect",
    # helpers
    "get_points_for_thick_line",
]
